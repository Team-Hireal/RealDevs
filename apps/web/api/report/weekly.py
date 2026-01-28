from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs, urlsplit
from datetime import datetime, timedelta, timezone
import psycopg2


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Generate a weekly summary report based on dashboard data.
        
        Returns: {"text": string}
        """
        try:
            qs = parse_qs(urlparse(self.path).query)
            range_days_param = qs.get("range_days", ["7"])[0]
            
            # Handle "all" for all-time data
            if range_days_param == 'all':
                range_days = None
            else:
                range_days = int(range_days_param)
            
            report_text = self._generate_report(range_days)
            
            payload = {"text": report_text}
            self._send_response(200, payload)
            
        except Exception as e:
            payload = {"text": f"Error generating report: {str(e)}"}
            self._send_response(500, payload)
    
    def _generate_report(self, range_days):
        """Generate a natural language summary report."""
        conn = None
        cursor = None
        try:
            conn, cursor = self._get_db_connection()
            
            # Calculate date range
            if range_days is None:
                start_date = datetime(2008, 1, 1, tzinfo=timezone.utc)
                period_name = "All time"
            else:
                start_date = datetime.now(timezone.utc) - timedelta(days=range_days)
                period_name = f"Past {range_days} days"
            
            # Get total commits
            cursor.execute("""
                SELECT SUM(commits_count) FROM daily_stats WHERE date >= %s
            """, (start_date,))
            total_commits = cursor.fetchone()[0] or 0
            
            # Get contributor count
            cursor.execute("""
                SELECT COUNT(DISTINCT c.login)
                FROM contributors c
                JOIN daily_stats d ON c.id = d.contributor_id
                WHERE d.date >= %s
            """, (start_date,))
            contributor_count = cursor.fetchone()[0] or 0
            
            # Get top contributor
            cursor.execute("""
                SELECT c.login, SUM(d.commits_count) as commits
                FROM contributors c
                JOIN daily_stats d ON c.id = d.contributor_id
                WHERE d.date >= %s
                GROUP BY c.login
                ORDER BY commits DESC
                LIMIT 1
            """, (start_date,))
            top_contributor = cursor.fetchone()
            
            # Get most active repo
            cursor.execute("""
                SELECT r.full_name, SUM(d.commits_count) as commits
                FROM repositories r
                JOIN daily_stats d ON r.id = d.repo_id
                WHERE d.date >= %s
                GROUP BY r.full_name
                ORDER BY commits DESC
                LIMIT 1
            """, (start_date,))
            top_repo = cursor.fetchone()
            
            # Calculate trend
            if range_days and range_days >= 2:
                mid_date = start_date + timedelta(days=range_days//2)
                
                cursor.execute("""
                    SELECT SUM(commits_count) FROM daily_stats 
                    WHERE date >= %s AND date < %s
                """, (start_date, mid_date))
                first_half = cursor.fetchone()[0] or 0
                
                cursor.execute("""
                    SELECT SUM(commits_count) FROM daily_stats 
                    WHERE date >= %s
                """, (mid_date,))
                second_half = cursor.fetchone()[0] or 0
                
                if first_half > 0:
                    trend = ((second_half - first_half) / first_half) * 100
                else:
                    trend = 0
            else:
                trend = 0
            
            # Build report
            lines = []
            lines.append(f"📊 Team Activity Summary ({period_name})")
            lines.append("")
            lines.append(f"Total Commits: {total_commits}")
            lines.append(f"Active Contributors: {contributor_count}")
            lines.append("")
            
            if top_contributor:
                lines.append(f"🏆 Top Contributor: {top_contributor[0]} ({top_contributor[1]} commits)")
            
            if top_repo:
                lines.append(f"📦 Most Active Repository: {top_repo[0]} ({top_repo[1]} commits)")
            
            lines.append("")
            
            if trend > 10:
                lines.append(f"📈 Activity is trending up by {trend:.1f}%")
            elif trend < -10:
                lines.append(f"📉 Activity is trending down by {abs(trend):.1f}%")
            else:
                lines.append(f"➡️ Activity is stable ({trend:+.1f}%)")
            
            if total_commits == 0:
                lines.append("")
                lines.append("⚠️ No commit data available. Sync your repositories to see activity.")
            
            return "\n".join(lines)
            
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


