# -*- coding: utf-8 -*-
import os
import time
import uuid
import torch
from diffusers import StableDiffusionPipeline
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Initialize Stable Diffusion
model_id = "stabilityai/stable-diffusion-2-1"
pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    revision="fp16"
)
pipe = pipe.to("cuda")
pipe.enable_attention_slicing()  # Reduce memory usage

def process_prompts():
    """Continuously checks for new prompts and generates images"""
    while True:
        try:
            # Get pending prompts from database
            response = supabase.table('prompts') \
                .select('*') \
                .eq('status', 'pending') \
                .order('created_at', ascending=True) \
                .limit(1) \
                .execute()

            if not response.data:
                print("No pending prompts found. Sleeping for 10 seconds...")
                time.sleep(10)
                continue

            prompt = response.data[0]
            print(f"Processing prompt ID: {prompt['id']} - {prompt['prompt_text']}")

            # Update status to 'processing'
            supabase.table('prompts') \
                .update({'status': 'processing'}) \
                .eq('id', prompt['id']) \
                .execute()

            # Generate image
            image = pipe(
                prompt['prompt_text'],
                num_inference_steps=50,
                guidance_scale=7.5
            ).images[0]

            # Save image temporarily
            image_filename = f"temp_{uuid.uuid4().hex}.png"
            image.save(image_filename)

            # Upload to Supabase Storage
            with open(image_filename, 'rb') as f:
                storage_response = supabase.storage() \
                    .from_('generated-images') \
                    .upload(f"{prompt['id']}.png", f)

            # Get public URL
            image_url = supabase.storage() \
                .from_('generated-images') \
                .get_public_url(f"{prompt['id']}.png")

            # Store metadata in database
            supabase.table('generated_images') \
                .insert({
                    'prompt_id': prompt['id'],
                    'image_url': image_url,
                    'model_used': model_id
                }).execute()

            # Update prompt status
            supabase.table('prompts') \
                .update({'status': 'completed'}) \
                .eq('id', prompt['id']) \
                .execute()

            # Clean up
            os.remove(image_filename)
            print(f"Completed processing for prompt ID: {prompt['id']}")

        except Exception as e:
            print(f"Error processing prompt: {str(e)}")
            if 'id' in locals():
                supabase.table('prompts') \
                    .update({'status': 'failed', 'error': str(e)}) \
                    .eq('id', prompt['id']) \
                    .execute()
            time.sleep(10)

if __name__ == "__main__":
    # Create required storage bucket if not exists
    try:
        supabase.storage().create_bucket("generated-images", {
            'public': True,
            'allowed_mime_types': ['image/png'],
            'file_size_limit': 1024 * 1024 * 5  # 5MB limit
        })
    except Exception as e:
        print(f"Storage bucket already exists or error creating: {str(e)}")

    process_prompts()