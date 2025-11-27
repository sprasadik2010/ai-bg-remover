from fastapi import FastAPI, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from PIL import Image
import io
import uvicorn

app = FastAPI()

# Updated CORS configuration with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://ai-bg-remover-04yd.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Test that rembg can load
    try:
        test_img = Image.new('RGBA', (10, 10), (255, 0, 0, 255))
        remove(test_img)
        print("✅ rembg loaded successfully")
    except Exception as e:
        print(f"❌ rembg failed to load: {e}")

# -----------------------
# 1️⃣ Remove Background
# -----------------------
@app.post("/remove-bg/")
async def remove_background(image: UploadFile = File(...)):
    try:
        img_bytes = await image.read()
        img = Image.open(io.BytesIO(img_bytes))
        result = remove(img).convert("RGBA")
        # ... rest of code
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

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

# ✅ ADD THIS HEALTH ENDPOINT FOR GITHUB ACTIONS
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI BG Remove API",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)