// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SafeInternalMove {
    mapping(address => uint256) public balanceOf;

    constructor() {
        balanceOf[msg.sender] = 1000 ether;
    }

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
    }

    function transfer(address to, uint256 amount) external {
        _move(msg.sender, to, amount);
    }

    function _move(address from, address to, uint256 amount) internal {
        require(to != address(0), "bad to");
        require(balanceOf[from] >= amount, "insufficient");
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
    }
}
