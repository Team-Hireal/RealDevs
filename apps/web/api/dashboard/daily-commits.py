from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Minimal placeholder implementation for /api/dashboard/daily-commits

        The frontend (see apps/web/src/lib/api.ts:getDailyCommits) expects a JSON object:
        {
          "daily_commits": [{ "date": string, "commits": number, "internal": number, "external": number }],
          "internal_external_split": [{ "category": string, "count": number }],
          "repo_contributions": [{ "name": string, "value": number, "type": "internal" | "external" }]
        }
        """
        # Parse query string so range_days / contributor_login are accepted (even if unused here)
        qs = parse_qs(urlparse(self.path).query)
        _range_days = qs.get("range_days", ["7"])[0]
        _contributor_login = qs.get("contributor_login", [None])[0]

        payload = {
            "daily_commits": [],
            "internal_external_split": [
                {"category": "Internal", "count": 0},
                {"category": "External", "count": 0},
            ],
            "repo_contributions": [],
        }

        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


