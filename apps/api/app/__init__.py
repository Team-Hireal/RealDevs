"""RealDevs API application factory."""
from flask import Flask
from flask_cors import CORS
from config import get_config
from app.models import db
from app.api import api_bp


def create_app(config=None):
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    if config is None:
        config = get_config()
    app.config.from_object(config)
    
    # Initialize extensions
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config["CORS_ORIGINS"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize database
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

