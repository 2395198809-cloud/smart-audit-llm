# SmartBugs 2.0 未授权转账多样本量化实验

说明：SmartBugs 2.0 是多工具执行框架。本文使用其 slither 工具配置对 5 个未授权转账类样本进行统一运行。

| 样本 | 运行状态 | 目标相关输出 | 函数定位 | 输出文件 |
|---|---|---|---|---|
| `UnauthorizedTokenTransfer` | 完成 | 失败 | 失败 | `reports/focused_quantification/smartbugs2_multi/slither/UnauthorizedTokenTransfer.txt` |
| `MissingAllowanceTransferFrom` | 完成 | 失败 | 失败 | `reports/focused_quantification/smartbugs2_multi/slither/MissingAllowanceTransferFrom.txt` |
| `WrongAllowanceOwner` | 完成 | 失败 | 失败 | `reports/focused_quantification/smartbugs2_multi/slither/WrongAllowanceOwner.txt` |
| `OnlyToCheckedTransfer` | 完成 | 失败 | 失败 | `reports/focused_quantification/smartbugs2_multi/slither/OnlyToCheckedTransfer.txt` |
| `PublicBurnFrom` | 完成 | 失败 | 失败 | `reports/focused_quantification/smartbugs2_multi/slither/PublicBurnFrom.txt` |

## 汇总

- 样本数：5
- SmartBugs2-slither 运行完成率：5/5 = 100.0%
- SmartBugs2-slither 目标相关输出率：0/5 = 0.0%
- SmartBugs2-slither 函数定位率：0/5 = 0.0%

## 论文可写结论

SmartBugs 2.0 能够作为统一执行框架运行底层分析工具。其检测能力取决于被调用工具本身；在未授权代币转移这类业务逻辑漏洞上，如果底层工具缺少专门 detector，仍可能无法直接识别漏洞。