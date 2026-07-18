// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/LLMFixedWallet.sol";

contract LLMFixedTxOriginPhishingAttacker {
    LLMFixedWallet public wallet;
    address payable public attacker;

    constructor(address _wallet, address payable _attacker) {
        wallet = LLMFixedWallet(_wallet);
        attacker = _attacker;
    }

    function attack() external {
        wallet.withdrawAll(attacker);
    }
}

contract LLMFixedWalletTest is Test {
    LLMFixedWallet wallet;
    LLMFixedTxOriginPhishingAttacker phishing;

    address owner = address(0xBEEF);
    address payable hacker = payable(address(0xCAFE));

    function setUp() public {
        vm.deal(owner, 10 ether);

        vm.prank(owner);
        wallet = new LLMFixedWallet{value: 10 ether}();

        phishing = new LLMFixedTxOriginPhishingAttacker(address(wallet), hacker);
    }

    function testLLMFixedTxOriginPhishingAttackFails() public {
        vm.startPrank(owner, owner);

        vm.expectRevert("not owner");
        phishing.attack();

        vm.stopPrank();

        assertEq(address(wallet).balance, 10 ether);
        assertEq(hacker.balance, 0);
    }

    function testLLMFixedOwnerDirectWithdrawStillWorks() public {
        vm.prank(owner);
        wallet.withdrawAll(hacker);

        assertEq(address(wallet).balance, 0);
        assertEq(hacker.balance, 10 ether);
    }
}
