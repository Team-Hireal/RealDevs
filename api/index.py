"""Vercel serverless function entry point - using index.py for zero-config support."""
import os
import sys

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
from run import app

# Export app for Vercel Python runtime
# Vercel will automatically detect this as the WSGI application
# The 'app' variable must be a Flask instance at module level

