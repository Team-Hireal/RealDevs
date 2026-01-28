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

            # Build query conditions
            conditions = ["ds.date >= %s"]
            params = [start_date]

            if contributor_login:
                conditions.append("c.login = %s")
                params.append(contributor_login)

            where_clause = " AND ".join(conditions)

            # Get daily commits grouped by date
            cursor.execute(f"""
                SELECT
                    ds.date,
                    SUM(ds.commits_count) as total_commits,
                    SUM(CASE WHEN c.is_team_member THEN ds.commits_count ELSE 0 END) as internal_commits,
                    SUM(CASE WHEN NOT c.is_team_member OR c.is_team_member IS NULL THEN ds.commits_count ELSE 0 END) as external_commits
                FROM daily_stats ds
                JOIN contributors c ON ds.contributor_id = c.id
                WHERE {where_clause}
                GROUP BY ds.date
                ORDER BY ds.date
            """, params)

            daily_commits = []
            for row in cursor.fetchall():
                daily_commits.append({
                    "date": row[0].strftime("%Y-%m-%d") if hasattr(row[0], 'strftime') else str(row[0])[:10],
                    "commits": row[1] or 0,
                    "internal": row[2] or 0,
                    "external": row[3] or 0
                })

            # Get internal/external split
            cursor.execute(f"""
                SELECT
                    SUM(CASE WHEN c.is_team_member THEN ds.commits_count ELSE 0 END) as internal,
                    SUM(CASE WHEN NOT c.is_team_member OR c.is_team_member IS NULL THEN ds.commits_count ELSE 0 END) as external
                FROM daily_stats ds
                JOIN contributors c ON ds.contributor_id = c.id
                WHERE {where_clause}
            """, params)

            split_row = cursor.fetchone()
            internal_total = split_row[0] or 0
            external_total = split_row[1] or 0

            internal_external_split = [
                {"category": "Internal", "count": internal_total},
                {"category": "External", "count": external_total}
            ]

            # Get repo contributions
            cursor.execute(f"""
                SELECT
                    r.full_name,
                    SUM(ds.commits_count) as commits,
                    CASE WHEN SUM(CASE WHEN c.is_team_member THEN ds.commits_count ELSE 0 END) > SUM(CASE WHEN NOT c.is_team_member OR c.is_team_member IS NULL THEN ds.commits_count ELSE 0 END) THEN 'internal' ELSE 'external' END as type
                FROM daily_stats ds
                JOIN contributors c ON ds.contributor_id = c.id
                JOIN repositories r ON ds.repo_id = r.id
                WHERE {where_clause}
                GROUP BY r.id, r.full_name
                ORDER BY commits DESC
                LIMIT 10
            """, params)

            repo_contributions = []
            for row in cursor.fetchall():
                repo_contributions.append({
                    "name": row[0],
                    "value": row[1],
                    "type": row[2]
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


