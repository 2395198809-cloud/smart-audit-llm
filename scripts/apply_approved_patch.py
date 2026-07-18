import shutil
import subprocess
import sys
from pathlib import Path

TARGET_PATH = Path("src/LLMFixedVault.sol")


def run_command(cmd):
    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
    )
    return result.returncode, result.stdout, result.stderr


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/apply_approved_patch.py <candidate-path>")
        raise SystemExit(1)

    candidate_path = Path(sys.argv[1])

    if not candidate_path.exists():
        print(f"Candidate file not found: {candidate_path}")
        raise SystemExit(1)

    print(f"Candidate selected: {candidate_path}")
    print(f"Target file: {TARGET_PATH}")
    print()
    print("This script will apply the selected candidate to src/LLMFixedVault.sol.")
    print("Only proceed after reviewing reports/llm_patch_candidates_report.md.")
    print()

    print("Running structure validation before approval...")
    code, out, err = run_command(
        ["python3", "scripts/validate_llm_patch.py", str(candidate_path)]
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

    print(f"Approved patch applied to {TARGET_PATH}")
    print("Next recommended commands:")
    print("  forge build")
    print("  forge test -vv")
    print("  slither src/LLMFixedVault.sol --json llm-fixed-slither-output.json")


if __name__ == "__main__":
    main()
