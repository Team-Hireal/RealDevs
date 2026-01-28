from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Select repositories to track."""
        try:
            import sys
            import psycopg2
            from cryptography.fernet import Fernet
            import base64
            import hashlib
            import httpx
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
            
            repo_full_names = data.get('repo_full_names', [])
            
            if not isinstance(repo_full_names, list):
                payload = {"ok": False, "error": "repo_full_names must be an array"}
                self._send_response(400, payload)
                return
            
            # Get database URL from environment
            database_url = os.getenv("POSTGRES_URL_NON_POOLING") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
            
            if not database_url:
                payload = {"ok": False, "error": "Database not configured"}
                self._send_response(500, payload)
                return
            
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
                # Get PAT from database
                cursor.execute("SELECT encrypted_token FROM auth_tokens LIMIT 1")
                auth_row = cursor.fetchone()
                
                if not auth_row or not auth_row[0]:
                    payload = {"ok": False, "error": "No PAT configured"}
                    self._send_response(400, payload)
                    return
                
                # Decrypt PAT
                secret_key = os.getenv("HIDEVS_SECRET_KEY", "dev-secret-change-in-production")
                key = base64.urlsafe_b64encode(hashlib.sha256(secret_key.encode()).digest())
                f = Fernet(key)
                pat = f.decrypt(auth_row[0].encode()).decode()
                
                # Fetch repos from GitHub to get metadata
                headers = {
                    "Authorization": f"Bearer {pat}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28"
                }
                
                # Get all available repos
                url = "https://api.github.com/user/repos"
                params = {
                    "visibility": "all",
                    "affiliation": "owner,collaborator,organization_member",
                    "per_page": 100
                }
                
                response = httpx.get(url, headers=headers, params=params, timeout=30.0)
                
                if response.status_code != 200:
                    payload = {"ok": False, "error": f"GitHub API error: {response.status_code}"}
                    self._send_response(500, payload)
                    return
                
                all_repos = response.json()
                repo_map = {repo['full_name']: repo for repo in all_repos}
                
                # Get currently selected repos
                cursor.execute("SELECT full_name FROM repositories")
                current_repos = {row[0] for row in cursor.fetchall()}
                
                # Convert new selection to a set
                new_repos = set(full_name.strip() for full_name in repo_full_names if full_name.strip())
                
                # Find repos to remove
                repos_to_remove = current_repos - new_repos
                if repos_to_remove:
                    for repo_name in repos_to_remove:
                        # Delete related data first (foreign keys)
                        cursor.execute("DELETE FROM daily_stats WHERE repo_id IN (SELECT id FROM repositories WHERE full_name = %s)", (repo_name,))
                        cursor.execute("DELETE FROM contributors WHERE repo_id IN (SELECT id FROM repositories WHERE full_name = %s)", (repo_name,))
                        cursor.execute("DELETE FROM repositories WHERE full_name = %s", (repo_name,))
                    print(f"Removed {len(repos_to_remove)} repo(s) from selection", file=sys.stderr)
                
                # Find repos to add or update
                selected_count = 0
                for full_name in repo_full_names:
                    full_name = full_name.strip()
                    if not full_name:
                        continue
                    
                    if full_name not in repo_map:
                        print(f"Repo not found: {full_name}", file=sys.stderr)
                        continue
                    
                    repo_data = repo_map[full_name]
                    
                    # Insert or update
                    cursor.execute(
                        """
                        INSERT INTO repositories (github_id, full_name, owner, name, private, default_branch, created_at, updated_at) 
                        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW()) 
                        ON CONFLICT (github_id) DO UPDATE SET 
                            full_name = EXCLUDED.full_name,
                            owner = EXCLUDED.owner,
                            name = EXCLUDED.name,
                            private = EXCLUDED.private,
                            default_branch = EXCLUDED.default_branch,
                            updated_at = NOW()
                        """,
                        (
                            repo_data['id'],
                            full_name,
                            repo_data['owner']['login'],
                            repo_data['name'],
                            repo_data.get('private', False),
                            repo_data.get('default_branch', 'main')
                        )
                    )
                    selected_count += 1
                
                conn.commit()
                
                # Get final list
                cursor.execute("SELECT id, full_name FROM repositories")
                final_repos = [{"id": row[0], "full_name": row[1]} for row in cursor.fetchall()]
                
                print(f"Selected {selected_count} repos", file=sys.stderr)
                
                payload = {
                    "ok": True,
                    "selected_count": len(final_repos),
                    "repos": final_repos
                }
                self._send_response(200, payload)
                
            finally:
                cursor.close()
                conn.close()
            
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
