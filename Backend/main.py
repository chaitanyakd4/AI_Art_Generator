from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3
import json
from fastapi import FastAPI
from pydantic import BaseModel
from sdxl_generator import generate_image
from ipfs_upload import upload_to_pinata, upload_metadata_to_pinata
import os
from dotenv import load_dotenv
import time
from pathlib import Path
import subprocess

from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(".env"))  # Ensure it loads from current dir


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to your frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Connect to Local Blockchain ===
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
if not w3.is_connected():
    raise ConnectionError("❌ Could not connect to local blockchain.")
w3.eth.default_account = w3.eth.accounts[0]

# === ABI Path and Contract Address ===
abi_path = Path(__file__).parent.parent / "smart-contracts" / "artifacts" / "contracts" / "AIArtNFT.sol" / "AIArtNFT.json"
contract_address = os.getenv("NFT_CONTRACT_ADDRESS")

if not contract_address:
    raise EnvironmentError("❌ NFT_CONTRACT_ADDRESS not found in .env file.")
print("Loaded NFT_CONTRACT_ADDRESS:", contract_address)

# === Compile Contract if ABI Not Found ===
if not abi_path.exists():
    print("🛠 ABI not found — compiling contract using Hardhat...")
    try:
           subprocess.run(["npx", "hardhat", "compile"], cwd=Path(__file__).parent.parent / "smart-contracts", check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("❌ Failed to compile contract via Hardhat.") from e

# === Wait for ABI to be Created ===
for i in range(10):
    if abi_path.exists():
        break
    print(f"⏳ Waiting for contract ABI... ({i+1}/10)")
    time.sleep(1)
else:
    raise FileNotFoundError(f"❌ ABI still not found at {abi_path}")

# === Load ABI and Bytecode ===
with abi_path.open() as f:
    contract_json = json.load(f)
    abi = contract_json.get("abi")
    bytecode = contract_json.get("bytecode")

if not abi or not bytecode:
    raise ValueError("❌ ABI or Bytecode missing in compiled contract JSON.")

# === Connect to Deployed Contract ===
contract = w3.eth.contract(address=contract_address, abi=abi)

# === Request Model ===
class PromptRequest(BaseModel):
    prompt: str

# === API Endpoint ===
@app.post("/generate")
async def generate(prompt_req: PromptRequest):
    print(f"🔹 Prompt received: {prompt_req.prompt}")

    try:
        # 1. Generate AI image
        image_bytes = generate_image(prompt_req.prompt)
        print("✅ Image generated.")

        # 2. Upload image to IPFS
        image_url = upload_to_pinata(image_bytes, "output.png")
        print(f"✅ Image uploaded to IPFS: {image_url}")

        # 3. Upload metadata to IPFS
        metadata_url = upload_metadata_to_pinata(
            name=prompt_req.prompt,
            description=f"AI-generated art based on: {prompt_req.prompt}",
            image_url=image_url
        )
        print(f"✅ Metadata uploaded to IPFS: {metadata_url}")

        # 4. Mint NFT via Smart Contract
        tx_hash = contract.functions.mintNFT(w3.eth.default_account, metadata_url).transact()
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ NFT Minted! Tx Hash: {tx_receipt.transactionHash.hex()}")

        return {
            "image_url": image_url,
            "metadata_url": metadata_url,
            "transaction_hash": tx_receipt.transactionHash.hex()
        }

    except Exception as e:
        print("❌ Error during generation/minting:", str(e))
        return {"error": "Internal Server Error"}
