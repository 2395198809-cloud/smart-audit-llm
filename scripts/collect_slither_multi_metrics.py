from pathlib import Path
import json

root = Path("/home/tianlang/smart-audit-llm")
out = root / "reports" / "focused_quantification"
slither_out = out / "slither_multi"

samples = [
    "UnauthorizedTokenTransfer",
    "MissingAllowanceTransferFrom",
    "WrongAllowanceOwner",
    "OnlyToCheckedTransfer",
    "PublicBurnFrom",
]

target_keywords = [
    "access-control",
    "arbitrary-send",
    "tx-origin",
    "unchecked-lowlevel",
    "controlled-delegatecall",
]

rows = []
detected = 0
located = 0

for name in samples:
    txt_path = slither_out / f"{name}.txt"
    json_path = slither_out / f"{name}.json"

    text = txt_path.read_text(encoding="utf-8", errors="ignore") if txt_path.exists() else ""
    json_text = json_path.read_text(encoding="utf-8", errors="ignore") if json_path.exists() else ""

    d = any(k in text or k in json_text for k in target_keywords)
    l = d and any(fn in text or fn in json_text for fn in ["transfer", "transferFrom", "move", "burnFrom"])

    detected += int(d)
    located += int(l)

    rows.append([
        name,
        "通过" if d else "失败",
        "通过" if l else "失败",
        str(txt_path.relative_to(root)) if txt_path.exists() else "缺失",
    ])

md = out / "slither_multi_metrics.md"
lines = [
    "# Slither 未授权转账多样本量化实验",
    "",
    "说明：Slither 对未授权代币转移这类业务逻辑漏洞缺少稳定专用 detector，因此这里只统计是否出现目标相关告警。",
    "",
    "| 样本 | 目标相关告警 | 函数定位 | Slither输出 |",
    "|---|---|---|---|",
]

for r in rows:
    lines.append(f"| `{r[0]}` | {r[1]} | {r[2]} | `{r[3]}` |")

n = len(samples)
lines += [
    "",
    "## 汇总",
    "",
    f"- 样本数：{n}",
    f"- Slither目标相关告警率：{detected}/{n} = {detected/n:.1%}",
    f"- Slither函数定位率：{located}/{n} = {located/n:.1%}",
]

md.write_text("\n".join(lines), encoding="utf-8")
print(md)
