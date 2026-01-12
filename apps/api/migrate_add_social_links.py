"""Migration script to add social link columns to contributors table."""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app
from app.models import db
from sqlalchemy import text

def migrate_add_social_links():
    """Add social link columns to contributors table if they don't exist."""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('contributors')]
            
            print(f"Existing columns: {', '.join(columns)}")
            
            # Add columns if they don't exist (SQLite compatible)
            with db.engine.connect() as conn:
                if 'linkedin_url' not in columns:
                    conn.execute(text("ALTER TABLE contributors ADD COLUMN linkedin_url VARCHAR(512)"))
                    conn.commit()
                    print("✅ Added linkedin_url column")
                else:
                    print("⏭️  linkedin_url column already exists")
                
                if 'twitter_url' not in columns:
                    conn.execute(text("ALTER TABLE contributors ADD COLUMN twitter_url VARCHAR(512)"))
                    conn.commit()
                    print("✅ Added twitter_url column")
                else:
                    print("⏭️  twitter_url column already exists")
                
                if 'website_url' not in columns:
                    conn.execute(text("ALTER TABLE contributors ADD COLUMN website_url VARCHAR(512)"))
                    conn.commit()
                    print("✅ Added website_url column")
                else:
                    print("⏭️  website_url column already exists")
            
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Error running migration: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    migrate_add_social_links()

