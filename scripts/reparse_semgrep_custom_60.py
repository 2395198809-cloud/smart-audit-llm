import csv, json
from pathlib import Path

ROOT = Path("/home/tianlang/smart-audit-llm")
MANIFEST = ROOT / "reports/publish_exp/sample_manifest.csv"
LOGDIR = ROOT / "reports/publish_exp_60/semgrep_custom"
OLDCSV = ROOT / "reports/publish_exp_60/semgrep_custom_runtime_60.csv"
NEWCSV = ROOT / "reports/publish_exp_60/semgrep_custom_runtime_60_reparsed.csv"

def extract_first_json_object(txt: str):
    start = txt.find("{")
    if start < 0:
        return None

    depth = 0
    in_str = False
    esc = False

    for i in range(start, len(txt)):
        ch = txt[i]

        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return txt[start:i+1]

    return None

def count_findings(logfile: Path):
    if not logfile.exists():
        return 0
    txt = logfile.read_text(encoding="utf-8", errors="ignore")
    js = extract_first_json_object(txt)
    if not js:
        return 0
    try:
        data = json.loads(js)
        return len(data.get("results", []))
    except Exception:
        return 0

# 读取旧 CSV，保留 status 和 seconds
old_map = {}
if OLDCSV.exists():
    for r in csv.DictReader(OLDCSV.open(encoding="utf-8")):
        old_map[r["sample"]] = r

rows = []
with MANIFEST.open(encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        sample = r["name"]
        typ = r["type"]
        log = LOGDIR / f"{sample}.txt"
        findings = count_findings(log)
        detected = "1" if findings > 0 else "0"

        old = old_map.get(sample, {})
        status = old.get("status", "0" if log.exists() else "1")
        seconds = old.get("seconds", "0.000")

        rows.append({
            "sample": sample,
            "type": typ,
            "method": "semgrep_custom",
            "status": status,
            "seconds": seconds,
            "detected": detected,
            "findings": str(findings),
        })

with NEWCSV.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["sample","type","method","status","seconds","detected","findings"])
    w.writeheader()
    w.writerows(rows)

v = [r for r in rows if r["type"] == "vulnerable"]
s = [r for r in rows if r["type"] == "safe"]

print("saved:", NEWCSV)
print("总样本:", len(rows))
print("漏洞样本命中:", sum(r["detected"]=="1" for r in v), "/", len(v))
print("安全样本误报:", sum(r["detected"]=="1" for r in s), "/", len(s))

print("\n命中的漏洞样本:")
for r in v:
    if r["detected"] == "1":
        print(r["sample"], "findings=", r["findings"])

print("\n误报的安全样本:")
for r in s:
    if r["detected"] == "1":
        print(r["sample"], "findings=", r["findings"])
