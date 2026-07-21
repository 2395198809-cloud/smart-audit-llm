#### 漏洞类型
**权限绕过（Permission Bypass）**

#### 漏洞位置
`transferFrom` 函数中对 `allowance[msg.sender][from]` 的检查逻辑错误。

#### 漏洞成因
在 `transferFrom` 函数中，调用者 `msg.sender` 被用来作为 allowance 的所有者（owner），而实际应该使用的是 `from` 地址。这导致攻击者可以通过构造恶意的调用链绕过授权机制，从而非法转移资金。

具体来说：
