import csv, re, math
from pathlib import Path
from collections import defaultdict

ROOT = Path("/home/tianlang/smart-audit-llm")
OUT = ROOT / "reports/publish_exp_60_system_repeat_keep"
MANIFEST = ROOT / "reports/publish_exp/sample_manifest.csv"

BASE_RUNTIME = OUT / "system_v2_repeat_60_runtime.csv"
RESUME_RUNTIME = OUT / "system_v2_repeat_60_runtime_resume.csv"

SUMMARY_MD = OUT / "system_v2_repeat_60_summary.md"
ROUND_CSV = OUT / "system_v2_repeat_60_accuracy_by_round.csv"
VAR_CSV = OUT / "system_v2_repeat_60_accuracy_variance.csv"
TIME_CSV = OUT / "system_v2_repeat_60_runtime_variance.csv"
DETAIL_CSV = OUT / "system_v2_repeat_60_sample_stage_detail.csv"

TARGET_RE = re.compile(
    r"未授权|权限绕过|授权绕过|任意用户|任意地址|任意转移|任意销毁|任意提取|"
    r"unauthorized|unauthorised|authorization bypass|access control|"
    r"missing allowance|without approval|without authorization|without permission|"
    r"approval check|operator approval|allowance check",
    re.I,
)

NEG_RE = re.compile(
    r"未发现|没有发现|无漏洞|不存在.*漏洞|不存在未授权|"
    r"not vulnerable|no vulnerability|no unauthorized|safe implementation",
    re.I,
)

def read_text(p):
    try:
        return Path(p).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def pct(a, b):
    return a / b * 100 if b else 0.0

def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0

def var(xs):
    if not xs:
        return 0.0
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)

def std(xs):
    return math.sqrt(var(xs))

def find_report(artifact_dir):
    p = Path(artifact_dir)
    if not p.exists():
        return None
    cs = list(p.rglob("audit_report.md"))
    if cs:
        return cs[0]
    cs = list(p.rglob("*audit*.md"))
    return cs[0] if cs else None

def vuln_report_detected(artifact_dir):
    rp = find_report(artifact_dir)
    txt = read_text(rp) if rp else ""
    if not txt.strip():
        return 0
    if NEG_RE.search(txt) and not TARGET_RE.search(txt):
        return 0
    return 1 if TARGET_RE.search(txt) else 0

def safe_false_positive(artifact_dir):
    rp = find_report(artifact_dir)
    txt = read_text(rp) if rp else ""
    if not txt.strip():
        return 0
    if NEG_RE.search(txt):
        return 0
    return 1 if TARGET_RE.search(txt) else 0

def parse_eval(eval_md):
    txt = read_text(eval_md)
    low = txt.lower()
    res = {"compile_ok": 0, "attack_ok": 0, "repair_ok": 0}

    if re.search(r"forge build[\s\S]{0,800}(successful|通过|pass)", txt, re.I):
        res["compile_ok"] = 1
    elif re.search(r"编译[\s\S]{0,200}(通过|pass|成功)", txt, re.I):
        res["compile_ok"] = 1

    if re.search(r"(攻击|attack|poc)[\s\S]{0,1200}(\[pass\]|1 passed|passed|通过|成功)", txt, re.I):
        res["attack_ok"] = 1

    if re.search(r"(修复验证|repair|validation|回归)[\s\S]{0,1200}(\[pass\]|passed|通过|成功)", txt, re.I):
        res["repair_ok"] = 1

    return res

# manifest
manifest = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
vuln_samples = [r["name"] for r in manifest if r["type"] == "vulnerable"]
safe_samples = [r["name"] for r in manifest if r["type"] == "safe"]
sample_type = {r["name"]: r["type"] for r in manifest}

# runtime merge: base + resume, duplicate keep last
runtime_rows = []
for p in [BASE_RUNTIME, RESUME_RUNTIME]:
    if p.exists():
        runtime_rows += list(csv.DictReader(p.open(encoding="utf-8")))

dedup = {}
for r in runtime_rows:
    if not r.get("round") or not r.get("sample") or not r.get("stage"):
        continue
    dedup[(r["round"], r["sample"], r["stage"])] = r
runtime_rows = list(dedup.values())

