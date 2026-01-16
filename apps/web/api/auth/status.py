from http.server import BaseHTTPRequestHandler
import json
import os


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Get authentication status from database."""
        try:
            configured = False
            user_info = None
            
            # Check database for authentication
            try:
                import psycopg2
                
                # Get database URL from environment
                database_url = os.getenv("POSTGRES_URL_NON_POOLING") or os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
                
                if database_url:
                    # Convert postgres:// to postgresql:// if needed
                    if database_url.startswith("postgres://"):
                        database_url = database_url.replace("postgres://", "postgresql://", 1)
                    
                    # Connect to database
                    conn = psycopg2.connect(database_url)
                    cursor = conn.cursor()
                    
                    try:
                        # Check for PAT authentication
                        cursor.execute("SELECT github_user_login, github_user_id FROM auth_tokens LIMIT 1")
                        auth_token = cursor.fetchone()
                        
                        if auth_token:
                            configured = True
                            user_info = {
                                "login": auth_token[0],
                                "id": auth_token[1]
                            }
                        else:
                            # Check for username-only mode
                            cursor.execute("SELECT value FROM settings WHERE key = 'github_username' LIMIT 1")
                            username_row = cursor.fetchone()
                            
                            if username_row and username_row[0]:
                                configured = True
                                # Fetch user info from GitHub
                                import httpx
                                try:
                                    response = httpx.get(
                                        f"https://api.github.com/users/{username_row[0]}",
                                        headers={
                                            "Accept": "application/vnd.github+json",
                                            "X-GitHub-Api-Version": "2022-11-28"
                                        },
                                        timeout=5.0
                                    )
                                    if response.status_code == 200:
                                        user_data = response.json()
                                        user_info = {
                                            "login": user_data.get("login"),
                                            "id": user_data.get("id"),
                                            "name": user_data.get("name"),
                                            "avatar_url": user_data.get("avatar_url")
                                        }
                                except Exception:
                                    pass
                    finally:
                        cursor.close()
                        conn.close()
            except Exception as db_error:
                # Database not configured or error - return not configured
                pass
            
            payload = {
                "ok": True,
                "configured": configured,
            }
            
            if user_info:
                payload["user"] = user_info
            
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
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

