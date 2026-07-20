// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract OnlyToCheckedTransfer {
    mapping(address => uint256) public balanceOf;

    event Transfer(address indexed from, address indexed to, uint256 amount);

    function mint(address to, uint256 amount) external {
        require(to != address(0), "zero address");
        balanceOf[to] += amount;
    }

    function move(address from, address to, uint256 amount) external returns (bool) {
        require(to != address(0), "zero address");
        require(from != address(0), "zero from");
        require(balanceOf[from] >= amount, "insufficient balance");

        balanceOf[from] -= amount;
        balanceOf[to] += amount;

        emit Transfer(from, to, amount);
        return true;
    }
}
