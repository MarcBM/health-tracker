from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import date, timedelta
from calendar import month_name

from app.database import get_db, DailyData

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
    scope: str = Query(default="dashboard", description="Scope of missing data check: 'dashboard', 'calories', 'steps', 'weight', etc."),
    db: Session = Depends(get_db)
):
    """
    API endpoint to check for missing data
    
    Args:
        scope: Type of data to check for
            - 'dashboard': Returns days with no DailyData row at all
            - 'calories': Returns days where any calorie fields are NULL
            - 'steps': Returns days where any step fields are NULL  
            - 'weight': Returns days where weight is NULL
            - 'cardio': Returns days where any cardio fields are NULL
            - 'strength': Returns days where strength fields are NULL
            - 'physio': Returns days where either physio_active is NULL or physio_completed is NULL while physio_active is True
    
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
    # Get date range: yesterday back to first day in database
    yesterday = date.today() - timedelta(days=1)
    
    # Get the earliest date in the database
    first_date_result = db.query(DailyData.date).order_by(DailyData.date).first()
    if not first_date_result:
        # No data in database at all
        return {"missing_days": []}
    
    first_date = first_date_result[0]
    
    # Generate all dates in range
    current_date = first_date
    all_dates = []
    while current_date <= yesterday:
        all_dates.append(current_date)
        current_date += timedelta(days=1)
    
    missing_dates = []
    
    if scope == "dashboard":
        # Find days with no DailyData row at all
        existing_dates = {row[0] for row in db.query(DailyData.date).all()}
        missing_dates = [d for d in all_dates if d not in existing_dates]
        
    elif scope == "calories":
        # Find days where any calorie fields are NULL
        query = db.query(DailyData.date).filter(
            (DailyData.calories_green_goal.is_(None)) |
            (DailyData.calories_green_actual.is_(None)) |
            (DailyData.calories_yellow_goal.is_(None)) |
            (DailyData.calories_yellow_actual.is_(None)) |
            (DailyData.calories_orange_goal.is_(None)) |
            (DailyData.calories_orange_actual.is_(None))
        ).filter(
            DailyData.date.between(first_date, yesterday)
        )
        missing_from_db = {row[0] for row in query.all()}
        
        # Also include dates not in database at all
        existing_dates = {row[0] for row in db.query(DailyData.date).all()}
        missing_completely = [d for d in all_dates if d not in existing_dates]
        
        missing_dates = list(missing_from_db) + missing_completely
        
    elif scope == "steps":
        # Find days where any step fields are NULL
        query = db.query(DailyData.date).filter(
            (DailyData.steps_goal.is_(None)) |
            (DailyData.steps_actual.is_(None))
        ).filter(
            DailyData.date.between(first_date, yesterday)
        )
        missing_from_db = {row[0] for row in query.all()}
        
        # Also include dates not in database at all
        existing_dates = {row[0] for row in db.query(DailyData.date).all()}
        missing_completely = [d for d in all_dates if d not in existing_dates]
        
        missing_dates = list(missing_from_db) + missing_completely
        
    elif scope == "weight":
        # Find days where weight is NULL
        query = db.query(DailyData.date).filter(
            DailyData.weight_kg.is_(None)
        ).filter(
            DailyData.date.between(first_date, yesterday)
        )
        missing_from_db = {row[0] for row in query.all()}
        
        # Also include dates not in database at all
        existing_dates = {row[0] for row in db.query(DailyData.date).all()}
        missing_completely = [d for d in all_dates if d not in existing_dates]
        
        missing_dates = list(missing_from_db) + missing_completely
        
    elif scope == "cardio":
        # Find days where any cardio fields are NULL
        query = db.query(DailyData.date).filter(
            (DailyData.cardio_high_intensity_minutes.is_(None)) |
            (DailyData.cardio_low_intensity_minutes.is_(None))
        ).filter(
            DailyData.date.between(first_date, yesterday)
        )
        missing_from_db = {row[0] for row in query.all()}
        
        # Also include dates not in database at all
        existing_dates = {row[0] for row in db.query(DailyData.date).all()}
        missing_completely = [d for d in all_dates if d not in existing_dates]
        
        missing_dates = list(missing_from_db) + missing_completely
        
    elif scope == "strength":
        # Find days where strength fields are NULL
        query = db.query(DailyData.date).filter(
            DailyData.strength_workout_type.is_(None)
        ).filter(
            DailyData.date.between(first_date, yesterday)
        )
        missing_from_db = {row[0] for row in query.all()}
        
        # Also include dates not in database at all
        existing_dates = {row[0] for row in db.query(DailyData.date).all()}
        missing_completely = [d for d in all_dates if d not in existing_dates]
        
        missing_dates = list(missing_from_db) + missing_completely
        
    elif scope == "physio":
        # Find days where physio_active is NULL or physio_completed is NULL while physio_active is True
        query = db.query(DailyData.date).filter(
            (DailyData.physio_active.is_(None)) |
            ((DailyData.physio_active == True) & (DailyData.physio_completed.is_(None)))
        ).filter(
            DailyData.date.between(first_date, yesterday)
        )
        missing_from_db = {row[0] for row in query.all()}
        
        # Also include dates not in database at all
        existing_dates = {row[0] for row in db.query(DailyData.date).all()}
        missing_completely = [d for d in all_dates if d not in existing_dates]
        
        missing_dates = list(missing_from_db) + missing_completely
        
    else:
        # Unknown scope, return empty
        missing_dates = []
    
    # Format the response
    def format_date(d):
        day_name = d.strftime('%A')
        day_num = d.day
        month_name_str = month_name[d.month]
        
        # Add ordinal suffix
        if 10 <= day_num % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day_num % 10, 'th')
        
        return f"{day_name}, {day_num}{suffix} {month_name_str}"
    
    # Remove duplicates and sort
    missing_dates = sorted(list(set(missing_dates)))
    
    formatted_missing = [
        {
            "date": d.strftime('%Y-%m-%d'),
            "display_name": format_date(d)
        }
        for d in missing_dates
    ]
    
    return {
        "missing_days": formatted_missing
    } 