# 未授权转账多样本量化实验

聚焦问题：未授权代币转移 / 权限绕过型资产转移。

| 样本 | 审计报告 | 补丁编译 | 攻击PoC | 修复验证 | 评估报告 |
|---|---|---|---|---|---|
| `UnauthorizedTokenTransfer` | 通过 | 通过 | 通过 | 通过 | `reports/auto_llm/UnauthorizedTokenTransfer_qwen3_coder_30b-evaluation.md` |
| `MissingAllowanceTransferFrom` | 通过 | 通过 | 通过 | 失败 | `reports/auto_llm/MissingAllowanceTransferFrom_qwen3_coder_30b-evaluation.md` |
| `WrongAllowanceOwner` | 通过 | 通过 | 失败 | 通过 | `reports/auto_llm/WrongAllowanceOwner_qwen3_coder_30b-evaluation.md` |
| `OnlyToCheckedTransfer` | 失败 | 通过 | 通过 | 通过 | `reports/auto_llm/OnlyToCheckedTransfer_qwen3_coder_30b-evaluation.md` |
| `PublicBurnFrom` | 通过 | 通过 | 通过 | 通过 | `reports/auto_llm/PublicBurnFrom_qwen3_coder_30b-evaluation.md` |

## 汇总

- 样本数：5
- 审计报告识别率：4/5 = 80.0%
- 补丁编译通过率：5/5 = 100.0%
- 攻击PoC成功率：4/5 = 80.0%
- 修复验证通过率：4/5 = 80.0%

## 论文可写结论

多样本实验用于观察 LLM 在同一类业务逻辑漏洞上的稳定性。若某些样本攻击PoC或修复验证失败，应作为失败案例分析，说明LLM 生成测试和补丁仍需自动评估与人工审批。