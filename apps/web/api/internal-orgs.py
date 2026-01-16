from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Get internal organizations and repos configuration from database."""
        try:
            organizations = []
            repos = []
            
            # Get configuration from database using raw SQL
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
                        # Get internal organizations setting
                        cursor.execute("SELECT value FROM settings WHERE key = 'internal_organizations' LIMIT 1")
                        orgs_row = cursor.fetchone()
                        if orgs_row and orgs_row[0]:
                            organizations = json.loads(orgs_row[0])
                        
                        # Get internal repos setting
                        cursor.execute("SELECT value FROM settings WHERE key = 'internal_repos' LIMIT 1")
                        repos_row = cursor.fetchone()
                        if repos_row and repos_row[0]:
                            repos = json.loads(repos_row[0])
                    finally:
                        cursor.close()
                        conn.close()
            except Exception as db_error:
                print(f"Database error: {db_error}", file=sys.stderr)
            
            payload = {
                "organizations": organizations,
                "repos": repos
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
        """Update internal organizations and repos configuration in database."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
            
            organizations = data.get('organizations', [])
            repos = data.get('repos', [])
            
            if not isinstance(organizations, list):
                payload = {
                    "ok": False,
                    "error": "organizations must be an array"
                }
                self._send_response(400, payload)
                return
            
            if not isinstance(repos, list):
                payload = {
                    "ok": False,
                    "error": "repos must be an array"
                }
                self._send_response(400, payload)
                return
            
            # Update configuration in database using raw SQL
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
                        # Update internal organizations setting
                        cursor.execute(
                            "INSERT INTO settings (key, value, created_at, updated_at) VALUES (%s, %s, NOW(), NOW()) "
                            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()",
                            ('internal_organizations', json.dumps(organizations))
                        )
                        
                        # Update internal repos setting
                        cursor.execute(
                            "INSERT INTO settings (key, value, created_at, updated_at) VALUES (%s, %s, NOW(), NOW()) "
                            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()",
                            ('internal_repos', json.dumps(repos))
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
                    "error": f"Failed to update internal organizations: {str(db_error)}"
                }
                self._send_response(500, payload)
                return
            
            payload = {
                "ok": True,
                "message": f"Internal organizations updated ({len(organizations)} orgs, {len(repos)} repos)"
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
