from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Minimal placeholder implementation for /api/report/weekly

        The frontend (see apps/web/src/lib/api.ts:getWeeklyReport) expects a JSON object:
        {
          "text": string
        }
        """
        # Accept range_days, even though we don't use it in this placeholder
        qs = parse_qs(urlparse(self.path).query)
        _range_days = qs.get("range_days", ["7"])[0]

        payload = {
            "text": (
                "Weekly report placeholder.\n\n"
                "Connect the /api/report/weekly endpoint to your backend to generate a real summary."
            )
        }

        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


