# SmartBugs2-semgrep-custom 未授权转账多样本量化实验

| 样本 | 运行状态 | 漏洞识别 | 函数定位 | 输出文件 |
|---|---|---|---|---|
| `UnauthorizedTokenTransfer` | 完成 | 通过 | 通过 | `reports/focused_quantification/smartbugs2_multi/semgrep_custom/UnauthorizedTokenTransfer.json` |
| `MissingAllowanceTransferFrom` | 完成 | 通过 | 通过 | `reports/focused_quantification/smartbugs2_multi/semgrep_custom/MissingAllowanceTransferFrom.json` |
| `WrongAllowanceOwner` | 完成 | 通过 | 通过 | `reports/focused_quantification/smartbugs2_multi/semgrep_custom/WrongAllowanceOwner.json` |
| `OnlyToCheckedTransfer` | 完成 | 通过 | 通过 | `reports/focused_quantification/smartbugs2_multi/semgrep_custom/OnlyToCheckedTransfer.json` |
| `PublicBurnFrom` | 完成 | 通过 | 通过 | `reports/focused_quantification/smartbugs2_multi/semgrep_custom/PublicBurnFrom.json` |

## 汇总

- 样本数：5
- 运行完成率：5/5 = 100.0%
- 漏洞识别率：5/5 = 100.0%
- 函数定位率：5/5 = 100.0%