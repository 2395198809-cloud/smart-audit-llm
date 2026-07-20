from pathlib import Path

root = Path("/home/tianlang/smart-audit-llm")
out = root / "reports" / "focused_quantification"
gpt_out = out / "gptscan_multi"

samples = [
    "UnauthorizedTokenTransfer",
    "MissingAllowanceTransferFrom",
    "WrongAllowanceOwner",
    "OnlyToCheckedTransfer",
    "PublicBurnFrom",
]

rows = []
detected = 0
located = 0

for name in samples:
    txt = gpt_out / f"{name}.txt"
    text = txt.read_text(encoding="utf-8", errors="ignore") if txt.exists() else ""

    d = "Unauthorized Transfer" in text
    l = d and ("Line Range" in text or "transfer" in text or "burnFrom" in text or "move" in text)

    detected += int(d)
    located += int(l)

    rows.append((name, "通过" if d else "失败", "通过" if l else "失败", str(txt.relative_to(root)) if txt.exists()
    else "缺失"))

md = out / "gptscan_multi_metrics.md"
lines = [
    "# GPTScan 未授权转账多样本量化实验",
    "",
    "| 样本 | 漏洞识别 | 函数定位 | GPTScan输出 |",
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
    f"- GPTScan漏洞识别率：{detected}/{n} = {detected/n:.1%}",
    f"- GPTScan函数定位率：{located}/{n} = {located/n:.1%}",
]

md.write_text("\n".join(lines), encoding="utf-8")
print(md)
