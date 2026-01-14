"""API Blueprint."""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Lazy import routes to avoid import-time errors
try:
    from app.api import routes
except Exception:
    # If routes fail to import, blueprint will still exist but have no routes
    # This allows the app to start even if routes have import errors
    pass

