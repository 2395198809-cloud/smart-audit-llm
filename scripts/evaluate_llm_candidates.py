import json
import shutil
import subprocess
from pathlib import Path

CANDIDATES_DIR = Path("candidates")
TARGET_PATH = Path("src/LLMFixedVault.sol")
REPORT_PATH = Path("reports/llm_patch_candidates_report.md")
SLITHER_REPORT_DIR = Path("reports/candidate_slither")


def run_command(cmd):
    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
    )
    return result.returncode, result.stdout, result.stderr


def has_reentrancy(slither_json_path: Path) -> bool:
    if not slither_json_path.exists():
        return True

    data = json.loads(slither_json_path.read_text(encoding="utf-8"))
    findings = data.get("results", {}).get("detectors", [])
    return any(finding.get("check") == "reentrancy-eth" for finding in findings)


def status(ok: bool) -> str:
    return "通过" if ok else "失败"


def main():
    candidates = sorted(CANDIDATES_DIR.glob("LLMFixedVault_candidate_*.sol"))

    if not candidates:
        raise SystemExit("No candidates found. Run python3 scripts/generate_llm_patch.py first.")

    REPORT_PATH.parent.mkdir(exist_ok=True)
    SLITHER_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    original_code = TARGET_PATH.read_text(encoding="utf-8") if TARGET_PATH.exists() else None

    rows = []
    detail_lines = []

    try:
        for candidate in candidates:
            print(f"\nEvaluating {candidate}...")

            structure_ok = False
            build_ok = False
            test_ok = False
            slither_ok = False

            code, out, err = run_command(
                ["python3", "scripts/validate_llm_patch.py", str(candidate)]
            )
            structure_ok = code == 0

            detail_lines.append(f"## {candidate.name}")
            detail_lines.append("")
            detail_lines.append("### 结构校验")
            detail_lines.append("```text")
            detail_lines.append((out + err).strip() or "(no output)")
            detail_lines.append("```")
            detail_lines.append("")

            if structure_ok:
                shutil.copyfile(candidate, TARGET_PATH)

                code, out, err = run_command(["forge", "build"])
                build_ok = code == 0

                detail_lines.append("### forge build")
                detail_lines.append("```text")
                detail_lines.append((out + err).strip() or "(no output)")
                detail_lines.append("```")
                detail_lines.append("")

                if build_ok:
                    code, out, err = run_command(["forge", "test", "-vv"])
                    test_ok = code == 0

                    detail_lines.append("### forge test")
                    detail_lines.append("```text")
                    detail_lines.append((out + err).strip() or "(no output)")
                    detail_lines.append("```")
                    detail_lines.append("")

                if test_ok:
                    slither_output = SLITHER_REPORT_DIR / f"{candidate.stem}-slither-output.json"
                    code, out, err = run_command(
                        [
                            "slither",
                            "src/LLMFixedVault.sol",
                            "--json",
                            str(slither_output),
                        ]
                    )

                    slither_ok = code in (0, 255) and not has_reentrancy(slither_output)

                    detail_lines.append("### Slither 重扫")
                    detail_lines.append("```text")
                    detail_lines.append((out + err).strip() or "(no output)")
                    detail_lines.append("```")
                    detail_lines.append("")

            recommended = structure_ok and build_ok and test_ok and slither_ok

            rows.append(
                [
                    candidate.name,
                    status(structure_ok),
                    status(build_ok),
                    status(test_ok),
                    status(slither_ok),
                    "是" if recommended else "否",
                ]
            )

    finally:
        if original_code is not None:
            TARGET_PATH.write_text(original_code, encoding="utf-8")

    lines = []
    lines.append("# LLM 补丁候选方案评估报告")
    lines.append("")
    lines.append("| 候选方案 | 结构校验 | 编译 | 测试 | Slither 重扫 | 是否推荐 |")
    lines.append("|---|---|---|---|---|---|")

    for row in rows:
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("说明：本脚本只评估候选补丁，不执行最终应用。通过全部检查的候选方案仍需人工审批后才能写入正式源码。")
    lines.append("")
    lines.extend(detail_lines)

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"\nCandidate report written to {REPORT_PATH}")
    print("Evaluation finished. src/LLMFixedVault.sol has been restored to its original content.")


if __name__ == "__main__":
    main()
