#!/usr/bin/env bash
set -u

ROOT=/home/tianlang/smart-audit-llm
OUT="$ROOT/reports/focused_quantification/smartbugs2_multi/semgrep_custom"

mkdir -p "$OUT"

samples=(
UnauthorizedTokenTransfer
MissingAllowanceTransferFrom
WrongAllowanceOwner
OnlyToCheckedTransfer
PublicBurnFrom
)

for name in "${samples[@]}"; do
docker run --rm \
    --entrypoint semgrep \
    -v "$ROOT:/work" \
    smartbugs/semgrep-unauth-transfer:local \
    scan \
    --disable-version-check \
    --json \
    --lang generic \
    -e 'balanceOf[from] -= amount' \
    "/work/benchmarks/gptscan/$name.sol" \
    > "$OUT/$name.json" 2> "$OUT/$name.err" || true
done

for name in "${samples[@]}"; do
if grep -q '"results":\[\]' "$OUT/$name.json"; then
    echo "$name: not_detected"
elif grep -q '"results":\[' "$OUT/$name.json"; then
    echo "$name: detected"
else
    echo "$name: no_json"
fi
done
