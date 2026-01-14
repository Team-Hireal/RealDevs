"""Configuration for RealDevs API."""
import os
from pathlib import Path

# Vercel environment detection
IS_VERCEL = bool(os.getenv("VERCEL") or os.getenv("VERCEL_ENV"))
VERCEL_URL = os.getenv("VERCEL_URL")
VERCEL_ENV = os.getenv("VERCEL_ENV")  # production, preview, development

class Config:
    """Base configuration."""
    
    # Flask
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"
    
    # Vercel detection
    IS_VERCEL = IS_VERCEL
    VERCEL_URL = VERCEL_URL
    VERCEL_ENV = VERCEL_ENV
    
    # Security
    SECRET_KEY = os.getenv("HIDEVS_SECRET_KEY", "dev-secret-change-in-production")
    
    # Database
    BASE_DIR = Path(__file__).parent
    # Support both SQLite (local) and PostgreSQL (production)
    # Check for DATABASE_URL first, then POSTGRES_URL_NON_POOLING (better for SQLAlchemy), then POSTGRES_URL
    DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL_NON_POOLING") or os.getenv("POSTGRES_URL")
    
    if not DATABASE_URL:
        # Fallback to SQLite for local development
        DATABASE_URL = f"sqlite:///{BASE_DIR}/realdevs.db"
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # PostgreSQL connection string (or other database)
        # Convert postgres:// to postgresql:// (SQLAlchemy requirement)
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
        # Ensure SSL mode for production databases
        if DATABASE_URL.startswith("postgresql://"):
            # Check if query parameters already exist
            if "?" in DATABASE_URL:
                # Add sslmode if not present
                if "sslmode" not in DATABASE_URL:
                    DATABASE_URL = f"{DATABASE_URL}&sslmode=require"
            else:
                # Add sslmode as first query parameter
                DATABASE_URL = f"{DATABASE_URL}?sslmode=require"
        
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Connection pooling for serverless (PostgreSQL)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Verify connections before using
        "pool_recycle": 300,    # Recycle connections after 5 minutes
    }
    
    # CORS
    # Auto-detect Vercel frontend URL if on Vercel and CORS_ORIGINS not explicitly set
    _cors_origins_env = os.getenv("CORS_ORIGINS")
    if _cors_origins_env:
        CORS_ORIGINS = _cors_origins_env.split(",")
    elif IS_VERCEL and VERCEL_URL:
        # On Vercel, automatically allow requests from the same deployment
        # Users can still override with CORS_ORIGINS env var
        CORS_ORIGINS = [
            f"https://{VERCEL_URL}",
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://localhost:3003"
        ]
    else:
        # Default development origins
        CORS_ORIGINS = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "http://localhost:3003"
        ]
    
    # GitHub API
    GITHUB_API_BASE = "https://api.github.com"
    GITHUB_RATE_LIMIT_BUFFER = 100  # Keep 100 requests in reserve
    
    # Pagination
    MAX_PAGE_SIZE = 100
    DEFAULT_PAGE_SIZE = 30


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


def get_config():
    """Get configuration based on environment."""
    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        return ProductionConfig()
    return DevelopmentConfig()

# https://github.com/SimonSaysGiveMeSmile
