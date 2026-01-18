"""Combined dashboard handler for /api/dashboard and /api/dashboard/daily-commits endpoints."""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs, urlsplit
import psycopg2
from datetime import datetime, timedelta, timezone


class handler(BaseHTTPRequestHandler):
    def _get_path_segment(self):
        """Extract the path segment after /api/dashboard/"""
        path = self.path
        # Remove query string
        if '?' in path:
            path = path.split('?')[0]
        # Extract segment after /api/dashboard/
        parts = path.strip('/').split('/')
        if len(parts) >= 3 and parts[0] == 'api' and parts[1] == 'dashboard':
            return parts[2] if len(parts) > 2 else None
        return None
    
    def do_GET(self):
        """Handle GET requests - /api/dashboard and /api/dashboard/daily-commits"""
        try:
        path_segment = self._get_path_segment()
        
        if path_segment == 'daily-commits':
            self._handle_daily_commits()
        elif path_segment is None:
            # /api/dashboard (no sub-path)
            self._handle_dashboard()
        else:
            payload = {
                "error": f"Endpoint not found: {self.path}"
            }
            self._send_response(404, payload)
        except Exception as e:
            self._send_response(500, {"error": f"Internal server error: {str(e)}"})
    
    def _handle_dashboard(self):
        """Return dashboard data."""
        # Parse query string
        qs = parse_qs(urlparse(self.path).query)
        range_days_param = qs.get("range_days", ["7"])[0]

        # Handle "all" for all-time data
        if range_days_param == 'all':
            range_days = None
        else:
            range_days = int(range_days_param)

        try:
            data = self._get_dashboard_data(range_days)
            self._send_response(200, data)
        except Exception as e:
            self._send_response(500, {"error": f"Failed to get dashboard data: {str(e)}"})
    
    def _handle_daily_commits(self):
        """Return daily commit data for charts."""
        # Parse query string
        qs = parse_qs(urlparse(self.path).query)
        range_days_param = qs.get("range_days", ["7"])[0]
        contributor_login = qs.get("contributor_login", [None])[0]

        # Handle "all" for all-time data
        if range_days_param == 'all':
            range_days = None
        else:
            range_days = int(range_days_param)

        try:
            data = self._get_daily_commits(range_days, contributor_login)
            self._send_response(200, data)
        except Exception as e:
            self._send_response(500, {"error": f"Failed to get daily commits: {str(e)}"})

    def _get_dashboard_data(self, range_days):
        """Get dashboard data from database."""
        conn = None
        cursor = None
        try:
            # Get database connection
            conn, cursor = self._get_db_connection()

            # Calculate date range
            if range_days is None:
                # All time - use a very old date
                start_date = datetime(2008, 1, 1, tzinfo=timezone.utc)  # GitHub launch date
            else:
                start_date = datetime.now(timezone.utc) - timedelta(days=range_days)

            # Get total commits
            cursor.execute("""
                SELECT COUNT(*) FROM daily_stats
                WHERE date >= %s
            """, (start_date,))
            total_commits = cursor.fetchone()[0]

            # Get internal vs external commits
            cursor.execute("""
                SELECT
                    SUM(internal_commits) as internal,
                    SUM(external_commits) as external
                FROM daily_stats
                WHERE date >= %s
            """, (start_date,))
            commit_split = cursor.fetchone()
            internal_commits = commit_split[0] or 0
            external_commits = commit_split[1] or 0

            # Calculate percentages
            total = internal_commits + external_commits
            internal_percentage = (internal_commits / total * 100) if total > 0 else 0
            external_percentage = (external_commits / total * 100) if total > 0 else 0

            # Get PR and issue stats (placeholder for now)
            total_prs_opened = 0
            total_prs_merged = 0
            total_issues_closed = 0

            # Calculate trend (simplified - compare last 7 days to previous 7 days)
            if range_days and range_days >= 14:
                mid_date = start_date + timedelta(days=range_days//2)
                cursor.execute("""
                    SELECT SUM(internal_commits + external_commits)
                    FROM daily_stats
                    WHERE date >= %s AND date < %s
                """, (start_date, mid_date))
                first_half = cursor.fetchone()[0] or 0

                cursor.execute("""
                    SELECT SUM(internal_commits + external_commits)
                    FROM daily_stats
                    WHERE date >= %s
                """, (mid_date,))
                second_half = cursor.fetchone()[0] or 0

                if first_half > 0:
                    average_trend = ((second_half - first_half) / first_half) * 100
                else:
                    average_trend = 0
            else:
                average_trend = 0

            # Get repo summaries
            cursor.execute("""
                SELECT
                    r.full_name,
                    r.owner,
                    r.name,
                    COUNT(ds.id) as days_active,
                    SUM(ds.internal_commits + ds.external_commits) as total_commits,
                    MAX(ds.date) as last_active
                FROM repositories r
                LEFT JOIN daily_stats ds ON r.id = ds.repository_id AND ds.date >= %s
                GROUP BY r.id, r.full_name, r.owner, r.name
                HAVING COUNT(ds.id) > 0
                ORDER BY total_commits DESC
                LIMIT 10
            """, (start_date,))
            repo_rows = cursor.fetchall()

            repo_summaries = []
            for row in repo_rows:
                repo_summaries.append({
                    "full_name": row[0],
                    "owner": row[1],
                    "name": row[2],
                    "days_active": row[3],
                    "total_commits": row[4],
                    "last_active": row[5].isoformat() if row[5] else None
                })

            # Get top contributors
            cursor.execute("""
                SELECT
                    c.github_login,
                    c.name,
                    COUNT(*) as commits,
                    MAX(d.date) as last_commit
                FROM contributors c
                JOIN daily_stats d ON c.id = d.contributor_id
                WHERE d.date >= %s
                GROUP BY c.id, c.github_login, c.name
                ORDER BY commits DESC
                LIMIT 10
            """, (start_date,))
            contributor_rows = cursor.fetchall()

            contributors = []
            for row in contributor_rows:
                contributors.append({
                    "github_login": row[0],
                    "name": row[1] or row[0],
                    "commits": row[2],
                    "last_commit": row[3].isoformat() if row[3] else None
                })

            # Get last synced time
            cursor.execute("SELECT MAX(last_synced_at) FROM repositories")
            last_synced = cursor.fetchone()[0]

            # Risk flags (simplified)
            risk_flags = []
            if total_commits == 0:
                risk_flags.append("No commit data available - try syncing repositories")
            elif range_days and range_days >= 30 and average_trend < -50:
                risk_flags.append("Significant decline in commit activity")

            return {
                "team_summary": {
                    "total_commits": total_commits,
                    "total_prs_opened": total_prs_opened,
                    "total_prs_merged": total_prs_merged,
                    "total_issues_closed": total_issues_closed,
                    "average_trend": round(average_trend, 2),
                    "internal_commits": internal_commits,
                    "external_commits": external_commits,
                    "internal_percentage": round(internal_percentage, 1),
                    "external_percentage": round(external_percentage, 1)
                },
                "repo_summaries": repo_summaries,
                "risk_flags": risk_flags,
                "contributors": contributors,
                "last_synced": last_synced.isoformat() if last_synced else None,
                "range_days": range_days or "all"
            }

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

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
                conditions.append("c.github_login = %s")
                params.append(contributor_login)

            where_clause = " AND ".join(conditions)

            # Get daily commits
            cursor.execute(f"""
                SELECT
                    ds.date,
                    SUM(ds.internal_commits + ds.external_commits) as total_commits,
                    SUM(ds.internal_commits) as internal_commits,
                    SUM(ds.external_commits) as external_commits
                FROM daily_stats ds
                JOIN contributors c ON ds.contributor_id = c.id
                WHERE {where_clause}
                GROUP BY ds.date
                ORDER BY ds.date
            """, params)

            daily_commits = []
            for row in cursor.fetchall():
                daily_commits.append({
                    "date": row[0].isoformat(),
                    "commits": row[1],
                    "internal": row[2],
                    "external": row[3]
                })

            # Get internal/external split
            cursor.execute(f"""
                SELECT
                    SUM(ds.internal_commits) as internal,
                    SUM(ds.external_commits) as external
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
                    SUM(ds.internal_commits + ds.external_commits) as commits,
                    CASE WHEN SUM(ds.internal_commits) > SUM(ds.external_commits) THEN 'internal' ELSE 'external' END as type
                FROM daily_stats ds
                JOIN contributors c ON ds.contributor_id = c.id
                JOIN repositories r ON ds.repository_id = r.id
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
