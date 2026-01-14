"""Minimal test Flask app for Vercel."""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "Flask is working!"})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "Test API"})

