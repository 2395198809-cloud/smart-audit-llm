# Auto LLM产物评估报告

产物目录：`auto_llm_artifacts/TxOriginPhishable_qwen3_coder_30b`

原始Slither结果：`reports/auto_llm/TxOriginPhishable-slither-output.json`
原始检测项：`arbitrary-send-eth, tx-origin, missing-zero-check, missing-zero-check, solc-version, low-level-calls, immutable-states`
目标检测项：`tx-origin, arbitrary-send-eth`

| 检查项 | 结果 |
|---|---|
| 审计报告生成 | 通过 |
| forge build | 失败 |
| LLM攻击测试 | 失败 |
| LLM修复验证测试 | 失败 |
| Slither重扫目标告警消失 | 失败 |


## forge build
```text
Compiling 35 files with Solc 0.8.35
Solc 0.8.35 finished in 44.36ms
Error: Compiler run failed:
Error (6933): Expected primary expression.
  --> test/LLMAutoValidation.t.sol:32:9:
   |
32 |         contract PhishingContract {
   |         ^^^^^^^^
```
