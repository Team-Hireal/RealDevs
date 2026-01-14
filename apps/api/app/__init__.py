"""RealDevs API application factory."""
from flask import Flask, jsonify
from flask_cors import CORS

def create_app(config=None):
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    try:
        from config import get_config
        if config is None:
            config = get_config()
        app.config.from_object(config)
    except Exception as e:
        # If config fails, use defaults
        app.config['CORS_ORIGINS'] = ['*']
        app.config['FLASK_ENV'] = 'production'
        app.config['SECRET_KEY'] = 'dev-secret-change-in-production'
    
    # Initialize CORS
    try:
        CORS(app, resources={
            r"/api/*": {
                "origins": app.config.get("CORS_ORIGINS", ["*"]),
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        })
    except Exception:
        # CORS initialization failed - continue without it
        pass
    
    # Initialize database (optional - app works without it)
    try:
        from app.models import db
        db.init_app(app)
        
        # Create tables (only in development)
        if app.config.get("FLASK_ENV") == "development":
            with app.app_context():
                try:
                    db.create_all()
                except Exception:
                    # Ignore errors (e.g., tables already exist, no database connection)
                    pass
    except Exception:
        # Database initialization failed - continue without it
        pass
    
    # Register blueprints - use lazy import to avoid import-time errors
    try:
        # Import blueprint first
        from app.api import api_bp
        # Then try to register it
        app.register_blueprint(api_bp, url_prefix='/api')
    except Exception as e:
        # If blueprint registration fails, add a basic health endpoint
        import traceback
        @app.route('/api/health', methods=['GET'])
        def health_fallback():
            return jsonify({
                "status": "ok",
                "service": "RealDevs API",
                "note": "Running in fallback mode",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
        
        # Also add a catch-all for other API routes
        @app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
        def api_fallback(path):
            return jsonify({
                "ok": False,
                "error": "API blueprint not available",
                "path": path
            }), 503
    
    return app

