"""Vercel serverless function entry point."""
import os
import sys
import traceback

# Ensure we're in the correct directory
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Change to the apps/api directory to ensure relative imports work
original_cwd = os.getcwd()
try:
    os.chdir(current_dir)
    from run import app
except Exception as e:
    # If import fails, try to create a minimal error handler
    # But first check if Flask is available
    try:
        from flask import Flask, jsonify
        error_app = Flask(__name__)
        
        @error_app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
        def error_handler(path):
            error_msg = f"Failed to import Flask app: {str(e)}"
            error_traceback = traceback.format_exc()
            return jsonify({
                "ok": False,
                "error": error_msg,
                "traceback": error_traceback,
                "current_dir": current_dir,
                "sys_path": sys.path[:5],  # First 5 paths
                "cwd": os.getcwd()
            }), 500
        
        app = error_app
    except ImportError:
        # If Flask itself isn't available, we can't create an error handler
        # This means dependencies aren't installed - raise the original error
        raise e
finally:
    os.chdir(original_cwd)

# Export app for Vercel
# Vercel automatically detects 'app' as the WSGI application

