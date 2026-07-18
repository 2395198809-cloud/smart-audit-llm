// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/LLMFixedVault.sol";

contract LLMFixedReentrancyAttacker {
    LLMFixedVault public vault;
    uint256 public attackCount;

    constructor(address _vault) {
        vault = LLMFixedVault(_vault);
    }

    function attack() external payable {
        require(msg.value > 0, "need eth");
        vault.deposit{value: msg.value}();
        vault.withdraw();
    }

    receive() external payable {
        attackCount++;

        if (address(vault).balance >= 1 ether && attackCount < 5) {
            vault.withdraw();
        }
    }
}

contract LLMFixedVaultTest is Test {
    LLMFixedVault vault;
    LLMFixedReentrancyAttacker attacker;

    address victim = address(0xBEEF);
    address hacker = address(0xCAFE);

    function setUp() public {
        vault = new LLMFixedVault();
        attacker = new LLMFixedReentrancyAttacker(address(vault));

        vm.deal(victim, 10 ether);
        vm.deal(hacker, 1 ether);

        vm.prank(victim);
        vault.deposit{value: 10 ether}();
    }

    function testLLMFixedReentrancyAttackFails() public {
        vm.prank(hacker);

        vm.expectRevert();
        attacker.attack{value: 1 ether}();

        assertEq(address(vault).balance, 10 ether);
    }

    function testLLMFixedNormalWithdrawStillWorks() public {
        vm.prank(victim);
        vault.withdraw();

        assertEq(address(vault).balance, 0);
        assertEq(vault.balances(victim), 0);
    }
}
