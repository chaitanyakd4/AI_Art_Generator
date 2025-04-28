from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3
import json
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from sdxl_generator import generate_image
from ipfs_upload import upload_to_pinata, upload_metadata_to_pinata
import os
from dotenv import load_dotenv
from pathlib import Path
import time
import base64
from io import BytesIO

load_dotenv(dotenv_path=Path(".env"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Request Model ===
class PromptRequest(BaseModel):
    prompt: str
    wallet_address: str

# === Blockchain Setup ===
def setup_web3():
    # Try different ways to connect to the local blockchain
    providers = [
        "http://127.0.0.1:8545",    # Default Hardhat
        "http://localhost:8545",    # Alternative
        "http://127.0.0.1:7545",    # Ganache default
    ]
    
    for provider_url in providers:
        w3 = Web3(Web3.HTTPProvider(provider_url, request_kwargs={'timeout': 30}))
        try:
            if w3.is_connected():
                print(f"✅ Connected to blockchain at {provider_url}")
                return w3
        except Exception as e:
            print(f"Failed to connect to {provider_url}: {e}")
            continue
    
    # Instead of raising an error, return None and handle gracefully
    print("⚠️ Warning: Could not connect to any local blockchain provider")
    return None

# Try to connect to Web3, but don't fail if it doesn't work
try:
    w3 = setup_web3()
    # Only setup contract if w3 connection succeeded
    if w3:
        # === Contract Setup ===
        def setup_contract():
            contract_address = os.getenv("NFT_CONTRACT_ADDRESS")
            if not contract_address:
                print("⚠️ NFT_CONTRACT_ADDRESS not found in environment variables")
                return None
            
            # Make sure address is properly formatted
            if not contract_address.startswith("0x"):
                contract_address = f"0x{contract_address}"
            
            # Load the contract ABI
            abi_path = Path(__file__).parent.parent / "smart-contracts" / "artifacts" / "contracts" / "AIArtNFT.sol" / "AIArtNFT.json"
            
            if not abi_path.exists():
                print(f"⚠️ Contract ABI not found at {abi_path}. Did you compile the contract?")
                return None
            
            try:
                with open(abi_path) as f:
                    contract_json = json.load(f)
                    abi = contract_json.get("abi")
                    if not abi:
                        print("⚠️ ABI not found in contract JSON")
                        return None
                
                # Create contract instance
                contract = w3.eth.contract(address=contract_address, abi=abi)
                print(f"✅ Contract loaded at address {contract_address}")
                return contract
            except Exception as e:
                print(f"⚠️ Error setting up contract: {str(e)}")
                return None

        contract = setup_contract()
    else:
        contract = None
except Exception as e:
    print(f"⚠️ Web3 setup error: {str(e)}")
    w3 = None
    contract = None

# === Simple image generation endpoint (without minting) ===
@app.post("/generate")
async def generate_only(prompt_req: PromptRequest):
    try:
        print(f"Generating image for prompt: {prompt_req.prompt}")
        
        # Generate image
        image_bytes = generate_image(prompt_req.prompt)
        
        # Convert to base64 for direct display
        img_base64 = base64.b64encode(image_bytes).decode()
        
        return {
            "success": True,
            "image": img_base64,
            "wallet_address": prompt_req.wallet_address
        }
    except Exception as e:
        print(f"❌ Error in image generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# === Generate and Mint NFT ===
@app.post("/api/generate")
async def generate(prompt_req: PromptRequest):
    try:
        # Validate wallet address
        if not Web3.is_address(prompt_req.wallet_address):
            raise HTTPException(status_code=400, detail="Invalid wallet address")
        
        # Check if Web3 is connected
        if not w3 or not w3.is_connected():
            raise HTTPException(status_code=503, detail="Blockchain connection unavailable")
            
        # Check if contract is available
        if not contract:
            raise HTTPException(status_code=503, detail="Smart contract not properly configured")
        
        print(f"Generating image for prompt: {prompt_req.prompt}")
        print(f"Will mint to wallet: {prompt_req.wallet_address}")
        
        # Generate image
        image_bytes = generate_image(prompt_req.prompt)
        
        # Upload to IPFS
        image_url = upload_to_pinata(image_bytes, "output.png")
        metadata_url = upload_metadata_to_pinata(
            name=prompt_req.prompt[:40],  # Trim name to reasonable length
            description=f"AI-generated art based on: {prompt_req.prompt}",
            image_url=image_url
        )
        
        print(f"✅ Uploaded to IPFS: {image_url}")
        print(f"✅ Metadata URL: {metadata_url}")
        
        # Get private key from env
        private_key = os.getenv("PRIVATE_KEY")
        if not private_key:
            raise ValueError("PRIVATE_KEY not found in environment variables")
        
        # Ensure private key is properly formatted
        if not private_key.startswith("0x"):
            private_key = f"0x{private_key}"
        
        # Get the account from private key
        account = w3.eth.account.from_key(private_key)
        from_address = account.address
        
        print(f"🔑 Using account: {from_address}")
        
        # Build the transaction
        tx = contract.functions.mintNFT(
            prompt_req.wallet_address, 
            metadata_url
        ).build_transaction({
            "from": from_address,
            "nonce": w3.eth.get_transaction_count(from_address),
            "gas": 3000000,  # Higher gas limit
            "gasPrice": w3.eth.gas_price,
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"⏳ Transaction sent: {tx_hash.hex()}")
        
        # Wait for receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
        
        print(f"✅ Transaction confirmed: {receipt.transactionHash.hex()}")
        
        return {
            "image_url": image_url,
            "metadata_url": metadata_url,
            "transaction_hash": receipt.transactionHash.hex()
        }

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/api/health")
async def health_check():
    connected = w3 and w3.is_connected()
    return {
        "status": "healthy" if connected else "unhealthy",
        "blockchain_connected": connected
    }