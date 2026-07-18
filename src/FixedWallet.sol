// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract FixedWallet {
    address public owner;

    constructor() payable {
        owner = msg.sender;
    }

    function withdrawAll(address payable to) external {
        require(msg.sender == owner, "not owner");

        (bool ok, ) = to.call{value: address(this).balance}("");
        require(ok, "transfer failed");
    }

    function totalBalance() external view returns (uint256) {
        return address(this).balance;
    }
}
