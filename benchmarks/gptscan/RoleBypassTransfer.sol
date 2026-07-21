// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract RoleBypassTransfer {
    mapping(address => uint256) public balanceOf;
    mapping(address => bool) public trustedRecipient;

    constructor() {
        balanceOf[msg.sender] = 1000 ether;
        trustedRecipient[msg.sender] = true;
    }

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
    }

    function setTrustedRecipient(address account, bool trusted) external {
        trustedRecipient[account] = trusted;
    }

    function privilegedTransfer(address from, address to, uint256 amount) external {
        require(trustedRecipient[to], "recipient not trusted");
        require(balanceOf[from] >= amount, "insufficient");
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
    }
}
