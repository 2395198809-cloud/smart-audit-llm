// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract FirstDepositVault {
    mapping(address => uint256) public balanceOf;

    uint256 public totalAssets;
    uint256 public totalShares;

    function deposit(uint256 assets) external returns (uint256 shares) {
        require(assets > 0, "zero assets");

        if (totalShares == 0) {
            shares = assets;
        } else {
            shares = assets * totalShares / totalAssets;
        }

        require(shares > 0, "zero shares");

        balanceOf[msg.sender] += shares;
        totalShares += shares;
        totalAssets += assets;
    }

    function donate(uint256 assets) external {
        require(assets > 0, "zero assets");
        totalAssets += assets;
    }

    function withdraw(uint256 shares) external returns (uint256 assets) {
        require(balanceOf[msg.sender] >= shares, "insufficient shares");

        assets = shares * totalAssets / totalShares;

        balanceOf[msg.sender] -= shares;
        totalShares -= shares;
        totalAssets -= assets;
    }
}
