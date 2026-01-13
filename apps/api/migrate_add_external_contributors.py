#!/usr/bin/env python3
"""
Migration script to add external_contributors table.

This script adds a new table to track external contributors that users
want to explicitly monitor. These contributors will have their commits
to selected repositories tracked and labeled as "External" in the dashboard.

Usage:
    python migrate_add_external_contributors.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Run the migration."""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if table already exists
            result = db.session.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='external_contributors'"
            ))
            if result.fetchone():
                logger.info("Table 'external_contributors' already exists. Skipping migration.")
                return
            
            # Create external_contributors table
            logger.info("Creating external_contributors table...")
            db.session.execute(text("""
                CREATE TABLE external_contributors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    github_login VARCHAR(255) NOT NULL UNIQUE,
                    github_user_id INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    last_synced_at DATETIME,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
            """))
            
            # Create indexes for better query performance
            logger.info("Creating indexes...")
            db.session.execute(text(
                "CREATE INDEX idx_external_contributors_github_login ON external_contributors(github_login)"
            ))
            db.session.execute(text(
                "CREATE INDEX idx_external_contributors_github_user_id ON external_contributors(github_user_id)"
            ))
            
            db.session.commit()
            logger.info("Migration completed successfully!")
            logger.info("External contributors table created.")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            db.session.rollback()
            raise


if __name__ == "__main__":
    migrate()

