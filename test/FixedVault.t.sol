pragma solidity ^0.8.20;

  import "forge-std/Test.sol";
  import "../src/FixedVault.sol";

  contract FixedReentrancyAttacker {
      FixedVault public vault;
      uint256 public attackCount;

      constructor(address _vault) {
          vault = FixedVault(_vault);
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

  contract FixedVaultTest is Test {
      FixedVault vault;
      FixedReentrancyAttacker attacker;

      address victim = address(0xBEEF);
      address hacker = address(0xCAFE);

      function setUp() public {
          vault = new FixedVault();
          attacker = new FixedReentrancyAttacker(address(vault));

          vm.deal(victim, 10 ether);
          vm.deal(hacker, 1 ether);

          vm.prank(victim);
          vault.deposit{value: 10 ether}();
      }

      function testReentrancyAttackFails() public {
          vm.prank(hacker);

          vm.expectRevert();
          attacker.attack{value: 1 ether}();

          assertEq(address(vault).balance, 10 ether);
      }

      function testNormalWithdrawStillWorks() public {
          vm.prank(victim);
          vault.withdraw();

          assertEq(address(vault).balance, 0);
          assertEq(vault.balances(victim), 0);
      }
  }
