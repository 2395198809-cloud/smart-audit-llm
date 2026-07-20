from pathlib import Path

root = Path("/home/tianlang/smart-audit-llm")
out = root / "reports" / "focused_quantification"
log_dir = out / "smartbugs2_multi" / "semgrep_custom"

samples = [
    "UnauthorizedTokenTransfer",
    "MissingAllowanceTransferFrom",
    "WrongAllowanceOwner",
    "OnlyToCheckedTransfer",
    "PublicBurnFrom",
]

rows = []
ran = 0
detected = 0
located = 0

for name in samples:
    jp = log_dir / f"{name}.json"
    text = jp.read_text(encoding="utf-8", errors="ignore") if jp.exists() else ""
    compact = text.replace(" ", "").replace("\n", "")

    run_ok = jp.exists() and '"results":[' in compact
    hit = run_ok and '"results":[]' not in compact
    loc = hit and any(x in text for x in ["balanceOf[from]", "transfer", "transferFrom", "move", "burnFrom", name])

    ran += int(run_ok)
    detected += int(hit)
    located += int(loc)

    rows.append([
        name,
        "完成" if run_ok else "未完成",
        "通过" if hit else "失败",
        "通过" if loc else "失败",
        str(jp.relative_to(root)) if jp.exists() else "缺失",
    ])

md = out / "smartbugs2_semgrep_custom_metrics.md"
lines = [
    "# SmartBugs2-semgrep-custom 未授权转账多样本量化实验",
    "",
    "| 样本 | 运行状态 | 漏洞识别 | 函数定位 | 输出文件 |",
    "|---|---|---|---|---|",
]

for r in rows:
    lines.append(f"| `{r[0]}` | {r[1]} | {r[2]} | {r[3]} | `{r[4]}` |")

n = len(samples)
lines += [
    "",
    "## 汇总",
    "",
    f"- 样本数：{n}",
    f"- 运行完成率：{ran}/{n} = {ran/n:.1%}",
    f"- 漏洞识别率：{detected}/{n} = {detected/n:.1%}",
    f"- 函数定位率：{located}/{n} = {located/n:.1%}",
]

md.write_text("\n".join(lines), encoding="utf-8")
print(md)
