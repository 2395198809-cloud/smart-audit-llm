// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnerableWallet {
    address public owner;

    constructor() payable {
        owner = msg.sender;
    }

    function withdrawAll(address payable to) external {
        require(tx.origin == owner, "not owner");

        (bool ok, ) = to.call{value: address(this).balance}("");
        require(ok, "transfer failed");
    }

    function totalBalance() external view returns (uint256) {
        return address(this).balance;
    }
}
