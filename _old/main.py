from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import auth, data
from app.middleware import AuthenticationMiddleware
import os

# Create FastAPI app
app = FastAPI(
    title="Health Tracker Dashboard",
    description="Personal health tracking dashboard with data visualization",
    version="1.0.0"
)

# Add authentication middleware
app.add_middleware(AuthenticationMiddleware)

# Mount static files from project root
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(data.router)

# Health check endpoint for Fly.io
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Health Tracker API is running"}

# Data routes (dashboard, data-entry, history) handled by data router
# Auth routes (login, logout, etc.) handled by auth router

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        reload=True
    ) 