#!/usr/bin/env python3
"""
Dummy Data Generation Script for Health Tracker

Generates 30+ days of realistic dummy daily health data
from July 1, 2025 to August 1, 2025 for testing the dashboard.
"""

import os
import sys
import random
from datetime import date, timedelta
from typing import Optional

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import database components
from app.database import SessionLocal, DailyData

def generate_dummy_data():
    """
    Generate dummy daily data for the specified date range
    """
    
    # Configuration - Dynamic date range (30 days leading up to yesterday)
    today = date.today()
    END_DATE = today - timedelta(days=1)  # Yesterday (don't include today)
    START_DATE = END_DATE - timedelta(days=29)  # 30 days total (including end date)
    
    # Calorie goals (stable throughout)
    CALORIE_GOALS = {
        'green': 1000,
        'yellow': 1500,
        'orange': 800
    }
    
    # Strength workout types
    STRENGTH_TYPES = ['Core', 'Lower Body', 'Upper Body', 'Full Body']
    
    # State variables
    current_steps_goal = 2000
    current_weight = 130.0
    physio_active = True
    physio_off_days = 0
    
    db = SessionLocal()
    
    try:
        current_date = START_DATE
        days_generated = 0
        
        while current_date <= END_DATE:
            # 10% chance to skip the entire day (no data entry)
            if random.random() < 0.10:
                print(f"📅 Skipping {current_date.strftime('%Y-%m-%d')} - no data entry")
                current_date += timedelta(days=1)
                continue
            
            print(f"📝 Generating data for {current_date.strftime('%Y-%m-%d')}")
            
            # Initialize daily data entry
            daily_data = DailyData(date=current_date)
            
            # ===================
            # CALORIE TRACKING
            # ===================
            if random.random() > 0.05:  # 95% chance to have calorie data
                # Goals stay stable
                daily_data.calories_green_goal = CALORIE_GOALS['green']
                daily_data.calories_yellow_goal = CALORIE_GOALS['yellow']
                daily_data.calories_orange_goal = CALORIE_GOALS['orange']
                
                # Actual values fluctuate around goals
                daily_data.calories_green_actual = max(0, int(random.normalvariate(CALORIE_GOALS['green'], 200)))
                daily_data.calories_yellow_actual = max(0, int(random.normalvariate(CALORIE_GOALS['yellow'], 300)))
                daily_data.calories_orange_actual = max(0, int(random.normalvariate(CALORIE_GOALS['orange'], 150)))
            
            # ===================
            # STEP TRACKING
            # ===================
            if random.random() > 0.08:  # 92% chance to have step data
                daily_data.steps_goal = current_steps_goal
                
                # Steps generally meet goal, sometimes exceed, rarely fall short
                if random.random() < 0.85:  # 85% chance to meet goal
                    if random.random() < 0.3:  # 30% chance to far exceed
                        daily_data.steps_actual = int(current_steps_goal * random.uniform(1.5, 2.2))
                    else:  # Normal meeting of goal
                        daily_data.steps_actual = int(current_steps_goal * random.uniform(1.0, 1.4))
                    
                    # Increase goal by 500 if met and under 10000
                    if current_steps_goal < 10000:
                        current_steps_goal = min(10000, current_steps_goal + 500)
                else:  # 15% chance to not meet goal
                    daily_data.steps_actual = int(current_steps_goal * random.uniform(0.7, 0.95))
                    # Don't increase goal if not met
            
            # ===================
            # CARDIO TRACKING
            # ===================
            if random.random() > 0.12:  # 88% chance to have cardio data
                # Never both types on same day
                if random.random() < 0.2:  # 20% of cardio days are high intensity
                    total_minutes = random.choice([15, 20, 30, 45])
                    daily_data.cardio_high_intensity_minutes = total_minutes
                    daily_data.cardio_low_intensity_minutes = None
                else:  # 80% are low intensity
                    total_minutes = random.choice([15, 30, 30, 45])  # More likely to be 30
                    daily_data.cardio_low_intensity_minutes = total_minutes
                    daily_data.cardio_high_intensity_minutes = None
            
            # ===================
            # STRENGTH TRAINING
            # ===================
            if random.random() > 0.15:  # 85% chance to have strength data
                if random.random() < 0.15:  # 15% chance for no workout
                    daily_data.strength_workout_type = None
                else:
                    daily_data.strength_workout_type = random.choice(STRENGTH_TYPES)
            
            # ===================
            # PHYSIO TRACKING
            # ===================
            if random.random() > 0.05:  # 95% chance to have physio data
                # Physio active/inactive logic
                if physio_active:
                    if physio_off_days == 0 and random.random() < 0.1:  # 10% chance to turn off
                        physio_active = False
                        physio_off_days = random.randint(3, 7)  # Off for 3-7 days
                else:
                    physio_off_days -= 1
                    if physio_off_days <= 0:
                        physio_active = True
                
                daily_data.physio_active = physio_active
                
                # Completion logic
                if physio_active:
                    daily_data.physio_completed = random.random() < 0.9  # 90% completion when active
                else:
                    daily_data.physio_completed = False  # Never completed when inactive
            
            # ===================
            # WEIGHT TRACKING
            # ===================
            if random.random() > 0.15:  # 85% chance to have weight data
                # General downward trend with some fluctuation
                trend_change = random.uniform(-0.3, 0.1)  # Bias towards weight loss
                daily_fluctuation = random.uniform(-0.5, 0.5)
                current_weight += trend_change + daily_fluctuation
                current_weight = max(120.0, current_weight)  # Don't go below 120kg
                daily_data.weight_kg = round(current_weight, 1)
            
            # Save to database
            db.add(daily_data)
            days_generated += 1
            
            current_date += timedelta(days=1)
        
        # Commit all changes
        db.commit()
        
        print(f"\n✅ Successfully generated {days_generated} days of dummy data!")
        print(f"📊 Data range: {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}")
        print(f"🎯 Final step goal: {current_steps_goal}")
        print(f"⚖️  Final weight: {current_weight:.1f}kg")
        print(f"🏥 Physio active: {physio_active}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating dummy data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def clear_existing_data():
    """
    Clear existing data in the date range before generating new data
    """
    # Use same dynamic date range as generate_dummy_data
    today = date.today()
    END_DATE = today - timedelta(days=1)  # Yesterday
    START_DATE = END_DATE - timedelta(days=29)  # 30 days total
    
    db = SessionLocal()
    
    try:
        # Delete existing data in the range
        deleted_count = db.query(DailyData).filter(
            DailyData.date >= START_DATE,
            DailyData.date <= END_DATE
        ).delete()
        
        db.commit()
        
        if deleted_count > 0:
            print(f"🗑️  Cleared {deleted_count} existing records in date range")
        else:
            print("📝 No existing data found in date range")
            
        return True
        
    except Exception as e:
        print(f"❌ Error clearing existing data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Main execution function"""
    
    # Calculate dynamic date range for display
    today = date.today()
    end_date = today - timedelta(days=1)  # Yesterday
    start_date = end_date - timedelta(days=29)  # 30 days total
    
    print("🚀 Health Tracker Dummy Data Generator")
    print("=" * 50)
    print(f"📅 Date range: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')} (30 days)")
    print(f"📋 Features:")
    print(f"   • Stable calorie goals with realistic fluctuations")
    print(f"   • Progressive step goals (2000 → 10000)")
    print(f"   • Varied cardio activities (high/low intensity)")
    print(f"   • Random strength training categories")
    print(f"   • Dynamic physio status with realistic completion")
    print(f"   • Gradual weight loss trend with daily fluctuations")
    print(f"   • Realistic missing data patterns")
    print("=" * 50)
    
    # Ask for confirmation
    response = input("\n🔄 Clear existing data and generate new dummy data? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        print("\n🔄 Starting data generation process...")
        
        # Clear existing data first
        if clear_existing_data():
            # Generate new dummy data
            if generate_dummy_data():
                print("\n🎉 Dummy data generation completed successfully!")
                print("\n💡 Next steps:")
                print("   1. Start the application: uvicorn app.main:app --reload")
                print("   2. View the dashboard to see the generated data")
                print("   3. Test charts and visualizations")
            else:
                print("\n❌ Dummy data generation failed!")
        else:
            print("\n❌ Failed to clear existing data!")
    else:
        print("\n🚫 Operation cancelled")

if __name__ == "__main__":
    main()