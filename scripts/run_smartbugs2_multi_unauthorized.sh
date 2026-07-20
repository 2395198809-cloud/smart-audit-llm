#!/usr/bin/env bash
set -u

ROOT=/home/tianlang/smart-audit-llm
SB=/home/tianlang/smartbugs
OUT=/home/tianlang/smart-audit-llm/reports/focused_quantification/smartbugs2_multi/slither

mkdir -p "$OUT"

samples=(
UnauthorizedTokenTransfer
MissingAllowanceTransferFrom
WrongAllowanceOwner
OnlyToCheckedTransfer
PublicBurnFrom
)

docker image inspect smartbugs/slither:0.11.3 >/dev/null 2>&1 || {
echo "missing image smartbugs/slither:0.11.3"
exit 1
}

cd "$SB"
source .venv/bin/activate

for name in "${samples[@]}"; do
sample="$ROOT/benchmarks/gptscan/$name.sol"
outfile="$OUT/$name.txt"

timeout 180 smartbugs \
    -t slither \
    -f "$sample" \
    > "$outfile" 2>&1 || true
done

cd "$ROOT"

for name in "${samples[@]}"; do
outfile="$OUT/$name.txt"
echo "===== $name ====="
if [ -f "$outfile" ]; then
    sed -n '1,60p' "$outfile"
else
    echo "missing output: $outfile"
fi
done
