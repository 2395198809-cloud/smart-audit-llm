// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract PermitNonceMissingTransfer {
    mapping(address => uint256) public balanceOf;
    mapping(address => uint256) public nonces;

    constructor() {
        balanceOf[msg.sender] = 1000 ether;
    }

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
    }

    function permitTransferFrom(address owner, address to, uint256 amount, uint256 deadline, bytes calldata signature)
    external {
        require(deadline >= block.timestamp, "expired");
        require(signature.length > 0, "empty signature");
        require(balanceOf[owner] >= amount, "insufficient");
        balanceOf[owner] -= amount;
        balanceOf[to] += amount;
    }
}
