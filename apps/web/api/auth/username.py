from http.server import BaseHTTPRequestHandler
import json
import os


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Validate GitHub username and configure username-only mode."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
            
            username = data.get('username', '').strip()
            
            if not username:
                payload = {
                    "ok": False,
                    "error": "Username is required"
                }
                self._send_response(400, payload)
                return
            
            # Validate username exists on GitHub
            import httpx
            
            try:
                response = httpx.get(
                    f"https://api.github.com/users/{username}",
                    headers={
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 404:
                    payload = {
                        "ok": False,
                        "error": f"GitHub user '{username}' not found"
                    }
                    self._send_response(404, payload)
                    return
                elif response.status_code != 200:
                    payload = {
                        "ok": False,
                        "error": f"Failed to validate username: GitHub API returned {response.status_code}"
                    }
                    self._send_response(500, payload)
                    return
                
                user_data = response.json()
                
                # Store username in database
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
                            # Store username in settings (upsert)
                            cursor.execute("""
                                INSERT INTO settings (key, value, created_at, updated_at)
                                VALUES ('github_username', %s, NOW(), NOW())
                                ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()
                            """, (username,))
                            
                            # Store auth mode
                            cursor.execute("""
                                INSERT INTO settings (key, value, created_at, updated_at)
                                VALUES ('auth_mode', 'username', NOW(), NOW())
                                ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()
                            """)
                            
                            conn.commit()
                        finally:
                            cursor.close()
                            conn.close()
                except Exception as db_error:
                    # If database fails, still return success but log the error
                    print(f"Database error: {db_error}")
                
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
