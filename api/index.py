"""Vercel serverless function entry point."""
import os
import sys

# Set up Python path BEFORE any imports
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
apps_api_path = os.path.join(root_dir, 'apps', 'api')

# Add to Python path
for path in [apps_api_path, root_dir]:
    if os.path.exists(path):
        abs_path = os.path.abspath(path)
        if abs_path not in sys.path:
            sys.path.insert(0, abs_path)

# Now import - this must happen after path setup
# Import the Flask app from apps/api/run.py
try:
    from run import app
except ImportError as e:
    # Fallback: try importing from apps.api.run
    if apps_api_path not in sys.path:
        sys.path.insert(0, apps_api_path)
    from run import app

# Export app for Vercel
# Vercel automatically detects 'app' as the WSGI application
