from diffusers import StableDiffusionPipeline, EulerAncestralDiscreteScheduler
import torch
from io import BytesIO

# Use EulerAncestral scheduler (more stable for SDXL)
pipe = StableDiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    variant="fp16",
    use_safetensors=True
)

pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
pipe.to("cuda")

def generate_image(prompt: str) -> bytes:
    print("⚙️ Generating image...")
    result = pipe(prompt, num_inference_steps=30)

    # Extra safety check
    if result is None or not result.images or result.images[0] is None:
        raise ValueError("Image generation failed")

    image = result.images[0]
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()
