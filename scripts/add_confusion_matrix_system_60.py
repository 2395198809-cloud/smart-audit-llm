import csv
from pathlib import Path
from collections import defaultdict

ROOT = Path("/home/tianlang/smart-audit-llm")
OUT = ROOT / "reports/publish_exp_60_system_repeat_keep"

DETAIL = OUT / "system_v2_repeat_60_sample_stage_detail_with_postcheck.csv"
SUMMARY_MD = OUT / "system_v2_repeat_60_confusion_matrix.md"
SUMMARY_CSV = OUT / "system_v2_repeat_60_confusion_matrix.csv"

rows = list(csv.DictReader(DETAIL.open(encoding="utf-8")))

def calc_metrics(tp, fp, tn, fn):
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    acc = (tp + tn) / (tp + fp + tn + fn) if tp + fp + tn + fn else 0.0
    return precision, recall, f1, fpr, acc

def confusion_for_round(round_id, mode):
    """
    mode:
    raw  -> raw_report_detected / raw_safe_fp
    post -> postchecked_report_detected / postchecked_safe_fp
    """
    rs = [r for r in rows if r["round"] == str(round_id)]

    vuln = [r for r in rs if r["type"] == "vulnerable"]
    safe = [r for r in rs if r["type"] == "safe"]

    if mode == "raw":
        tp = sum(1 for r in vuln if r["raw_report_detected"] == "1")
        fn = len(vuln) - tp
        fp = sum(1 for r in safe if r["raw_safe_fp"] == "1")
        tn = len(safe) - fp
    else:
        tp = sum(1 for r in vuln if r["postchecked_report_detected"] == "1")
        fn = len(vuln) - tp
        fp = sum(1 for r in safe if r["postchecked_safe_fp"] == "1")
        tn = len(safe) - fp

    precision, recall, f1, fpr, acc = calc_metrics(tp, fp, tn, fn)

    return {
        "round": round_id,
        "mode": mode,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision * 100,
        "recall": recall * 100,
        "f1": f1 * 100,
        "fpr": fpr * 100,
        "accuracy": acc * 100,
    }

all_stats = []
for rd in [1, 2, 3]:
    all_stats.append(confusion_for_round(rd, "raw"))
    all_stats.append(confusion_for_round(rd, "post"))

# 三轮合计
for mode in ["raw", "post"]:
    items = [s for s in all_stats if s["mode"] == mode]
    tp = sum(s["tp"] for s in items)
    fp = sum(s["fp"] for s in items)
    tn = sum(s["tn"] for s in items)
    fn = sum(s["fn"] for s in items)
    precision, recall, f1, fpr, acc = calc_metrics(tp, fp, tn, fn)
    all_stats.append({
        "round": "total",
        "mode": mode,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision * 100,
        "recall": recall * 100,
        "f1": f1 * 100,
        "fpr": fpr * 100,
        "accuracy": acc * 100,
    })

with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(
        f,
        fieldnames=[
            "round", "mode", "tp", "fp", "tn", "fn",
            "precision", "recall", "f1", "fpr", "accuracy"
        ],
    )
    w.writeheader()
    for s in all_stats:
        w.writerow({
            "round": s["round"],
            "mode": s["mode"],
            "tp": s["tp"],
            "fp": s["fp"],
            "tn": s["tn"],
            "fn": s["fn"],
            "precision": f"{s['precision']:.2f}",
            "recall": f"{s['recall']:.2f}",
            "f1": f"{s['f1']:.2f}",
            "fpr": f"{s['fpr']:.2f}",
            "accuracy": f"{s['accuracy']:.2f}",
        })

md = []
md.append("# 本文系统60样本三轮实验混淆矩阵统计")
md.append("")
md.append("说明：漏洞样本数为40，安全样本数为20。三轮合计时，漏洞判断总数为120，安全判断总数为60。")
md.append("")
md.append("TP表示漏洞样本被正确识别；FN表示漏洞样本漏报；FP表示安全样本被误报；TN表示安全样本被正确判定为非目标漏洞。")
md.append("")

md.append("## 每轮混淆矩阵")
md.append("")
md.append("| 轮次 | 统计口径 | TP | FP | TN | FN | Precision/% | Recall/% | F1/% | FPR/% | Accuracy/% |")
md.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

name_map = {
    "raw": "原始LLM报告",
    "post": "后置校验后",
}

for s in all_stats:
    if s["round"] == "total":
        continue
    md.append(
        f"| {s['round']} | {name_map[s['mode']]} | "
        f"{s['tp']} | {s['fp']} | {s['tn']} | {s['fn']} | "
        f"{s['precision']:.2f} | {s['recall']:.2f} | {s['f1']:.2f} | "
        f"{s['fpr']:.2f} | {s['accuracy']:.2f} |"
    )

md.append("")
md.append("## 三轮合计混淆矩阵")
md.append("")
md.append("| 统计口径 | TP | FP | TN | FN | Precision/% | Recall/% | F1/% | FPR/% | Accuracy/% |")
md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

for s in all_stats:
    if s["round"] != "total":
        continue
    md.append(
        f"| {name_map[s['mode']]} | "
        f"{s['tp']} | {s['fp']} | {s['tn']} | {s['fn']} | "
        f"{s['precision']:.2f} | {s['recall']:.2f} | {s['f1']:.2f} | "
        f"{s['fpr']:.2f} | {s['accuracy']:.2f} |"
    )


SUMMARY_MD.write_text("\n".join(md), encoding="utf-8")

print(SUMMARY_MD)
print(SUMMARY_CSV)
print(SUMMARY_MD.read_text(encoding="utf-8"))
