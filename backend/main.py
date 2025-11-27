from fastapi import FastAPI, UploadFile, File, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import uvicorn
from datetime import datetime
import os

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
    return {"message": "Background Removal API", "status": "healthy"}

@app.post("/remove-bg")
async def remove_background_simple(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        if len(contents) > 3 * 1024 * 1024:
            raise HTTPException(400, "Image too large (max 3MB)")
        
        image = Image.open(io.BytesIO(contents)).convert("RGBA")
        image.thumbnail((600, 600))
        
        # Remove white background
        pixels = image.load()
        width, height = image.size
        
        for x in range(width):
            for y in range(height):
                r, g, b, a = pixels[x, y]
                if r > 200 and g > 200 and b > 200:
                    pixels[x, y] = (255, 255, 255, 0)
        
        output = io.BytesIO()
        image.save(output, format="PNG")
        
        return Response(content=output.getvalue(), media_type="image/png")
        
    except Exception as e:
        raise HTTPException(500, f"Processing failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)