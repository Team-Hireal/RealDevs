"""RealDevs API application factory."""
from flask import Flask, jsonify
from flask_cors import CORS
import traceback

def create_app(config=None):
    """Create and configure Flask application."""
    try:
        from config import get_config
        from app.models import db
        from app.api import api_bp
        
        app = Flask(__name__)
        
        # Load configuration
        if config is None:
            config = get_config()
        app.config.from_object(config)
        
        # Initialize extensions
        try:
            CORS(app, resources={
                r"/api/*": {
                    "origins": app.config.get("CORS_ORIGINS", ["*"]),
                    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                    "allow_headers": ["Content-Type", "Authorization"]
                }
            })
        except Exception as e:
            # CORS initialization failed - continue without it
            pass
        
        # Initialize database
        try:
            db.init_app(app)
        except Exception as e:
            # Database initialization failed - continue without it
            pass
        
        # Create tables (only in development or if explicitly requested)
        # In production, tables should be created via migrations or init script
        if app.config.get("FLASK_ENV") == "development":
            with app.app_context():
                try:
                    db.create_all()
                except Exception:
                    # Ignore errors (e.g., tables already exist, no database connection)
                    pass
        
        # Register blueprints
        try:
            app.register_blueprint(api_bp, url_prefix='/api')
        except Exception as e:
            # Blueprint registration failed - add error route
            @app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
            def blueprint_error(path):
                return jsonify({
                    "ok": False,
                    "error": f"Blueprint registration failed: {str(e)}"
                }), 500
        
        return app
    except Exception as e:
        # If app creation fails, create a minimal error handler app
        error_app = Flask(__name__)
        
        @error_app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
        def error_handler(path):
            return jsonify({
                "ok": False,
                "error": f"Failed to create Flask app: {str(e)}",
                "traceback": traceback.format_exc()
            }), 500
        
        return error_app

