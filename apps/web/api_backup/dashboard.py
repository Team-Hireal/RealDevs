from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Return data in the format expected by the frontend
        payload = {
            "team_summary": {
                "total_commits": 0,
                "total_prs_opened": 0,
                "total_prs_merged": 0,
                "total_issues_closed": 0,
                "average_trend": 0,
                "internal_commits": 0,
                "external_commits": 0,
                "internal_percentage": 0,
                "external_percentage": 0
            },
            "repo_summaries": [],
            "risk_flags": [],
            "contributors": [],
            "last_synced": None,
            "range_days": 7
        }
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

