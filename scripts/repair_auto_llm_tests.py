import re
import sys
from pathlib import Path

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3-coder:30b"


def extract_section(text: str, label: str) -> str:
    pattern = rf"### {re.escape(label)}\s*```(?:[a-zA-Z0-9_+-]*)?\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/repair_auto_llm_tests.py <artifact-dir> <evaluation-report>")
        raise SystemExit(1)

    artifact_dir = Path(sys.argv[1])
    evaluation_report = Path(sys.argv[2])

    if not artifact_dir.exists():
        raise SystemExit(f"Artifact dir not found: {artifact_dir}")

    if not evaluation_report.exists():
        raise SystemExit(f"Evaluation report not found: {evaluation_report}")

    attack_test_path = artifact_dir / "LLMAutoAttack.t.sol"
    validation_test_path = artifact_dir / "LLMAutoValidation.t.sol"
    patch_path = artifact_dir / "LLMAutoFixed.sol"

    if not attack_test_path.exists():
        raise SystemExit(f"Missing {attack_test_path}")

    if not validation_test_path.exists():
        raise SystemExit(f"Missing {validation_test_path}")

    if not patch_path.exists():
        raise SystemExit(f"Missing {patch_path}")

    vulnerable_source = Path("src/VulnerableWallet.sol").read_text(encoding="utf-8")
    attack_test = attack_test_path.read_text(encoding="utf-8")
    validation_test = validation_test_path.read_text(encoding="utf-8")
    patch = patch_path.read_text(encoding="utf-8")
    eval_log = evaluation_report.read_text(encoding="utf-8")

    prompt = f"""
你是Foundry智能合约测试修复助手。

任务：根据失败日志，修复LLM自动生成的测试文件。
禁止修改补丁合约LLMAutoFixed.sol。
只输出两个完整Solidity测试文件。

背景：
目标漏洞是tx.origin权限绕过。
VulnerableWallet使用tx.origin == owner做权限判断。
LLMAutoFixed使用msg.sender == owner做权限判断。
LLMAutoFixed.sol已经通过Slither重扫，不要修改它。

关键语义要求：
1. VulnerableWallet的owner必须通过vm.prank(owner)部署，不能让测试合约成为owner。
2. LLMAutoFixed的owner也必须通过vm.prank(owner)部署，不能让测试合约成为owner。
3. tx.origin钓鱼攻击PoC必须模拟：
    owner -> malicious.attack() -> wallet.withdrawAll(hacker)
4. 在Foundry中必须使用vm.startPrank(owner, owner)来同时设置msg.sender和tx.origin。
5. 在VulnerableWallet攻击测试中，攻击应该成功，wallet余额变为0，hacker收到10 ether。
6. 在LLMAutoFixed验证测试中，同样的钓鱼攻击应该失败，wallet余额仍为10 ether，hacker余额为0。
7. LLMAutoFixed验证测试还要证明owner直接withdrawAll(hacker)仍然成功。
8. 不要使用vm.deal(address(wallet), 10 ether)给合约硬塞余额，应通过构造函数payable部署时转入10 ether。
9. 不要输出解释，不要输出Markdown标题以外的额外内容。

输出格式必须严格如下：

### ATTACK_TEST
```solidity
这里输出修复后的完整LLMAutoAttack.t.sol

### VALIDATION_TEST

这里输出修复后的完整LLMAutoValidation.t.sol

原始漏洞合约VulnerableWallet.sol：

{vulnerable_source}

补丁合约LLMAutoFixed.sol，不要修改：

{patch}

原始LLM攻击测试：

{attack_test}

原始LLM修复验证测试：

{validation_test}

Foundry失败日志：

{eval_log}

"""

    print(f"Requesting Ollama model: {MODEL}...")
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 8000,
            },
        },
        timeout=600,
    )
    response.raise_for_status()

    raw_output = response.json()["response"]

    out_dir = artifact_dir.parent / f"{artifact_dir.name}_repaired_tests"
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "repair_raw_output.md").write_text(raw_output, encoding="utf-8")

    repaired_attack = extract_section(raw_output, "ATTACK_TEST")
    repaired_validation = extract_section(raw_output, "VALIDATION_TEST")

    if repaired_attack:
        (out_dir / "LLMAutoAttack.t.sol").write_text(repaired_attack + "\n", encoding="utf-8")

    if repaired_validation:
        (out_dir / "LLMAutoValidation.t.sol").write_text(repaired_validation + "\n", encoding="utf-8")

    # Copy original patch and audit report for evaluation convenience.
    (out_dir / "LLMAutoFixed.sol").write_text(patch, encoding="utf-8")

    audit_report = artifact_dir / "audit_report.md"
    if audit_report.exists():
        (out_dir / "audit_report.md").write_text(audit_report.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"Repaired tests written to {out_dir}")

    missing = []

    if not repaired_attack:
        missing.append("ATTACK_TEST")
    if not repaired_validation:
        missing.append("VALIDATION_TEST")

    if missing:
        print("Warning: missing sections:", ", ".join(missing))
        print(f"Inspect raw output: {out_dir / 'repair_raw_output.md'}")

if __name__ == "__main__":
    main()
