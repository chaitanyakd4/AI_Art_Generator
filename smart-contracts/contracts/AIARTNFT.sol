// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract AIArtNFT is ERC721URIStorage, Ownable {
    uint256 public nextTokenId;

    event NFTMinted(address to, uint256 tokenId, string metadataURI);

    constructor() ERC721("AI Art NFT", "AIART") Ownable(msg.sender) {}

    // function for owner usage
    function mintNFT(address to, string memory metadataURI) public onlyOwner {
        uint256 tokenId = nextTokenId;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, metadataURI);
        nextTokenId++;
        
        emit NFTMinted(to, tokenId, metadataURI);
    }
    
    // function that anyone can call to mint directly to their wallet
    function mintToSender(string memory metadataURI) public {
        uint256 tokenId = nextTokenId;
        _safeMint(msg.sender, tokenId);
        _setTokenURI(tokenId, metadataURI);
        nextTokenId++;
        
        emit NFTMinted(msg.sender, tokenId, metadataURI);
    }
}