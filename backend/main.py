from fastapi import FastAPI, UploadFile, File, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Background Remover API", "status": "working"}

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    try:
        # Check file size
        contents = await file.read()
        if len(contents) > 2 * 1024 * 1024:  # 2MB max
            raise HTTPException(400, "Image too large (max 2MB)")
        
        # Open image
        image = Image.open(io.BytesIO(contents)).convert("RGBA")
        
        # Resize to save memory
        image.thumbnail((600, 600))
        
        # Simple background removal - remove white pixels
        pixels = image.load()
        width, height = image.size
        
        for x in range(width):
            for y in range(height):
                r, g, b, a = pixels[x, y]
                # If pixel is white/light, make it transparent
                if r > 200 and g > 200 and b > 200:
                    pixels[x, y] = (255, 255, 255, 0)
        
        # Convert to bytes
        output = io.BytesIO()
        image.save(output, format="PNG")
        output.seek(0)
        
        return Response(content=output.read(), media_type="image/png")
        
    except Exception as e:
        raise HTTPException(500, f"Error processing image: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)