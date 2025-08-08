from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text, func
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
        "calories": get_calorie_dashboard_data(db),
        "steps": get_steps_dashboard_data(db),
        "cardio": get_cardio_dashboard_data(db),
        "strength": get_strength_dashboard_data(db),
        "physio": get_physio_dashboard_data(db),
        "weight": get_weight_dashboard_data(db),
    }

def get_calorie_dashboard_data(db: Session):
    """
    Returns the last 7 days of calorie data, including day of week and all calorie goal/actual fields.
    """
    
    # Get the date range for the last 7 days
    today = date.today()
    start_date, end_date = get_7_days_before_date(today)
    
    # Query the database for calorie data in the last 7 days
    calorie_data = db.query(DailyData).filter(
        DailyData.date.between(start_date, end_date)
    ).order_by(DailyData.date).all()
    
    # Create a list to store the formatted data
    formatted_data = []
    
    # Process each day's data
    for day_data in calorie_data:
        formatted_day = {
            "date": day_data.date.strftime('%Y-%m-%d'),
            "day_of_week": day_data.day_of_week,
            "calories_green_goal": day_data.calories_green_goal,
            "calories_green_actual": day_data.calories_green_actual,
            "calories_yellow_goal": day_data.calories_yellow_goal,
            "calories_yellow_actual": day_data.calories_yellow_actual,
            "calories_orange_goal": day_data.calories_orange_goal,
            "calories_orange_actual": day_data.calories_orange_actual
        }
        formatted_data.append(formatted_day)
    
    return formatted_data

def get_steps_dashboard_data(db: Session):
    """
    Returns steps dashboard data: yesterday's stats, 7-day averages, all-time high, and streaks.
    """
    
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # 1. Yesterday's steps actual and goal
    yesterday_data = db.query(DailyData.steps_actual, DailyData.steps_goal).filter(
        DailyData.date == yesterday
    ).first()
    
    yesterday_steps = {
        "actual": yesterday_data.steps_actual if yesterday_data else None,
        "goal": yesterday_data.steps_goal if yesterday_data else None
    }
    
    # 2. Average steps for last 7 days and 7 days before that
    # Get date ranges using helper method
    last_7_start, last_7_end = get_7_days_before_date(today)
    prev_7_start, prev_7_end = get_7_days_before_date(last_7_start)
    
    # Average for last 7 days
    last_7_sum = db.query(func.sum(DailyData.steps_actual)).filter(
        DailyData.date.between(last_7_start, last_7_end)
    ).scalar()
    last_7_avg = last_7_sum / 7 if last_7_sum is not None else 0
    
    # Average for previous 7 days
    prev_7_sum = db.query(func.sum(DailyData.steps_actual)).filter(
        DailyData.date.between(prev_7_start, prev_7_end)
    ).scalar()
    prev_7_avg = prev_7_sum / 7 if prev_7_sum is not None else 0
    
    averages = {
        "last_7_days": float(last_7_avg) if last_7_avg else None,
        "previous_7_days": float(prev_7_avg) if prev_7_avg else None
    }
    
    # 3. Highest steps actual in history
    max_steps_data = db.query(DailyData.steps_actual, DailyData.date).filter(
        DailyData.steps_actual.isnot(None)
    ).order_by(DailyData.steps_actual.desc()).first()
    
    highest_steps = {
        "steps": max_steps_data.steps_actual if max_steps_data else None,
        "date": max_steps_data.date.strftime('%Y-%m-%d') if max_steps_data else None
    }
    
    # 4. Current streak (from yesterday backwards)
    current_streak = 0
    check_date = yesterday
    
    while True:
        day_data = db.query(DailyData.steps_actual, DailyData.steps_goal).filter(
            DailyData.date == check_date
        ).first()
        
        # If no data exists for this date, or if either field is NULL, break the streak
        if not day_data or day_data.steps_actual is None or day_data.steps_goal is None:
            break
        
        if day_data.steps_actual >= day_data.steps_goal:
            current_streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    # 5. Longest streak in history
    # Get all data ordered by date (including days with NULL values)
    all_steps_data = db.query(DailyData.date, DailyData.steps_actual, DailyData.steps_goal).order_by(DailyData.date).all()
    
    longest_streak = 0
    longest_streak_end_date = None
    current_streak_count = 0
    previous_date = None
    
    for day_data in all_steps_data:
        # Check for date continuity (should be consecutive days)
        if previous_date and (day_data.date - previous_date).days > 1:
            # Gap found, break the streak
            current_streak_count = 0
        
        # Check if this day meets the goal (both fields must be non-NULL and actual >= goal)
        if (day_data.steps_actual is not None and 
            day_data.steps_goal is not None and 
            day_data.steps_actual >= day_data.steps_goal):
            current_streak_count += 1
            if current_streak_count > longest_streak:
                longest_streak = current_streak_count
                longest_streak_end_date = day_data.date
        else:
            current_streak_count = 0
        
        previous_date = day_data.date
    
    longest_streak_info = {
        "streak": longest_streak,
        "end_date": longest_streak_end_date.strftime('%Y-%m-%d') if longest_streak_end_date else None
    }
    
    return {
        "yesterday": yesterday_steps,
        "averages": averages,
        "highest": highest_steps,
        "current_streak": current_streak,
        "longest_streak": longest_streak_info
    }

