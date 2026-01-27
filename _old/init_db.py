#!/usr/bin/env python3
"""
Database Initialization Script for Health Tracker

This script creates the database tables and SQLite file.
Run this once before starting the application.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import database components
from app.database import Base, engine, User, DailyData

def create_tables():
    """
    Create all database tables and SQLite file
    """
    print("Creating database tables...")
    
    # Import models to ensure they're registered with Base.metadata
    # (This is already done by importing above, but being explicit)
    
    # Create all tables - this will also create the SQLite file if it doesn't exist
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    print("✅ SQLite database file created!")

def init_database():
    """
    Complete database initialization - schema only
    """
    print("🚀 Initializing Health Tracker Database Schema")
    print("=" * 45)
    
    # Create tables
    create_tables()
    
    print("=" * 45)
    print("✅ Database schema initialization complete!")
    print("\nNext steps:")
    print("1. Create user accounts through the application")
    print("2. Start the application with: uvicorn main:app --reload")

if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1) 