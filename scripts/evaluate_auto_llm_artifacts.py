import json
import shutil
import subprocess
import sys
from pathlib import Path

SRC_PATCH = Path("src/LLMAutoFixed.sol")
TEST_ATTACK = Path("test/LLMAutoAttack.t.sol")
TEST_VALIDATION = Path("test/LLMAutoValidation.t.sol")
REPORTS_DIR = Path("reports/auto_llm")

SUPPORTED_TARGET_CHECKS = [
    "reentrancy-eth",
    "reentrancy-no-eth",
    "tx-origin",
    "unchecked-lowlevel",
    "unchecked-transfer",
    "arbitrary-send-eth",
    "weak-prng",
    "timestamp",
]

NOISE_CHECKS = {
    "solc-version",
    "low-level-calls",
    "missing-zero-check",
    "immutable-states",
    "naming-convention",
}


def run_command(cmd):
    result = subprocess.run(cmd, text=True, capture_output=True)
    return result.returncode, result.stdout, result.stderr


def backup_file(path: Path):
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def restore_file(path: Path, content):
    if content is None:
        if path.exists():
            path.unlink()
    else:
        path.write_text(content, encoding="utf-8")


def load_checks(slither_json_path: Path) -> list[str]:
    if not slither_json_path.exists():
        return []

    data = json.loads(slither_json_path.read_text(encoding="utf-8"))
    findings = data.get("results", {}).get("detectors", [])

    checks = []
    for finding in findings:
        check = finding.get("check")
        if check:
            checks.append(check)

    return checks


def infer_stem_from_artifact_dir(artifact_dir: Path) -> str:
    name = artifact_dir.name

    suffixes = [
        "_qwen3_coder_30b_repaired_tests",
        "_qwen3_coder_30b",
        "_qwen25_7b",
    ]

    for suffix in suffixes:
        if name.endswith(suffix):
            return name[: -len(suffix)]

    return name


def find_original_slither_output(stem: str) -> Path | None:
    candidates = [
        REPORTS_DIR / f"{stem}-slither-output.json",
        REPORTS_DIR / f"{stem}-fixed-slither.json",
    ]

    for path in candidates:
        if path.exists():
            return path

    return None


def choose_target_checks(original_checks: list[str]) -> list[str]:
    selected = []

    for check in SUPPORTED_TARGET_CHECKS:
        if check in original_checks and check not in selected:
            selected.append(check)

    if selected:
        return selected

    for check in original_checks:
        if check not in NOISE_CHECKS and check not in selected:
            selected.append(check)

    return selected


def target_checks_removed(slither_json_path: Path, target_checks: list[str]) -> bool:
    if not target_checks:
        return False

    fixed_checks = load_checks(slither_json_path)
    return all(check not in fixed_checks for check in target_checks)


def status(ok: bool) -> str:
    return "通过" if ok else "失败"


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/evaluate_auto_llm_artifacts.py <artifact-dir>")
        raise SystemExit(1)

    artifact_dir = Path(sys.argv[1])

    if not artifact_dir.exists():
        raise SystemExit(f"Artifact dir not found: {artifact_dir}")

    attack_path = artifact_dir / "LLMAutoAttack.t.sol"
    patch_path = artifact_dir / "LLMAutoFixed.sol"
    validation_path = artifact_dir / "LLMAutoValidation.t.sol"
    audit_path = artifact_dir / "audit_report.md"

    missing = [
        str(path)
        for path in [attack_path, patch_path, validation_path, audit_path]
        if not path.exists()
    ]

    if missing:
        print("Missing generated files:")
        for item in missing:
            print("-", item)
        raise SystemExit(1)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    stem = infer_stem_from_artifact_dir(artifact_dir)
    original_slither = find_original_slither_output(stem)

    original_checks = load_checks(original_slither) if original_slither else []
    target_checks = choose_target_checks(original_checks)

    name = artifact_dir.name
    report_path = REPORTS_DIR / f"{name}-evaluation.md"
    slither_output = REPORTS_DIR / f"{name}-fixed-slither.json"

    original_patch = backup_file(SRC_PATCH)
    original_attack = backup_file(TEST_ATTACK)
    original_validation = backup_file(TEST_VALIDATION)

    build_ok = False
    attack_test_ok = False
    validation_test_ok = False
    slither_ok = False

    details = []

    try:
        shutil.copyfile(patch_path, SRC_PATCH)
        shutil.copyfile(attack_path, TEST_ATTACK)
        shutil.copyfile(validation_path, TEST_VALIDATION)

        code, out, err = run_command(["forge", "build"])
        build_ok = code == 0

        details.append("## forge build")
        details.append("```text")
        details.append((out + err).strip() or "(no output)")
        details.append("```")
        details.append("")

        if build_ok:
            code, out, err = run_command(
                ["forge", "test", "--match-path", "test/LLMAutoAttack.t.sol", "-vv"]
            )
            attack_test_ok = code == 0

            details.append("## LLM生成攻击测试")
            details.append("```text")
            details.append((out + err).strip() or "(no output)")
            details.append("```")
            details.append("")

            code, out, err = run_command(
                ["forge", "test", "--match-path", "test/LLMAutoValidation.t.sol", "-vv"]
            )
            validation_test_ok = code == 0

            details.append("## LLM生成修复验证测试")
            details.append("```text")
            details.append((out + err).strip() or "(no output)")
            details.append("```")
            details.append("")

            if slither_output.exists():
                slither_output.unlink()

            code, out, err = run_command([
                "slither",
                "src/LLMAutoFixed.sol",
                "--json",
                str(slither_output),
            ])

            slither_ok = code in (0, 255) and target_checks_removed(
                slither_output,
                target_checks,
            )

            details.append("## Slither重扫LLM补丁")
            details.append("```text")
            details.append((out + err).strip() or "(no output)")
            details.append("```")
            details.append("")

    finally:
        restore_file(SRC_PATCH, original_patch)
        restore_file(TEST_ATTACK, original_attack)
        restore_file(TEST_VALIDATION, original_validation)

    rows = [
        ["审计报告生成", status(audit_path.exists())],
        ["forge build", status(build_ok)],
        ["LLM攻击测试", status(attack_test_ok)],
        ["LLM修复验证测试", status(validation_test_ok)],
        ["Slither重扫目标告警消失", status(slither_ok)],
    ]

    lines = []
    lines.append("# Auto LLM产物评估报告")
    lines.append("")
    lines.append(f"产物目录：`{artifact_dir}`")
    lines.append("")

    if original_slither:
        lines.append(f"原始Slither结果：`{original_slither}`")
    else:
        lines.append("原始Slither结果：未找到")

    lines.append(f"原始检测项：`{', '.join(original_checks) if original_checks else '无'}`")
    lines.append(f"目标检测项：`{', '.join(target_checks) if target_checks else '未识别'}`")
    lines.append("")

    lines.append("| 检查项 | 结果 |")
    lines.append("|---|---|")

    for row in rows:
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("")
    lines.extend(details)

    report_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Evaluation report written to {report_path}")
    print("Temporary files restored.")


if __name__ == "__main__":
    main()
