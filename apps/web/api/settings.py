from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Get all settings from database."""
        try:
            settings = {}
            
            # Get settings from database using raw SQL
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
                        cursor.execute("SELECT key, value FROM settings")
                        rows = cursor.fetchall()
                        
                        settings = {row[0]: row[1] for row in rows}
                    finally:
                        cursor.close()
                        conn.close()
            except Exception as db_error:
                print(f"Database error: {db_error}")
            
            payload = {"settings": settings}
            self._send_response(200, payload)
            
        except Exception as e:
            payload = {"ok": False, "error": f"Internal server error: {str(e)}"}
            self._send_response(500, payload)
    
    def do_POST(self):
        """Update a setting in database."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
            
            key = data.get('key', '')
            value = data.get('value', '')
            
            if not key:
                payload = {"ok": False, "error": "key is required"}
                self._send_response(400, payload)
                return
            
            # Update setting in database using raw SQL
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
                        # Upsert the setting
                        cursor.execute(
                            """
                            INSERT INTO settings (key, value, updated_at) 
                            VALUES (%s, %s, NOW()) 
                            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()
                            """,
                            (key, value)
                        )
                        
                        conn.commit()
                    finally:
                        cursor.close()
                        conn.close()
                else:
                    payload = {"ok": False, "error": "Database not configured"}
                    self._send_response(500, payload)
                    return
                    
            except Exception as db_error:
                print(f"Database error: {db_error}")
                payload = {"ok": False, "error": f"Failed to update setting: {str(db_error)}"}
                self._send_response(500, payload)
                return
            
            payload = {"ok": True, "message": f"Setting '{key}' updated successfully"}
            self._send_response(200, payload)
            
        except json.JSONDecodeError:
            payload = {"ok": False, "error": "Invalid JSON in request body"}
            self._send_response(400, payload)
        except Exception as e:
            payload = {"ok": False, "error": f"Internal server error: {str(e)}"}
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
