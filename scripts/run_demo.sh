#!/usr/bin/env bash

set -u

MODEL="qwen3-coder:30b"

export PATH="$HOME/.foundry/bin:$HOME/.local/bin:$PATH"

line() {
echo "------------------------------------------------------------"
}

run() {
echo
echo "[run] $*"
"$@"
}

check_cmd() {
if command -v "$1" >/dev/null 2>&1; then
    echo "[ok] $1: $(command -v "$1")"
else
    echo "[missing] $1"
fi
}

status() {
line
echo "Demo status"
line

echo "Project: $(pwd)"
echo "Model: $MODEL"
echo

check_cmd forge
check_cmd slither
check_cmd python3
check_cmd ollama
echo

echo "[forge]"
forge --version 2>/dev/null || true
echo

echo "[slither]"
slither --version 2>/dev/null || true
echo

echo "[ollama models]"
ollama list 2>/dev/null | grep -E "qwen|NAME" || true
echo

echo "[key files]"
ls -l src test scripts reports 2>/dev/null || true
}

scan_core() {
line
echo "Slither scans"
line

rm -f slither-output.json
run slither src/VulnerableVault.sol --json slither-output.json

rm -f fixed-slither-output.json
run slither src/FixedVault.sol --json fixed-slither-output.json

if [ -f src/LLMFixedVault.sol ]; then
    rm -f llm-fixed-slither-output.json
    run slither src/LLMFixedVault.sol --json llm-fixed-slither-output.json
fi

if [ -f src/VulnerableWallet.sol ]; then
    rm -f wallet-slither-output.json
    run slither src/VulnerableWallet.sol --json wallet-slither-output.json
fi

if [ -f src/FixedWallet.sol ]; then
    rm -f fixed-wallet-slither-output.json
    run slither src/FixedWallet.sol --json fixed-wallet-slither-output.json
fi

if [ -f src/LLMFixedWallet.sol ]; then
    rm -f llm-fixed-wallet-slither-output.json
    run slither src/LLMFixedWallet.sol --json llm-fixed-wallet-slither-output.json
fi
}

show_checks() {
line
echo "Slither detector summary"
line

for f in \
    slither-output.json \
    fixed-slither-output.json \
    llm-fixed-slither-output.json \
    wallet-slither-output.json \
    fixed-wallet-slither-output.json \
    llm-fixed-wallet-slither-output.json
do
    if [ -f "$f" ]; then
    echo
    echo "[$f]"
    grep -n '"check"' "$f" || true
    fi
done
}

core() {
line
echo "Core demo: build, test, scan"
line

run forge build
run forge test -vv

if [ -f scripts/validate_llm_patch.py ]; then
    run python3 scripts/validate_llm_patch.py || true
fi

if [ -f scripts/validate_llm_wallet_patch.py ]; then
    run python3 scripts/validate_llm_wallet_patch.py || true
fi

scan_core
show_checks
}

reports() {
line
echo "Report generation"
line

if [ -f scripts/generate_report.py ]; then
    run python3 scripts/generate_report.py
fi

if [ -f scripts/generate_llm_report.py ]; then
    echo
    echo "This step requires Ollama service."
    run python3 scripts/generate_llm_report.py || true
fi

echo
echo "[reports]"
ls -l reports 2>/dev/null || true
}

llm_candidates() {
line
echo "LLM candidate patch generation and evaluation"
line

echo "This step requires Ollama service and model: $MODEL"
echo

if [ -f scripts/generate_llm_patch.py ]; then
    run python3 scripts/generate_llm_patch.py || true
fi

if [ -f scripts/evaluate_llm_candidates.py ]; then
    run python3 scripts/evaluate_llm_candidates.py || true
fi

if [ -f scripts/generate_llm_wallet_patch.py ]; then
    run python3 scripts/generate_llm_wallet_patch.py || true
fi

if [ -f scripts/evaluate_llm_wallet_candidates.py ]; then
    run python3 scripts/evaluate_llm_wallet_candidates.py || true
fi
}

smartbugs() {
line
echo "SmartBugs migrated benchmark auto LLM experiment"
line

mkdir -p benchmarks/smartbugs

if [ ! -f benchmarks/smartbugs/TxOriginPhishable.sol ]; then
    echo "[warn] benchmarks/smartbugs/TxOriginPhishable.sol not found"
fi

for target in \
    benchmarks/smartbugs/TxOriginPhishable.sol \
    benchmarks/smartbugs/SimpleDAO.sol \
    benchmarks/smartbugs/UncheckedCall.sol
do
    if [ -f "$target" ]; then
    run python3 scripts/auto_llm_generate_artifacts.py "$target" || true
    fi
done

for dir in \
    auto_llm_artifacts/TxOriginPhishable_qwen3_coder_30b \
    auto_llm_artifacts/SimpleDAO_qwen3_coder_30b \
    auto_llm_artifacts/UncheckedCall_qwen3_coder_30b
do
    if [ -d "$dir" ]; then
    run python3 scripts/evaluate_auto_llm_artifacts.py "$dir" || true
    fi
done

if [ -f scripts/summarize_auto_llm_results.py ]; then
    run python3 scripts/summarize_auto_llm_results.py || true
fi

echo
echo "[auto_llm reports]"
ls -l reports/auto_llm 2>/dev/null || true
}

auto() {
line
echo "Auto LLM artifact generation"
line

for target in \
    src/VulnerableWallet.sol \
    src/VulnerableVault.sol
do
    if [ -f "$target" ]; then
    run python3 scripts/auto_llm_generate_artifacts.py "$target" || true
    fi
done

for dir in \
    auto_llm_artifacts/VulnerableWallet_qwen3_coder_30b \
    auto_llm_artifacts/VulnerableVault_qwen3_coder_30b
do
    if [ -d "$dir" ]; then
    run python3 scripts/evaluate_auto_llm_artifacts.py "$dir" || true
    fi
done
}

all() {
status
core
reports
llm_candidates
auto
smartbugs

line
echo "Demo finished"
line
}

help() {
echo "Usage:"
echo "  bash scripts/run_demo.sh status       # check environment and files"
echo "  bash scripts/run_demo.sh core         # build, test, Slither scan"
echo "  bash scripts/run_demo.sh reports      # generate template and LLM audit reports"
echo "  bash scripts/run_demo.sh candidates   # generate and evaluate LLM patch candidates"
echo "  bash scripts/run_demo.sh auto         # no-vulnerability-type auto LLM generation"
echo "  bash scripts/run_demo.sh smartbugs    # run SmartBugs migrated samples"
echo "  bash scripts/run_demo.sh all          # run full demo"
}

case "${1:-help}" in
status)
    status
    ;;
core)
    core
    ;;
reports)
    reports
    ;;
candidates)
    llm_candidates
    ;;
auto)
    auto
    ;;
smartbugs)
    smartbugs
    ;;
all)
    all
    ;;
help|--help|-h)
    help
    ;;
*)
    echo "Unknown command: $1"
    help
    exit 1
    ;;
esac
