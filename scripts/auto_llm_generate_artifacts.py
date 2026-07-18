import json
import re
import subprocess
import sys
from pathlib import Path

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3-coder:30b"

REPORTS_DIR = Path("reports/auto_llm")
ARTIFACTS_DIR = Path("auto_llm_artifacts")


def run_command(cmd):
    result = subprocess.run(cmd, text=True, capture_output=True)
    return result.returncode, result.stdout, result.stderr


def extract_contract_name(source_code: str) -> str:
    match = re.search(r"\bcontract\s+([A-Za-z_][A-Za-z0-9_]*)", source_code)
    if not match:
        raise SystemExit("Cannot find contract name in target source")
    return match.group(1)


def run_slither(target_path: Path, output_path: Path):
    if output_path.exists():
        output_path.unlink()

    code, out, err = run_command([
        "slither",
        str(target_path),
        "--json",
        str(output_path),
    ])

    if not output_path.exists():
        print(out)
        print(err)
        raise SystemExit("Slither did not generate JSON output")

    return code, out, err


def summarize_slither(slither_json_path: Path) -> str:
    data = json.loads(slither_json_path.read_text(encoding="utf-8"))
    findings = data.get("results", {}).get("detectors", [])

    lines = []

    for i, finding in enumerate(findings, start=1):
        lines.append(f"Finding {i}")
        lines.append(f"check: {finding.get('check', '')}")
        lines.append(f"impact: {finding.get('impact', '')}")
        lines.append(f"confidence: {finding.get('confidence', '')}")
        lines.append("description:")
        lines.append(finding.get("description", "").strip())
        lines.append("")

    if not lines:
        return "Slither did not report detectors."

    return "\n".join(lines)


def extract_section(text: str, label: str) -> str:
    pattern = rf"### {re.escape(label)}\s*```(?:[a-zA-Z0-9_+-]*)?\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return ""


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/auto_llm_generate_artifacts.py <target-solidity-file>")
        raise SystemExit(1)

    target_path = Path(sys.argv[1])

    if not target_path.exists():
        raise SystemExit(f"Target file not found: {target_path}")

    source_code = target_path.read_text(encoding="utf-8")
    original_contract = extract_contract_name(source_code)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    stem = target_path.stem
    slither_output = REPORTS_DIR / f"{stem}-slither-output.json"

    print(f"Running Slither for {target_path}...")
    run_slither(target_path, slither_output)

    slither_summary = summarize_slither(slither_output)

    prompt = f"""
你是智能合约安全审计、漏洞验证与补丁生成助手。

用户不会告诉你具体漏洞类型。
你必须根据Solidity源码和Slither检测结果，自己判断主要漏洞类型，并生成完整实验材料。

目标合约路径：
{target_path}

原始合约名：
{original_contract}

固定要求：
1. 不要假设用户已经指定漏洞类型。
2. 你需要自己从Slither结果中判断主要漏洞。
3. 如果Slither报告多个问题，请优先选择高危或最能被Foundry测试验证的问题。
4. 输出必须严格包含以下4个部分。
5. 每个部分必须使用指定标题。
6. Solidity代码必须可用于Foundry项目。
7. 修复补丁合约名必须统一为LLMAutoFixed。
8. 攻击测试文件中应测试原始漏洞合约。
9. 修复验证测试文件中应测试LLMAutoFixed。
10. 不要让补丁依赖OpenZeppelin。
11. 不要输出额外章节。
12. 不要把Slither原始报告当作代码输出。
13. 不要输出伪代码。
14. 所有Solidity代码都必须完整，可直接保存为.sol文件。

输出格式必须严格如下：

### AUDIT_REPORT
```markdown
这里输出中文审计报告。必须包含：自动识别出的漏洞类型、漏洞位置、漏洞成因、攻击路径、影响、修复建议。

### ATTACK_TEST

这里输出Foundry攻击PoC测试完整源码。必须import目标合约路径：../{target_path}

### PATCH

这里输出修复后的完整Solidity源码。合约名必须是LLMAutoFixed。

### VALIDATION_TEST

这里输出Foundry修复验证测试完整源码。必须import ../src/LLMAutoFixed.sol，并证明攻击失败且正常功能可用。

请注意：

- 如果漏洞是重入漏洞，攻击测试应使用恶意合约receive()回调重入。
- 如果漏洞是tx.origin权限绕过，攻击测试应模拟owner调用钓鱼合约，并使用vm.startPrank(owner, owner)设置msg.sender和
tx.origin。

- 修复补丁应尽量保持原始public/external接口语义。
- 修复测试不能只检查编译通过，必须验证攻击失败和正常功能仍然可用。

Solidity源码：

{source_code}

Slither检测结果摘要：

{slither_summary}

"""

    print(f"Requesting Ollama model: {MODEL}...")
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.15,
                "num_predict": 12000,
            },
        },
        timeout=600,
    )
    response.raise_for_status()

    raw_output = response.json()["response"]

    raw_path = REPORTS_DIR / f"{stem}-raw-output-qwen3-coder-30b.md"
    raw_path.write_text(raw_output, encoding="utf-8")

    audit_report = extract_section(raw_output, "AUDIT_REPORT")
    attack_test = extract_section(raw_output, "ATTACK_TEST")
    patch = extract_section(raw_output, "PATCH")
    validation_test = extract_section(raw_output, "VALIDATION_TEST")

    out_dir = ARTIFACTS_DIR / f"{stem}_qwen3_coder_30b"
    out_dir.mkdir(parents=True, exist_ok=True)

    if audit_report:
        (out_dir / "audit_report.md").write_text(audit_report + "\n", encoding="utf-8")

    if attack_test:
        (out_dir / "LLMAutoAttack.t.sol").write_text(attack_test + "\n", encoding="utf-8")

    if patch:
        (out_dir / "LLMAutoFixed.sol").write_text(patch + "\n", encoding="utf-8")

    if validation_test:
        (out_dir / "LLMAutoValidation.t.sol").write_text(validation_test + "\n", encoding="utf-8")

    print("Generated artifacts:")
    print(f"- raw output: {raw_path}")
    print(f"- output dir: {out_dir}")

    missing = []

    if not audit_report:
        missing.append("AUDIT_REPORT")
    if not attack_test:
        missing.append("ATTACK_TEST")
    if not patch:
        missing.append("PATCH")
    if not validation_test:
        missing.append("VALIDATION_TEST")

    if missing:
        print("Warning: missing sections:", ", ".join(missing))
        print("Inspect raw output manually.")

    print("No generated artifact was applied to src/ or test/.")

if __name__ == "__main__":
    main()
