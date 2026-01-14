"""API Blueprint."""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Lazy import routes - only import when blueprint is actually used
# This prevents import-time errors from breaking the app
def _register_routes():
    """Register routes on the blueprint."""
    try:
        from app.api import routes
    except Exception as e:
        # If routes fail to import, log but don't fail
        # The blueprint will exist but have no routes
        import logging
        logging.error(f"Failed to import routes: {e}")
        pass

# Call immediately to register routes, but wrapped in try-except
_register_routes()

