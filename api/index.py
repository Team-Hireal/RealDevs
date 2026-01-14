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

# Add paths to sys.path - Vercel needs absolute paths
if apps_api_path not in sys.path:
    sys.path.insert(0, apps_api_path)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Now import the Flask app from apps/api/run.py
# Use absolute import path
from run import app

# Export app for Vercel
# Vercel automatically detects 'app' as the WSGI application
