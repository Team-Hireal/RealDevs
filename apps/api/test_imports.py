"""Test imports progressively to find the issue."""
from flask import Flask, jsonify
import sys
import os

# Set up path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

app = Flask(__name__)

@app.route('/api/health', methods=['GET'])
def health():
    try:
        # Test imports one by one
        results = []
        
        # Test 1: dotenv
        try:
            from dotenv import load_dotenv
            results.append("✓ dotenv imported")
        except Exception as e:
            results.append(f"✗ dotenv failed: {e}")
        
        # Test 2: config
        try:
            from config import get_config
            results.append("✓ config imported")
        except Exception as e:
            results.append(f"✗ config failed: {e}")
        
        # Test 3: app.models
        try:
            from app.models import db
            results.append("✓ app.models imported")
        except Exception as e:
            results.append(f"✗ app.models failed: {e}")
        
        # Test 4: app.api
        try:
            from app.api import api_bp
            results.append("✓ app.api imported")
        except Exception as e:
            results.append(f"✗ app.api failed: {e}")
        
        # Test 5: create_app
        try:
            from app import create_app
            results.append("✓ create_app imported")
        except Exception as e:
            results.append(f"✗ create_app failed: {e}")
        
        return jsonify({
            "status": "ok",
            "import_tests": results,
            "current_dir": current_dir,
            "sys_path": sys.path[:3]
        })
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

