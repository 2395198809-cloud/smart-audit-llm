#!/usr/bin/env bash
set -u

ROOT=/home/tianlang/smart-audit-llm
GPT=/home/tianlang/GPTScan
OUT="$ROOT/reports/focused_quantification/gptscan_multi"

samples=(
UnauthorizedTokenTransfer
MissingAllowanceTransferFrom
WrongAllowanceOwner
OnlyToCheckedTransfer
PublicBurnFrom
)

mkdir -p "$OUT"

for name in "${samples[@]}"; do
mkdir -p "$GPT/samples/$name" "$GPT/output"
cp "$ROOT/benchmarks/gptscan/$name.sol" "$GPT/samples/$name/"

cd "$GPT/src"
source ../.venv-gptscan/bin/activate 2>/dev/null || true

timeout 90 python main.py \
    -s "../samples/$name" \
    -o "../output/${name}_qwen3.json" \
    -k local \
    > "$OUT/${name}.txt" 2>&1 || true
done

cd "$ROOT"

for name in "${samples[@]}"; do
if grep -q "Unauthorized Transfer" "$OUT/${name}.txt"; then
    echo "$name: detected"
else
    echo "$name: not_detected"
fi
done
