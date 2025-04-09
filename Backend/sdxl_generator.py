from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler
import torch
from io import BytesIO

# Load SDXL pipeline optimized for performance
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    variant="fp16",
    use_safetensors=True
)

# Use a stable and efficient scheduler
pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)

# Move to GPU
pipe.to("cuda")

def generate_image(prompt: str) -> bytes:
    print("⚙️ Generating image...")

    result = pipe(
        prompt,
        height=1024,
        width=1024,
        num_inference_steps=30,
        guidance_scale=7.5  # Adjust for better control (higher = more focused on prompt)
    )

    if result is None or not result.images or result.images[0] is None:
        raise ValueError("❌ Image generation failed")

    image = result.images[0]

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()
