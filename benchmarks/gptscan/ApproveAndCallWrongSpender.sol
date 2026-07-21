// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ApproveAndCallWrongSpender {
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

    function transferWithApproval(address owner, address spender, address to, uint256 amount) external {
        require(allowance[msg.sender][spender] >= amount, "allowance too low");
        require(balanceOf[owner] >= amount, "insufficient");
        allowance[msg.sender][spender] -= amount;
        balanceOf[owner] -= amount;
        balanceOf[to] += amount;
    }
}
