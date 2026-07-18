// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/*
* Adapted from SmartBugs Curated:
* dataset/unchecked_low_level_calls/unchecked_return_value.sol
*
* Vulnerability: unchecked low-level call return value.
*/
contract UncheckedCall {
    bool public called;

    function callChecked(address callee) external {
        (bool ok, ) = callee.call("");
        require(ok, "call failed");
        called = true;
    }

    function callNotChecked(address callee) external {
        callee.call("");
        called = true;
    }
}
