from fastapi import FastAPI, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from PIL import Image
import io
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# -----------------------
# 1️⃣ Remove Background
# -----------------------
@app.post("/remove-bg/")
async def remove_background(image: UploadFile = File(...)):
    img_bytes = await image.read()
    img = Image.open(io.BytesIO(img_bytes))
    result = remove(img).convert("RGBA")

    # Convert result to bytes
    img_byte_arr = io.BytesIO()
    result.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    return Response(content=img_byte_arr, media_type="image/png")

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

    # Convert result to bytes
    img_byte_arr = io.BytesIO()
    final.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    return Response(content=img_byte_arr, media_type="image/png")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)