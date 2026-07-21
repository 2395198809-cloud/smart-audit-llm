// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SafeBurnFromWithAllowance {
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    uint256 public totalSupply;

    constructor() {
        balanceOf[msg.sender] = 1000 ether;
        totalSupply = 1000 ether;
    }

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
        totalSupply += amount;
    }

    function approve(address spender, uint256 amount) external {
        allowance[msg.sender][spender] = amount;
    }

    function burnFrom(address from, uint256 amount) external {
        if (msg.sender != from) {
            require(allowance[from][msg.sender] >= amount, "allowance too low");
            allowance[from][msg.sender] -= amount;
        }
        require(balanceOf[from] >= amount, "insufficient");
        balanceOf[from] -= amount;
        totalSupply -= amount;
    }
}
