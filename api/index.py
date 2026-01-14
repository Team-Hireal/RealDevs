"""Vercel serverless function entry point - using index.py for zero-config support."""
import os
import sys
import traceback

# Get the current file's directory (api/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the project root directory (one level up from api/)
root_dir = os.path.dirname(current_dir)

# Add apps/api to Python path so we can import the Flask app
apps_api_path = os.path.join(root_dir, 'apps', 'api')
if os.path.exists(apps_api_path):
    abs_path = os.path.abspath(apps_api_path)
    if abs_path not in sys.path:
        sys.path.insert(0, abs_path)

# Also add root directory to path
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import the Flask app from run.py
# The app instance is created by create_app() in apps/api/run.py
try:
    from run import app
except ImportError as e:
    # If import fails, create a minimal error handler with detailed info
    import logging
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import Flask app: {e}")
    logger.error(f"Current dir: {current_dir}")
    logger.error(f"Root dir: {root_dir}")
    logger.error(f"Apps API path: {apps_api_path}")
    logger.error(f"Python path: {sys.path[:5]}")
    logger.error(traceback.format_exc())
    
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    def error_handler(path):
        return jsonify({
            "ok": False,
            "error": f"Failed to import Flask app: {str(e)}",
            "current_dir": current_dir,
            "root_dir": root_dir,
            "apps_api_path": apps_api_path,
            "python_path": sys.path[:10],
            "traceback": traceback.format_exc()
        }), 500

# Export app for Vercel Python runtime
# Vercel will automatically detect this as the WSGI application
# The 'app' variable must be a Flask instance at module level
# DO NOT use 'handler = app' - just export 'app' directly

