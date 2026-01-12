"""Migration script to add external_commits table."""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app
from app.models import db, ExternalCommit

def migrate():
    """Add external_commits table if it doesn't exist."""
    app = create_app()
    
    with app.app_context():
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'external_commits' not in tables:
                print("Creating external_commits table...")
                # Create only the ExternalCommit table
                ExternalCommit.__table__.create(db.engine)
                print("✅ external_commits table created successfully!")
            else:
                print("ℹ️  external_commits table already exists")
            
            # Verify table was created
            tables = inspector.get_table_names()
            if 'external_commits' in tables:
                print(f"✅ Migration complete. Current tables: {', '.join(tables)}")
            else:
                print("❌ Failed to create external_commits table")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    migrate()

