from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from PIL import Image
import io
import os
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

INPUT_DIR = "static/input"
OUTPUT_DIR = "static/output"
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------
# 1️⃣ Remove Background
# -----------------------
@app.post("/remove-bg/")
async def remove_background(image: UploadFile = File(...)):
    img_bytes = await image.read()
    img = Image.open(io.BytesIO(img_bytes))
    result = remove(img).convert("RGBA")

    output_path = f"{OUTPUT_DIR}/removed.png"
    result.save(output_path)
    return {"output_url": output_path}


# -----------------------
# 2️⃣ Replace Background
# -----------------------
@app.post("/replace-bg/")
async def replace_background(
    foreground: UploadFile = File(...),
    background: UploadFile = File(...)
):
    fg_bytes = await foreground.read()
    bg_bytes = await background.read()

    fg_img = Image.open(io.BytesIO(fg_bytes))
    bg_img = Image.open(io.BytesIO(bg_bytes))

    # Remove bg from foreground
    fg_no_bg = remove(fg_img).convert("RGBA")

    # Resize background to match size
    bg_img = bg_img.convert("RGBA")
    bg_img = bg_img.resize(fg_no_bg.size)

    # Merge both
    final = Image.alpha_composite(bg_img, fg_no_bg)

    output_path = f"{OUTPUT_DIR}/replaced.png"
    final.save(output_path)

    return {"output_url": output_path}

# Add this at the end to run the server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)