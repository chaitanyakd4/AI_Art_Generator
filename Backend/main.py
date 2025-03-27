import os
import time
import torch
from dotenv import load_dotenv
from diffusers import StableDiffusionPipeline
from supabase import create_client

# Configuration
BUCKET_NAME = "generated-images"
MODEL_ID = "stabilityai/stable-diffusion-2-1"

def initialize_supabase():
    """Initialize and verify Supabase connection"""
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials in .env file")
    
    return create_client(supabase_url, supabase_key)

def initialize_model():
    """Initialize Stable Diffusion pipeline"""
    return StableDiffusionPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16,
        variant="fp16",
        safety_checker=None
    ).to("cuda")

def upload_to_storage(supabase, image, prompt_id):
    """Handle image upload to Supabase Storage"""
    image_path = f"temp_{prompt_id}.png"
    try:
        # Save image temporarily
        image.save(image_path)
        
        # Upload with proper headers
        with open(image_path, 'rb') as f:
            res = supabase.storage.from_(BUCKET_NAME).upload(
                file=f,
                path=f"{prompt_id}.png",
                file_options={
                    'content-type': 'image/png',
                    'x-upsert': 'true'  # String instead of boolean
                }
            )
            
            if isinstance(res, dict) and res.get('error'):
                raise Exception(res['error'])
        
        # Get public URL
        return supabase.storage.from_(BUCKET_NAME).get_public_url(f"{prompt_id}.png")
        
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

def process_prompts(supabase, pipe):
    """Main processing loop"""
    while True:
        try:
            # Get oldest pending prompt
            res = supabase.table('prompts') \
                .select('*') \
                .eq('status', 'pending') \
                .order('created_at') \
                .limit(1) \
                .execute()

            if not res.data:
                time.sleep(5)
                continue

            prompt = res.data[0]
            print(f"Processing: {prompt['id']} - {prompt['prompt_text']}")

            # Update status to processing
            supabase.table('prompts') \
                .update({'status': 'processing'}) \
                .eq('id', prompt['id']) \
                .execute()

            # Generate and upload image
            image = pipe(prompt['prompt_text']).images[0]
            image_url = upload_to_storage(supabase, image, prompt['id'])

            # Update database records
            supabase.table('generated_images').insert({
                'prompt_id': prompt['id'],
                'image_url': image_url,
                'model_used': MODEL_ID
            }).execute()

            supabase.table('prompts') \
                .update({'status': 'completed'}) \
                .eq('id', prompt['id']) \
                .execute()

            print(f"Completed: {prompt['id']}")

        except Exception as e:
            print(f"Error processing prompt: {str(e)}")
            if 'prompt' in locals():
                supabase.table('prompts') \
                    .update({
                        'status': 'failed',
                        'error': str(e)[:500]  # Truncate long errors
                    }) \
                    .eq('id', prompt['id']) \
                    .execute()
            time.sleep(5)

if __name__ == "__main__":
    try:
        # Initialize services
        sb = initialize_supabase()
        model = initialize_model()
        
        print("Services initialized. Starting processing...")
        process_prompts(sb, model)
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")