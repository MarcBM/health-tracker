#!/usr/bin/env python3
"""
User Creation Script for Health Tracker

This script creates new users with specified permissions.
All users are created with a secure generated password that should be changed on first login.

Usage examples:
  ./create_user.py marc --can-edit
  ./create_user.py alice
  ./create_user.py bob --can-edit
"""

import argparse
import sys
import os
import secrets
import string

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from passlib.context import CryptContext
from app.database import SessionLocal, User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_secure_password(length=12):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def create_user(username, can_edit=False):
    """
    Create a new user in the database with a generated password
    """
    # Always generate a secure password
    password = generate_secure_password()
    
    # Hash the password
    hashed_password = pwd_context.hash(password)
    
    # Create database session
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"❌ Error: User '{username}' already exists")
            return False
        
        # Create new user
        new_user = User(
            username=username,
            hashed_password=hashed_password,
            can_edit=can_edit
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Success message
        print("✅ User created successfully!")
        print(f"   Username: {username}")
        print(f"   Can edit: {can_edit}")
        print(f"   User ID: {new_user.id}")
        print(f"   Password: {password}")
        print("   ⚠️  IMPORTANT: This is a generated password. The user should change it immediately!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(
        description="Create a new user for the Health Tracker application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s marc --can-edit
  %(prog)s alice
  %(prog)s bob --can-edit
  %(prog)s readonly_user

All users are created with view-only permissions by default and a secure generated password.
        """
    )
    
    parser.add_argument(
        'username',
        help='Username for the new user'
    )
    

    
    parser.add_argument(
        '--can-edit',
        action='store_true',
        help='Give the user edit permissions (default: view-only)'
    )
    
    args = parser.parse_args()
    
    # Validate username
    if not args.username or len(args.username.strip()) == 0:
        print("❌ Error: Username cannot be empty")
        sys.exit(1)
    
    if len(args.username) > 50:
        print("❌ Error: Username cannot be longer than 50 characters")
        sys.exit(1)
    
    # Create the user
    print(f"🚀 Creating user '{args.username}'...")
    print("=" * 40)
    
    success = create_user(
        username=args.username.strip(),
        can_edit=args.can_edit
    )
    
    if success:
        print("=" * 40)
        print("✅ User creation completed!")
        if args.can_edit:
            print("🔓 User can create and edit health data")
        else:
            print("👁️  User has view-only access")
    else:
        print("=" * 40)
        print("❌ User creation failed!")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ User creation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1) 