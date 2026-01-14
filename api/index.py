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

# Add paths to sys.path in the correct order
paths_to_add = [
    apps_api_path,  # apps/api - where run.py is
    root_dir,       # project root
    current_dir     # api/ directory
]

for path in paths_to_add:
    if os.path.exists(path):
        abs_path = os.path.abspath(path)
        if abs_path not in sys.path:
            sys.path.insert(0, abs_path)

# Now import the Flask app from apps/api/run.py
# Change to apps/api directory temporarily to ensure relative imports work
original_cwd = os.getcwd()
try:
    if os.path.exists(apps_api_path):
        os.chdir(apps_api_path)
    from run import app
finally:
    os.chdir(original_cwd)

# Export app for Vercel
# Vercel automatically detects 'app' as the WSGI application
