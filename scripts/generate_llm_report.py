import json
from pathlib import Path

import requests

CONTRACT_PATH = Path("src/VulnerableVault.sol")
SLITHER_PATH = Path("slither-output.json")
REPORT_PATH = Path("reports/audit_report_llm.md")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3-coder:30b"


def main():
    contract_code = CONTRACT_PATH.read_text(encoding="utf-8")
    slither_data = json.loads(SLITHER_PATH.read_text(encoding="utf-8"))

    prompt = f"""
你是一名严谨的智能合约安全审计员。请基于 Solidity 源码和 Slither 扫描结果，生成中文审计报告。

要求：
1. 不要编造源码和 Slither 结果都无法支持的问题。
2. 重点解释 Slither 已经发现的问题。
3. 每个问题包含：漏洞名称、风险等级、漏洞位置、漏洞原因、攻击路径、影响、修复建议。
4. 如果能判断 PoC 思路，请说明如何用 Foundry 验证。
5. 输出 Markdown。
6. 语言要适合本科毕业设计报告使用，清晰、严谨。

Solidity 源码：

```solidity
{contract_code}

Slither JSON：

{json.dumps(slither_data, ensure_ascii=False, indent=2)}

"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0
            },
        },
        timeout=180,
    )

    response.raise_for_status()
    report = response.json()["response"]

    REPORT_PATH.parent.mkdir(exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")

    print(f"LLM report written to {REPORT_PATH}")

if __name__ == "__main__":
    main()
