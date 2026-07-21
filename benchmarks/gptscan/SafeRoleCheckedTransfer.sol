// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SafeRoleCheckedTransfer {
    mapping(address => uint256) public balanceOf;
    mapping(address => bool) public operator;

    constructor() {
        balanceOf[msg.sender] = 1000 ether;
        operator[msg.sender] = true;
    }

    function mint(address to, uint256 amount) external {
        require(operator[msg.sender], "not operator");
        balanceOf[to] += amount;
    }

    function setOperator(address account, bool approved) external {
        require(operator[msg.sender], "not operator");
        operator[account] = approved;
    }

    function operatorTransfer(address from, address to, uint256 amount) external {
        require(operator[msg.sender] || msg.sender == from, "not authorized");
        require(to != address(0), "bad to");
        require(balanceOf[from] >= amount, "insufficient");
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
    }
}
