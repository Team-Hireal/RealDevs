"""Configuration for RealDevs API."""
import os
from pathlib import Path

class Config:
    """Base configuration."""
    
    # Flask
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"
    
    # Security
    SECRET_KEY = os.getenv("HIDEVS_SECRET_KEY", "dev-secret-change-in-production")
    
    # Database
    BASE_DIR = Path(__file__).parent
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/realdevs.db")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace("sqlite:///", "sqlite:///")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003").split(",")
    
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

