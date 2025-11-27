from fastapi import FastAPI, UploadFile, File, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import uvicorn
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="BG Remover API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to import rembg with comprehensive error handling
try:
    from rembg import remove
    REMBG_AVAILABLE = True
    logger.info("✅ rembg imported successfully")
except ImportError as e:
    REMBG_AVAILABLE = False
    logger.error(f"❌ rembg import failed: {e}")
except Exception as e:
    REMBG_AVAILABLE = False
    logger.error(f"❌ rembg initialization failed: {e}")

rembg_loaded = False
rembg_error = None

@app.on_event("startup")
async def startup_event():
    global rembg_loaded, rembg_error
    
    if not REMBG_AVAILABLE:
        rembg_error = "rembg package not available"
        logger.error(rembg_error)
        return
    
    try:
        logger.info("🚀 Testing rembg model loading...")
        # Test with smallest possible image
        test_img = Image.new('RGBA', (2, 2), (255, 255, 255, 255))
        result = remove(test_img)
        rembg_loaded = True
        logger.info("✅ rembg model loaded successfully")
    except Exception as e:
        rembg_loaded = False
        rembg_error = str(e)
        logger.error(f"❌ rembg model failed to load: {e}")

# Health endpoint
@app.get("/")
async def root():
    return {
        "message": "Background Removal API",
        "status": "healthy" if rembg_loaded else "degraded",
        "rembg_available": rembg_loaded
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy" if rembg_loaded else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI BG Remove API", 
        "rembg_loaded": rembg_loaded,
        "error": rembg_error
    }

# Remove background endpoint
@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    if not rembg_loaded:
        raise HTTPException(
            status_code=503,
            detail=f"Background removal service unavailable: {rembg_error}"
        )
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "File must be an image")
    
    try:
        # Read file with size limit
        contents = await file.read()
        if len(contents) > 2 * 1024 * 1024:  # 2MB limit
            raise HTTPException(400, "Image too large (max 2MB)")
        
        # Process image
        image = Image.open(io.BytesIO(contents))
        
        # Resize to save memory
        image.thumbnail((800, 800))
        
        # Remove background
        result = remove(image)
        result = result.convert("RGBA")
        
        # Convert to bytes
        output = io.BytesIO()
        result.save(output, format="PNG")
        output.seek(0)
        
        return Response(content=output.read(), media_type="image/png")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(500, f"Processing failed: {str(e)}")

# Simple background removal (fallback)
@app.post("/remove-bg-simple")
async def remove_background_simple(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        if len(contents) > 3 * 1024 * 1024:
            raise HTTPException(400, "Image too large (max 3MB)")
        
        image = Image.open(io.BytesIO(contents)).convert("RGBA")
        image.thumbnail((800, 800))
        
        # Simple background removal (removes white backgrounds)
        pixels = image.load()
        width, height = image.size
        
        for x in range(width):
            for y in range(height):
                r, g, b, a = pixels[x, y]
                # If pixel is white/light, make it transparent
                if r > 200 and g > 200 and b > 200:
                    pixels[x, y] = (255, 255, 255, 0)
        
        output = io.BytesIO()
        image.save(output, format="PNG")
        output.seek(0)
        
        return Response(content=output.read(), media_type="image/png")
        
    except Exception as e:
        raise HTTPException(500, f"Simple removal failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        access_log=False  # Reduce logging overhead
    )