def get_cardio_dashboard_data(db: Session):
    """
    Returns cardio dashboard data:
    1. Total low and high intensity minutes (last 7 days)
    2. Current streak of days (from yesterday) with ≥15 total minutes
    3. Longest such streak and its end date
    """
    
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Get date range for last 7 days
    last_7_start, last_7_end = get_7_days_before_date(today)
    
    # 1. Total low intensity minutes across last 7 days
    last_7_low_total = db.query(func.sum(DailyData.cardio_low_intensity_minutes)).filter(
        DailyData.date.between(last_7_start, last_7_end)
    ).scalar() or 0
    
    # 2. Total high intensity minutes across last 7 days
    last_7_high_total = db.query(func.sum(DailyData.cardio_high_intensity_minutes)).filter(
        DailyData.date.between(last_7_start, last_7_end)
    ).scalar() or 0
    
    # 3. Current streak (from yesterday backwards)
    current_streak = 0
    check_date = yesterday
    
    while True:
        day_data = db.query(DailyData.cardio_low_intensity_minutes, DailyData.cardio_high_intensity_minutes).filter(
            DailyData.date == check_date
        ).first()
        
        # If no data exists for this date, break the streak
        if not day_data:
            break
        
        total_minutes = (day_data.cardio_low_intensity_minutes or 0) + (day_data.cardio_high_intensity_minutes or 0)
        
        if total_minutes >= 15:
            current_streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    # 4. Longest streak in history
    # Get all cardio data ordered by date (including days with NULL values)
    all_cardio_data = db.query(DailyData.date, DailyData.cardio_low_intensity_minutes, DailyData.cardio_high_intensity_minutes).order_by(DailyData.date).all()
    
    longest_streak = 0
    longest_streak_end_date = None
    current_streak_count = 0
    previous_date = None
    
    for day_data in all_cardio_data:
        # Check for date continuity (should be consecutive days)
        if previous_date and (day_data.date - previous_date).days > 1:
            # Gap found, break the streak
            current_streak_count = 0
        
        total_minutes = (day_data.cardio_low_intensity_minutes or 0) + (day_data.cardio_high_intensity_minutes or 0)
        
        if total_minutes >= 15:
            current_streak_count += 1
            if current_streak_count > longest_streak:
                longest_streak = current_streak_count
                longest_streak_end_date = day_data.date
        else:
            current_streak_count = 0
        
        previous_date = day_data.date
    
    longest_streak_info = {
        "streak": longest_streak,
        "end_date": longest_streak_end_date.strftime('%Y-%m-%d') if longest_streak_end_date else None
    }
    
    return {
        "last_7_days": {
            "low_intensity": last_7_low_total,
            "high_intensity": last_7_high_total
        },
        "current_streak": current_streak,
        "longest_streak": longest_streak_info
    }

def get_strength_dashboard_data(db: Session):
    """
    Returns: 
    1. Number of days with a strength workout in the last 7 days.
    2. Counts of each strength_workout_type in all history (excluding NULL/'None').
    """
    
    today = date.today()
    
    # Get date range for last 7 days
    last_7_start, last_7_end = get_7_days_before_date(today)
    
    # 1. Number of days in last 7 days with strength workout
    last_7_days_count = db.query(func.count(DailyData.strength_workout_type)).filter(
        DailyData.date.between(last_7_start, last_7_end),
        DailyData.strength_workout_type.isnot(None),
        DailyData.strength_workout_type != 'None'
    ).scalar() or 0
    
    # 2. Counts of each strength_workout_type in full history
    # Get all strength data with valid workout types
    all_strength_data = db.query(DailyData.date, DailyData.strength_workout_type).filter(
        DailyData.strength_workout_type.isnot(None),
        DailyData.strength_workout_type != 'None'
    ).order_by(DailyData.date).all()
    
    # Count occurrences of each workout type
    workout_type_counts = {}
    for day_data in all_strength_data:
        workout_type = day_data.strength_workout_type
        if workout_type:
            workout_type_counts[workout_type] = workout_type_counts.get(workout_type, 0) + 1
    
    return {
        "last_7_days_count": last_7_days_count,
        "workout_type_counts": workout_type_counts
    }

