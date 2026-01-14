"""Vercel serverless function entry point."""
import os
import sys
import traceback

# Get the current file's directory (api/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the project root directory (one level up from api/)
root_dir = os.path.dirname(current_dir)

# On Vercel, files might be in different locations
# Try to find apps/api directory by walking up from current location
def find_apps_api():
    """Find the apps/api directory by searching from current location."""
    search_dirs = [
        os.path.join(root_dir, 'apps', 'api'),  # Standard monorepo
        os.path.join(root_dir, 'api'),          # Flattened
        current_dir,                            # Current directory
        root_dir,                               # Root
    ]
    
    # Also try walking up directories
    check_dir = current_dir
    for _ in range(5):  # Don't go too far up
        apps_api = os.path.join(check_dir, 'apps', 'api')
        if os.path.exists(apps_api) and os.path.exists(os.path.join(apps_api, 'run.py')):
            return apps_api
        check_dir = os.path.dirname(check_dir)
    
    # Return first existing path
    for path in search_dirs:
        if os.path.exists(path):
            return path
    
    return None

# Find and add apps/api to path
apps_api_path = find_apps_api()
if apps_api_path:
    abs_path = os.path.abspath(apps_api_path)
    if abs_path not in sys.path:
        sys.path.insert(0, abs_path)

# Also add root and current dir
for path in [root_dir, current_dir]:
    abs_path = os.path.abspath(path)
    if abs_path not in sys.path:
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
    search_paths = [
        apps_api_path,
        os.path.join(root_dir, 'apps', 'api'),
        os.path.join(root_dir, 'api'),
        current_dir,
        root_dir,
    ]
    for path in search_paths:
        if not path:
            continue
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

