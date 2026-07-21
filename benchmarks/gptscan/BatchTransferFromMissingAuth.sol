// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract BatchTransferFromMissingAuth {
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

    function batchTransferFrom(address[] calldata froms, address[] calldata tos, uint256[] calldata amounts) external
    {
        require(froms.length == tos.length && tos.length == amounts.length, "length mismatch");
        for (uint256 i = 0; i < froms.length; i++) {
            require(balanceOf[froms[i]] >= amounts[i], "insufficient");
            balanceOf[froms[i]] -= amounts[i];
            balanceOf[tos[i]] += amounts[i];
        }
    }
}
