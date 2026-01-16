"""RealDevs Flask app for Vercel - Full Application with Frontend Serving."""
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
    
    # Import and create the full Flask application directly
    from app import create_app
    app = create_app()
    
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

# Serve Next.js static files in production
if os.getenv('VERCEL_ENV') or os.getenv('NODE_ENV') == 'production':
    from flask import send_from_directory, send_file
    
    # Path to Next.js build output
    nextjs_static_path = os.path.join(current_dir, 'apps', 'web', '.next', 'static')
    nextjs_public_path = os.path.join(current_dir, 'apps', 'web', 'public')
    nextjs_standalone_path = os.path.join(current_dir, 'apps', 'web', '.next', 'standalone')
    
    # Serve _next/static files
    @app.route('/_next/static/<path:path>')
    def serve_nextjs_static(path):
        return send_from_directory(nextjs_static_path, path)
    
    # Serve public files (images, favicon, etc.)
    @app.route('/public/<path:path>')
    def serve_public(path):
        return send_from_directory(nextjs_public_path, path)
    
    # Serve root-level public files
    @app.route('/<path:filename>')
    def serve_public_root(filename):
        # Only serve files with extensions (to avoid catching dynamic routes)
        if '.' in filename:
            public_file = os.path.join(nextjs_public_path, filename)
            if os.path.exists(public_file):
                return send_from_directory(nextjs_public_path, filename)
        
        # For all other routes, serve index.html (SPA routing)
        index_file = os.path.join(current_dir, 'apps', 'web', 'out', 'index.html')
        if not os.path.exists(index_file):
            # Fallback to .next/server/app/index.html if using app router
            index_file = os.path.join(current_dir, 'apps', 'web', '.next', 'server', 'app', 'index.html')
        
        if os.path.exists(index_file):
            return send_file(index_file)
        else:
            return jsonify({"error": "Frontend not built"}), 404
    
    # Catch-all for SPA routing (must be last)
    @app.route('/', defaults={'path': ''})
    def serve_spa(path):
        index_file = os.path.join(current_dir, 'apps', 'web', 'out', 'index.html')
        if not os.path.exists(index_file):
            # Fallback to .next/server/app/index.html if using app router
            index_file = os.path.join(current_dir, 'apps', 'web', '.next', 'server', 'app', 'index.html')
        
        if os.path.exists(index_file):
            return send_file(index_file)
        else:
            return jsonify({"service": "RealDevs", "status": "ok", "note": "Frontend not built"})
