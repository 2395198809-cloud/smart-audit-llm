# 智能合约自动审计报告

## 1. 审计对象

- 合约文件：`src/VulnerableVault.sol`
- Slither 告警数量：`3`

## 2. Slither 检测结果

### 2.1 reentrancy-eth

- 风险等级：`High`
- 置信度：`Medium`

Slither 原始描述：

```text
Reentrancy in VulnerableVault.withdraw() (src/VulnerableVault.sol#11-19):
	External calls:
	- (ok,None) = msg.sender.call{value: amount}() (src/VulnerableVault.sol#15)
	State variables written after the call(s):
	- balances[msg.sender] = 0 (src/VulnerableVault.sol#18)
	VulnerableVault.balances (src/VulnerableVault.sol#5) can be used in cross function reentrancies:
	- VulnerableVault.balances (src/VulnerableVault.sol#5)
	- VulnerableVault.deposit() (src/VulnerableVault.sol#7-9)
	- VulnerableVault.withdraw() (src/VulnerableVault.sol#11-19)
```

## 3. 漏洞解释：重入攻击

该合约的 `withdraw()` 函数存在典型重入风险。
函数在向 `msg.sender` 执行外部转账之后，才将 `balances[msg.sender]` 清零。
攻击者可以部署恶意合约，在 `receive()` 回调函数中再次调用 `withdraw()`。
由于余额尚未清零，攻击者可以重复提款。

危险代码模式如下：

```solidity
(bool ok, ) = msg.sender.call{value: amount}("");
require(ok, "transfer failed");

balances[msg.sender] = 0;
```

## 4. 攻击路径

1. 攻击者向合约存入少量 ETH。
2. 攻击者调用 `withdraw()`。
3. 合约向攻击者合约转账。
4. 攻击者合约的 `receive()` 被触发。
5. `receive()` 中再次调用 `withdraw()`。
6. 因为余额尚未清零，攻击者可以重复提取资金。

## 5. 影响

攻击者可能提取超过自己存款的 ETH，导致其他用户存入合约的资产被盗。

## 6. 修复建议

应遵循 Checks-Effects-Interactions 模式：先检查条件，再更新状态，最后执行外部调用。

修复方式如下：

```solidity
function withdraw() external {
    uint256 amount = balances[msg.sender];
    require(amount > 0, "no balance");

    balances[msg.sender] = 0;

    (bool ok, ) = msg.sender.call{value: amount}("");
    require(ok, "transfer failed");
}
```

也可以使用 OpenZeppelin 的 `ReentrancyGuard`。

## 7. PoC 验证

当前项目中的 Foundry 测试 `test/VulnerableVault.t.sol` 已经验证该漏洞可被利用。

运行：

```bash
forge test -vv
```

如果 `testReentrancyAttack()` 通过，说明攻击 PoC 成功。

### 2.2 solc-version

- 风险等级：`Informational`
- 置信度：`High`

Slither 原始描述：

```text
Version constraint ^0.8.20 contains known severe issues (https://solidity.readthedocs.io/en/latest/bugs.html)
	- VerbatimInvalidDeduplication
	- FullInlinerNonExpressionSplitArgumentEvaluationOrder
	- MissingSideEffectsOnSelectorAccess.
It is used by:
	- ^0.8.20 (src/VulnerableVault.sol#2)
```

### 2.3 low-level-calls

- 风险等级：`Informational`
- 置信度：`High`

Slither 原始描述：

```text
Low level call in VulnerableVault.withdraw() (src/VulnerableVault.sol#11-19):
	- (ok,None) = msg.sender.call{value: amount}() (src/VulnerableVault.sol#15)
```

## 附录：被审计合约源码

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnerableVault {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() external {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "no balance");

        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "transfer failed");

        balances[msg.sender] = 0;
    }

    function totalBalance() external view returns (uint256) {
        return address(this).balance;
    }
}

```