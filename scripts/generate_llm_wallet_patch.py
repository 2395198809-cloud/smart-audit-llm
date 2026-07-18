import json
import re
import subprocess
from pathlib import Path

import requests

SOURCE_PATH = Path("src/VulnerableWallet.sol")
SLITHER_PATH = Path("wallet-slither-output.json")
CANDIDATES_DIR = Path("candidates_wallet")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3-coder:30b"


def looks_like_solidity_contract(block: str) -> bool:
    required = [
        "pragma solidity",
        "contract LLMFixedWallet",
        "address public owner",
        "constructor() payable",
        "function withdrawAll(address payable to) external",
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
    result = subprocess.run(cmd, text=True, capture_output=True)
    return result.returncode, result.stdout, result.stderr


def summarize_slither(slither_data: dict) -> str:
    findings = slither_data.get("results", {}).get("detectors", [])
    lines = []

    for finding in findings:
        check = finding.get("check", "")
        if check in ("tx-origin", "arbitrary-send-eth"):
            lines.append(f"check: {check}")
            lines.append(f"impact: {finding.get('impact', '')}")
            lines.append(f"confidence: {finding.get('confidence', '')}")
            lines.append("description:")
            lines.append(finding.get("description", "").strip())
            lines.append("")

    if not lines:
        return "The wallet uses tx.origin for authorization. Replace tx.origin with msg.sender."

    return "\n".join(lines)


def main():
    print("Reading wallet source and Slither report...")

    source_code = SOURCE_PATH.read_text(encoding="utf-8")
    slither_data = json.loads(SLITHER_PATH.read_text(encoding="utf-8"))
    slither_summary = summarize_slither(slither_data)

    prompt = f"""
你是Solidity代码补丁生成器，不是审计报告生成器。

任务：输出3个完整Solidity合约候选版本，用于替换src/LLMFixedWallet.sol。

绝对禁止：
- 禁止输出解释、分析、标题、建议、Markdown列表。
- 禁止引入OpenZeppelin。
- 禁止使用Ownable或onlyOwner。
- 禁止修改Solidity版本。
- 禁止修改withdrawAll(address payable to)接口。
- 禁止生成withdrawAll()无参数版本。
- 禁止修改合约名。
- 禁止输出VulnerableWallet合约名。
- 禁止输出import语句。
- 禁止使用tx.origin。
- 禁止输出中文说明。

每个候选都必须是一个独立的```solidity代码块。

每个候选必须满足：
- 第一行必须是// SPDX-License-Identifier: MIT
- 必须包含pragma solidity ^0.8.20;
- 合约名必须是LLMFixedWallet
- 必须包含address public owner;
- 必须包含constructor() payable
- 必须包含function withdrawAll(address payable to) external
- 必须包含function totalBalance() external view returns (uint256)
- totalBalance()必须返回address(this).balance
- 权限校验必须使用require(msg.sender == owner, "not owner");
- 不能出现tx.origin

withdrawAll()必须严格使用以下逻辑：

function withdrawAll(address payable to) external {{
    require(msg.sender == owner, "not owner");

    (bool ok, ) = to.call{{value: address(this).balance}}("");
    require(ok, "transfer failed");
}}

请严格输出3个Solidity代码块，格式如下：

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LLMFixedWallet {{
    address public owner;

    constructor() payable {{
        owner = msg.sender;
    }}

    function withdrawAll(address payable to) external {{
        require(msg.sender == owner, "not owner");

        (bool ok, ) = to.call{{value: address(this).balance}}("");
        require(ok, "transfer failed");
    }}

    function totalBalance() external view returns (uint256) {{
        return address(this).balance;
    }}
}}

下面是漏洞合约源码，仅用于理解上下文，不要照抄合约名：

{source_code}

下面是Slither检测摘要，仅用于理解漏洞，不要输出报告：

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
    Path("reports/llm_wallet_patch_raw_output.md").write_text(raw_output, encoding="utf-8")

    candidates = extract_solidity_blocks(raw_output)

    CANDIDATES_DIR.mkdir(exist_ok=True)

    for old_file in CANDIDATES_DIR.glob("LLMFixedWallet_candidate_*.sol"):
        old_file.unlink()

    if not candidates:
        raise SystemExit("No Solidity wallet candidates generated")

    print(f"Extracted {len(candidates)} candidate block(s).")

    for i, fixed_code in enumerate(candidates[:3], start=1):
        output_path = CANDIDATES_DIR / f"LLMFixedWallet_candidate_{i}.sol"
        output_path.write_text(fixed_code + "\n", encoding="utf-8")
        print(f"Candidate written to {output_path}")

    print("\nRunning structure validation for generated wallet candidates...")

    for candidate_path in sorted(CANDIDATES_DIR.glob("LLMFixedWallet_candidate_*.sol")):
        print(f"\nValidating {candidate_path}...")
        code, out, err = run_command(
            ["python3", "scripts/validate_llm_wallet_patch.py", str(candidate_path)]
        )

        if out:
            print(out)
        if err:
            print(err)

        if code != 0:
            print("candidate rejected")
        else:
            print("candidate passed structure validation")

    print("\nGeneration finished. No candidate was applied to src/LLMFixedWallet.sol.")

if __name__ == "__main__":
    main()
