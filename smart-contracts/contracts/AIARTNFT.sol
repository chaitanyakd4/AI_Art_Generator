// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract AIArtNFT is ERC721URIStorage, Ownable {
    uint256 public nextTokenId;

    constructor() ERC721("AI Art NFT", "AIART") {}

    // Mint NFT to a user, with custom metadata URI
    function mintNFT(address to, string memory metadataURI) public onlyOwner {
        uint256 tokenId = nextTokenId;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, metadataURI); // This points to IPFS metadata JSON
        nextTokenId++;
    }
}
