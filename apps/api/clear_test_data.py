#!/usr/bin/env python3
"""Script to clear all test data from the database."""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app
from app.services.auth_service import AuthService

def clear_all_test_data():
    """Clear all test data from the database."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🗑️  Clearing all test data...")
            AuthService.clear_all_data()
            print("✅ All test data cleared successfully!")
            print("\nThe following data has been removed:")
            print("  - Authentication tokens (PAT)")
            print("  - Repositories")
            print("  - Contributors")
            print("  - Daily statistics")
            print("  - Team members")
            print("  - Settings")
            print("  - External commits")
            print("\n💡 Note: Database tables are preserved, only data was cleared.")
            print("   To recreate tables, run: python init_db.py")
        except Exception as e:
            print(f"❌ Error clearing test data: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    # Confirm before clearing
    response = input("⚠️  This will delete ALL data from the database. Are you sure? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        clear_all_test_data()
    else:
        print("❌ Operation cancelled.")

