"""Vercel serverless function entry point."""
import os
import sys

# Set up Python path BEFORE any imports
# Get the directory where this file is located (api/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the project root (one level up from api/)
root_dir = os.path.dirname(current_dir)
# Path to apps/api where the Flask app lives
apps_api_path = os.path.join(root_dir, 'apps', 'api')

# Debug: Print paths for troubleshooting
# print(f"Current dir: {current_dir}")
# print(f"Root dir: {root_dir}")
# print(f"Apps API path: {apps_api_path}")
# print(f"Apps API exists: {os.path.exists(apps_api_path)}")

# Add paths to sys.path - Vercel needs absolute paths
paths_to_add = [apps_api_path, root_dir]
for path in paths_to_add:
    if os.path.exists(path):
        abs_path = os.path.abspath(path)
        if abs_path not in sys.path:
            sys.path.insert(0, abs_path)

# Now import the Flask app from apps/api/run.py
try:
    from run import app
except ImportError as e:
    # If direct import fails, try with explicit path manipulation
    import importlib.util
    run_py_path = os.path.join(apps_api_path, 'run.py')
    if os.path.exists(run_py_path):
        spec = importlib.util.spec_from_file_location("run", run_py_path)
        run_module = importlib.util.module_from_spec(spec)
        sys.modules["run"] = run_module
        spec.loader.exec_module(run_module)
        app = run_module.app
    else:
        raise ImportError(f"Cannot find run.py at {run_py_path}. Error: {e}")

# Export app for Vercel
# Vercel automatically detects 'app' as the WSGI application
