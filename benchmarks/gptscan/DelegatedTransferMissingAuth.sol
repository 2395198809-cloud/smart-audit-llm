// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract DelegatedTransferMissingAuth {
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => bool)) public delegates;

    constructor() {
        balanceOf[msg.sender] = 1000 ether;
    }

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
    }

    function setDelegate(address delegate, bool approved) external {
        delegates[msg.sender][delegate] = approved;
    }

    function delegatedTransfer(address from, address to, uint256 amount) external {
        require(to != address(0), "bad to");
        require(balanceOf[from] >= amount, "insufficient");
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
    }
}