stage_map = defaultdict(dict)
for r in runtime_rows:
    stage_map[(int(r["round"]), r["sample"])][r["stage"]] = r

round_stats = []
details = []

for rd in [1, 2, 3]:
    report_ok = compile_ok = attack_ok = repair_ok = safe_fp = 0

    for sample in vuln_samples:
        sm = stage_map.get((rd, sample), {})
        gen = sm.get("auto_llm_generate_v2", {})
        eva = sm.get("auto_llm_evaluate_v2", {})

        artifact = gen.get("artifact_dir") or str(OUT / f"round_{rd}/artifacts/{sample}_qwen3_coder_30b")
        eval_md = eva.get("evaluation_md") or str(OUT / f"round_{rd}/evaluations/{sample}_evaluation.md")

        r_ok = vuln_report_detected(artifact)
        ev = parse_eval(eval_md)

        report_ok += r_ok
        compile_ok += ev["compile_ok"]
        attack_ok += ev["attack_ok"]
        repair_ok += ev["repair_ok"]

        details.append({
            "round": rd, "sample": sample, "type": "vulnerable",
            "report_detected": r_ok,
            "compile_ok": ev["compile_ok"],
            "attack_ok": ev["attack_ok"],
            "repair_ok": ev["repair_ok"],
            "safe_fp": "",
            "artifact_dir": artifact,
            "evaluation_md": eval_md,
        })

    for sample in safe_samples:
        sm = stage_map.get((rd, sample), {})
        gen = sm.get("auto_llm_generate_v2", {})
        artifact = gen.get("artifact_dir") or str(OUT / f"round_{rd}/artifacts/{sample}_qwen3_coder_30b")

        fp = safe_false_positive(artifact)
        safe_fp += fp

        details.append({
            "round": rd, "sample": sample, "type": "safe",
            "report_detected": "",
            "compile_ok": "",
            "attack_ok": "",
            "repair_ok": "",
            "safe_fp": fp,
            "artifact_dir": artifact,
            "evaluation_md": str(OUT / f"round_{rd}/evaluations/{sample}_evaluation.md"),
        })

    round_stats.append({
        "round": rd,
        "report_ok": report_ok,
        "compile_ok": compile_ok,
        "attack_ok": attack_ok,
        "repair_ok": repair_ok,
        "safe_fp": safe_fp,
        "vuln_n": len(vuln_samples),
        "safe_n": len(safe_samples),
    })

# write detail
with DETAIL_CSV.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(details[0].keys()))
    w.writeheader()
    w.writerows(details)

# by round
with ROUND_CSV.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=[
        "round","report_rate","report_ok","report_n",
        "compile_rate","compile_ok","compile_n",
        "attack_rate","attack_ok","attack_n",
        "repair_rate","repair_ok","repair_n",
        "safe_fp_rate","safe_fp","safe_n"
    ])
    w.writeheader()
    for s in round_stats:
        n = s["vuln_n"]
        sn = s["safe_n"]
        w.writerow({
            "round": s["round"],
            "report_rate": f"{pct(s['report_ok'], n):.2f}",
            "report_ok": s["report_ok"], "report_n": n,
            "compile_rate": f"{pct(s['compile_ok'], n):.2f}",
            "compile_ok": s["compile_ok"], "compile_n": n,
            "attack_rate": f"{pct(s['attack_ok'], n):.2f}",
            "attack_ok": s["attack_ok"], "attack_n": n,
            "repair_rate": f"{pct(s['repair_ok'], n):.2f}",
            "repair_ok": s["repair_ok"], "repair_n": n,
            "safe_fp_rate": f"{pct(s['safe_fp'], sn):.2f}",
            "safe_fp": s["safe_fp"], "safe_n": sn,
        })

metrics = {
    "审计报告识别率": [pct(s["report_ok"], s["vuln_n"]) for s in round_stats],
    "补丁编译通过率": [pct(s["compile_ok"], s["vuln_n"]) for s in round_stats],
    "攻击PoC成功率": [pct(s["attack_ok"], s["vuln_n"]) for s in round_stats],
    "修复验证通过率": [pct(s["repair_ok"], s["vuln_n"]) for s in round_stats],
    "安全样本误报率": [pct(s["safe_fp"], s["safe_n"]) for s in round_stats],
}

