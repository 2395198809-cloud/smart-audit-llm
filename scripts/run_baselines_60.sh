#!/usr/bin/env bash
set -u

ROOT="/home/tianlang/smart-audit-llm"
GPT="/home/tianlang/GPTScan"
MANIFEST="$ROOT/reports/publish_exp/sample_manifest.csv"
OUT="$ROOT/reports/publish_exp_60"
CSV="$OUT/baseline_runtime_metrics_60.csv"

export PATH="$HOME/.foundry/bin:$HOME/.local/bin:$PATH"

mkdir -p "$OUT/slither" "$OUT/smartbugs2_slither" "$OUT/gptscan" "$OUT/semgrep_custom"

echo "sample,type,method,status,seconds,detected" > "$CSV"

record_time() {
local sample="$1"
local typ="$2"
local method="$3"
local status="$4"
local start="$5"
local end="$6"
local detected="$7"

python3 - "$sample" "$typ" "$method" "$status" "$start" "$end" "$detected" >> "$CSV" <<'PY'
import sys
sample, typ, method, status, start, end, detected = sys.argv[1:]
sec = float(end) - float(start)
print(f"{sample},{typ},{method},{status},{sec:.3f},{detected}")
PY
}

target_detected() {
local file="$1"
if [ ! -f "$file" ]; then
    echo 0
    return
fi

if grep -Eiq \
    'unauthori|unauthoriz|authorization|auth|allowance|approval|approved|operator|spender|owner|transferFrom|
    safeTransferFrom|burnFrom|withdrawFrom|权限|授权|未授权|绕过|资产转移' \
    "$file"; then
    echo 1
else
    echo 0
fi
}

run_one() {
local sample="$1"
local typ="$2"
local method="$3"
local start end status detected logfile

logfile="$OUT/${method}/${sample}.txt"
start=$(date +%s.%N)

if [ "$method" = "slither" ]; then
    (
    cd "$ROOT" || exit 1
    timeout 120 slither "benchmarks/gptscan/${sample}.sol" \
        --json "$OUT/slither/${sample}.json"
    ) > "$logfile" 2>&1
    status=$?

elif [ "$method" = "smartbugs2_slither" ]; then
    (
    cd "$ROOT" || exit 1
    timeout 180 docker run --rm \
        -v "$ROOT:/work" \
        smartbugs/slither:0.11.3 \
        slither "/work/benchmarks/gptscan/${sample}.sol" \
        --json "/work/reports/publish_exp_60/smartbugs2_slither/${sample}.json"
    ) > "$logfile" 2>&1
    status=$?

elif [ "$method" = "gptscan" ]; then
    (
    if [ ! -d "$GPT/src" ]; then
        echo "GPTScan dir not found: $GPT/src"
        exit 127
    fi

    mkdir -p "$GPT/samples/$sample" "$GPT/output"
    cp "$ROOT/benchmarks/gptscan/${sample}.sol" "$GPT/samples/$sample/"

    cd "$GPT/src" || exit 1
    if [ -f "../.venv-gptscan/bin/activate" ]; then
        source "../.venv-gptscan/bin/activate"
    fi

    timeout 900 python3 main.py \
        -s "../samples/$sample" \
        -o "../output/${sample}_qwen3_60.json" \
        -k local

    cp "../output/${sample}_qwen3_60.json" "$OUT/gptscan/${sample}.json" 2>/dev/null || true
    cat "../output/${sample}_qwen3_60.json" 2>/dev/null || true
    ) > "$logfile" 2>&1
    status=$?

elif [ "$method" = "semgrep_custom" ]; then
    (
    cd "$ROOT" || exit 1
    timeout 180 docker run --rm \
        --entrypoint semgrep \
        -v "$ROOT:/work" \
        smartbugs/semgrep-unauth-transfer:local \
        scan \
        --disable-version-check \
        --json \
        --config "/work/reports/publish_exp/semgrep_unauth_rules.yml" \
        "/work/benchmarks/gptscan/${sample}.sol"
    ) > "$logfile" 2>&1
    status=$?

else
    echo "unknown method: $method" > "$logfile"
    status=127
fi

end=$(date +%s.%N)
detected=$(target_detected "$logfile")
record_time "$sample" "$typ" "$method" "$status" "$start" "$end" "$detected"
}

echo "=== baseline experiment for 60 samples ==="
echo "manifest: $MANIFEST"
echo "output: $OUT"

tail -n +2 "$MANIFEST" | while IFS=, read -r id sample typ category expected; do
[ -z "$sample" ] && continue

sol="$ROOT/benchmarks/gptscan/${sample}.sol"
if [ ! -f "$sol" ]; then
    echo "[MISS] $sample"
    echo "$sample,$typ,missing_sample,1,0.000,0" >> "$CSV"
    continue
fi

echo
echo "===== $sample [$typ] ====="

echo "[1/4] Slither"
run_one "$sample" "$typ" "slither"

echo "[2/4] SmartBugs2-slither"
run_one "$sample" "$typ" "smartbugs2_slither"

echo "[3/4] GPTScan-local"
run_one "$sample" "$typ" "gptscan"

echo "[4/4] Semgrep-custom"
run_one "$sample" "$typ" "semgrep_custom"
done

echo
echo "Saved: $CSV"
cat "$CSV"
