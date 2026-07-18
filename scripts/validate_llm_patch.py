import sys
from pathlib import Path

PATCH_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("src/LLMFixedVault.sol")

if not PATCH_PATH.exists():
    print(f"LLM patch validation failed: {PATCH_PATH}")
    print("- 补丁文件不存在")
    raise SystemExit(1)

code = PATCH_PATH.read_text(encoding="utf-8")

errors = []

if "pragma solidity ^0.8.20;" not in code:
    errors.append("Solidity 版本必须保持 pragma solidity ^0.8.20;")

if "contract LLMFixedVault" not in code:
    errors.append("合约名必须是 LLMFixedVault")

if "mapping(address => uint256) public balances" not in code:
    errors.append("必须保留 public balances 映射")

if "function deposit() external payable" not in code:
    errors.append("必须保留 deposit() external payable")

if "function withdraw() external" not in code:
    errors.append("withdraw 必须保持无参数 external 接口")

if "function withdraw(uint256" in code:
    errors.append("withdraw 不能改成带参数接口")

if "function totalBalance() external view returns (uint256)" not in code:
    errors.append("必须保留 totalBalance() external view returns (uint256)")

if "return address(this).balance;" not in code:
    errors.append("totalBalance() 必须保持返回 address(this).balance")

for forbidden in [
    "tx.origin",
    "selfdestruct",
    "delegatecall",
    "onlyOwner",
    "Ownable",
    "Pausable",
    "blacklist",
]:
    if forbidden in code:
        errors.append(f"不能引入无关或危险机制: {forbidden}")

balance_read = code.find("uint256 amount = balances[msg.sender]")
balance_update = code.find("balances[msg.sender] = 0")
external_call = code.find(".call{value: amount}")

if balance_read == -1:
    errors.append("withdraw 中必须先读取 uint256 amount = balances[msg.sender]")

if balance_update == -1:
    errors.append("withdraw 中必须执行 balances[msg.sender] = 0")

if external_call == -1:
    errors.append('withdraw 中必须使用 msg.sender.call{value: amount}("") 转账')

if balance_read != -1 and balance_update != -1 and balance_read > balance_update:
    errors.append("读取 amount 必须发生在清零之前")

if balance_update != -1 and external_call != -1 and balance_update > external_call:
    errors.append("balances[msg.sender] 清零必须发生在外部 call 之前")

if "balances[msg.sender] -=" in code:
    errors.append("不能使用 balances[msg.sender] -= amount 作为修复")

if errors:
    print(f"LLM patch validation failed: {PATCH_PATH}")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print(f"LLM patch validation passed: {PATCH_PATH}")
