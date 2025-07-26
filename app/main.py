from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

# Create FastAPI app
app = FastAPI(
    title="Health Tracker Dashboard",
    description="Personal health tracking dashboard with data visualization",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="../static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Health check endpoint for Fly.io
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Health Tracker API is running"}

# Root endpoint - will redirect to dashboard or login
@app.get("/")
async def root():
    return {"message": "Health Tracker Dashboard API", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        reload=True
    ) 