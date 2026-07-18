import shutil
import subprocess
import sys
from pathlib import Path

TARGET_PATH = Path("src/LLMFixedWallet.sol")


def run_command(cmd):
    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
    )
    return result.returncode, result.stdout, result.stderr


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/apply_approved_wallet_patch.py <candidate-path>")
        raise SystemExit(1)

    candidate_path = Path(sys.argv[1])

    if not candidate_path.exists():
        print(f"Candidate file not found: {candidate_path}")
        raise SystemExit(1)

    print(f"Candidate selected: {candidate_path}")
    print(f"Target file: {TARGET_PATH}")
    print()
    print("This script will apply the selected wallet candidate to src/LLMFixedWallet.sol.")
    print("Only proceed after reviewing reports/llm_wallet_patch_candidates_report.md.")
    print()

    print("Running structure validation before approval...")
    code, out, err = run_command(
        ["python3", "scripts/validate_llm_wallet_patch.py", str(candidate_path)]
    )

    if out:
        print(out)
    if err:
        print(err)

    if code != 0:
        print("Approval blocked: candidate failed structure validation.")
        raise SystemExit(1)

    print("Manual approval required.")
    confirmation = input("Type APPROVE to apply this patch: ")

    if confirmation != "APPROVE":
        print("Approval cancelled. No files were changed.")
        raise SystemExit(1)

    TARGET_PATH.parent.mkdir(exist_ok=True)
    shutil.copyfile(candidate_path, TARGET_PATH)

    print(f"Approved wallet patch applied to {TARGET_PATH}")
    print("Next recommended commands:")
    print("  python3 scripts/validate_llm_wallet_patch.py")
    print("  forge build")
    print("  forge test --match-contract LLMFixedWalletTest -vv")
    print("  rm -f llm-fixed-wallet-slither-output.json")
    print("  slither src/LLMFixedWallet.sol --json llm-fixed-wallet-slither-output.json")
    print("  grep -n '\"check\"' llm-fixed-wallet-slither-output.json")


if __name__ == "__main__":
    main()
