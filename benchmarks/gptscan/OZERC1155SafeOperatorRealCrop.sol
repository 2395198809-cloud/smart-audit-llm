// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/*
Real-cropped/adapted benchmark sample.
Source project: OpenZeppelin ERC1155
Source URL: https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/v4.9.6/contracts/token/ERC1155/ERC1155.sol
Note: Safe ERC1155-style operator check cropped from real approval pattern.
This benchmark is cropped/adapted for controlled audit experiments.
It does NOT claim the upstream project contains this vulnerability.
*/

contract OZERC1155SafeOperatorRealCrop {
    mapping(uint256 => mapping(address => uint256)) public balanceOf;
    mapping(address => mapping(address => bool)) public isApprovedForAll;

    constructor() {
        balanceOf[1][msg.sender] = 100;
    }

    function setApprovalForAll(address operator, bool approved) external {
        isApprovedForAll[msg.sender][operator] = approved;
    }

    function safeTransferFrom(address from, address to, uint256 id, uint256 amount) external {
        require(msg.sender == from || isApprovedForAll[from][msg.sender], "not-approved");
        require(balanceOf[id][from] >= amount, "balance");
        balanceOf[id][from] -= amount;
        balanceOf[id][to] += amount;
    }
}
