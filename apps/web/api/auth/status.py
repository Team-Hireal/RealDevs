from http.server import BaseHTTPRequestHandler
import json
import os
import sys


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Get authentication status from database."""
        try:
            configured = False
            user_info = None
            
            # Check database for authentication using raw SQL
            try:
                import psycopg2
                from urllib.parse import urlparse
                
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
                        # Check for PAT authentication
                        cursor.execute("SELECT github_user_login, github_user_id, encrypted_token FROM auth_tokens LIMIT 1")
                        auth_token = cursor.fetchone()
                        
                        if auth_token and auth_token[0]:
                            configured = True
                            user_info = {
                                "login": auth_token[0],
                                "id": auth_token[1]
                            }
                            
                            # Try to fetch avatar_url from GitHub if we have a valid PAT
                            if auth_token[2]:
                                try:
                                    from cryptography.fernet import Fernet
                                    import base64
                                    import hashlib
                                    import httpx
                                    
                                    secret_key = os.getenv("HIDEVS_SECRET_KEY", "dev-secret-change-in-production")
                                    key = base64.urlsafe_b64encode(hashlib.sha256(secret_key.encode()).digest())
                                    f = Fernet(key)
                                    pat = f.decrypt(auth_token[2].encode()).decode()
                                    
                                    response = httpx.get(
                                        "https://api.github.com/user",
                                        headers={
                                            "Authorization": f"token {pat}",
                                            "Accept": "application/vnd.github+json",
                                            "X-GitHub-Api-Version": "2022-11-28"
                                        },
                                        timeout=5.0
                                    )
                                    if response.status_code == 200:
                                        user_data = response.json()
                                        user_info["name"] = user_data.get("name")
                                        user_info["avatar_url"] = user_data.get("avatar_url")
                                except Exception as e:
                                    print(f"Failed to fetch user info from GitHub: {e}", file=sys.stderr)
                        
                        # If no PAT auth, check for username-only mode
                        if not auth_token or not auth_token[0]:
                            cursor.execute("SELECT value FROM settings WHERE key = 'github_username' LIMIT 1")
                            username_row = cursor.fetchone()
                            
                            if username_row and username_row[0]:
                                configured = True
                                username = username_row[0]
                                
                                # Fetch user info from GitHub
                                import httpx
                                try:
                                    response = httpx.get(
                                        f"https://api.github.com/users/{username}",
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
                print(f"Database error: {db_error}", file=sys.stderr)
            
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

