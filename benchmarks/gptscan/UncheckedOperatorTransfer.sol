// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract UncheckedOperatorTransfer {
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => bool)) public operatorApproval;

    constructor() {
        balanceOf[msg.sender] = 1000 ether;
    }

    function setApprovalForAll(address operator, bool approved) external {
        operatorApproval[msg.sender][operator] = approved;
    }

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
    }

    function operatorTransfer(address operator, address from, address to, uint256 amount) external {
        require(operator != address(0), "bad operator");
        require(to != address(0), "bad to");
        require(balanceOf[from] >= amount, "insufficient");
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
    }
}