def get_physio_dashboard_data(db: Session):
    """
    Get physio dashboard data: 
    1. Current physio_active state (yesterday).
    2. Current streak of consecutive days (from yesterday back) where both physio_active and physio_completed are True (skipping days where physio_active is False).
    3. Longest such streak and its end date.
    """
    
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # 1. Current state of physio_active field
    current_physio_data = db.query(DailyData.physio_active).filter(
        DailyData.date == yesterday
    ).first()
    
    current_physio_active = current_physio_data.physio_active if current_physio_data else None
    
    # 2. Current streak (from yesterday backwards)
    current_streak = 0
    check_date = yesterday
    
    while True:
        day_data = db.query(DailyData.physio_active, DailyData.physio_completed).filter(
            DailyData.date == check_date
        ).first()
        
        # If no data exists for this date, break the streak
        if not day_data:
            break
        
        # Streak continues if: physio_active is True AND physio_completed is True
        # Streak breaks if: physio_active is True AND (physio_completed is False OR NULL)
        # Streak is NOT broken if: physio_active is False (skip this day)
        
        if day_data.physio_active is True:
            if day_data.physio_completed is True:
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                # physio_active is True but physio_completed is False or NULL - break streak
                break
        else:
            # physio_active is False or NULL - skip this day (don't break streak)
            check_date -= timedelta(days=1)
    
    # 3. Longest streak in history
    # Get all physio data ordered by date
    all_physio_data = db.query(DailyData.date, DailyData.physio_active, DailyData.physio_completed).order_by(DailyData.date).all()
    
    longest_streak = 0
    longest_streak_end_date = None
    current_streak_count = 0
    previous_date = None
    
    for day_data in all_physio_data:
        # Check for date continuity (should be consecutive days)
        if previous_date and (day_data.date - previous_date).days > 1:
            # Gap found, break the streak
            current_streak_count = 0
        
        # Streak logic: only count days where both active and completed are True
        if day_data.physio_active is True and day_data.physio_completed is True:
            current_streak_count += 1
            if current_streak_count > longest_streak:
                longest_streak = current_streak_count
                longest_streak_end_date = day_data.date
        elif day_data.physio_active is True:
            # physio_active is True but physio_completed is False or NULL - break streak
            current_streak_count = 0
        # If physio_active is False or NULL, don't break streak, just continue
        
        previous_date = day_data.date
    
    longest_streak_info = {
        "streak": longest_streak,
        "end_date": longest_streak_end_date.strftime('%Y-%m-%d') if longest_streak_end_date else None
    }
    
    return {
        "current_active": current_physio_active,
        "current_streak": current_streak,
        "longest_streak": longest_streak_info
    }

def get_weight_dashboard_data(db: Session):
    """
    Retrieve up to the last 1 year of recorded weights with their dates.
    """
    # Find the last recorded weight date
    last_date = db.query(func.max(DailyData.date)).filter(
        DailyData.weight_kg.isnot(None)
    ).scalar()
    
    if last_date is None:
        return {"weight_history": []}
    
    # Compute 1-year window inclusive of last_date (approx 365 days)
    window_start = last_date - timedelta(days=364)
    
    # Get weight data within the last year
    all_weight_data = db.query(DailyData.date, DailyData.weight_kg).filter(
        DailyData.weight_kg.isnot(None),
        DailyData.date.between(window_start, last_date)
    ).order_by(DailyData.date).all()
    
    # Format the data for the frontend
    weight_history = []
    for day_data in all_weight_data:
        weight_history.append({
            "date": day_data.date.strftime('%Y-%m-%d'),
            "weight_kg": day_data.weight_kg
        })
    
    return {
        "weight_history": weight_history
    }

def get_7_days_before_date(today: date) -> tuple[date, date]:
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


