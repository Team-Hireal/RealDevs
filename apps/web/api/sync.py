from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from datetime import datetime, timedelta, timezone


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Trigger a sync of repository data."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
            
            range_days_param = data.get('range_days', 7)
            # Handle "all" for all-time sync (use a large range like 5 years)
            if range_days_param == 'all' or range_days_param is None:
                range_days = 365 * 5  # 5 years max
            else:
                try:
                    range_days = int(range_days_param)
                    if range_days < 1:
                        range_days = 7  # Default to 7 days if invalid
                except (ValueError, TypeError):
                    range_days = 7  # Default to 7 days if invalid
            
            import psycopg2
            from urllib.parse import urlparse
            from cryptography.fernet import Fernet
            import base64
            import hashlib
            import httpx
            
            # Get database URL from environment
            database_url = os.getenv("POSTGRES_URL_NON_POOLING") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
            
            if not database_url:
                payload = {
                    "ok": False,
                    "error": "Database connection not configured"
                }
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
                cursor.execute("SELECT encrypted_token, github_user_login FROM auth_tokens LIMIT 1")
                auth_row = cursor.fetchone()
                
                if not auth_row or not auth_row[0]:
                    print("No PAT found in auth_tokens table", file=sys.stderr)
                    payload = {
                        "ok": False,
                        "error": "No PAT configured. Please add a Personal Access Token first.",
                        "debug": "auth_tokens table is empty",
                        "stats": {
                            "repos_synced": 0,
                            "total_commits": 0,
                            "total_prs": 0
                        }
                    }
                    self._send_response(400, payload)
                    return
                
                print(f"Found PAT for user: {auth_row[1]}", file=sys.stderr)
                
                # Decrypt PAT
                try:
                    secret_key = os.getenv("HIDEVS_SECRET_KEY", "dev-secret-change-in-production")
                    key = base64.urlsafe_b64encode(hashlib.sha256(secret_key.encode()).digest())
                    f = Fernet(key)
                    pat = f.decrypt(auth_row[0].encode()).decode()
                    print("PAT decrypted successfully", file=sys.stderr)
                except Exception as decrypt_error:
                    print(f"PAT decryption failed: {decrypt_error}", file=sys.stderr)
                    payload = {
                        "ok": False,
                        "error": "Failed to decrypt PAT. The encryption key may have changed.",
                        "debug": str(decrypt_error),
                        "stats": {
                            "repos_synced": 0,
                            "total_commits": 0,
                            "total_prs": 0
                        }
                    }
                    self._send_response(500, payload)
                    return
                
                # Get selected repositories
                cursor.execute("SELECT id, github_id, full_name, owner, name, default_branch FROM repositories")
                repos = cursor.fetchall()
                
                if not repos:
                    print("No repos found in repositories table", file=sys.stderr)
                    payload = {
                        "ok": False,
                        "error": "No repos selected. Please select repositories first.",
                        "debug": "repositories table is empty",
                        "stats": {
                            "repos_synced": 0,
                            "total_commits": 0,
                            "total_prs": 0
                        }
                    }
                    self._send_response(400, payload)
                    return
                
                print(f"Found {len(repos)} repos to sync", file=sys.stderr)
                
                # Calculate date range
                until = datetime.now(timezone.utc)
                since = until - timedelta(days=range_days)
                
                synced_repos = []
                failed_repos = []
                total_commits = 0
                
                print(f"Starting sync for {len(repos)} repo(s), range: {range_days} days", file=sys.stderr)
                
                # Sync each repository
                for repo_row in repos:
                    repo_id, github_id, full_name, owner, name, default_branch = repo_row
                    
                    try:
                        print(f"Syncing {full_name}...", file=sys.stderr)
                        
                        # Fetch commits from GitHub
                        headers = {
                            "Authorization": f"Bearer {pat}",
                            "Accept": "application/vnd.github+json",
                            "X-GitHub-Api-Version": "2022-11-28"
                        }
                        
                        # Get commits
                        url = f"https://api.github.com/repos/{owner}/{name}/commits"
                        params = {
                            "since": since.isoformat(),
                            "until": until.isoformat(),
                            "per_page": 100
                        }
                        
                        response = httpx.get(url, headers=headers, params=params, timeout=30.0)
                        
                        if response.status_code != 200:
                            print(f"  GitHub API error for {full_name}: {response.status_code}", file=sys.stderr)
                            failed_repos.append({
                                "repo": full_name,
                                "error": f"GitHub API returned {response.status_code}"
                            })
                            continue
                        
                        commits = response.json()
                        print(f"  Fetched {len(commits)} commits from {full_name}", file=sys.stderr)
                        total_commits += len(commits)
                        
                        # Aggregate commits by contributor and day
                        from collections import defaultdict
                        commit_counts = defaultdict(lambda: defaultdict(int))
                        contributor_info = {}
                        
                        for commit in commits:
                            if not commit.get('author'):
                                continue
                            
                            author = commit['author']
                            if not author or not author.get('id') or not author.get('login'):
                                continue
                            
                            github_user_id = author['id']
                            login = author['login']
                            commit_date_str = commit['commit']['author']['date']
                            commit_date = datetime.fromisoformat(commit_date_str.replace('Z', '+00:00'))
                            
                            # Filter by date range
                            if commit_date < since or commit_date > until:
                                continue
                            
                            day = commit_date.replace(hour=0, minute=0, second=0, microsecond=0)
                            
                            # Store contributor info
                            if github_user_id not in contributor_info:
                                contributor_info[github_user_id] = {
                                    'login': login,
                                    'name': commit['commit']['author']['name'],
                                    'avatar_url': author.get('avatar_url')
                                }
                            
                            commit_counts[github_user_id][day] += 1
                        
                        print(f"  Processing {len(commit_counts)} contributors", file=sys.stderr)
                        
                        # Process each contributor
                        for github_user_id, day_counts in commit_counts.items():
                            info = contributor_info[github_user_id]
                            
                            # Ensure contributor exists
                            cursor.execute(
                                "SELECT id FROM contributors WHERE repo_id = %s AND github_id = %s",
                                (repo_id, github_user_id)
                            )
                            contributor_row = cursor.fetchone()
                            
                            if not contributor_row:
                                cursor.execute(
                                    "INSERT INTO contributors (github_id, login, name, avatar_url, repo_id, created_at, updated_at) "
                                    "VALUES (%s, %s, %s, %s, %s, NOW(), NOW()) RETURNING id",
                                    (github_user_id, info['login'], info['name'], info['avatar_url'], repo_id)
                                )
                                contributor_id = cursor.fetchone()[0]
                            else:
                                contributor_id = contributor_row[0]
                            
                            # Update daily stats for each day
                            for day, count in day_counts.items():
                                cursor.execute(
                                    "SELECT id FROM daily_stats WHERE date = %s AND repo_id = %s AND contributor_id = %s",
                                    (day, repo_id, contributor_id)
                                )
                                stats_row = cursor.fetchone()
                                
                                if stats_row:
                                    cursor.execute(
                                        "UPDATE daily_stats SET commits_count = %s, updated_at = NOW() WHERE id = %s",
                                        (count, stats_row[0])
                                    )
                                else:
                                    cursor.execute(
                                        "INSERT INTO daily_stats (date, repo_id, contributor_id, commits_count, created_at, updated_at) "
                                        "VALUES (%s, %s, %s, %s, NOW(), NOW())",
                                        (day, repo_id, contributor_id, count)
                                    )
                        
                        # Update repository last_synced_at
                        cursor.execute(
                            "UPDATE repositories SET last_synced_at = NOW(), updated_at = NOW() WHERE id = %s",
                            (repo_id,)
                        )
                        
                        conn.commit()
                        synced_repos.append(full_name)
                        print(f"  Successfully synced {full_name}", file=sys.stderr)
                        
                    except Exception as e:
                        error_msg = str(e)
                        print(f"Error syncing {full_name}: {error_msg}", file=sys.stderr)
                        failed_repos.append({
                            "repo": full_name,
                            "error": error_msg
                        })
                        conn.rollback()
                        continue
                
                result = {
                    "ok": len(failed_repos) == 0,
                    "synced_repos": synced_repos,
                    "failed_repos": failed_repos,
                    "stats": {
                        "repos_synced": len(synced_repos),
                        "total_commits": total_commits,
                        "total_prs": 0
                    }
                }
                
                print(f"Sync completed: {len(synced_repos)} successful, {len(failed_repos)} failed", file=sys.stderr)
                self._send_response(200, result)
                
            finally:
                cursor.close()
                conn.close()
            
        except json.JSONDecodeError:
            payload = {"ok": False, "error": "Invalid JSON in request body"}
            self._send_response(400, payload)
        except Exception as e:
            print(f"Sync error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
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
