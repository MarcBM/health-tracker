from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

# Create FastAPI app
app = FastAPI(
    title="Health Tracker Dashboard",
    description="Personal health tracking dashboard with data visualization",
    version="1.0.0"
)

# Mount static files from project root
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates from app/templates directory
templates = Jinja2Templates(directory="app/templates")

# Health check endpoint for Fly.io
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Health Tracker API is running"}

# Root endpoint - dashboard
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page with health metrics overview"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

# Login page
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page for user authentication"""
    return templates.TemplateResponse("login.html", {"request": request})

# Login form submission (placeholder)
@app.post("/login")
async def login_submit(request: Request):
    """Handle login form submission - placeholder for now"""
    # TODO: Implement actual authentication logic
    return {"message": "Login endpoint - authentication logic coming soon"}

# Placeholder routes for navbar links
@app.get("/data-entry", response_class=HTMLResponse)
async def data_entry(request: Request):
    """Data entry page - placeholder"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "page_title": "Data Entry - Coming Soon"
    })

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    """History page - placeholder"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "page_title": "History - Coming Soon"
    })

@app.get("/logout")
async def logout():
    """Logout endpoint - placeholder"""
    return {"message": "Logout endpoint - coming soon"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        reload=True
    ) 