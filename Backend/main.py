import os
import time
import torch
import asyncio
from dotenv import load_dotenv
from diffusers import (
    StableDiffusionXLPipeline,
    StableDiffusionXLImg2ImgPipeline,
    DPMSolverSinglestepScheduler
)
from supabase import create_client, ClientOptions  # Add this import

BUCKET_NAME = os.getenv("BUCKET_NAME", "nft-generations")
MODEL_ID = os.getenv("MODEL_ID", "stabilityai/stable-diffusion-xl-base-1.0")
REFINER_ID = os.getenv("REFINER_ID", "stabilityai/stable-diffusion-xl-refiner-1.0")

def initialize_supabase():
    """Initialize and verify Supabase connection"""
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials in .env file")
    
    # Use ClientOptions instead of raw dict
    options = ClientOptions(
        postgrest_client_timeout=10,
        storage_client_timeout=30,
        schema="public"
    )
    
    return create_client(supabase_url, supabase_key, options)

def initialize_models():
    """Load SDXL base model + refiner with performance optimizations"""
    # Base model
    pipe = StableDiffusionXLPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16,
        variant="fp16",
        use_safetensors=True,
        device_map="auto"
    ).to("cuda")
    
    # Refiner model
    refiner = StableDiffusionXLImg2ImgPipeline.from_pretrained(
        REFINER_ID,
        torch_dtype=torch.float16
    ).to("cuda")

    # Optimizations
    pipe.scheduler = DPMSolverSinglestepScheduler.from_config(pipe.scheduler.config)
    pipe.enable_attention_slicing()  # Reduces VRAM usage
    if torch.cuda.get_device_properties(0).total_memory < 16 * 1024**3:  # <16GB VRAM
        pipe.enable_model_cpu_offload()  # Offloads to CPU when idle
    else:
        torch.backends.cuda.enable_flash_sdp(True)  # Alternative to xformers (PyTorch 2.0+)
    
    # Optional PyTorch 2.0+ compilation
    if hasattr(torch, 'compile'):
        pipe = torch.compile(pipe, mode='reduce-overhead')
    
    return pipe, refiner

async def generate_nft_asset(prompt, pipe, refiner):
    """Generate high-quality NFT image with refinement"""
    # First stage generation
    image = pipe(
        prompt,
        negative_prompt="blurry, lowres, bad anatomy, text",
        num_inference_steps=30,
        guidance_scale=7.5,
        height=1024,
        width=1024,
        output_type="latent"  # Required for refiner
    ).images[0]
    
    # Refinement stage
    refined_image = refiner(
        prompt=prompt,
        image=image,
        num_inference_steps=15,  # Total steps = 30 + 15
        strength=0.3
    ).images[0]
    
    return refined_image

async def upload_nft_package(supabase, image, prompt_id, metadata):
    """Upload image + metadata as an NFT package"""
    # Save image temporarily
    image_path = f"nft_{prompt_id}.png"
    image.save(image_path, quality=100)
    
    try:
        # Upload image
        with open(image_path, 'rb') as f:
            supabase.storage.from_(BUCKET_NAME).upload(
                path=f"nfts/{prompt_id}.png",
                file=f,
                file_options={
                    'content-type': 'image/png',
                    'x-upsert': 'true',
                    'cache-control': 'public, max-age=31536000, immutable'
                }
            )
        
        # Store metadata
        supabase.table('nft_metadata').upsert({
            'id': prompt_id,
            'image_url': f"{BUCKET_NAME}/nfts/{prompt_id}.png",
            'metadata': metadata,
            'generated_at': time.time()
        }).execute()
        
        return f"https://{supabase.supabase_url}/storage/v1/object/public/{BUCKET_NAME}/nfts/{prompt_id}.png"
    
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

async def process_nft_prompt(supabase, pipe, refiner, prompt):
    """End-to-end NFT generation pipeline"""
    try:
        # Update status
        supabase.table('nft_prompts') \
            .update({'status': 'processing'}) \
            .eq('id', prompt['id']) \
            .execute()
        
        # Generate NFT asset
        image = await generate_nft_asset(prompt['prompt_text'], pipe, refiner)
        
        # Prepare NFT metadata (OpenSea standard)
        metadata = {
            "name": f"AI NFT #{prompt['id']}",
            "description": prompt['prompt_text'],
            "attributes": [
                {"trait_type": "model", "value": MODEL_ID},
                {"trait_type": "refined", "value": True}
            ]
        }
        
        # Upload package
        asset_url = await upload_nft_package(supabase, image, prompt['id'], metadata)
        
        # Mark complete
        supabase.table('nft_prompts') \
            .update({
                'status': 'completed',
                'asset_url': asset_url,
                'generation_time': time.time() - prompt['created_at']
            }) \
            .eq('id', prompt['id']) \
            .execute()
        
        return True
    
    except Exception as e:
        supabase.table('nft_prompts') \
            .update({
                'status': 'failed',
                'error': str(e)[:500]
            }) \
            .eq('id', prompt['id']) \
            .execute()
        return False

async def nft_generation_worker(supabase, pipe, refiner):
    """Continuous processing loop"""
    while True:
        try:
            # Get next NFT prompt
            res = supabase.table('nft_prompts') \
                .select('*') \
                .eq('status', 'pending') \
                .order('created_at') \
                .limit(1) \
                .execute()
            
            if res.data:
                await process_nft_prompt(supabase, pipe, refiner, res.data[0])
            else:
                await asyncio.sleep(5)
                
        except Exception as e:
            print(f"Worker error: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    # Initialize with async
    sb = initialize_supabase()
    model, refiner = initialize_models()
    
    print("🚀 NFT Generation Service Ready")
    asyncio.run(nft_generation_worker(sb, model, refiner))