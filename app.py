"""RealDevs Flask app for Vercel - Full Application."""
import os
import sys

# Add apps/api to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
apps_api_path = os.path.join(current_dir, 'apps', 'api')
if apps_api_path not in sys.path:
    sys.path.insert(0, apps_api_path)

# Change to apps/api directory to ensure relative imports work
original_cwd = os.getcwd()
try:
    os.chdir(apps_api_path)
    
    # Import the full Flask application
    from run import app
    
except Exception as e:
    # Fallback to minimal app if full app fails to load
    import traceback
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            "status": "error",
            "service": "RealDevs API",
            "message": "Failed to load full application",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500
    
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({
            "status": "error",
            "service": "RealDevs API",
            "error": "Full application failed to load"
        }), 500
finally:
    os.chdir(original_cwd)
