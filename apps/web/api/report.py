"""Combined report handler for /api/report/weekly endpoint."""
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs


class handler(BaseHTTPRequestHandler):
    def _get_path_segment(self):
        """Extract the path segment after /api/report/"""
        path = self.path
        # Remove query string
        if '?' in path:
            path = path.split('?')[0]
        # Extract segment after /api/report/
        parts = path.strip('/').split('/')
        if len(parts) >= 3 and parts[0] == 'api' and parts[1] == 'report':
            return parts[2] if len(parts) > 2 else None
        return None
    
    def do_GET(self):
        """Handle GET requests - /api/report/weekly"""
        path_segment = self._get_path_segment()
        
        if path_segment == 'weekly':
            self._handle_weekly()
        else:
            payload = {
                "ok": False,
                "error": f"Endpoint not found: {self.path}"
            }
            self._send_response(404, payload)
    
    def _handle_weekly(self):
        """Generate weekly report text."""
        # Parse query string
        qs = parse_qs(urlparse(self.path).query)
        range_days_param = qs.get("range_days", ["7"])[0]

        # Handle "all" for all-time data
        if range_days_param == 'all':
            range_days = None
        else:
            range_days = int(range_days_param)

        try:
            text = self._generate_weekly_report(range_days)
            self._send_response(200, {"text": text})
        except Exception as e:
            self._send_response(500, {"error": f"Failed to generate report: {str(e)}"})

    def _generate_weekly_report(self, range_days):
        """Generate weekly report text from database."""
        import os
        from urllib.parse import urlsplit
        import psycopg2
        from datetime import datetime, timedelta, timezone

        conn = None
        cursor = None
        try:
            # Get database connection
            database_url = os.getenv("POSTGRES_URL_NON_POOLING") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")

            if not database_url:
                return "Database not configured. Please set up your database connection."

            result = urlsplit(database_url)

            conn = psycopg2.connect(
                database=result.path[1:],
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port,
                sslmode='require'
            )

            cursor = conn.cursor()

            # Calculate date range
            if range_days is None:
                start_date = datetime(2008, 1, 1, tzinfo=timezone.utc)
                period_desc = "all time"
            else:
                start_date = datetime.now(timezone.utc) - timedelta(days=range_days)
                period_desc = f"last {range_days} days"

            # Get basic stats
            cursor.execute("""
                SELECT
                    COUNT(*) as total_commits,
                    SUM(internal_commits) as internal_commits,
                    SUM(external_commits) as external_commits,
                    COUNT(DISTINCT repository_id) as repos_active,
                    COUNT(DISTINCT contributor_id) as contributors_active
                FROM daily_stats
                WHERE date >= %s
            """, (start_date,))

            stats = cursor.fetchone()
            total_commits = stats[0] or 0
            internal_commits = stats[1] or 0
            external_commits = stats[2] or 0
            repos_active = stats[3] or 0
            contributors_active = stats[4] or 0

            # Get top contributors
            cursor.execute("""
                SELECT
                    c.github_login,
                    COUNT(*) as commits
                FROM contributors c
                JOIN daily_stats ds ON c.id = ds.contributor_id
                WHERE ds.date >= %s
                GROUP BY c.id, c.github_login
                ORDER BY commits DESC
                LIMIT 5
            """, (start_date,))

            top_contributors = cursor.fetchall()

            # Get top repositories
            cursor.execute("""
                SELECT
                    r.full_name,
                    COUNT(*) as commits
                FROM repositories r
                JOIN daily_stats ds ON r.id = ds.repository_id
                WHERE ds.date >= %s
                GROUP BY r.id, r.full_name
                ORDER BY commits DESC
                LIMIT 5
            """, (start_date,))

            top_repos = cursor.fetchall()

            # Get team members count
            cursor.execute("SELECT COUNT(*) FROM team_members WHERE is_active = TRUE")
            team_members_count = cursor.fetchone()[0]

            # Generate report text
            report_lines = []
            report_lines.append(f"# Weekly Development Report ({period_desc})")
            report_lines.append("")

            if total_commits == 0:
                report_lines.append("No commit data available for the selected period.")
                report_lines.append("Try syncing some repositories to see activity.")
                return "\n".join(report_lines)

            report_lines.append("## Summary")
            report_lines.append(f"- **Total Commits**: {total_commits}")
            report_lines.append(f"- **Internal Commits**: {internal_commits} ({internal_commits/total_commits*100:.1f}%)" if total_commits > 0 else "")
            report_lines.append(f"- **External Commits**: {external_commits} ({external_commits/total_commits*100:.1f}%)" if total_commits > 0 else "")
            report_lines.append(f"- **Active Repositories**: {repos_active}")
            report_lines.append(f"- **Active Contributors**: {contributors_active}")
            report_lines.append(f"- **Team Members**: {team_members_count}")
            report_lines.append("")

            if top_contributors:
                report_lines.append("## Top Contributors")
                for i, (login, commits) in enumerate(top_contributors, 1):
                    report_lines.append(f"{i}. **{login}**: {commits} commits")
                report_lines.append("")

            if top_repos:
                report_lines.append("## Most Active Repositories")
                for i, (repo, commits) in enumerate(top_repos, 1):
                    report_lines.append(f"{i}. **{repo}**: {commits} commits")
                report_lines.append("")

            # Get recent activity trend
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
                    trend_pct = ((second_half - first_half) / first_half) * 100
                    trend_desc = "increasing" if trend_pct > 0 else "decreasing"
                    report_lines.append(f"## Trend Analysis")
                    report_lines.append(f"Activity is {trend_desc} by {abs(trend_pct):.1f}% compared to the first half of the period.")
                    report_lines.append("")

            report_lines.append("---")
            report_lines.append(f"*Report generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*")

            return "\n".join(report_lines)

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
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

