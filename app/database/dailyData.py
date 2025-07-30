from sqlalchemy import Column, Integer, String, Float, Date, Boolean
from .base import Base
import pytz
from datetime import datetime


class DailyData(Base):
    """Daily health tracking data model"""
    __tablename__ = "daily_data"
    
    # Date information - primary key
    date = Column(Date, primary_key=True)  # The actual date this data refers to
    
    # Calorie tracking (6 fields - 3 categories with goal/actual each)
    calories_green_goal = Column(Integer, nullable=True)
    calories_green_actual = Column(Integer, nullable=True)
    calories_yellow_goal = Column(Integer, nullable=True)
    calories_yellow_actual = Column(Integer, nullable=True)
    calories_orange_goal = Column(Integer, nullable=True)
    calories_orange_actual = Column(Integer, nullable=True)
    
    # Step tracking
    steps_goal = Column(Integer, nullable=True)
    steps_actual = Column(Integer, nullable=True)
    
    # Cardio tracking
    cardio_high_intensity_minutes = Column(Integer, nullable=True)
    cardio_low_intensity_minutes = Column(Integer, nullable=True)
    
    # Strength training
    strength_workout_type = Column(String(100), nullable=True)
    
    # Physio exercises
    physio_completed = Column(Boolean, nullable=True)
    
    # Weight tracking
    weight_kg = Column(Float, nullable=True)
    
    @property
    def day_of_week(self):
        """Get day of week based on Sydney, Australia timezone"""
        sydney_tz = pytz.timezone('Australia/Sydney')
        sydney_datetime = sydney_tz.localize(datetime.combine(self.date, datetime.min.time()))
        return sydney_datetime.strftime('%A')  # Returns full day name (e.g., 'Monday') 