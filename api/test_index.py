"""Minimal test Flask app for Vercel."""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "Flask app is working!"})

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "service": "RealDevs API"})

