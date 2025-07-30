from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["data"])

# Templates setup
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page with health metrics overview"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": request.state.user
    })

@router.get("/data-entry", response_class=HTMLResponse)
async def data_entry(request: Request):
    """Data entry page - placeholder"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": request.state.user,
        "page_title": "Data Entry - Coming Soon"
    })

@router.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    """History page - placeholder"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": request.state.user,
        "page_title": "History - Coming Soon"
    }) 