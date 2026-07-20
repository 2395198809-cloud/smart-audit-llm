from pathlib import Path
import csv

root = Path("/home/tianlang/smart-audit-llm")
out = root / "reports" / "focused_quantification"
out.mkdir(parents=True, exist_ok=True)

samples = [
    "UnauthorizedTokenTransfer",
    "MissingAllowanceTransferFrom",
    "WrongAllowanceOwner",
    "OnlyToCheckedTransfer",
    "PublicBurnFrom",
]

def read(path):
    if path.exists():
        return path.read_text(encoding="utf-8", errors="ignore")
    return ""

rows = []
audit_ok = 0
build_ok = 0
attack_ok = 0
validation_ok = 0

for name in samples:
    artifact = root / "auto_llm_artifacts" / f"{name}_qwen3_coder_30b"
    report = artifact / "audit_report.md"
    eval_md = root / "reports" / "auto_llm" / f"{name}_qwen3_coder_30b-evaluation.md"

    report_text = read(report)
    eval_text = read(eval_md)

    audit = report.exists() and any(k in report_text for k in ["未授权", "授权", "权限", "Unauthorized"])
    build = "| forge build | 通过 |" in eval_text
    attack = "| LLM攻击测试 | 通过 |" in eval_text
    validation = "| LLM修复验证测试 | 通过 |" in eval_text

    audit_ok += int(audit)
    build_ok += int(build)
    attack_ok += int(attack)
    validation_ok += int(validation)

    rows.append([
        name,
        "通过" if audit else "失败",
        "通过" if build else "失败",
        "通过" if attack else "失败",
        "通过" if validation else "失败",
        str(eval_md.relative_to(root)) if eval_md.exists() else "缺失",
    ])

csv_path = out / "multi_unauthorized_metrics.csv"
with csv_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["样本", "审计报告", "补丁编译", "攻击PoC", "修复验证", "评估报告"])
    writer.writerows(rows)

md_path = out / "multi_unauthorized_metrics.md"
lines = [
    "# 未授权转账多样本量化实验",
    "",
    "聚焦问题：未授权代币转移 / 权限绕过型资产转移。",
    "",
    "| 样本 | 审计报告 | 补丁编译 | 攻击PoC | 修复验证 | 评估报告 |",
    "|---|---|---|---|---|---|",
]

for r in rows:
    lines.append(f"| `{r[0]}` | {r[1]} | {r[2]} | {r[3]} | {r[4]} | `{r[5]}` |")

n = len(samples)
lines += [
    "",
    "## 汇总",
    "",
    f"- 样本数：{n}",
    f"- 审计报告识别率：{audit_ok}/{n} = {audit_ok/n:.1%}",
    f"- 补丁编译通过率：{build_ok}/{n} = {build_ok/n:.1%}",
    f"- 攻击PoC成功率：{attack_ok}/{n} = {attack_ok/n:.1%}",
    f"- 修复验证通过率：{validation_ok}/{n} = {validation_ok/n:.1%}",
    "",
    "## 论文可写结论",
    "",
    "多样本实验用于观察 LLM 在同一类业务逻辑漏洞上的稳定性。若某些样本攻击PoC或修复验证失败，应作为失败案例分析，说明LLM 生成测试和补丁仍需自动评估与人工审批。",
]

md_path.write_text("\n".join(lines), encoding="utf-8")

print(md_path)
print(csv_path)
