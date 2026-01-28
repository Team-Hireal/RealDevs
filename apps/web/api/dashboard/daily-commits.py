from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs, urlsplit
from datetime import datetime, timedelta, timezone
import psycopg2


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Return daily commit data for charts.

        The frontend expects:
        {
          "daily_commits": [{ "date": string, "commits": number, "internal": number, "external": number }],
          "internal_external_split": [{ "category": string, "count": number }],
          "repo_contributions": [{ "name": string, "value": number, "type": "internal" | "external" }]
        }
        """
        try:
            # Parse query string
            qs = parse_qs(urlparse(self.path).query)
            range_days_param = qs.get("range_days", ["7"])[0]
            contributor_login = qs.get("contributor_login", [None])[0]

            # Handle "all" for all-time data
            if range_days_param == 'all':
                range_days = None
            else:
                range_days = int(range_days_param)

            data = self._get_daily_commits(range_days, contributor_login)
            self._send_response(200, data)
        except Exception as e:
            self._send_response(500, {"error": f"Failed to get daily commits: {str(e)}"})

    def _get_daily_commits(self, range_days, contributor_login):
        """Get daily commit data for charts."""
        conn = None
        cursor = None
        try:
            # Get database connection
            conn, cursor = self._get_db_connection()

            # Calculate date range
            if range_days is None:
                # All time - use a very old date
                start_date = datetime(2008, 1, 1, tzinfo=timezone.utc)
            else:
                start_date = datetime.now(timezone.utc) - timedelta(days=range_days)

            # Get internal organizations and repos from settings
            cursor.execute("SELECT value FROM settings WHERE key = 'internal_organizations' LIMIT 1")
            orgs_row = cursor.fetchone()
            internal_orgs = json.loads(orgs_row[0]) if orgs_row and orgs_row[0] else []
            
            cursor.execute("SELECT value FROM settings WHERE key = 'internal_repos' LIMIT 1")
            repos_row = cursor.fetchone()
            internal_repos_setting = json.loads(repos_row[0]) if repos_row and repos_row[0] else []
            
            # Convert to lowercase for case-insensitive comparison
            internal_orgs_lower = [org.lower() for org in internal_orgs]
            internal_repos_lower = [repo.lower() for repo in internal_repos_setting]

            # Build query conditions
            conditions = ["ds.date >= %s"]
            params = [start_date]

            if contributor_login:
                conditions.append("c.login = %s")
                params.append(contributor_login)

            where_clause = " AND ".join(conditions)

            # Get daily commits with repo information
            cursor.execute(f"""
                SELECT
                    ds.date,
                    ds.commits_count,
                    r.owner,
                    r.full_name
                FROM daily_stats ds
                JOIN contributors c ON ds.contributor_id = c.id
                JOIN repositories r ON ds.repo_id = r.id
                WHERE {where_clause}
                ORDER BY ds.date
            """, params)

            # Aggregate by date and classify as internal/external
            from collections import defaultdict
            daily_data = defaultdict(lambda: {"total": 0, "internal": 0, "external": 0})
            
            for row in cursor.fetchall():
                date = row[0].strftime("%Y-%m-%d") if hasattr(row[0], 'strftime') else str(row[0])[:10]
                commits = row[1] or 0
                owner = row[2].lower() if row[2] else ""
                full_name = row[3].lower() if row[3] else ""
                
                # Check if repo is internal
                is_internal = owner in internal_orgs_lower or full_name in internal_repos_lower
                
                daily_data[date]["total"] += commits
                if is_internal:
                    daily_data[date]["internal"] += commits
                else:
                    daily_data[date]["external"] += commits
            
            # Convert to list format
            daily_commits = [
                {
                    "date": date,
                    "commits": data["total"],
                    "internal": data["internal"],
                    "external": data["external"]
                }
                for date, data in sorted(daily_data.items())
            ]

            # Calculate total internal/external split
            internal_total = sum(d["internal"] for d in daily_commits)
            external_total = sum(d["external"] for d in daily_commits)

            internal_external_split = [
                {"category": "Internal", "count": internal_total},
                {"category": "External", "count": external_total}
            ]

            # Get repo contributions
            cursor.execute(f"""
                SELECT
                    r.full_name,
                    r.owner,
                    SUM(ds.commits_count) as commits
                FROM daily_stats ds
                JOIN contributors c ON ds.contributor_id = c.id
                JOIN repositories r ON ds.repo_id = r.id
                WHERE {where_clause}
                GROUP BY r.id, r.full_name, r.owner
                ORDER BY commits DESC
                LIMIT 10
            """, params)

            repo_contributions = []
            for row in cursor.fetchall():
                full_name = row[0]
                owner = row[1].lower() if row[1] else ""
                full_name_lower = full_name.lower() if full_name else ""
                commits = row[2]
                
                # Determine if repo is internal
                is_internal = owner in internal_orgs_lower or full_name_lower in internal_repos_lower
                
                repo_contributions.append({
                    "name": full_name,
                    "value": commits,
                    "type": "internal" if is_internal else "external"
                })

            return {
                "daily_commits": daily_commits,
                "internal_external_split": internal_external_split,
                "repo_contributions": repo_contributions
            }

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _get_db_connection(self):
        """Get database connection."""
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


