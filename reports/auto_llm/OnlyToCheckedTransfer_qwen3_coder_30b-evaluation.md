# Auto LLM产物评估报告

产物目录：`auto_llm_artifacts/OnlyToCheckedTransfer_qwen3_coder_30b`

原始Slither结果：`reports/auto_llm/OnlyToCheckedTransfer-slither-output.json`
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
Solc 0.8.35 finished in 513.50ms
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

Ran 1 test for test/LLMAutoAttack.t.sol:AttackTest
[PASS] testNoVulnerability() (gas: 42145)
Suite result: ok. 1 passed; 0 failed; 0 skipped; finished in 280.40µs (47.96µs CPU time)

Ran 1 test suite in 5.18ms (280.40µs CPU time): 1 tests passed, 0 failed, 0 skipped (1 total tests)
```

## LLM生成修复验证测试
```text
No files changed, compilation skipped

Ran 3 tests for test/LLMAutoValidation.t.sol:ValidationTest
[PASS] testInsufficientBalanceFails() (gas: 12693)
[PASS] testNormalFunctionality() (gas: 42122)
[PASS] testTransferToZeroAddressFails() (gas: 10402)
Suite result: ok. 3 passed; 0 failed; 0 skipped; finished in 466.70µs (136.51µs CPU time)

Ran 1 test suite in 4.60ms (466.70µs CPU time): 3 tests passed, 0 failed, 0 skipped (3 total tests)
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
