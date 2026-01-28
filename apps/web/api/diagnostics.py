from http.server import BaseHTTPRequestHandler
import json
import os
import sys


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Get diagnostic information about the current state."""
        try:
            import psycopg2
            from urllib.parse import urlparse
            
            diagnostics = {
                "database_configured": False,
                "pat_configured": False,
                "github_user": None,
                "repos_selected": 0,
                "repos": [],
                "team_members_count": 0,
                "contributors_count": 0,
                "daily_stats_count": 0,
                "errors": []
            }
            
            # Get database URL from environment
            database_url = os.getenv("POSTGRES_URL_NON_POOLING") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
            
            if not database_url:
                diagnostics["errors"].append("Database URL not configured in environment")
                self._send_response(200, diagnostics)
                return
            
            diagnostics["database_configured"] = True
            
            # Check if HIDEVS_SECRET_KEY is set
            secret_key = os.getenv("HIDEVS_SECRET_KEY")
            if not secret_key:
                diagnostics["errors"].append("HIDEVS_SECRET_KEY not set - using default (insecure)")
            
            try:
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
                    # Check auth_tokens table
                    cursor.execute("SELECT COUNT(*) FROM auth_tokens")
                    auth_count = cursor.fetchone()[0]
                    
                    if auth_count > 0:
                        cursor.execute("SELECT github_user_login, github_user_id, store_mode, created_at FROM auth_tokens LIMIT 1")
                        auth_row = cursor.fetchone()
                        if auth_row:
                            diagnostics["pat_configured"] = True
                            diagnostics["github_user"] = auth_row[0]
                            diagnostics["github_user_id"] = auth_row[1]
                            diagnostics["pat_store_mode"] = auth_row[2]
                            diagnostics["pat_created_at"] = auth_row[3].isoformat() if auth_row[3] else None
                    
                    # Check repositories table
                    cursor.execute("SELECT id, full_name, owner, name, last_synced_at FROM repositories ORDER BY full_name")
                    repos = cursor.fetchall()
                    diagnostics["repos_selected"] = len(repos)
                    diagnostics["repos"] = [
                        {
                            "id": r[0],
                            "full_name": r[1],
                            "owner": r[2],
                            "name": r[3],
                            "last_synced": r[4].isoformat() if r[4] else None
                        }
                        for r in repos
                    ]
                    
                    # Check contributors
                    cursor.execute("SELECT COUNT(*) FROM contributors")
                    diagnostics["contributors_count"] = cursor.fetchone()[0]
                    
                    # Check daily_stats
                    cursor.execute("SELECT COUNT(*) FROM daily_stats")
                    diagnostics["daily_stats_count"] = cursor.fetchone()[0]
                    
                    # Check team_members
                    cursor.execute("SELECT COUNT(*) FROM team_members WHERE is_active = true")
                    diagnostics["team_members_count"] = cursor.fetchone()[0]
                    
                    # Check external_commits
                    cursor.execute("SELECT COUNT(*) FROM external_commits")
                    diagnostics["external_commits_count"] = cursor.fetchone()[0]
                    
                    # Check external_contributors
                    cursor.execute("SELECT COUNT(*) FROM external_contributors WHERE is_active = true")
                    diagnostics["external_contributors_count"] = cursor.fetchone()[0]
                    
                    # Check settings
                    cursor.execute("SELECT key, value FROM settings")
                    settings = cursor.fetchall()
                    diagnostics["settings"] = {s[0]: s[1] for s in settings}
                    
                    # Summary
                    diagnostics["ready_to_sync"] = diagnostics["pat_configured"] and diagnostics["repos_selected"] > 0
                    
                finally:
                    cursor.close()
                    conn.close()
                    
            except Exception as db_error:
                diagnostics["errors"].append(f"Database error: {str(db_error)}")
            
            self._send_response(200, diagnostics)
            
        except Exception as e:
            print(f"Diagnostics error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            payload = {"ok": False, "error": f"Internal server error: {str(e)}"}
            self._send_response(500, payload)
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def _send_response(self, status_code, payload):
        """Helper to send JSON response."""
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
