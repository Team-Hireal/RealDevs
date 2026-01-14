"""RealDevs Flask app for Vercel."""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "status": "ok",
        "service": "RealDevs API",
        "message": "Backend is running"
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "service": "RealDevs API"
    })
