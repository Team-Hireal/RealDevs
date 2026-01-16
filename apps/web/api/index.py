# apps/web/api/index.py
from pathlib import Path
import sys

# Ensure we can import the backend package
# index.py path: apps/web/api/index.py
# backend path: apps/web/backend
WEB_ROOT = Path(__file__).resolve().parents[1]          # apps/web
BACKEND_ROOT = WEB_ROOT / "backend"                    # apps/web/backend
sys.path.insert(0, str(BACKEND_ROOT))

# Try common patterns
# backend/app/__init__.py typically provides create_app()
try:
    from app import create_app  # apps/web/backend/app/__init__.py
    app = create_app()
except Exception:
    # fallback if backend/run.py defines `app = Flask(__name__)`
    from run import app  # apps/web/backend/run.py

# Optional: allow both /api/foo and /api/foo/
try:
    app.url_map.strict_slashes = False
except Exception:
    pass

