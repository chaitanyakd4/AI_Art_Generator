import requests

NFT_STORAGE_API_KEY = "66d5d7d2.310e1cf923394c25b1d13182b3517d4a"  # replace with your actual token

def upload_file_to_nft_storage(image_bytes: bytes, filename: str) -> str:
    headers = {
        "Authorization": f"Bearer {NFT_STORAGE_API_KEY}",
    }
    files = {
        "file": (filename, image_bytes, "image/png")
    }

    try:
        response = requests.post("https://api.nft.storage/upload", headers=headers, files=files)
        response.raise_for_status()
        cid = response.json()["value"]["cid"]
        return f"https://{cid}.ipfs.nftstorage.link/{filename}"
    except Exception as e:
        print("❌ Upload to NFT.storage failed:", str(e))
        raise e
