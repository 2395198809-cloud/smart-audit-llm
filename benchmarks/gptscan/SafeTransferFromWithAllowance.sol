// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SafeTransferFromWithAllowance {
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    constructor() {
        balanceOf[msg.sender] = 1000 ether;
    }

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
    }

    function approve(address spender, uint256 amount) external {
        allowance[msg.sender][spender] = amount;
    }

    function transferFrom(address from, address to, uint256 amount) external {
        require(to != address(0), "bad to");
        require(balanceOf[from] >= amount, "insufficient");
        if (msg.sender != from) {
            require(allowance[from][msg.sender] >= amount, "allowance too low");
            allowance[from][msg.sender] -= amount;
        }
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
    }
}
