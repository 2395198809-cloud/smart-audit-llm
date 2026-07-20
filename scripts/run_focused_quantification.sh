#!/usr/bin/env bash
set -u

ROOT=/home/tianlang/smart-audit-llm
GPT=/home/tianlang/GPTScan
CASE=UnauthorizedTokenTransfer

cd "$ROOT"
export PATH="$HOME/.foundry/bin:$HOME/.local/bin:$PATH"

mkdir -p reports/focused_quantification reports/auto_llm
mkdir -p benchmarks/gptscan

slither "benchmarks/gptscan/$CASE.sol" \
--json "reports/auto_llm/$CASE-slither-output.json" \
> /tmp/slither_unauth.txt 2>&1 || true

if [ -d "$GPT" ]; then
mkdir -p "$GPT/samples/$CASE" "$GPT/output"
cp "benchmarks/gptscan/$CASE.sol" "$GPT/samples/$CASE/"
cd "$GPT/src"
source ../.venv-gptscan/bin/activate 2>/dev/null || true
timeout 90 python main.py \
    -s "../samples/$CASE" \
    -o "../output/${CASE}_qwen3.json" \
    -k local \
    2>&1 | tee "$ROOT/reports/focused_quantification/gptscan_console.txt"
fi

cd "$ROOT"

python3 scripts/auto_llm_generate_artifacts.py "benchmarks/gptscan/$CASE.sol"
python3 scripts/evaluate_auto_llm_artifacts.py "auto_llm_artifacts/${CASE}_qwen3_coder_30b" || true
python3 scripts/collect_focused_quantification.py

cat reports/focused_quantification/focused_metrics.md
