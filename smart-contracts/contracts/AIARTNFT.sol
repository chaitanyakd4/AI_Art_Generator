// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract AIArtNFT is ERC721URIStorage, Ownable {
    uint256 public nextTokenId;

    constructor() ERC721("AI Art NFT", "AIART") Ownable(msg.sender) {}

    function mintNFT(address to, string memory metadataURI) public onlyOwner {
        uint256 tokenId = nextTokenId;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, metadataURI);
        nextTokenId++;
    }
}
