# Smart Audit LLM Demo

这是一个LLM辅助智能合约审计与自动修复验证Demo。

项目结合：

- Slither静态分析
- Foundry攻击PoC与回归测试
- 本地Ollama模型
- Qwen3-Coder 30B
- LLM中文审计报告生成
- LLM候选补丁生成
- 结构校验
- Slither重扫
- 人工审批应用

## 项目目标

本项目不是让智能合约在链上调用大模型，而是在链下使用LLM辅助智能合约安全审计。

核心观点：

> LLM可以辅助漏洞解释、审计报告生成和补丁生成，但不能直接信任其输出。必须结合静态分析、编译、动态测试、结构校验和人工
审批。

## 已支持实验

### 重入漏洞

相关文件：

- `src/VulnerableVault.sol`
- `src/FixedVault.sol`
- `src/LLMFixedVault.sol`
- `test/VulnerableVault.t.sol`
- `test/FixedVault.t.sol`
- `test/LLMFixedVault.t.sol`

### tx.origin权限绕过

相关文件：

- `src/VulnerableWallet.sol`
- `src/FixedWallet.sol`
- `src/LLMFixedWallet.sol`
- `test/VulnerableWallet.t.sol`
- `test/FixedWallet.t.sol`
- `test/LLMFixedWallet.t.sol`

### SmartBugs迁移样本

相关文件：

- `benchmarks/smartbugs/TxOriginPhishable.sol`
- `benchmarks/smartbugs/SimpleDAO.sol`
- `benchmarks/smartbugs/UncheckedCall.sol`

样本改编自SmartBugs Curated，仅用于安全研究与教学实验：

https://github.com/smartbugs/smartbugs-curated

## 环境依赖

- Ubuntu / WSL
- Foundry
- Slither
- Python 3
- Ollama
- qwen3-coder:30b

安装模型：

```bash
ollama pull qwen3-coder:30b

启动Ollama：

ollama serve

## 快速运行

检查环境：

bash scripts/run_demo.sh status

运行核心Demo：

bash scripts/run_demo.sh core

运行不指定漏洞类型的自动生成实验：

bash scripts/run_demo.sh auto

运行SmartBugs样本实验：

bash scripts/run_demo.sh smartbugs

完整运行：

bash scripts/run_demo.sh all

## 安全边界

LLM生成的补丁不会直接写入正式源码。系统采用：

1. 候选补丁生成
2. 结构校验
3. forge build
4. forge test
5. Slither重扫
6. 人工输入APPROVE后应用

