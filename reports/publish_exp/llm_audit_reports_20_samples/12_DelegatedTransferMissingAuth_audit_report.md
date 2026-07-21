#### 漏洞类型
权限绕过（Missing Authorization）

#### 漏洞位置
函数 `delegatedTransfer(address from, address to, uint256 amount)` 在合约 `DelegatedTransferMissingAuth` 中。

#### 漏洞成因
该函数没有对调用者是否被授权执行转账操作进行检查。虽然存在一个 `setDelegate()` 函数用于设置委托关系，但 `delegatedTransfer()` 并未验证调用者是否为 `from` 地址的合法代理人。因此，任何地址都可以代表任意账户发起转账。

#### 攻击路径
1. 用户A拥有资金并调用 `setDelegate(addressB, true)` 将地址B设为其代理。
2. 地址B可以调用 `delegatedTransfer(from=A, to=C, amount=100)`，绕过权限控制直接转移A的资金到C。
3. 由于未检查调用者是否为授权代理人，攻击者可任意操作他人资产。

#### 影响
此漏洞允许任意地址代表其他账户执行转账操作，导致资金被盗或滥用。这是一个严重的安全问题，可能导致用户资产损失。

#### 修复建议
在 `delegatedTransfer()` 函数中添加对调用者是否为 `from` 账户代理的检查逻辑。若未授权，则拒绝交易。