with VAR_CSV.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f,
    fieldnames=["metric","rounds","mean_percent","variance_percent2","std_percent","min_percent","max_percent"])
    w.writeheader()
    for k, xs in metrics.items():
        w.writerow({
            "metric": k, "rounds": len(xs),
            "mean_percent": f"{mean(xs):.2f}",
            "variance_percent2": f"{var(xs):.2f}",
            "std_percent": f"{std(xs):.2f}",
            "min_percent": f"{min(xs):.2f}",
            "max_percent": f"{max(xs):.2f}",
        })

# runtime stats
time_groups = defaultdict(list)
for r in runtime_rows:
    try:
        sec = float(r["seconds"])
    except Exception:
        continue
    time_groups[r["stage"]].append(sec)

total_map = defaultdict(float)
for r in runtime_rows:
    if r["stage"] in {"auto_llm_generate_v2", "auto_llm_evaluate_v2"}:
        try:
            total_map[(r["round"], r["sample"])] += float(r["seconds"])
        except Exception:
            pass
time_groups["total_v2_pipeline"] = list(total_map.values())

with TIME_CSV.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f,
    fieldnames=["stage","count","mean_seconds","variance_seconds2","std_seconds","min_seconds","max_seconds"])
    w.writeheader()
    for stage, xs in sorted(time_groups.items()):
        if not xs:
            continue
        w.writerow({
            "stage": stage,
            "count": len(xs),
            "mean_seconds": f"{mean(xs):.3f}",
            "variance_seconds2": f"{var(xs):.3f}",
            "std_seconds": f"{std(xs):.3f}",
            "min_seconds": f"{min(xs):.3f}",
            "max_seconds": f"{max(xs):.3f}",
        })

md = []
md.append("# 本文系统60样本三轮重复实验汇总\n")
md.append(f"- 样本数：{len(manifest)}")
md.append(f"- 漏洞样本数：{len(vuln_samples)}")
md.append(f"- 安全样本数：{len(safe_samples)}\n")

md.append("## 各轮准确率\n")
md.append("| 轮次 | 审计报告识别率 | 补丁编译通过率 | 攻击PoC成功率 | 修复验证通过率 | 安全样本误报率 |")
md.append("|---:|---:|---:|---:|---:|---:|")
for s in round_stats:
    n, sn = s["vuln_n"], s["safe_n"]
    md.append(
        f"| {s['round']} | "
        f"{s['report_ok']}/{n} = {pct(s['report_ok'], n):.1f}% | "
        f"{s['compile_ok']}/{n} = {pct(s['compile_ok'], n):.1f}% | "
        f"{s['attack_ok']}/{n} = {pct(s['attack_ok'], n):.1f}% | "
        f"{s['repair_ok']}/{n} = {pct(s['repair_ok'], n):.1f}% | "
        f"{s['safe_fp']}/{sn} = {pct(s['safe_fp'], sn):.1f}% |"
    )

md.append("\n## 准确率均值与方差\n")
md.append("| 指标 | 轮数 | 均值/% | 方差/%² | 标准差/% | 最小/% | 最大/% |")
md.append("|---|---:|---:|---:|---:|---:|---:|")
for k, xs in metrics.items():
    md.append(f"| {k} | {len(xs)} | {mean(xs):.2f} | {var(xs):.2f} | {std(xs):.2f} | {min(xs):.2f} | {max(xs):.2f} |")

md.append("\n## 运行时间均值与方差\n")
md.append("| 阶段 | 次数 | 平均耗时/s | 方差/s² | 标准差/s | 最短/s | 最长/s |")
md.append("|---|---:|---:|---:|---:|---:|---:|")
for stage, xs in sorted(time_groups.items()):
    if xs:
        md.append(f"| {stage} | {len(xs)} | {mean(xs):.3f} | {var(xs):.3f} | {std(xs):.3f} | {min(xs):.3f} |{max(xs):.3f} |")

md.append("\n## 输出文件\n")
md.append(f"- `{ROUND_CSV}`")
md.append(f"- `{VAR_CSV}`")
md.append(f"- `{TIME_CSV}`")
md.append(f"- `{DETAIL_CSV}`")

SUMMARY_MD.write_text("\n".join(md), encoding="utf-8")

print(SUMMARY_MD)
print(SUMMARY_MD.read_text(encoding="utf-8"))
