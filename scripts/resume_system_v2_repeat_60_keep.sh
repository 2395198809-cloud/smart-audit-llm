#!/usr/bin/env bash
set -u

ROOT="/home/tianlang/smart-audit-llm"
MANIFEST="$ROOT/reports/publish_exp/sample_manifest.csv"
OUT="$ROOT/reports/publish_exp_60_system_repeat_keep"
RUNTIME_CSV="$OUT/system_v2_repeat_60_runtime_resume.csv"
MODEL_SUFFIX="qwen3_coder_30b"

export PATH="$HOME/.foundry/bin:$HOME/.local/bin:$PATH"

mkdir -p "$OUT"

if [ ! -f "$RUNTIME_CSV" ]; then
echo "round,sample,type,stage,status,seconds,artifact_dir,evaluation_md" > "$RUNTIME_CSV"
fi

record_time() {
local round="$1"
local sample="$2"
local typ="$3"
local stage="$4"
local status="$5"
local start="$6"
local end="$7"
local artifact_dir="$8"
local evaluation_md="$9"

local sec
sec=$(awk -v s="$start" -v e="$end" 'BEGIN { printf "%.3f", e - s }')
echo "${round},${sample},${typ},${stage},${status},${sec},${artifact_dir},${evaluation_md}" >> "$RUNTIME_CSV"
}

run_one_sample() {
local round="$1"
local sample="$2"
local typ="$3"

local sol="$ROOT/benchmarks/gptscan/${sample}.sol"
local canonical_artifact="$ROOT/auto_llm_artifacts/${sample}_${MODEL_SUFFIX}"
local round_dir="$OUT/round_${round}"
local artifact_keep="$round_dir/artifacts/${sample}_${MODEL_SUFFIX}"
local gen_log="$round_dir/logs/${sample}_generate.txt"
local eval_log="$round_dir/logs/${sample}_evaluate.txt"
local eval_keep="$round_dir/evaluations/${sample}_evaluation.md"

mkdir -p "$round_dir/logs" "$round_dir/artifacts" "$round_dir/evaluations"

if [ -f "$eval_keep" ]; then
    echo "[SKIP] round=$round sample=$sample already has evaluation"
    return 0
fi

echo
echo "===== RESUME round=$round sample=$sample type=$typ ====="

if [ ! -f "$sol" ]; then
    echo "[MISS] $sol"
    now=$(date +%s.%N)
    record_time "$round" "$sample" "$typ" "missing_sample" "1" "$now" "$now" "" ""
    return 0
fi

echo "[generate] round=$round sample=$sample"
start=$(date +%s.%N)
(
    cd "$ROOT" || exit 1
    timeout 1200 python3 scripts/auto_llm_generate_artifacts.py "$sol"
) > "$gen_log" 2>&1
status=$?
end=$(date +%s.%N)

if [ -d "$canonical_artifact" ]; then
    rm -rf "$artifact_keep"
    cp -a "$canonical_artifact" "$artifact_keep"
fi

record_time "$round" "$sample" "$typ" "auto_llm_generate_v2" "$status" "$start" "$end" "$artifact_keep" ""

echo "[evaluate] round=$round sample=$sample"
start=$(date +%s.%N)
if [ -d "$artifact_keep" ]; then
    (
    cd "$ROOT" || exit 1
    timeout 600 python3 scripts/evaluate_auto_llm_artifacts.py "$artifact_keep"
    ) > "$eval_log" 2>&1
    status=$?
else
    echo "artifact not found: $artifact_keep" > "$eval_log"
    status=1
fi
end=$(date +%s.%N)

latest_eval=$(ls -t "$ROOT"/reports/auto_llm/*"${sample}"*evaluation*.md 2>/dev/null | head -n 1 || true)
if [ -n "$latest_eval" ] && [ -f "$latest_eval" ]; then
    cp "$latest_eval" "$eval_keep"
else
    cp "$eval_log" "$eval_keep"
fi

record_time "$round" "$sample" "$typ" "auto_llm_evaluate_v2" "$status" "$start" "$end" "$artifact_keep" "$eval_keep"
}

echo "=== resume system v2 repeat 60 ==="
echo "output: $OUT"
echo "resume runtime csv: $RUNTIME_CSV"

for round in 1 2 3; do
echo
echo "================ RESUME ROUND $round ================"

tail -n +2 "$MANIFEST" | while IFS=, read -r id sample typ category expected; do
    [ -z "$sample" ] && continue
    run_one_sample "$round" "$sample" "$typ"
done
done

echo
echo "Resume finished."
