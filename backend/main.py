from fastapi import FastAPI, UploadFile, File, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from PIL import Image
import io
import uvicorn
from datetime import datetime
import os

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

# Global variables to track rembg status
rembg_loaded = False
rembg_error = None

@app.on_event("startup")
async def startup_event():
    """Test rembg loading with minimal memory usage"""
    global rembg_loaded, rembg_error
    print("🚀 Starting up application...")
    
    try:
        # Create smallest possible test image
        test_img = Image.new('RGBA', (1, 1), (255, 0, 0, 255))
        
        # Test rembg with minimal input
        print("🔄 Loading rembg model...")
        result = remove(test_img)
        print("✅ rembg loaded successfully")
        rembg_loaded = True
        
    except Exception as e:
        error_msg = f"❌ rembg failed to load: {str(e)}"
        print(error_msg)
        rembg_error = error_msg
        rembg_loaded = False

# -----------------------
# 1️⃣ Remove Background (OPTIMIZED)
# -----------------------
@app.post("/remove-bg/")
async def remove_background(image: UploadFile = File(...)):
    # Check if rembg is loaded
    if not rembg_loaded:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {rembg_error}")
    
    try:
        # 1. Strict file size limit for free tier
        MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB max
        
        # Read and validate file size
        img_bytes = await image.read()
        if len(img_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"Image too large. Max size: {MAX_FILE_SIZE//1024//1024}MB")
        
        # 2. Open and optimize image
        img = Image.open(io.BytesIO(img_bytes))
        
        # 3. Force resize to reduce memory usage
        max_dimension = 800  # Reduced from original
        img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        
        # 4. Process with rembg
        print(f"🔄 Processing image: {img.size}")
        result = remove(img)
        result = result.convert("RGBA")
        
        # 5. Optimize output
        img_byte_arr = io.BytesIO()
        result.save(img_byte_arr, format='PNG', optimize=True)
        img_byte_arr = img_byte_arr.getvalue()

        return Response(content=img_byte_arr, media_type="image/png")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# -----------------------
# 2️⃣ Replace Background (OPTIMIZED)
# -----------------------
@app.post("/replace-bg/")
async def replace_background(
    foreground: UploadFile = File(...),
    background: UploadFile = File(...)
):
    # Check if rembg is loaded
    if not rembg_loaded:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {rembg_error}")
    
    try:
        MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB max per file
        
        # Read and validate foreground
        fg_bytes = await foreground.read()
        if len(fg_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Foreground image too large")
        
        # Read and validate background  
        bg_bytes = await background.read()
        if len(bg_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Background image too large")

        # Process images with size limits
        fg_img = Image.open(io.BytesIO(fg_bytes))
        bg_img = Image.open(io.BytesIO(bg_bytes))
        
        # Resize both images to manageable size
        max_dimension = 600  # Even smaller for two images
        fg_img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        bg_img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        
        # Remove bg from foreground
        print("🔄 Removing background from foreground...")
        fg_no_bg = remove(fg_img).convert("RGBA")

        # Resize background to match foreground size
        bg_img = bg_img.convert("RGBA")
        bg_img = bg_img.resize(fg_no_bg.size)

        # Merge both
        final = Image.alpha_composite(bg_img, fg_no_bg)

        # Convert result to bytes with optimization
        img_byte_arr = io.BytesIO()
        final.save(img_byte_arr, format='PNG', optimize=True)
        img_byte_arr = img_byte_arr.getvalue()

        return Response(content=img_byte_arr, media_type="image/png")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Background replacement failed: {str(e)}")

# -----------------------
# 3️⃣ Simple Background Removal (FALLBACK - No AI)
# -----------------------
@app.post("/remove-bg-simple/")
async def remove_background_simple(image: UploadFile = File(...)):
    """Color-based background removal as fallback"""
    try:
        MAX_FILE_SIZE = 3 * 1024 * 1024  # 3MB for simple method
        
        img_bytes = await image.read()
        if len(img_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Image too large")
            
        img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
        # Simple color-based background removal
        datas = img.getdata()
        new_data = []
        
        for item in datas:
            # Remove white/light backgrounds (adjust threshold as needed)
            if item[0] > 200 and item[1] > 200 and item[2] > 200:
                new_data.append((255, 255, 255, 0))  # transparent
            else:
                new_data.append(item)
        
        img.putdata(new_data)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG', optimize=True)
        
        return Response(content=img_byte_arr.getvalue(), media_type="image/png")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simple removal failed: {str(e)}")

# ✅ Health Endpoint with rembg status
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy" if rembg_loaded else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI BG Remove API",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "version": "1.0.0",
        "rembg_loaded": rembg_loaded,
        "rembg_error": rembg_error if not rembg_loaded else None
    }

# ✅ Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Background Removal API",
        "status": "operational" if rembg_loaded else "degraded",
        "endpoints": [
            "/remove-bg",
            "/replace-bg", 
            "/remove-bg-simple",
            "/api/health"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        # Optimize for low memory
        workers=1,  # Single worker to save memory
        log_level="info"
    )