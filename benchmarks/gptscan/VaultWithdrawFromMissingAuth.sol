// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VaultWithdrawFromMissingAuth {
    mapping(address => uint256) public shares;

    constructor() {
        shares[msg.sender] = 1000 ether;
    }

    function depositFor(address account, uint256 amount) external {
        shares[account] += amount;
    }

    function withdrawFrom(address owner, address receiver, uint256 amount) external {
        require(receiver != address(0), "bad receiver");
        require(shares[owner] >= amount, "insufficient shares");
        shares[owner] -= amount;
        shares[receiver] += amount;
    }
}
