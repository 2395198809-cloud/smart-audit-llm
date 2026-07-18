// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/*
* Adapted from SmartBugs Curated:
* dataset/reentrancy/simple_dao.sol
*
* Vulnerability: reentrancy.
*/
contract SimpleDAO {
    mapping(address => uint256) public credit;

    function donate(address to) external payable {
        credit[to] += msg.value;
    }

    function withdraw(uint256 amount) external {
        if (credit[msg.sender] >= amount) {
            (bool ok, ) = msg.sender.call{value: amount}("");
            require(ok, "transfer failed");

            credit[msg.sender] -= amount;
        }
    }

    function queryCredit(address to) external view returns (uint256) {
        return credit[to];
    }

    function totalBalance() external view returns (uint256) {
        return address(this).balance;
    }
}
