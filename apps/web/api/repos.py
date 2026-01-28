"""Combined repos handler for /api/repos and /api/repos/selected endpoints."""
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse


class handler(BaseHTTPRequestHandler):
    def _get_path_segment(self):
        """Extract the path segment after /api/repos/"""
        path = self.path
        # Remove query string
        if '?' in path:
            path = path.split('?')[0]
        # Extract segment after /api/repos/
        parts = path.strip('/').split('/')
        if len(parts) >= 3 and parts[0] == 'api' and parts[1] == 'repos':
            return parts[2] if len(parts) > 2 else None
        return None
    
    def do_GET(self):
        """Handle GET requests - /api/repos and /api/repos/selected"""
        path_segment = self._get_path_segment()
        
        if path_segment == 'selected':
            self._handle_selected()
        elif path_segment is None:
            # /api/repos (no sub-path)
            self._handle_list()
        else:
            payload = {
                "repos": [],
                "error": f"Endpoint not found: {self.path}"
            }
            self._send_response(404, payload)
    
    def _handle_list(self):
        """List all repos accessible to the user."""
        try:
            repos = self._get_available_repos()
            self._send_response(200, {"repos": repos})
        except Exception as e:
            self._send_response(500, {"error": f"Failed to list repos: {str(e)}"})

    def _handle_selected(self):
        """Get currently selected repos."""
        try:
            repos = self._get_selected_repos()
            self._send_response(200, {"repos": repos})
        except Exception as e:
            self._send_response(500, {"error": f"Failed to get selected repos: {str(e)}"})

    def _get_available_repos(self):
        """Get available repos from GitHub API."""
        import os
        import sys
        from urllib.parse import urlsplit
        import psycopg2
        from cryptography.fernet import Fernet
        import base64
        import hashlib
        import httpx
        
        try:
            # Get database URL from environment
            database_url = os.getenv("POSTGRES_URL_NON_POOLING") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
            
            if not database_url:
                print("Database URL not configured", file=sys.stderr)
                return []
            
            # Parse connection string
            result = urlsplit(database_url)
            
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
                # Get PAT from database
                cursor.execute("SELECT encrypted_token FROM auth_tokens LIMIT 1")
                auth_row = cursor.fetchone()
                
                if not auth_row or not auth_row[0]:
                    print("No PAT configured", file=sys.stderr)
                    return []
                
                # Decrypt PAT
                secret_key = os.getenv("HIDEVS_SECRET_KEY", "dev-secret-change-in-production")
                key = base64.urlsafe_b64encode(hashlib.sha256(secret_key.encode()).digest())
                f = Fernet(key)
                pat = f.decrypt(auth_row[0].encode()).decode()
                
                # Fetch repos from GitHub
                headers = {
                    "Authorization": f"Bearer {pat}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28"
                }
                
                # Get user's repos
                repos = []
                url = "https://api.github.com/user/repos"
                params = {
                    "visibility": "all",
                    "affiliation": "owner,collaborator,organization_member",
                    "per_page": 100,
                    "sort": "updated"
                }
                
                response = httpx.get(url, headers=headers, params=params, timeout=30.0)
                
                if response.status_code != 200:
                    print(f"GitHub API error: {response.status_code}", file=sys.stderr)
                    return []
                
                repo_data = response.json()
                
                for repo in repo_data:
                    repos.append({
                        "id": repo['id'],
                        "full_name": repo['full_name'],
                        "owner": repo['owner']['login'],
                        "name": repo['name'],
                        "private": repo.get('private', False),
                        "default_branch": repo.get('default_branch', 'main'),
                        "updated_at": repo.get('updated_at')
                    })
                
                print(f"Fetched {len(repos)} repos from GitHub", file=sys.stderr)
                return repos
                
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            print(f"Error fetching repos: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return []

    def _get_selected_repos(self):
        """Get selected repos from database."""
        conn = None
        cursor = None
        try:
            conn, cursor = self._get_db_connection()

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
                    "private": row[4],
                    "last_synced_at": row[5].isoformat() if row[5] else None
                })

            return repos

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _get_db_connection(self):
        """Get database connection."""
        import os
        from urllib.parse import urlsplit
        import psycopg2

        database_url = os.getenv("POSTGRES_URL_NON_POOLING") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")

        if not database_url:
            raise Exception("Database URL not configured")

        result = urlsplit(database_url)

        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port,
            sslmode='require'
        )

        return conn, conn.cursor()
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
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
