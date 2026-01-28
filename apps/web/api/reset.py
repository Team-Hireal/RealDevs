from http.server import BaseHTTPRequestHandler
import json
import os
import sys


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Reset all data (repositories, team members, etc.)."""
        try:
            import psycopg2
            from urllib.parse import urlparse
            
            # Get database URL from environment
            database_url = os.getenv("POSTGRES_URL_NON_POOLING") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
            
            if not database_url:
                payload = {
                    "ok": False,
                    "error": "Database connection not configured"
                }
                self._send_response(500, payload)
                return
            
            # Parse connection string
            result = urlparse(database_url)
            
            # Connect to database
            conn = psycopg2.connect(
                database=result.path[1:],
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port,
                sslmode='require'
            )
            
            cursor = conn.cursor()
            
            try:
                # Delete all data in correct order (respecting foreign keys)
                cursor.execute("DELETE FROM daily_stats")
                cursor.execute("DELETE FROM external_commits")
                cursor.execute("DELETE FROM contributors")
                cursor.execute("DELETE FROM repositories")
                cursor.execute("DELETE FROM team_members")
                cursor.execute("DELETE FROM external_contributors")
                cursor.execute("DELETE FROM auth_tokens")  # Delete PAT
                cursor.execute("DELETE FROM settings")  # Delete all settings
                
                conn.commit()
                
                print("All data cleared successfully", file=sys.stderr)
                
                payload = {
                    "ok": True,
                    "message": "Data reset successfully"
                }
                self._send_response(200, payload)
                
            finally:
                cursor.close()
                conn.close()
            
        except Exception as e:
            print(f"Error resetting data: {e}", file=sys.stderr)
            payload = {"ok": False, "error": f"Internal server error: {str(e)}"}
            self._send_response(500, payload)
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def _send_response(self, status_code, payload):
        """Helper to send JSON response."""
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
