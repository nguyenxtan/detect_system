#!/usr/bin/env python3
"""
Script to create admin user for Defect System
Usage: python3 scripts/create_admin.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
import getpass


def create_admin():
    """Create admin user interactively"""
    print("=" * 50)
    print("Create Admin User for Defect System")
    print("=" * 50)
    print()

    # Get user input
    username = input("Enter admin username: ").strip()
    if not username:
        print("❌ Username cannot be empty!")
        return

    full_name = input("Enter full name: ").strip()
    email = input("Enter email (optional): ").strip()

    # Get password securely
    while True:
        password = getpass.getpass("Enter password: ")
        password_confirm = getpass.getpass("Confirm password: ")

        if password != password_confirm:
            print("❌ Passwords don't match! Try again.")
            continue

        if len(password) < 8:
            print("❌ Password must be at least 8 characters!")
            continue

        break

    # Create user in database
    db = SessionLocal()
    try:
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"❌ User '{username}' already exists!")
            return

        # Create new admin user
        user = User(
            username=username,
            hashed_password=get_password_hash(password),
            full_name=full_name or username,
            email=email or None,
            role='admin',
            is_active=True
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print()
        print("=" * 50)
        print("✅ Admin user created successfully!")
        print("=" * 50)
        print(f"Username:  {user.username}")
        print(f"Full name: {user.full_name}")
        print(f"Email:     {user.email or 'N/A'}")
        print(f"Role:      {user.role}")
        print()
        print("You can now login at: http://localhost:3001/login")
        print("=" * 50)

    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    try:
        create_admin()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
