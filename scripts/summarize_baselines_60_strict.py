import csv, json, re
from pathlib import Path

ROOT = Path("/home/tianlang/smart-audit-llm")
CSV = ROOT / "reports/publish_exp_60/baseline_runtime_metrics_60.csv"
OUT = ROOT / "reports/publish_exp_60"

rows = list(csv.DictReader(CSV.open(encoding="utf-8")))

TARGET_RE = re.compile(
    r"未授权|权限绕过|授权绕过|任意用户|任意地址|"
    r"unauthorized|unauthorised|authorization bypass|access control|"
    r"missing allowance|allowance check|approval check|operator approval|"
    r"can transfer.*without|transfer.*without.*approval|burn.*without|withdraw.*without",
    re.I
)

def load_text(p):
    try:
        return Path(p).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def slither_detected(sample, method):
    if method == "slither":
        p = OUT / "slither" / f"{sample}.json"
    else:
        p = OUT / "smartbugs2_slither" / f"{sample}.json"

    if not p.exists():
        return 0

    try:
        data = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return 0

    detectors = data.get("results", {}).get("detectors", [])
    for d in detectors:
        check = str(d.get("check", ""))
        impact = str(d.get("impact", ""))
        desc = str(d.get("description", ""))

        # 过滤 Slither 常见无关告警
        if check in {
            "solc-version",
            "naming-convention",
            "pragma",
            "unused-return",
            "low-level-calls",
            "similar-names",
            "external-function",
            "constable-states",
            "immutable-states",
        }:
            continue

        if TARGET_RE.search(check + "\n" + impact + "\n" + desc):
            return 1

    return 0

def semgrep_detected(sample):
    p = OUT / "semgrep_custom" / f"{sample}.txt"
    txt = load_text(p)
    if not txt:
        return 0

    # semgrep 输出里第一段可能混有日志，从第一个 { 开始解析 JSON
    idx = txt.find("{")
    if idx >= 0:
        js = txt[idx:]
        try:
            data = json.loads(js)
            return 1 if data.get("results") else 0
        except Exception:
            pass

    # 兜底，只认 Findings: N 且 N > 0
    m = re.search(r"Findings:\s*(\d+)", txt)
    if m and int(m.group(1)) > 0:
        return 1

    return 0

def gptscan_detected(sample):
    p_json = OUT / "gptscan" / f"{sample}.json"
    p_txt = OUT / "gptscan" / f"{sample}.txt"

    txt = ""
    txt += load_text(p_json)
    txt += "\n"
    txt += load_text(p_txt)

    if not txt.strip():
        return 0

    # 先排除明显无发现
    if re.search(r"no vulnerability|not vulnerable|未发现|没有发现|无漏洞|不存在", txt, re.I):
        return 0

    return 1 if TARGET_RE.search(txt) else 0

def is_completed(sample, method, status):
    # Docker timeout 124、命令不存在 127 都算未完成
    if str(status) in {"124", "127"}:
        return False

    if method == "slither":
        return (OUT / "slither" / f"{sample}.json").exists() or (OUT / "slither" / f"{sample}.txt").exists()
    if method == "smartbugs2_slither":
        return (OUT / "smartbugs2_slither" / f"{sample}.json").exists() or (OUT / "smartbugs2_slither" /
        f"{sample}.txt").exists()
    if method == "gptscan":
        return (OUT / "gptscan" / f"{sample}.json").exists() or (OUT / "gptscan" / f"{sample}.txt").exists()
    if method == "semgrep_custom":
        return (OUT / "semgrep_custom" / f"{sample}.txt").exists()

    return str(status) == "0"

def detect(sample, method):
    if method in {"slither", "smartbugs2_slither"}:
        return slither_detected(sample, method)
    if method == "semgrep_custom":
        return semgrep_detected(sample)
    if method == "gptscan":
        return gptscan_detected(sample)
    return 0

methods = []
for r in rows:
    if r["method"] not in methods and r["method"] != "missing_sample":
        methods.append(r["method"])

out = []
out.append("# 60样本基线实验严格汇总")
out.append("")
out.append("说明：本汇总不再使用路径/函数名关键词粗略 grep，而是按各工具结果文件解析目标相关漏洞输出。")
out.append("")

out.append("## 总体结果")
out.append("")
out.append("| 方法 | 样本数 | 运行完成率 | 漏洞识别率 | 安全样本误报率 | Precision | Recall | F1 | 平均耗时/s | 最短/s | 最长/s |")
out.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

summary = []

for m in methods:
    rs = [r for r in rows if r["method"] == m]
    vuln = [r for r in rs if r["type"] == "vulnerable"]
    safe = [r for r in rs if r["type"] == "safe"]

    for r in rs:
        r["strict_detected"] = str(detect(r["sample"], r["method"]))
        r["completed"] = "1" if is_completed(r["sample"], r["method"], r["status"]) else "0"

    ok = sum(1 for r in rs if r["completed"] == "1")
    tp = sum(1 for r in vuln if r["strict_detected"] == "1")
    fn = len(vuln) - tp
    fp = sum(1 for r in safe if r["strict_detected"] == "1")
    tn = len(safe) - fp

    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / len(vuln) if vuln else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0

    times = [float(r["seconds"]) for r in rs if float(r["seconds"]) >= 0]
    avg = sum(times) / len(times) if times else 0
    mn = min(times) if times else 0
    mx = max(times) if times else 0

    out.append(
        f"| {m} | {len(rs)} | {ok}/{len(rs)} = {ok/len(rs)*100:.1f}% | "
        f"{tp}/{len(vuln)} = {tp/len(vuln)*100:.1f}% | "
        f"{fp}/{len(safe)} = {fp/len(safe)*100:.1f}% | "
        f"{precision*100:.1f}% | {recall*100:.1f}% | {f1*100:.1f}% | "
        f"{avg:.3f} | {mn:.3f} | {mx:.3f} |"
    )

    summary.append((m, tp, fp, tn, fn))

out.append("")
out.append("## 混淆矩阵")
out.append("")
out.append("| 方法 | TP | FP | TN | FN |")
out.append("|---|---:|---:|---:|---:|")
for m, tp, fp, tn, fn in summary:
    out.append(f"| {m} | {tp} | {fp} | {tn} | {fn} |")

out.append("")
out.append("## 每个样本严格检测情况")
out.append("")
out.append("| 样本 | 类型 | 方法 | 原状态码 | 运行完成 | 严格目标检测 | 耗时/s |")
out.append("|---|---|---|---:|---:|---:|---:|")
for r in rows:
    if r["method"] == "missing_sample":
        continue
    sd = detect(r["sample"], r["method"])
    comp = 1 if is_completed(r["sample"], r["method"], r["status"]) else 0
    out.append(
        f"| {r['sample']} | {r['type']} | {r['method']} | {r['status']} | "
        f"{comp} | {sd} | {float(r['seconds']):.3f} |"
    )

md = OUT / "baseline_summary_60_strict.md"
md.write_text("\n".join(out), encoding="utf-8")

print(md)
print(md.read_text(encoding="utf-8"))
