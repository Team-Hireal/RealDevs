"""Main entry point for Flask application."""
import os
import sys
import traceback

# Ensure current directory is in Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Try to load environment variables (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available - continue without it
    pass
except Exception:
    # dotenv failed - continue without it
    pass

# Import and create app with error handling
try:
    from app import create_app
    app = create_app()
except Exception as e:
    # If app creation fails completely, create a minimal error handler
    from flask import Flask, jsonify
    error_app = Flask(__name__)
    
    @error_app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    def error_handler(path):
        return jsonify({
            "ok": False,
            "error": f"Failed to create Flask app: {str(e)}",
            "traceback": traceback.format_exc(),
            "current_dir": current_dir
        }), 500
    
    app = error_app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

