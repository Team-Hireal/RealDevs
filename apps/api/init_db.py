"""Initialize database tables for production deployment."""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app
from app.models import db

def init_database():
    """Create all database tables."""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
            
            # Verify tables were created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Created tables: {', '.join(tables)}")
            
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
            sys.exit(1)

if __name__ == '__main__':
    init_database()

