from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Validate and store GitHub PAT."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
            
            pat = data.get('pat', '').strip()
            store_mode = data.get('store_mode', 'encrypted')
            
            if not pat:
                payload = {
                    "ok": False,
                    "error": "PAT is required"
                }
                self._send_response(400, payload)
                return
            
            # Validate PAT with GitHub
            import httpx
            
            try:
                response = httpx.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {pat}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 401:
                    payload = {
                        "ok": False,
                        "error": "Invalid PAT. Please check your token and try again."
                    }
                    self._send_response(401, payload)
                    return
                elif response.status_code != 200:
                    payload = {
                        "ok": False,
                        "error": f"Failed to validate PAT: GitHub API returned {response.status_code}"
                    }
                    self._send_response(500, payload)
                    return
                
                user_data = response.json()
                
                # Store PAT in database using raw SQL
                try:
                    import psycopg2
                    from cryptography.fernet import Fernet
                    import base64
                    import hashlib
                    
                    # Get database URL from environment
                    database_url = os.getenv("POSTGRES_URL_NON_POOLING") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
                    
                    if database_url:
                        # Encrypt the PAT
                        secret_key = os.getenv("HIDEVS_SECRET_KEY", "dev-secret-change-in-production")
                        # Create a Fernet key from the secret
                        key = base64.urlsafe_b64encode(hashlib.sha256(secret_key.encode()).digest())
                        f = Fernet(key)
                        encrypted_pat = f.encrypt(pat.encode()).decode()
                        
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
                            # Delete existing tokens
                            cursor.execute("DELETE FROM auth_tokens")
                            
                            # Create new token
                            cursor.execute(
                                "INSERT INTO auth_tokens (encrypted_token, github_user_login, github_user_id, store_mode, created_at, updated_at) "
                                "VALUES (%s, %s, %s, %s, NOW(), NOW())",
                                (encrypted_pat, user_data.get("login"), user_data.get("id"), store_mode)
                            )
                            
                            # Update auth mode setting
                            cursor.execute(
                                "INSERT INTO settings (key, value, created_at, updated_at) VALUES (%s, %s, NOW(), NOW()) "
                                "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()",
                                ('auth_mode', 'pat')
                            )
                            
                            # Clear username setting if it exists
                            cursor.execute("DELETE FROM settings WHERE key = 'github_username'")
                            
                            conn.commit()
                        finally:
                            cursor.close()
                            conn.close()
                except Exception as db_error:
                    print(f"Database error: {db_error}", file=sys.stderr)
                    payload = {
                        "ok": False,
                        "error": f"Failed to store PAT: {str(db_error)}"
                    }
                    self._send_response(500, payload)
                    return
                
                # Return success response
                payload = {
                    "ok": True,
                    "user": {
                        "login": user_data.get("login"),
                        "id": user_data.get("id"),
                        "name": user_data.get("name"),
                        "avatar_url": user_data.get("avatar_url")
                    }
                }
                self._send_response(200, payload)
                
            except httpx.RequestError as e:
                payload = {
                    "ok": False,
                    "error": f"Failed to connect to GitHub: {str(e)}"
                }
                self._send_response(500, payload)
                
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
