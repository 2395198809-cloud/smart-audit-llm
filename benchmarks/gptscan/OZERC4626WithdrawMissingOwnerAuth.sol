// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/*
Real-cropped/adapted benchmark sample.
Source project: OpenZeppelinERC4626
Source URL: https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/v4.9.6/contracts/token/ERC20/extensions/ERC4626.sol
Note: ERC4626/Vault-style withdraw/redeem cropped and mutated: missing_owner.
This benchmark is cropped/adapted for controlled audit experiments.
It does NOT claim the upstream project contains this vulnerability.
*/

contract OZERC4626WithdrawMissingOwnerAuth {
    mapping(address => uint256) public shares;
    mapping(address => mapping(address => uint256)) public allowance;

    constructor() {
        shares[msg.sender] = 1_000_000 ether;
    }

    function approve(address spender, uint256 amount) external {
        allowance[msg.sender][spender] = amount;
    }

    function withdrawFrom(address owner, address receiver, uint256 amount) external {
        require(shares[owner] >= amount, "shares");
        if (allowance[owner][msg.sender] >= amount) allowance[owner][msg.sender]-= amount;
        shares[owner] -= amount;
        shares[receiver] += amount;
    }
}
