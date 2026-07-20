// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract PublicBurnFrom {
    mapping(address => uint256) public balanceOf;
    uint256 public totalSupply;

    event Transfer(address indexed from, address indexed to, uint256 amount);

    function mint(address to, uint256 amount) external {
        require(to != address(0), "zero address");
        balanceOf[to] += amount;
        totalSupply += amount;
        emit Transfer(address(0), to, amount);
    }

    function burnFrom(address from, uint256 amount) external returns (bool) {
        require(from != address(0), "zero from");
        require(balanceOf[from] >= amount, "insufficient balance");

        balanceOf[from] -= amount;
        totalSupply -= amount;

        emit Transfer(from, address(0), amount);
        return true;
    }
}
