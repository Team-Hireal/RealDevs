"""Service for computing metrics and risk flags."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from app.models import Repository, Contributor, DailyStats, TeamMember, Settings
from sqlalchemy import func
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class MetricsService:
    """Computes team momentum metrics and risk flags."""
    
    DEFAULT_WEIGHTS = {
        "commits": 1.0,
        "prs_opened": 1.5,
        "prs_merged": 2.0,
        "issues_closed": 1.0
    }
    
    @staticmethod
    def get_weights() -> Dict[str, float]:
        """Get weights from settings or use defaults."""
        weights = MetricsService.DEFAULT_WEIGHTS.copy()
        
        # Load from settings if available
        for key in weights.keys():
            setting = Settings.query.filter_by(key=f"weight_{key}").first()
            if setting:
                try:
                    weights[key] = float(setting.value)
                except ValueError:
                    pass
        
        return weights
    
    @staticmethod
    def _get_internal_orgs_config() -> Dict[str, List]:
        """Get internal organizations and repos configuration."""
        import json
        
        orgs_setting = Settings.query.filter_by(key='internal_organizations').first()
        repos_setting = Settings.query.filter_by(key='internal_repos').first()
        
        organizations = json.loads(orgs_setting.value) if orgs_setting else []
        repos = json.loads(repos_setting.value) if repos_setting else []
        
        return {
            "organizations": organizations,
            "repos": repos
        }
    
    @staticmethod
    def _is_internal_contributor(login: str, repo_full_name: str, team_logins: set, internal_orgs_config: Dict) -> bool:
        """
        Determine if a contributor is internal based on:
        1. Team member list
        2. Internal organizations (repo owner is in internal orgs)
        3. Internal repos list (repo is explicitly listed)
        """
        # Check if contributor is in team members
        if login in team_logins:
            return True
        
        # Check if repo is in internal repos list
        if repo_full_name in internal_orgs_config.get("repos", []):
            return True
        
        # Check if repo owner is in internal organizations
        repo_owner = repo_full_name.split('/')[0] if '/' in repo_full_name else None
        if repo_owner and repo_owner in internal_orgs_config.get("organizations", []):
            return True
        
        return False
    
    @staticmethod
    def _calculate_trendline_slope(daily_scores: List[float]) -> float:
        """
        Calculate the slope of a trendline using least squares regression.
        
        Args:
            daily_scores: List of weighted scores for each day (ordered chronologically)
        
        Returns:
            The slope of the trendline. Positive values indicate upward trend,
            negative values indicate downward trend.
        """
        if not daily_scores or len(daily_scores) < 2:
            return 0.0
        
        n = len(daily_scores)
        # x values are day indices (0, 1, 2, ...)
        x_values = list(range(n))
        
        # Calculate sums for least squares formula
        sum_x = sum(x_values)
        sum_y = sum(daily_scores)
        sum_xy = sum(x * y for x, y in zip(x_values, daily_scores))
        sum_x_squared = sum(x * x for x in x_values)
        
        # Least squares slope formula: slope = (n*Σ(xy) - Σ(x)*Σ(y)) / (n*Σ(x²) - (Σ(x))²)
        denominator = n * sum_x_squared - sum_x * sum_x
        if denominator == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope
    
    @staticmethod
    def get_dashboard_data(range_days: Optional[int] = 7) -> Dict:
        """Get all dashboard data including metrics and risk flags."""
        until = datetime.now(timezone.utc)
        # If range_days is None, use a very early date (effectively all time)
        if range_days is None:
            since = datetime(2000, 1, 1, tzinfo=timezone.utc)  # GitHub was founded in 2008, but use 2000 to be safe
        else:
            since = until - timedelta(days=range_days)
        
        # Normalize to start of day for since and end of day for until
        # This ensures we include all commits from the date range, even if stored dates are timezone-naive
        since = since.replace(hour=0, minute=0, second=0, microsecond=0)
        until = until.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        repos = Repository.query.all()
        if not repos:
            return {
                "team_summary": {},
                "repo_summaries": [],
                "risk_flags": [],
                "contributors": [],
                "last_synced": None
            }
        
        # Get team members
        team_logins = {tm.github_login for tm in TeamMember.query.filter_by(is_active=True).all()}
        
        # Get internal organizations and repos configuration
        internal_orgs_config = MetricsService._get_internal_orgs_config()
        
        # Compute team summary
        team_summary = MetricsService._compute_team_summary(repos, since, until, team_logins, internal_orgs_config)
        
        # Compute per-repo summaries
        repo_summaries = [
            MetricsService._compute_repo_summary(repo, since, until, team_logins)
            for repo in repos
        ]
        
        # Compute risk flags
        risk_flags = MetricsService._compute_risk_flags(repos, since, until, team_logins)
        
        # Get contributor breakdown
        contributors = MetricsService._get_contributor_breakdown(repos, since, until, team_logins, internal_orgs_config)
        
        # Last synced time
        last_synced = None
        for repo in repos:
            if repo.last_synced_at:
                if not last_synced or repo.last_synced_at > last_synced:
                    last_synced = repo.last_synced_at
        
        return {
            "team_summary": team_summary,
            "repo_summaries": repo_summaries,
            "risk_flags": risk_flags,
            "contributors": contributors,
            "last_synced": last_synced.isoformat() if last_synced else None,
            "range_days": range_days if range_days is not None else None
        }
    
    @staticmethod
    def _compute_team_summary(repos: List[Repository], since: datetime, until: datetime, team_logins: set, internal_orgs_config: Dict) -> Dict:
        """Compute team-level summary metrics."""
        repo_ids = [r.id for r in repos]
        
        # Create repo id to full_name mapping
        repo_map = {r.id: r.full_name for r in repos}
        
        # Query aggregated stats
        stats = DailyStats.query.filter(
            DailyStats.repo_id.in_(repo_ids),
            DailyStats.date >= since,
            DailyStats.date <= until
        ).all()
        
        # Fetch all contributors upfront to avoid N+1 queries
        contributor_ids = list(set(stat.contributor_id for stat in stats))
        contributors_list = Contributor.query.filter(Contributor.id.in_(contributor_ids)).all()
        contributors_map = {c.id: c for c in contributors_list}
        
        # Aggregate by GitHub user (not by contributor_id, since same user can have multiple contributor records)
        user_stats = defaultdict(lambda: {
            "commits": 0,
            "prs_opened": 0,
            "prs_merged": 0,
            "issues_closed": 0,
            "login": None,
            "is_internal": False
        })
        
        for stat in stats:
            contributor = contributors_map.get(stat.contributor_id)
            if not contributor:
                continue
            
            # Get repo full name for this stat
            repo_full_name = repo_map.get(stat.repo_id, "")
            
            # Use github_id as the key to aggregate same user across multiple repos
            github_id = contributor.github_id
            login = contributor.login
            is_internal = MetricsService._is_internal_contributor(login, repo_full_name, team_logins, internal_orgs_config)
            
            user_stats[github_id]["commits"] += stat.commits_count
            user_stats[github_id]["prs_opened"] += stat.prs_opened
            user_stats[github_id]["prs_merged"] += stat.prs_merged
            user_stats[github_id]["issues_closed"] += stat.issues_closed
            user_stats[github_id]["login"] = login
            # Mark as internal if ANY of their work is internal
            if is_internal:
                user_stats[github_id]["is_internal"] = True
        
        # Now sum up totals from the aggregated user stats
        total_commits = sum(u["commits"] for u in user_stats.values())
        total_prs_opened = sum(u["prs_opened"] for u in user_stats.values())
        total_prs_merged = sum(u["prs_merged"] for u in user_stats.values())
        total_issues_closed = sum(u["issues_closed"] for u in user_stats.values())
        
        internal_commits = sum(u["commits"] for u in user_stats.values() if u["is_internal"])
        external_commits = sum(u["commits"] for u in user_stats.values() if not u["is_internal"])
        
        # Calculate average trend using least squares regression
        weights = MetricsService.get_weights()
        
        # Group stats by date to calculate daily weighted scores
        # Include ALL stats, not just those with valid contributors, for accurate trend calculation
        daily_weighted_scores = defaultdict(float)
        for stat in stats:
            # Calculate weighted score for this day (aggregate across all contributors/repos)
            daily_score = (
                stat.commits_count * weights["commits"] +
                stat.prs_opened * weights["prs_opened"] +
                stat.prs_merged * weights["prs_merged"] +
                stat.issues_closed * weights["issues_closed"]
            )
            
            # Normalize date to date object (handle both datetime and date objects)
            if isinstance(stat.date, datetime):
                date_key = stat.date.date()
            else:
                date_key = stat.date
            
            daily_weighted_scores[date_key] += daily_score
        
        # Sort by date and extract scores
        sorted_dates = sorted(daily_weighted_scores.keys())
        daily_scores = [daily_weighted_scores[date] for date in sorted_dates]
        
        # Log for debugging
        if len(daily_scores) > 0:
            logger.debug(f"Team summary trend calculation: {len(daily_scores)} days, scores: {daily_scores[:5]}... (showing first 5)")
        else:
            logger.debug("Team summary trend calculation: No daily scores found")
        
        # Calculate trendline slope
        average_trend = MetricsService._calculate_trendline_slope(daily_scores)
        
        # Calculate percentages
        # https://github.com/SimonSaysGiveMeSmile
        internal_pct = (internal_commits / total_commits * 100) if total_commits > 0 else 0
        external_pct = (external_commits / total_commits * 100) if total_commits > 0 else 0
        
        return {
            "total_commits": total_commits,
            "total_prs_opened": total_prs_opened,
            "total_prs_merged": total_prs_merged,
            "total_issues_closed": total_issues_closed,
            "average_trend": round(average_trend, 2),
            "internal_commits": internal_commits,
            "external_commits": external_commits,
            "internal_percentage": round(internal_pct, 1),
            "external_percentage": round(external_pct, 1)
        }
    
    @staticmethod
    def _compute_repo_summary(repo: Repository, since: datetime, until: datetime, team_logins: set) -> Dict:
        """Compute summary for a single repo."""
        stats = DailyStats.query.filter(
            DailyStats.repo_id == repo.id,
            DailyStats.date >= since,
            DailyStats.date <= until
        ).all()
        
        total_commits = sum(s.commits_count for s in stats)
        total_prs_opened = sum(s.prs_opened for s in stats)
        total_prs_merged = sum(s.prs_merged for s in stats)
        total_issues_closed = sum(s.issues_closed for s in stats)
        
        # Calculate average trend using least squares regression
        weights = MetricsService.get_weights()
        
        # Group stats by date to calculate daily weighted scores
        daily_weighted_scores = defaultdict(float)
        for stat in stats:
            # Calculate weighted score for this day
            daily_score = (
                stat.commits_count * weights["commits"] +
                stat.prs_opened * weights["prs_opened"] +
                stat.prs_merged * weights["prs_merged"] +
                stat.issues_closed * weights["issues_closed"]
            )
            
            # Use date as key (normalize to date only, ignoring time)
            date_key = stat.date.date() if hasattr(stat.date, 'date') else stat.date
            daily_weighted_scores[date_key] += daily_score
        
        # Sort by date and extract scores
        sorted_dates = sorted(daily_weighted_scores.keys())
        daily_scores = [daily_weighted_scores[date] for date in sorted_dates]
        
        # Calculate trendline slope
        average_trend = MetricsService._calculate_trendline_slope(daily_scores)
        
        return {
            "repo_id": repo.id,
            "full_name": repo.full_name,
            "commits": total_commits,
            "prs_opened": total_prs_opened,
            "prs_merged": total_prs_merged,
            "issues_closed": total_issues_closed,
            "average_trend": round(average_trend, 2),
            "last_synced": repo.last_synced_at.isoformat() if repo.last_synced_at else None
        }
    
    @staticmethod
    def _get_contributor_breakdown(repos: List[Repository], since: datetime, until: datetime, team_logins: set, internal_orgs_config: Dict) -> List[Dict]:
        """Get per-contributor stats."""
        repo_ids = [r.id for r in repos]
        
        # Create repo id to full_name mapping
        repo_map = {r.id: r.full_name for r in repos}
        
        # Group stats by GitHub user (not by contributor_id, since same user can have multiple contributor records across repos)
        user_stats = defaultdict(lambda: {
            "commits": 0,
            "prs_opened": 0,
            "prs_merged": 0,
            "issues_closed": 0,
            "login": None,
            "name": None,
            "avatar_url": None,
            "is_internal": False,
            "daily_scores": defaultdict(float)  # Track daily weighted scores for trend calculation
        })
        
        stats = DailyStats.query.filter(
            DailyStats.repo_id.in_(repo_ids),
            DailyStats.date >= since,
            DailyStats.date <= until
        ).all()
        
        # Fetch all contributors upfront to avoid N+1 queries
        contributor_ids = list(set(stat.contributor_id for stat in stats))
        contributors_list = Contributor.query.filter(Contributor.id.in_(contributor_ids)).all()
        contributors_map = {c.id: c for c in contributors_list}
        
        weights = MetricsService.get_weights()
        
        for stat in stats:
            contributor = contributors_map.get(stat.contributor_id)
            if not contributor:
                continue
            
            # Get repo full name for this stat
            repo_full_name = repo_map.get(stat.repo_id, "")
            
            # Use github_id as the key to aggregate same user across multiple repos
            github_id = contributor.github_id
            
            is_internal = MetricsService._is_internal_contributor(contributor.login, repo_full_name, team_logins, internal_orgs_config)
            
            user_stats[github_id]["commits"] += stat.commits_count
            user_stats[github_id]["prs_opened"] += stat.prs_opened
            user_stats[github_id]["prs_merged"] += stat.prs_merged
            user_stats[github_id]["issues_closed"] += stat.issues_closed
            user_stats[github_id]["login"] = contributor.login
            user_stats[github_id]["name"] = contributor.name
            user_stats[github_id]["avatar_url"] = contributor.avatar_url
            # Mark as internal if ANY of their work is internal
            if is_internal:
                user_stats[github_id]["is_internal"] = True
            
            # Calculate weighted score for this day
            daily_score = (
                stat.commits_count * weights["commits"] +
                stat.prs_opened * weights["prs_opened"] +
                stat.prs_merged * weights["prs_merged"] +
                stat.issues_closed * weights["issues_closed"]
            )
            
            # Use date as key (normalize to date only, ignoring time)
            date_key = stat.date.date() if hasattr(stat.date, 'date') else stat.date
            user_stats[github_id]["daily_scores"][date_key] += daily_score
        
        # Build result
        results = []
        
        for github_id, metrics in user_stats.items():
            # Calculate average trend using least squares regression
            sorted_dates = sorted(metrics["daily_scores"].keys())
            daily_scores = [metrics["daily_scores"][date] for date in sorted_dates]
            average_trend = MetricsService._calculate_trendline_slope(daily_scores)
            
            results.append({
                "login": metrics["login"],
                "name": metrics["name"],
                "avatar_url": metrics["avatar_url"],
                "is_internal": metrics["is_internal"],
                "commits": metrics["commits"],
                "prs_opened": metrics["prs_opened"],
                "prs_merged": metrics["prs_merged"],
                "issues_closed": metrics["issues_closed"],
                "average_trend": round(average_trend, 2)
            })
        
        # Sort by average trend (descending)
        results.sort(key=lambda x: x["average_trend"], reverse=True)
        
        return results
    
    @staticmethod
    def _compute_risk_flags(repos: List[Repository], since: datetime, until: datetime, team_logins: set) -> List[Dict]:
        """Compute risk flags based on heuristics."""
        flags = []
        
        # Get thresholds from settings
        no_activity_days = MetricsService._get_setting("threshold_no_activity_days", 3)
        stale_pr_days = MetricsService._get_setting("threshold_stale_pr_days", 7)
        single_contributor_pct = MetricsService._get_setting("threshold_single_contributor_pct", 70)
        
        repo_ids = [r.id for r in repos]
        
        # Check for repos with no recent activity
        # Normalize since to start of day for proper comparison with stored dates
        since_normalized = since.replace(hour=0, minute=0, second=0, microsecond=0) if since else None
        for repo in repos:
            if since_normalized:
                stats = DailyStats.query.filter(
                    DailyStats.repo_id == repo.id,
                    DailyStats.date >= since_normalized
                ).all()
            else:
                stats = DailyStats.query.filter_by(repo_id=repo.id).all()
            
            if not stats or all(s.commits_count == 0 and s.prs_merged == 0 for s in stats):
                flags.append({
                    "type": "no_activity",
                    "severity": "high",
                    "title": f"No activity in {repo.full_name}",
                    "description": f"No commits or merged PRs in the last {(until - since).days} days",
                    "repo": repo.full_name
                })
        
        # Check for single point of failure (one person doing most work)
        since_normalized = since.replace(hour=0, minute=0, second=0, microsecond=0) if since else None
        for repo in repos:
            if since_normalized:
                stats = DailyStats.query.filter(
                    DailyStats.repo_id == repo.id,
                    DailyStats.date >= since_normalized
                ).all()
            else:
                stats = DailyStats.query.filter_by(repo_id=repo.id).all()
            
            contributor_commits = defaultdict(int)
            total = 0
            
            for stat in stats:
                contributor_commits[stat.contributor_id] += stat.commits_count + stat.prs_merged
                total += stat.commits_count + stat.prs_merged
            
            if total > 10:  # Only flag if there's significant activity
                for contributor_id, count in contributor_commits.items():
                    pct = (count / total) * 100
                    if pct >= single_contributor_pct:
                        contributor = Contributor.query.get(contributor_id)
                        if contributor:
                            flags.append({
                                "type": "single_point_of_failure",
                                "severity": "medium",
                                "title": f"Heavy reliance on {contributor.login}",
                                "description": f"{contributor.login} accounts for {pct:.0f}% of activity in {repo.full_name}",
                                "repo": repo.full_name,
                                "contributor": contributor.login
                            })
        
        # Check for external contributor opening new repos (potential security concern)
        for repo in repos:
            contributors = Contributor.query.filter_by(repo_id=repo.id).all()
            for contrib in contributors:
                if contrib.login not in team_logins:
                    # Check if they have recent commits
                    since_normalized = since.replace(hour=0, minute=0, second=0, microsecond=0) if since else None
                    if since_normalized:
                        recent_stats = DailyStats.query.filter(
                            DailyStats.repo_id == repo.id,
                            DailyStats.contributor_id == contrib.id,
                            DailyStats.date >= since_normalized
                        ).all()
                    else:
                        recent_stats = DailyStats.query.filter_by(
                            repo_id=repo.id,
                            contributor_id=contrib.id
                        ).all()
                    
                    if any(s.commits_count > 0 for s in recent_stats):
                        flags.append({
                            "type": "external_contributor",
                            "severity": "low",
                            "title": f"External contributor active in {repo.full_name}",
                            "description": f"{contrib.login} (not in team list) has made recent contributions",
                            "repo": repo.full_name,
                            "contributor": contrib.login
                        })
        
        return flags
    
    @staticmethod
    def _get_setting(key: str, default):
        """Get a setting value or return default."""
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            try:
                return type(default)(setting.value)
            except ValueError:
                pass
        return default
    
    @staticmethod
    def get_daily_commits(range_days: Optional[int] = 7, contributor_login: Optional[str] = None) -> Dict:
        """Get daily commit counts for charting, optionally filtered by contributor."""
        until = datetime.now(timezone.utc)
        # If range_days is None, use a very early date (effectively all time)
        if range_days is None:
            since = datetime(2000, 1, 1, tzinfo=timezone.utc)
        else:
            since = until - timedelta(days=range_days)
        
        # Normalize to start of day for since and end of day for until
        since = since.replace(hour=0, minute=0, second=0, microsecond=0)
        until = until.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        repos = Repository.query.all()
        if not repos:
            return {"daily_commits": [], "internal_external_split": [], "repo_contributions": []}
        
        repo_ids = [r.id for r in repos]
        
        # Get team members and internal orgs config
        team_logins = {tm.github_login for tm in TeamMember.query.filter_by(is_active=True).all()}
        internal_orgs_config = MetricsService._get_internal_orgs_config()
        repo_map = {r.id: r.full_name for r in repos}
        
        # Group commits by date
        stats = DailyStats.query.filter(
            DailyStats.repo_id.in_(repo_ids),
            DailyStats.date >= since,
            DailyStats.date <= until
        ).all()
        
        # Fetch all contributors upfront
        contributor_ids = list(set(stat.contributor_id for stat in stats))
        contributors_list = Contributor.query.filter(Contributor.id.in_(contributor_ids)).all()
        contributors_map = {c.id: c for c in contributors_list}
        
        # If filtering by contributor, get their github_id
        target_github_id = None
        if contributor_login:
            for c in contributors_list:
                if c.login == contributor_login:
                    target_github_id = c.github_id
                    break
        
        # Aggregate by date
        daily_data = defaultdict(lambda: {"total": 0, "internal": 0, "external": 0})
        
        for stat in stats:
            contributor = contributors_map.get(stat.contributor_id)
            if not contributor:
                continue
            
            # If filtering by contributor, skip others
            if target_github_id is not None and contributor.github_id != target_github_id:
                continue
            
            # Get repo full name
            repo_full_name = repo_map.get(stat.repo_id, "")
            
            # Determine if internal
            is_internal = MetricsService._is_internal_contributor(
                contributor.login, repo_full_name, team_logins, internal_orgs_config
            )
            
            # Format date as YYYY-MM-DD
            date_str = stat.date.strftime("%Y-%m-%d")
            
            daily_data[date_str]["total"] += stat.commits_count
            if is_internal:
                daily_data[date_str]["internal"] += stat.commits_count
            else:
                daily_data[date_str]["external"] += stat.commits_count
        
        # Convert to sorted list
        daily_commits = [
            {
                "date": date_str,
                "commits": data["total"],
                "internal": data["internal"],
                "external": data["external"]
            }
            for date_str, data in sorted(daily_data.items())
        ]
        
        # Calculate overall internal/external split
        total_internal = sum(d["internal"] for d in daily_commits)
        total_external = sum(d["external"] for d in daily_commits)
        
        internal_external_split = [
            {"category": "Internal", "count": total_internal},
            {"category": "External", "count": total_external}
        ]
        
        # Calculate repository-level breakdown
        repo_breakdown = defaultdict(lambda: {"internal": 0, "external": 0})
        
        for stat in stats:
            contributor = contributors_map.get(stat.contributor_id)
            if not contributor:
                continue
            
            # If filtering by contributor, skip others
            if target_github_id is not None and contributor.github_id != target_github_id:
                continue
            
            # Get repo full name
            repo_full_name = repo_map.get(stat.repo_id, "")
            if not repo_full_name:
                continue
            
            # Determine if internal
            is_internal = MetricsService._is_internal_contributor(
                contributor.login, repo_full_name, team_logins, internal_orgs_config
            )
            
            if is_internal:
                repo_breakdown[repo_full_name]["internal"] += stat.commits_count
            else:
                repo_breakdown[repo_full_name]["external"] += stat.commits_count
        
        # Build repository contribution list
        repo_contributions = []
        total_external_commits = 0
        
        for repo_name, counts in sorted(repo_breakdown.items()):
            if counts["internal"] > 0:
                repo_contributions.append({
                    "name": repo_name,
                    "value": counts["internal"],
                    "type": "internal"
                })
            total_external_commits += counts["external"]
        
        # Add external commitments as a separate category
        if total_external_commits > 0:
            repo_contributions.append({
                "name": "External Commitments",
                "value": total_external_commits,
                "type": "external"
            })
        
        return {
            "daily_commits": daily_commits,
            "internal_external_split": internal_external_split,
            "repo_contributions": repo_contributions
        }
    
    @staticmethod
    def get_weekly_recap(range_days: Optional[int] = 7) -> str:
        """Generate weekly recap text."""
        data = MetricsService.get_dashboard_data(range_days)
        
        # Adjust label for all-time
        if range_days is None:
            range_days_label = "All Time"
        else:
            range_days_label = f"{range_days} days"
        
        summary = data["team_summary"]
        repos = data["repo_summaries"]
        flags = data["risk_flags"]
        contributors = data["contributors"]
        
        # Build text
        lines = []
        lines.append(f"📊 Weekly Recap ({range_days_label})")
        lines.append("=" * 50)
        lines.append("")
        
        # Team summary
        lines.append("🔹 Team Activity:")
        lines.append(f"  • {summary.get('total_commits', 0)} commits")
        lines.append(f"  • {summary.get('total_prs_merged', 0)} PRs merged")
        lines.append(f"  • {summary.get('total_prs_opened', 0)} PRs opened")
        lines.append(f"  • {summary.get('total_issues_closed', 0)} issues closed")
        avg_trend = summary.get('average_trend', 0)
        trend_label = "↑ Positive" if avg_trend > 0 else "↓ Negative" if avg_trend < 0 else "→ Neutral"
        lines.append(f"  • Average Trend: {avg_trend:.2f} ({trend_label})")
        lines.append("")
        
        # Internal vs External
        lines.append("🔹 Contribution Split:")
        lines.append(f"  • Internal: {summary.get('internal_percentage', 0):.1f}%")
        lines.append(f"  • External: {summary.get('external_percentage', 0):.1f}%")
        lines.append("")
        
        # Top repos
        if repos:
            top_repos = sorted(repos, key=lambda r: r.get('average_trend', 0), reverse=True)[:3]
            lines.append("🔹 Most Active Repos:")
            for repo in top_repos:
                trend = repo.get('average_trend', 0)
                lines.append(f"  • {repo['full_name']} (trend: {trend:.2f})")
            lines.append("")
        
        # Top contributors
        if contributors:
            top_contributors = [c for c in contributors if c['is_internal']][:5]
            if top_contributors:
                lines.append("🔹 Top Contributors:")
                for contrib in top_contributors:
                    trend = contrib.get('average_trend', 0)
                    lines.append(f"  • {contrib['login']} (trend: {trend:.2f})")
                lines.append("")
        
        # Risk flags
        if flags:
            lines.append("⚠️ Risk Flags:")
            for flag in flags[:5]:  # Limit to top 5
                lines.append(f"  • [{flag['severity'].upper()}] {flag['title']}")
            lines.append("")
        
        # Recommendations
        lines.append("💡 Suggested Actions:")
        if summary.get('total_prs_opened', 0) > summary.get('total_prs_merged', 0) * 1.5:
            lines.append("  • Review and merge pending PRs to reduce bottleneck")
        if any(f['type'] == 'single_point_of_failure' for f in flags):
            lines.append("  • Consider knowledge sharing to reduce bus factor")
        if any(f['type'] == 'no_activity' for f in flags):
            lines.append("  • Check on stale repos and close or archive if no longer needed")
        if not flags:
            lines.append("  • Keep up the great work! No major issues detected.")
        
        return "\n".join(lines)

