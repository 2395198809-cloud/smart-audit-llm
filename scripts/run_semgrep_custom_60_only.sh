#!/usr/bin/env bash
set -u

ROOT="/home/tianlang/smart-audit-llm"
MANIFEST="$ROOT/reports/publish_exp/sample_manifest.csv"
OUT="$ROOT/reports/publish_exp_60"
CSV="$OUT/semgrep_custom_runtime_60.csv"

mkdir -p "$OUT/semgrep_custom"

echo "sample,type,method,status,seconds,detected" > "$CSV"

count_findings() {
local file="$1"
python3 - "$file" <<'PY'
import json, sys
p=sys.argv[1]
txt=open(p,encoding="utf-8",errors="ignore").read()
idx=txt.find("{")
if idx < 0:
    print(0)
else:
    try:
        data=json.loads(txt[idx:])
        print(len(data.get("results",[])))
    except Exception:
        print(0)
PY
}

record() {
local sample="$1"
local typ="$2"
local status="$3"
local start="$4"
local end="$5"
local detected="$6"

python3 - "$sample" "$typ" "$status" "$start" "$end" "$detected" >> "$CSV" <<'PY'
import sys
sample, typ, status, start, end, detected = sys.argv[1:]
sec = float(end) - float(start)
print(f"{sample},{typ},semgrep_custom,{status},{sec:.3f},{detected}")
PY
}

tail -n +2 "$MANIFEST" | while IFS=, read -r id sample typ category expected; do
[ -z "$sample" ] && continue

sol="$ROOT/benchmarks/gptscan/${sample}.sol"
log="$OUT/semgrep_custom/${sample}.txt"

if [ ! -f "$sol" ]; then
    echo "[MISS] $sample"
    echo "$sample,$typ,semgrep_custom,1,0.000,0" >> "$CSV"
    continue
fi

echo "===== semgrep $sample [$typ] ====="

start=$(date +%s.%N)

(
    cd "$ROOT" || exit 1
    timeout 180 docker run --rm \
    --entrypoint semgrep \
    -v "$ROOT:/work" \
    smartbugs/semgrep-unauth-transfer:local \
    scan \
    --disable-version-check \
    --json \
    --config "/work/reports/publish_exp/semgrep_unauth_rules.json" \
    "/work/benchmarks/gptscan/${sample}.sol"
) > "$log" 2>&1

status=$?
end=$(date +%s.%N)

findings=$(count_findings "$log")
if [ "$findings" -gt 0 ]; then
    detected=1
else
    detected=0
fi

record "$sample" "$typ" "$status" "$start" "$end" "$detected"
done

echo "Saved: $CSV"
cat "$CSV"
