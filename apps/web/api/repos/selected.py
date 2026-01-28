from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Get currently selected repos."""
        try:
            repos = self._get_selected_repos()
            payload = {"repos": repos}
            self._send_response(200, payload)
        except Exception as e:
            payload = {"ok": False, "error": f"Failed to get selected repos: {str(e)}"}
            self._send_response(500, payload)
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def _get_selected_repos(self):
        """Get selected repos from database."""
        conn = None
        cursor = None
        try:
            import psycopg2
            
            # Get database URL from environment
            database_url = os.getenv("POSTGRES_URL_NON_POOLING") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
            
            if not database_url:
                return []
            
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
            
            cursor.execute("""
                SELECT
                    id,
                    full_name,
                    owner,
                    name,
                    private,
                    last_synced_at
                FROM repositories
                ORDER BY full_name
            """)
            
            repos = []
            for row in cursor.fetchall():
                repos.append({
                    "id": row[0],
                    "full_name": row[1],
                    "owner": row[2],
                    "name": row[3],
                    "private": row[4] if row[4] is not None else False,
                    "last_synced_at": row[5].isoformat() if row[5] else None
                })
            
            return repos
        except Exception as e:
            print(f"Database error: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def _send_response(self, status_code, payload):
        """Helper to send JSON response."""
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

