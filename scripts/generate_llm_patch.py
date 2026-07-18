import json
import re
import subprocess
from pathlib import Path

import requests

SOURCE_PATH = Path("src/VulnerableVault.sol")
SLITHER_PATH = Path("slither-output.json")
CANDIDATES_DIR = Path("candidates")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3-coder:30b"


def looks_like_solidity_contract(block: str) -> bool:
    required = [
        "pragma solidity",
        "contract LLMFixedVault",
        "mapping(address => uint256) public balances",
        "function deposit() external payable",
        "function withdraw() external",
        "function totalBalance() external view returns (uint256)",
    ]

    return all(item in block for item in required)


def extract_solidity_blocks(text: str) -> list[str]:
    solidity_blocks = re.findall(r"```solidity\s*(.*?)```", text, re.DOTALL)

    generic_blocks = re.findall(r"```\s*(.*?)```", text, re.DOTALL)

    all_blocks = solidity_blocks + generic_blocks

    candidates = []
    for block in all_blocks:
        block = block.strip()
        if looks_like_solidity_contract(block):
            candidates.append(block)

    if looks_like_solidity_contract(text.strip()):
        candidates.append(text.strip())

    unique_candidates = []
    seen = set()

    for candidate in candidates:
        if candidate not in seen:
            unique_candidates.append(candidate)
            seen.add(candidate)

    return unique_candidates

def run_command(cmd):
    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
    )
    return result.returncode, result.stdout, result.stderr



def summarize_slither(slither_data: dict) -> str:
    findings = slither_data.get("results", {}).get("detectors", [])
    lines = []

    for finding in findings:
        check = finding.get("check", "")
        impact = finding.get("impact", "")
        confidence = finding.get("confidence", "")
        description = finding.get("description", "").strip()

        if check == "reentrancy-eth":
            lines.append(f"check: {check}")
            lines.append(f"impact: {impact}")
            lines.append(f"confidence: {confidence}")
            lines.append("description:")
            lines.append(description)

    if not lines:
        return "Target withdraw function is vulnerable to reentrancy. Use Checks-Effects-Interactions."

    return "\n".join(lines)

def main():
    print("Reading source and Slither report...")

    source_code = SOURCE_PATH.read_text(encoding="utf-8")
    slither_data = json.loads(SLITHER_PATH.read_text(encoding="utf-8"))
    slither_summary = summarize_slither(slither_data)

    prompt = f"""
你是 Solidity 代码补丁生成器，不是审计报告生成器。

任务：输出 3 个完整 Solidity 合约候选版本，用于替换 src/LLMFixedVault.sol。

绝对禁止：
- 禁止输出解释、分析、标题、建议、Markdown 列表。
- 禁止引入 OpenZeppelin。
- 禁止使用 ReentrancyGuard。
- 禁止修改 Solidity 版本。
- 禁止修改 withdraw() 接口。
- 禁止生成 withdraw(uint256 amount)。
- 禁止修改合约名。
- 禁止输出 VulnerableVault 合约名。
- 禁止输出 import 语句。
- 禁止输出中文说明。

每个候选都必须是一个独立的 ```solidity 代码块。

每个候选必须满足：
- 第一行必须是 // SPDX-License-Identifier: MIT
- 必须包含 pragma solidity ^0.8.20;
- 合约名必须是 LLMFixedVault
- 必须包含 mapping(address => uint256) public balances;
- 必须包含 function deposit() external payable
- 必须包含 function withdraw() external
- 必须包含 function totalBalance() external view returns (uint256)
- totalBalance() 必须返回 address(this).balance
- withdraw() 必须使用 Checks-Effects-Interactions

withdraw() 必须严格使用以下逻辑：

function withdraw() external {{
    uint256 amount = balances[msg.sender];
    require(amount > 0, "no balance");

    balances[msg.sender] = 0;

    (bool ok, ) = msg.sender.call{{value: amount}}("");
    require(ok, "transfer failed");
}}

你只能在以下位置做轻微变化：
- require 的错误字符串
- 局部变量名不能变，必须仍然叫 amount
- 转账结果变量名不能变，必须仍然叫 ok

请严格输出 3 个 Solidity 代码块，格式如下：

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LLMFixedVault {{
    mapping(address => uint256) public balances;

    function deposit() external payable {{
        balances[msg.sender] += msg.value;
    }}

    function withdraw() external {{
        uint256 amount = balances[msg.sender];
        require(amount > 0, "no balance");

        balances[msg.sender] = 0;

        (bool ok, ) = msg.sender.call{{value: amount}}("");
        require(ok, "transfer failed");
    }}

    function totalBalance() external view returns (uint256) {{
        return address(this).balance;
    }}
}}

下面是漏洞合约源码，仅用于理解上下文，不要照抄合约名：

{source_code}

下面是 Slither 检测摘要，仅用于理解漏洞，不要输出报告：

{slither_summary}

"""

    print("Requesting Ollama model...")
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 4096,
            },
        },
        timeout=240,
    )

    response.raise_for_status()

    print("Parsing model output...")
    raw_output = response.json()["response"]

    Path("reports").mkdir(exist_ok=True)
    Path("reports/llm_patch_raw_output.md").write_text(raw_output, encoding="utf-8")

    candidates = extract_solidity_blocks(raw_output)

    CANDIDATES_DIR.mkdir(exist_ok=True)

    for old_file in CANDIDATES_DIR.glob("LLMFixedVault_candidate_*.sol"):
        old_file.unlink()

    if not candidates:
        raise SystemExit("No Solidity candidates generated")

    print(f"Extracted {len(candidates)} candidate block(s).")

    for i, fixed_code in enumerate(candidates[:3], start=1):
        output_path = CANDIDATES_DIR / f"LLMFixedVault_candidate_{i}.sol"
        output_path.write_text(fixed_code + "\n", encoding="utf-8")
        print(f"Candidate written to {output_path}")

    print("\nRunning structure validation for generated candidates...")

    for candidate_path in sorted(CANDIDATES_DIR.glob("LLMFixedVault_candidate_*.sol")):
        print(f"\nValidating {candidate_path}...")
        code, out, err = run_command(
            ["python3", "scripts/validate_llm_patch.py", str(candidate_path)]
        )

        if out:
            print(out)
        if err:
            print(err)

        if code != 0:
            print("candidate rejected")
        else:
            print("candidate passed structure validation")

    print("\nGeneration finished. No candidate was applied to src/LLMFixedVault.sol.")

if __name__ == "__main__":
    main()
