// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/*
Real-cropped/adapted benchmark sample.
Source project: OpenZeppelinERC20Permit
Source URL: https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/v4.9.6/contracts/token/ERC20/ERC20.sol
Note: ERC20-style authorization logic cropped and mutated: permit_no_sig.
This benchmark is cropped/adapted for controlled audit experiments.
It does NOT claim the upstream project contains this vulnerability.
*/

contract OZERC20PermitNoSignatureRealCrop {
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    mapping(address => uint256) public nonces;
    uint256 public totalSupply;

    constructor() {
        balanceOf[msg.sender] = 1_000_000 ether;
        totalSupply = 1_000_000 ether;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }


    function permitTransfer(address from, address to, uint256 amount, uint256 nonce) external returns (bool) {
        require(nonce == nonces[from], "nonce");
        require(balanceOf[from] >= amount, "balance");
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }

}
