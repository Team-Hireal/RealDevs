"""Vercel entry point - minimal imports."""
import os
import sys

# Set up path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import Flask first (should always work)
from flask import Flask

# Create minimal app first
app = Flask(__name__)

# Add basic health endpoint immediately
@app.route('/api/health', methods=['GET'])
def health():
    from flask import jsonify
    return jsonify({
        "status": "ok",
        "service": "RealDevs API"
    })

# Now try to load the real app
try:
    # Change to apps/api directory
    original_cwd = os.getcwd()
    try:
        os.chdir(current_dir)
        from app import create_app
        # Replace with real app
        real_app = create_app()
        # Copy routes from real app to our app
        for rule in real_app.url_map.iter_rules():
            if rule.endpoint != 'static':
                app.add_url_rule(
                    rule.rule,
                    endpoint=rule.endpoint,
                    view_func=real_app.view_functions[rule.endpoint],
                    methods=rule.methods
                )
    finally:
        os.chdir(original_cwd)
except Exception as e:
    # If real app fails, keep the minimal app with health endpoint
    import traceback
    @app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    def fallback(path):
        from flask import jsonify
        return jsonify({
            "ok": False,
            "error": f"App initialization failed: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500

