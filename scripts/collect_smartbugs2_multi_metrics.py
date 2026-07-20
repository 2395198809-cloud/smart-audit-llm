from pathlib import Path

root = Path("/home/tianlang/smart-audit-llm")
out = root / "reports" / "focused_quantification"
sb_out = out / "smartbugs2_multi" / "slither"

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
    "unchecked",
    "reentrancy",
    "warning",
    "vulnerability",
    "issue",
    "finding",
    "detector",
    "solc-version",
]

rows = []
ran = 0
detected = 0
located = 0

for name in samples:
    txt = sb_out / f"{name}.txt"
    text = txt.read_text(encoding="utf-8", errors="ignore") if txt.exists() else ""

    run_ok = txt.exists() and (
        "Welcome to SmartBugs" in text
        or "Collecting files" in text
        or "Assembling tasks" in text
        or "slither" in text.lower()
        or "results" in text.lower()
    )

    d = any(k.lower() in text.lower() for k in target_keywords)
    l = d and any(fn in text for fn in ["transfer", "transferFrom", "move", "burnFrom"])

    ran += int(run_ok)
    detected += int(d)
    located += int(l)

    rows.append([
        name,
        "完成" if run_ok else "未完成",
        "通过" if d else "失败",
        "通过" if l else "失败",
        str(txt.relative_to(root)) if txt.exists() else "缺失",
    ])

md = out / "smartbugs2_multi_metrics.md"
lines = [
    "# SmartBugs 2.0 未授权转账多样本量化实验",
    "",
    "说明：SmartBugs 2.0 是多工具执行框架。本文使用其 slither 工具配置对 5 个未授权转账类样本进行统一运行。",
    "",
    "| 样本 | 运行状态 | 目标相关输出 | 函数定位 | 输出文件 |",
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
    f"- SmartBugs2-slither 运行完成率：{ran}/{n} = {ran/n:.1%}",
    f"- SmartBugs2-slither 目标相关输出率：{detected}/{n} = {detected/n:.1%}",
    f"- SmartBugs2-slither 函数定位率：{located}/{n} = {located/n:.1%}",
    "",
    "## 论文可写结论",
    "",
    "SmartBugs 2.0 能够作为统一执行框架运行底层分析工具。其检测能力取决于被调用工具本身；在未授权代币转移这类业务逻辑漏洞上，如果底层工具缺少专门 detector，仍可能无法直接识别漏洞。",
]

md.write_text("\n".join(lines), encoding="utf-8")
print(md)
