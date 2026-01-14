"""Vercel serverless function entry point."""
import os
import sys
import traceback

# Get the current file's directory (api/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the project root directory (one level up from api/)
root_dir = os.path.dirname(current_dir)

# Try multiple path strategies for Vercel compatibility
possible_paths = [
    os.path.join(root_dir, 'apps', 'api'),  # Standard monorepo structure
    os.path.join(root_dir, 'api'),          # If apps/api is flattened
    current_dir,                            # If handler is in apps/api
    root_dir,                               # Root directory
]

# Add all possible paths to sys.path
for path in possible_paths:
    abs_path = os.path.abspath(path)
    if abs_path not in sys.path and os.path.exists(abs_path):
        sys.path.insert(0, abs_path)

# Debug: Log paths (will appear in Vercel function logs)
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Handler file: {__file__}")
logger.info(f"Current dir: {current_dir}")
logger.info(f"Root dir: {root_dir}")
logger.info(f"Python path: {sys.path[:5]}...")  # First 5 entries

# Try to find and import the Flask app
handler = None
import_error = None

# Strategy 1: Direct import from run (if apps/api is in path)
try:
    from run import app
    handler = app
    logger.info("✅ Successfully imported Flask app from 'run'")
except ImportError as e:
    logger.warning(f"Import from 'run' failed: {str(e)}")
    import_error = e

# Strategy 2: Import from apps.api.run
if handler is None:
    try:
        from apps.api.run import app
        handler = app
        logger.info("✅ Successfully imported Flask app from 'apps.api.run'")
    except ImportError as e:
        logger.warning(f"Import from 'apps.api.run' failed: {str(e)}")
        import_error = e

# Strategy 3: Try to find run.py and import dynamically
if handler is None:
    for path in possible_paths:
        run_py = os.path.join(path, 'run.py')
        if os.path.exists(run_py):
            try:
                # Add the directory to path and try importing
                run_dir = os.path.dirname(run_py)
                if run_dir not in sys.path:
                    sys.path.insert(0, run_dir)
                from run import app
                handler = app
                logger.info(f"✅ Successfully imported Flask app from {run_py}")
                break
            except ImportError as e:
                logger.warning(f"Failed to import from {run_py}: {str(e)}")
                continue

# If all imports failed, create an error handler
if handler is None:
    logger.error("❌ All import attempts failed!")
    logger.error(f"Last error: {str(import_error)}")
    logger.error(traceback.format_exc())
    
    from flask import Flask, jsonify
    error_app = Flask(__name__)
    
    @error_app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    def error_handler(path):
        # List all files in possible paths for debugging
        debug_info = {
            "error": str(import_error),
            "handler_file": __file__,
            "current_dir": current_dir,
            "root_dir": root_dir,
            "possible_paths": {},
            "sys_path": sys.path[:10],  # First 10 entries
        }
        
        # Check what files exist in each path
        for path_name, path_val in [
            ("apps_api", os.path.join(root_dir, 'apps', 'api')),
            ("api_dir", os.path.join(root_dir, 'api')),
            ("current", current_dir),
            ("root", root_dir),
        ]:
            if os.path.exists(path_val):
                try:
                    files = os.listdir(path_val)
                    debug_info["possible_paths"][path_name] = {
                        "path": path_val,
                        "exists": True,
                        "files": [f for f in files if f.endswith('.py')][:10]
                    }
                except:
                    debug_info["possible_paths"][path_name] = {"path": path_val, "exists": True, "error": "Cannot list"}
            else:
                debug_info["possible_paths"][path_name] = {"path": path_val, "exists": False}
        
        return jsonify({
            "ok": False,
            "error": f"Failed to initialize Flask app: {str(import_error)}",
            "debug": debug_info
        }), 500
    
    handler = error_app

logger.info("Handler initialized successfully" if handler else "Handler initialization failed")

