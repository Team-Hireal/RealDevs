from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Get configured team members from database."""
        try:
            members = []
            
            # Get team members from database using raw SQL
            try:
                import psycopg2
                
                # Get database URL from environment
                database_url = os.getenv("POSTGRES_URL_NON_POOLING") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
                
                if database_url:
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
                        cursor.execute("SELECT id, github_login, created_at FROM team_members")
                        rows = cursor.fetchall()
                        
                        members = [
                            {
                                "id": row[0],
                                "github_login": row[1],
                                "created_at": row[2].isoformat() if row[2] else None
                            }
                            for row in rows
                        ]
                    finally:
                        cursor.close()
                        conn.close()
            except Exception as db_error:
                print(f"Database error: {db_error}", file=sys.stderr)
            
            payload = {
                "members": members
            }
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
            
        except Exception as e:
            payload = {
                "ok": False,
                "error": f"Internal server error: {str(e)}"
            }
            body = json.dumps(payload).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
    
    def do_POST(self):
        """Update team members list in database."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
            
            github_logins = data.get('github_logins', [])
            
            if not isinstance(github_logins, list):
                payload = {
                    "ok": False,
                    "error": "github_logins must be an array"
                }
                self._send_response(400, payload)
                return
            
            # Update team members in database using raw SQL
            try:
                import psycopg2
                
                # Get database URL from environment
                database_url = os.getenv("POSTGRES_URL_NON_POOLING") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
                
                if database_url:
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
                        # Delete existing team members
                        cursor.execute("DELETE FROM team_members")
                        
                        # Add new team members
                        for login in github_logins:
                            if login and login.strip():
                                cursor.execute(
                                    "INSERT INTO team_members (github_login, created_at, updated_at) VALUES (%s, NOW(), NOW())",
                                    (login.strip(),)
                                )
                        
                        conn.commit()
                    finally:
                        cursor.close()
                        conn.close()
                else:
                    payload = {
                        "ok": False,
                        "error": "Database not configured"
                    }
                    self._send_response(500, payload)
                    return
                    
            except Exception as db_error:
                print(f"Database error: {db_error}", file=sys.stderr)
                payload = {
                    "ok": False,
                    "error": f"Failed to update team members: {str(db_error)}"
                }
                self._send_response(500, payload)
                return
            
            payload = {
                "ok": True,
                "message": f"Team members updated successfully ({len(github_logins)} members)"
            }
            self._send_response(200, payload)
            
        except json.JSONDecodeError:
            payload = {
                "ok": False,
                "error": "Invalid JSON in request body"
            }
            self._send_response(400, payload)
        except Exception as e:
            payload = {
                "ok": False,
                "error": f"Internal server error: {str(e)}"
            }
            self._send_response(500, payload)
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
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
