"""Vercel serverless function entry point."""
import os
import sys
import traceback

# Get the current file's directory (apps/api/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the project root directory (two levels up from apps/api/)
root_dir = os.path.dirname(os.path.dirname(current_dir))

# Add apps/api to Python path so we can import the Flask app
# This ensures we can import 'run' module
if current_dir not in sys.path:
    abs_path = os.path.abspath(current_dir)
    sys.path.insert(0, abs_path)

# Also add root directory to path for any cross-package imports
if root_dir not in sys.path:
    abs_root_path = os.path.abspath(root_dir)
    sys.path.insert(0, abs_root_path)

# Import the Flask app from run.py
try:
    from run import app
except ImportError as e:
    # If import fails, create a minimal error handler
    import logging
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import Flask app: {e}")
    logger.error(traceback.format_exc())
    
    try:
        from flask import Flask, jsonify
        error_app = Flask(__name__)
        
        @error_app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
        def error_handler(path):
            return jsonify({
                "ok": False,
                "error": f"Failed to import Flask app: {str(e)}",
                "traceback": traceback.format_exc(),
                "current_dir": current_dir,
                "root_dir": root_dir,
                "sys_path": sys.path[:5]  # First 5 paths for debugging
            }), 500
        
        app = error_app
    except ImportError:
        # If Flask itself isn't available, we can't create an error handler
        # This means dependencies aren't installed - raise the original error
        raise e

# Export app for Vercel Python runtime
# Vercel will detect this as the WSGI application
# The 'app' variable must be a Flask instance at module level

