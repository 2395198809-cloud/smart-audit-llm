# GPTScan 未授权转账多样本量化实验

| 样本 | 漏洞识别 | 函数定位 | GPTScan输出 |
|---|---|---|---|
| `UnauthorizedTokenTransfer` | 通过 | 通过 | `reports/focused_quantification/gptscan_multi/UnauthorizedTokenTransfer.txt` |
| `MissingAllowanceTransferFrom` | 通过 | 通过 | `reports/focused_quantification/gptscan_multi/MissingAllowanceTransferFrom.txt` |
| `WrongAllowanceOwner` | 失败 | 失败 | `reports/focused_quantification/gptscan_multi/WrongAllowanceOwner.txt` |
| `OnlyToCheckedTransfer` | 失败 | 失败 | `reports/focused_quantification/gptscan_multi/OnlyToCheckedTransfer.txt` |
| `PublicBurnFrom` | 通过 | 通过 | `reports/focused_quantification/gptscan_multi/PublicBurnFrom.txt` |

## 汇总

- 样本数：5
- GPTScan漏洞识别率：3/5 = 60.0%
- GPTScan函数定位率：3/5 = 60.0%