from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        payload = {
            "ok": True,
            "data": {
                "total_commits": 0,
                "total_contributors": 0,
                "total_repos": 0,
                "last_sync_at": None,
                "trend": []
            }
        }
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

