// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/*
* Adapted from SmartBugs Curated:
* dataset/access_control/phishable.sol
*
* Vulnerability: tx.origin authorization bypass.
*/
contract TxOriginPhishable {
    address public owner;

    constructor(address _owner) payable {
        owner = _owner;
    }

    receive() external payable {}

    function withdrawAll(address payable recipient) external {
        require(tx.origin == owner, "not owner");

        (bool ok, ) = recipient.call{value: address(this).balance}("");
        require(ok, "transfer failed");
    }

    function totalBalance() external view returns (uint256) {
        return address(this).balance;
    }
}
