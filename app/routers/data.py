from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

router = APIRouter(tags=["data"])

# Templates setup
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page with health metrics overview"""
    return templates.TemplateResponse("dashboard/dashboard.html", {
        "request": request,
        "user": request.state.user
    })

@router.get("/data-entry", response_class=HTMLResponse)
async def data_entry(request: Request):
    """Data entry page - placeholder"""
    return templates.TemplateResponse("dashboard/dashboard.html", {
        "request": request,
        "user": request.state.user,
        "page_title": "Data Entry - Coming Soon"
    })

@router.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    """History page - placeholder"""
    return templates.TemplateResponse("dashboard/dashboard.html", {
        "request": request,
        "user": request.state.user,
        "page_title": "History - Coming Soon"
    })

@router.get("/missing-data")
async def get_missing_data(
    request: Request,
    scope: str = Query(default="dashboard", description="Scope of missing data check: 'dashboard', 'calories', 'steps', 'weight', etc.")
):
    """
    API endpoint to check for missing data
    
    Args:
        scope: Type of data to check for
            - 'dashboard': Returns days with no DailyData row at all
            - 'calories': Returns days where calorie fields are NULL
            - 'steps': Returns days where step fields are NULL  
            - 'weight': Returns days where weight is NULL
            - 'cardio': Returns days where cardio fields are NULL
            - 'strength': Returns days where strength fields are NULL
            - 'physio': Returns days where physio_completed is NULL
    
    Returns:
        JSON format:
        {
            "missing_days": [
                {
                    "date": "2024-01-13",
                    "display_name": "Monday, 13th January"
                },
                {
                    "date": "2024-01-15", 
                    "display_name": "Wednesday, 15th January"
                }
            ]
        }
    """
    # TODO: Implement actual database queries based on scope
    # Query will be determined by scope parameter, result will always be same format
    
    return {
        "missing_days": []
    } 