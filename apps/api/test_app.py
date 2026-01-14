"""RealDevs Flask app for Vercel."""
import os
import sys

# Set up Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from flask import Flask, jsonify

# Create app first
app = Flask(__name__)

# Add health endpoint immediately
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "service": "RealDevs API"
    })

# Try to load the real app and register its routes
try:
    # Change to apps/api directory for imports
    original_cwd = os.getcwd()
    try:
        os.chdir(current_dir)
        
        # Try to load dotenv (optional)
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except:
            pass
        
        # Import and create real app
        from app import create_app
        real_app = create_app()
        
        # Register all routes from real app
        for rule in real_app.url_map.iter_rules():
            if rule.endpoint != 'static':
                try:
                    view_func = real_app.view_functions[rule.endpoint]
                    app.add_url_rule(
                        rule.rule,
                        endpoint=rule.endpoint,
                        view_func=view_func,
                        methods=rule.methods
                    )
                except Exception:
                    # Skip routes that can't be registered
                    pass
    finally:
        os.chdir(original_cwd)
except Exception as e:
    # If real app fails, keep basic health endpoint
    import traceback
    @app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    def fallback(path):
        return jsonify({
            "ok": False,
            "error": f"App initialization failed: {str(e)}",
            "traceback": traceback.format_exc()[:500]  # Limit traceback size
        }), 500

