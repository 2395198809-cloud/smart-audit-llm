// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ERC1155TransferMissingOperator {
    mapping(uint256 => mapping(address => uint256)) public balanceOf;
    mapping(address => mapping(address => bool)) public isApprovedForAll;

    constructor() {
        balanceOf[1][msg.sender] = 1000;
    }

    function mint(address to, uint256 id, uint256 amount) external {
        balanceOf[id][to] += amount;
    }

    function setApprovalForAll(address operator, bool approved) external {
        isApprovedForAll[msg.sender][operator] = approved;
    }

    function safeTransferFrom(address from, address to, uint256 id, uint256 amount, bytes calldata data) external {
        require(data.length >= 0, "unused");
        require(to != address(0), "bad to");
        require(balanceOf[id][from] >= amount, "insufficient");
        balanceOf[id][from] -= amount;
        balanceOf[id][to] += amount;
    }
}
