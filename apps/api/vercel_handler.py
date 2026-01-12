"""Vercel serverless function entry point."""
import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from run import app

# Export the Flask app for Vercel
# Vercel will automatically detect this as the WSGI application
handler = app

