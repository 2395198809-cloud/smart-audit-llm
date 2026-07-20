# Auto LLM产物评估报告

产物目录：`auto_llm_artifacts/PublicBurnFrom_qwen3_coder_30b`

原始Slither结果：`reports/auto_llm/PublicBurnFrom-slither-output.json`
原始检测项：`solc-version`
目标检测项：`未识别`

| 检查项 | 结果 |
|---|---|
| 审计报告生成 | 通过 |
| forge build | 通过 |
| LLM攻击测试 | 通过 |
| LLM修复验证测试 | 通过 |
| Slither重扫目标告警消失 | 失败 |


## forge build
```text
Compiling 38 files with Solc 0.8.35
Solc 0.8.35 finished in 515.17ms
Compiler run successful with warnings:
Warning (9302): Return value of low-level calls not used.
  --> benchmarks/smartbugs/UncheckedCall.sol:20:9:
   |
20 |         callee.call("");
   |         ^^^^^^^^^^^^^^^
```

## LLM生成攻击测试
```text
No files changed, compilation skipped

Ran 1 test for test/LLMAutoAttack.t.sol:PublicBurnFromAttackTest
[PASS] testBurnFromWithoutAuthorization() (gas: 30607)
Suite result: ok. 1 passed; 0 failed; 0 skipped; finished in 470.83µs (51.18µs CPU time)

Ran 1 test suite in 4.97ms (470.83µs CPU time): 1 tests passed, 0 failed, 0 skipped (1 total tests)
```

## LLM生成修复验证测试
```text
No files changed, compilation skipped

Ran 2 tests for test/LLMAutoValidation.t.sol:LLMAutoFixedValidationTest
[PASS] testBurnFromWithApproval() (gas: 55867)
[PASS] testBurnFromWithoutApprovalShouldFail() (gas: 18973)
Suite result: ok. 2 passed; 0 failed; 0 skipped; finished in 849.35µs (220.36µs CPU time)

Ran 1 test suite in 4.83ms (849.35µs CPU time): 2 tests passed, 0 failed, 0 skipped (2 total tests)
```

## Slither重扫LLM补丁
```text
'forge clean' running (wd: /home/tianlang/smart-audit-llm)
'forge config --json' running
'forge build --build-info src/LLMAutoFixed.sol' running (wd: /home/tianlang/smart-audit-llm)

Detector: solc-version
Version constraint ^0.8.19 contains known severe issues (https://solidity.readthedocs.io/en/latest/bugs.html)
	- VerbatimInvalidDeduplication
	- FullInlinerNonExpressionSplitArgumentEvaluationOrder
	- MissingSideEffectsOnSelectorAccess.
It is used by:
	- ^0.8.19 (src/LLMAutoFixed.sol#2)
Reference: https://github.com/crytic/slither/wiki/Detector-Documentation#incorrect-versions-of-solidity
src/LLMAutoFixed.sol analyzed (1 contracts with 101 detectors), 1 result(s) found
```
