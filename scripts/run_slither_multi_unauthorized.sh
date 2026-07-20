#!/usr/bin/env bash
set -u

ROOT=/home/tianlang/smart-audit-llm
OUT="$ROOT/reports/focused_quantification/slither_multi"

samples=(
UnauthorizedTokenTransfer
MissingAllowanceTransferFrom
WrongAllowanceOwner
OnlyToCheckedTransfer
PublicBurnFrom
)

mkdir -p "$OUT"

cd "$ROOT"

for name in "${samples[@]}"; do
slither "benchmarks/gptscan/${name}.sol" \
    --json "$OUT/${name}.json" \
    > "$OUT/${name}.txt" 2>&1 || true
done

for name in "${samples[@]}"; do
if grep -qiE "access-control|arbitrary-send|controlled-delegatecall|tx-origin|unchecked-lowlevel" "$OUT/
${name}.txt"; then
    echo "$name: target_like_warning"
else
    echo "$name: no_target_warning"
fi
done
