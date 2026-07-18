// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/FixedWallet.sol";

contract FixedTxOriginPhishingAttacker {
    FixedWallet public wallet;
    address payable public attacker;

    constructor(address _wallet, address payable _attacker) {
        wallet = FixedWallet(_wallet);
        attacker = _attacker;
    }

    function attack() external {
        wallet.withdrawAll(attacker);
    }
}

contract FixedWalletTest is Test {
    FixedWallet wallet;
    FixedTxOriginPhishingAttacker phishing;

    address owner = address(0xBEEF);
    address payable hacker = payable(address(0xCAFE));

    function setUp() public {
        vm.deal(owner, 10 ether);

        vm.prank(owner);
        wallet = new FixedWallet{value: 10 ether}();

        phishing = new FixedTxOriginPhishingAttacker(address(wallet), hacker);
    }

    function testTxOriginPhishingAttackFails() public {
        vm.startPrank(owner, owner);

        vm.expectRevert("not owner");
        phishing.attack();

        vm.stopPrank();

        assertEq(address(wallet).balance, 10 ether);
        assertEq(hacker.balance, 0);
    }

    function testOwnerDirectWithdrawStillWorks() public {
        vm.prank(owner);
        wallet.withdrawAll(hacker);

        assertEq(address(wallet).balance, 0);
        assertEq(hacker.balance, 10 ether);
    }
}
