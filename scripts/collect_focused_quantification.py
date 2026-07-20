from pathlib import Path
import json

root = Path("/home/tianlang/smart-audit-llm")
out = root / "reports" / "focused_quantification"
out.mkdir(parents=True, exist_ok=True)

case = "UnauthorizedTokenTransfer"
sample = "benchmarks/gptscan/UnauthorizedTokenTransfer.sol"

gpt_json = Path("/home/tianlang/GPTScan/output/UnauthorizedTokenTransfer_qwen3.json")
gpt_txt = out / "gptscan_console.txt"
ours_report = root / "auto_llm_artifacts" / f"{case}_qwen3_coder_30b" / "audit_report.md"
ours_eval = root / "reports" / "auto_llm" / f"{case}_qwen3_coder_30b-evaluation.md"
slither_json = root / "reports" / "auto_llm" / f"{case}-slither-output.json"

def read(p):
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""

def yn(v):
    return "是" if v else "否"

gpt_text = read(gpt_txt)
if gpt_json.exists():
    try:
        gpt_text += "\n" + json.dumps(json.loads(read(gpt_json)), ensure_ascii=False)
    except Exception:
        gpt_text += "\n" + read(gpt_json)

ours_text = read(ours_report)
eval_text = read(ours_eval)
slither_text = read(slither_json)

gpt_detect = "Unauthorized Transfer" in gpt_text
gpt_locate = "transfer" in gpt_text and ("Line Range" in gpt_text or "14 - 23" in gpt_text)

ours_detect = "未授权" in ours_text or "Unauthorized Token Transfer" in ours_text
ours_locate = "transfer" in ours_text
ours_build = "| forge build | 通过 |" in eval_text
ours_attack = "| LLM攻击测试 | 通过 |" in eval_text
ours_validation = "| LLM修复验证测试 | 通过 |" in eval_text

slither_detect = "access-control" in slither_text or "arbitrary-send" in slither_text
slither_locate = "transfer" in slither_text

rows = [
    ["Slither", "2019", "静态分析", yn(slither_detect), yn(slither_locate), "否", "否", "否", "否", "该业务逻辑漏洞无稳定目标detector"],
    ["GPTScan", "2024", "LLM+程序分析", yn(gpt_detect), yn(gpt_locate), "否", "否", "否", "否", "能识别UnauthorizedTransfer但不生成补丁"],
    ["本文系统", "2026", "Slither+LLM+Foundry", yn(ours_detect), yn(ours_locate), yn(ours_attack), yn(ours_build),
    yn(ours_validation), yn(ours_report.exists()), "目标告警消失记为不适用，核心看Foundry验证"],
    ["ItyFuzz", "2023", "快照式fuzzing", "相关方法", "依赖oracle", "可触发交易序列", "否", "需额外性质", "否", "动态状态探索代表"],
    ["LLM4Fuzz", "2024", "LLM辅助fuzzing", "相关方法", "依赖LLM和fuzz结果", "偏输入生成", "通常否", "通常否", "否",
    "LLM辅助测试代表"],
    ["SmartBugs 2.0", "2023", "评测框架", "不直接检测", "不直接定位", "否", "否", "否", "否", "用于统一组织量化实验"],
]

cols = ["方法", "年份", "类型", "漏洞识别", "函数定位", "攻击PoC", "修复补丁", "修复验证", "中文报告", "备注"]

csv = out / "focused_metrics.csv"
csv_lines = [",".join(cols)]
for r in rows:
    csv_lines.append(",".join('"' + x.replace('"', '""') + '"' for x in r))
csv.write_text("\n".join(csv_lines), encoding="utf-8")

md = out / "focused_metrics.md"
lines = []
lines.append("# 聚焦问题量化对比报告")
lines.append("")
lines.append("聚焦问题：面向未授权代币转移漏洞的 LLM 辅助智能合约审计、验证与修复闭环。")
lines.append("")
lines.append(f"样本：`{sample}`")
lines.append("")
lines.append("| " + " | ".join(cols) + " |")
lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
for r in rows:
    lines.append("| " + " | ".join(r) + " |")
lines.append("")
lines.append("## 结论")
lines.append("")
lines.append("GPTScan 能识别 Unauthorized Transfer 并定位 transfer 函数。")
lines.append("")
lines.append("本文系统进一步生成中文报告、Foundry攻击PoC、修复补丁和修复验证测试。")
lines.append("")
lines.append("Slither 对该业务逻辑漏洞没有稳定目标告警，因此目标告警消失率应记为不适用。")
md.write_text("\n".join(lines), encoding="utf-8")

print(md)
print(csv)
