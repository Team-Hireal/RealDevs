"""Vercel serverless function entry point."""
import os
import sys

# Ensure we're in the correct directory
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Change to the apps/api directory to ensure relative imports work
original_cwd = os.getcwd()
try:
    os.chdir(current_dir)
    from run import app
finally:
    os.chdir(original_cwd)

# Export app for Vercel
# Vercel automatically detects 'app' as the WSGI application

