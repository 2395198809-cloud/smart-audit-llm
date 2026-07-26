// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/*
Real-cropped/adapted benchmark sample.
Source project: OpenZeppelinERC721Burnable
Source URL: https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/v4.9.6/contracts/token/ERC721/ERC721.sol
Note: ERC721-style ownership/approval logic cropped and mutated: public_burn.
This benchmark is cropped/adapted for controlled audit experiments.
It does NOT claim the upstream project contains this vulnerability.
*/

contract OZERC721PublicBurnFrom {
    mapping(uint256 => address) public ownerOf;
    mapping(uint256 => address) public getApproved;
    mapping(address => mapping(address => bool)) public isApprovedForAll;

    constructor() {
        ownerOf[1] = msg.sender;
        ownerOf[2] = msg.sender;
    }

    function approve(address spender, uint256 tokenId) external {
        require(ownerOf[tokenId] == msg.sender, "owner");
        getApproved[tokenId] = spender;
    }

    function setApprovalForAll(address operator, bool approved) external {
        isApprovedForAll[msg.sender][operator] = approved;
    }


    function burnFrom(address from, uint256 tokenId) external {
        require(ownerOf[tokenId] == from, "owner");
        ownerOf[tokenId] = address(0);
    }

}
