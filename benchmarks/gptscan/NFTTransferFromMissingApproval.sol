// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract NFTTransferFromMissingApproval {
    mapping(uint256 => address) public ownerOf;
    mapping(uint256 => address) public getApproved;

    constructor() {
        ownerOf[1] = msg.sender;
    }

    function mint(address to, uint256 tokenId) external {
        ownerOf[tokenId] = to;
    }

    function approve(address spender, uint256 tokenId) external {
        require(msg.sender == ownerOf[tokenId], "not owner");
        getApproved[tokenId] = spender;
    }

    function transferFrom(address from, address to, uint256 tokenId) external {
        require(ownerOf[tokenId] == from, "wrong owner");
        require(to != address(0), "bad to");
        ownerOf[tokenId] = to;
        getApproved[tokenId] = address(0);
    }
}
