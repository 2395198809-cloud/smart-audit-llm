import sys
from pathlib import Path

PATCH_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("src/LLMFixedWallet.sol")

if not PATCH_PATH.exists():
    print(f"LLM wallet patch validation failed: {PATCH_PATH}")
    print("- 补丁文件不存在")
    raise SystemExit(1)

code = PATCH_PATH.read_text(encoding="utf-8")

errors = []

if "pragma solidity ^0.8.20;" not in code:
    errors.append("Solidity版本必须保持pragma solidity ^0.8.20;")

if "contract LLMFixedWallet" not in code:
    errors.append("合约名必须是LLMFixedWallet")

if "address public owner" not in code:
    errors.append("必须保留address public owner")

if "constructor() payable" not in code:
    errors.append("必须保留constructor() payable")

if "function withdrawAll(address payable to) external" not in code:
    errors.append("必须保留withdrawAll(address payable to) external接口")

if "function totalBalance() external view returns (uint256)" not in code:
    errors.append("必须保留totalBalance() external view returns (uint256)")

if "return address(this).balance;" not in code:
    errors.append("totalBalance()必须返回address(this).balance")

if "tx.origin" in code:
    errors.append("不能使用tx.origin进行权限校验")

if "msg.sender == owner" not in code:
    errors.append("必须使用msg.sender == owner进行权限校验")

if "function withdrawAll()" in code:
    errors.append("不能修改withdrawAll为无参数接口")

for forbidden in ["Ownable", "onlyOwner", "import ", "delegatecall", "selfdestruct"]:
    if forbidden in code:
        errors.append(f"不能引入无关或危险机制:{forbidden}")

if errors:
    print(f"LLM wallet patch validation failed: {PATCH_PATH}")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print(f"LLM wallet patch validation passed: {PATCH_PATH}")
