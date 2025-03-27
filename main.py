from fastapi import FastAPI
from pydantic import BaseModel
from diffusers import StableDiffusionPipeline
import torch
import uuid

app = FastAPI()

# Load model (will be loaded when the server starts)
model_id = "stabilityai/stable-diffusion-2-1"
pipe = None

@app.on_event("startup")
async def startup_event():
    global pipe
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    if torch.cuda.is_available():
        pipe = pipe.to("cuda")

class ImageRequest(BaseModel):
    prompt: str
    num_inference_steps: int = 50
    guidance_scale: float = 7.5

@app.post("/generate/")
async def generate_image(request: ImageRequest):
    image = pipe(
        request.prompt,
        num_inference_steps=request.num_inference_steps,
        guidance_scale=request.guidance_scale
    ).images[0]

    image_filename = f"output_{uuid.uuid4().hex}.png"
    image.save(image_filename)

    return {"message": "Image generated successfully!", "image": image_filename}