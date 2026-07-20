# Slither 未授权转账多样本量化实验

说明：Slither 对未授权代币转移这类业务逻辑漏洞缺少稳定专用 detector，因此这里只统计是否出现目标相关告警。

| 样本 | 目标相关告警 | 函数定位 | Slither输出 |
|---|---|---|---|
| `UnauthorizedTokenTransfer` | 失败 | 失败 | `reports/focused_quantification/slither_multi/UnauthorizedTokenTransfer.txt` |
| `MissingAllowanceTransferFrom` | 失败 | 失败 | `reports/focused_quantification/slither_multi/MissingAllowanceTransferFrom.txt` |
| `WrongAllowanceOwner` | 失败 | 失败 | `reports/focused_quantification/slither_multi/WrongAllowanceOwner.txt` |
| `OnlyToCheckedTransfer` | 失败 | 失败 | `reports/focused_quantification/slither_multi/OnlyToCheckedTransfer.txt` |
| `PublicBurnFrom` | 失败 | 失败 | `reports/focused_quantification/slither_multi/PublicBurnFrom.txt` |

## 汇总

- 样本数：5
- Slither目标相关告警率：0/5 = 0.0%
- Slither函数定位率：0/5 = 0.0%