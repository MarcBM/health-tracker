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

@router.get("/data/dashboard")
async def get_dashboard_data(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    API endpoint to get dashboard data
    """
    return {
        "calories": await get_calorie_dashboard_data(db),
        "steps": await get_steps_dashboard_data(db),
        "cardio": await get_cardio_dashboard_data(db),
        "strength": await get_strength_dashboard_data(db),
        "physio": await get_physio_dashboard_data(db),
        "weight": await get_weight_dashboard_data(db),
    }

async def get_calorie_dashboard_data(db: Session):
    """
    Get calorie data for the dashboard displays. Data includes the last 7 days, package each day with the day of the week and each calorie field from the DailyData table.
    """
    # TODO

async def get_steps_dashboard_data(db: Session):
    """
    Get steps data for the dashboard displays. Data includes 5 items. 1. An object containing yesterday's steps actual and goal. 2. An object containing the average steps actual for the last 7 days, and the average steps actual for the 7 days before that. 3. An object containing the highest steps actual in the history, and the date of that day. 4. The current streak of days where steps actual was greater than or equal to the goal (streak starts from yesterday and goes back in time). 5. An object containing the longest streak of days where steps actual was greater than or equal to the goal (longest uninterrupted streak) and the last date of that streak.
    """
    # TODO

async def get_cardio_dashboard_data(db: Session):
    """
    Get cardio data for the dashboard displays. Data includes 4 items. 1. The total number of low intensity minutes across the last 7 days. 2. The total number of high intensity minutes across the last 7 days. 3. The current streak of days where the total number of minutes was greater than or equal to 15 (streak starts from yesterday and goes back in time). 4. An object containing the longest streak of days where the total number of minutes was greater than or equal to 15 (longest uninterrupted streak) and the last date of that streak.
    """
    # TODO

async def get_strength_dashboard_data(db: Session):
    """
    Get strength data for the dashboard displays. Data includes 2 items. 1. The number of days in the last 7 days where the strength_workout_type is not NULL or 'None'. 2. An object containing the counts of each strength_workout_type in the full history where the strength_workout_type is not NULL or 'None'.
    """
    # TODO

async def get_physio_dashboard_data(db: Session):
    """
    Get physio data for the dashboard displays. Data includes 3 items. 1. The current state of the physio_active field. 2. The current streak of days where physio_active was True and physio_completed was True (streak starts from yesterday and goes back in time). 3. An object containing the longest streak of days where physio_active was True and physio_completed was True (longest uninterrupted streak) and the last date of that streak. Streaks in the physio data only count days where both fields are True, but the streak is not broken by a day where physio_active is False, only by days where physio_active is True and physio_completed is False, or when either field is NULL.
    """
    # TODO

async def get_weight_dashboard_data(db: Session):
    """
    Get weight data for the dashboard displays. Data includes 1 item. 1. The full history of weight data, including the date and weight_kg field.
    """
    # TODO

async def get_7_days_before_date(today: date) -> tuple[date, date]:
    """
    Get the date range for the 7 days prior to the given date (today).
    
    Args:
        today: The current date
        
    Returns:
        tuple[date, date]: A tuple of (start_date, end_date) where:
            end_date is yesterday (today - 1)
            start_date is 7 days before yesterday (for a total of 7 days)
    """
    yesterday = today - timedelta(days=1)
    start_date = yesterday - timedelta(days=6)  # 6 days before yesterday
    return start_date, yesterday


