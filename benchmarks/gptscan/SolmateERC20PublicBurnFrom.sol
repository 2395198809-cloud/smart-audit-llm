// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/*
Real-cropped/adapted benchmark sample.
Source project: Solmate ERC20
Source URL: https://raw.githubusercontent.com/transmissions11/solmate/main/src/tokens/ERC20.sol
Note: ERC20-style authorization logic cropped and mutated: public_burn.
This benchmark is cropped/adapted for controlled audit experiments.
It does NOT claim the upstream project contains this vulnerability.
*/

contract SolmateERC20PublicBurnFrom {
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


    function burnFrom(address from, uint256 amount) external {
        require(balanceOf[from] >= amount, "balance");
        balanceOf[from] -= amount;
        totalSupply -= amount;
    }

}
