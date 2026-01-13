"""Service for computing metrics and risk flags."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from app.models import Repository, Contributor, DailyStats, TeamMember, Settings, ExternalCommit, ExternalContributor
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
        4. NOT in external contributors list (explicitly marked as external)
        """
        # Check if contributor is explicitly marked as external
        external_contributor = ExternalContributor.query.filter_by(
            github_login=login,
            is_active=True
        ).first()
        if external_contributor:
            return False  # Explicitly external
        
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
        
        This uses the standard least squares method (not RMS - Root Mean Square).
        RMS is used for error measurement, not for calculating trendline slope.
        
        Formula: slope = (n*Σ(xy) - Σ(x)*Σ(y)) / (n*Σ(x²) - (Σ(x))²)
        where n = number of data points, x = day index (0, 1, 2, ...), y = daily score
        
        Args:
            daily_scores: List of weighted scores for each day (ordered chronologically from oldest to newest)
        
        Returns:
            The slope of the trendline. Positive values indicate upward trend,
            negative values indicate downward trend.
        """
        if not daily_scores or len(daily_scores) < 2:
            return 0.0
        
        n = len(daily_scores)
        # x values are day indices (0, 1, 2, ...)
        # Day 0 is the oldest, day n-1 is the newest
        x_values = list(range(n))
        
        # Calculate sums for least squares formula
        sum_x = sum(x_values)
        sum_y = sum(daily_scores)
        sum_xy = sum(x * y for x, y in zip(x_values, daily_scores))
        sum_x_squared = sum(x * x for x in x_values)
        
        # Least squares slope formula: slope = (n*Σ(xy) - Σ(x)*Σ(y)) / (n*Σ(x²) - (Σ(x))²)
        # This is the standard formula for linear regression slope
        denominator = n * sum_x_squared - sum_x * sum_x
        if denominator == 0:
            logger.warning(f"Trend calculation denominator is zero for {n} data points")
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        
        # Debug logging to help identify issues
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"Trend calculation: n={n}, first_score={daily_scores[0]:.2f}, "
                f"last_score={daily_scores[-1]:.2f}, slope={slope:.4f}"
            )
        
        return slope
    
    @staticmethod
    def get_dashboard_data(range_days: Optional[int] = 7) -> Dict:
        """Get all dashboard data including metrics and risk flags."""
        until = datetime.now(timezone.utc)
        # If range_days is None, use 5 years ago as limit (to reduce query load)
        if range_days is None:
            since = until - timedelta(days=365 * 5)  # 5 years max
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
            
            # Check if this user is explicitly marked as external contributor
            is_external_contributor = ExternalContributor.query.filter_by(
                github_login=login,
                is_active=True
            ).first() is not None
            
            # If explicitly marked as external contributor, always mark as external
            if is_external_contributor:
                is_internal = False
            else:
                # Otherwise, use normal internal/external logic
                is_internal = MetricsService._is_internal_contributor(login, repo_full_name, team_logins, internal_orgs_config)
            
            user_stats[github_id]["commits"] += stat.commits_count
            user_stats[github_id]["prs_opened"] += stat.prs_opened
            user_stats[github_id]["prs_merged"] += stat.prs_merged
            user_stats[github_id]["issues_closed"] += stat.issues_closed
            user_stats[github_id]["login"] = login
            # Mark as internal if ANY of their work is internal (but not if explicitly external contributor)
            if is_internal:
                user_stats[github_id]["is_internal"] = True
            elif is_external_contributor:
                user_stats[github_id]["is_internal"] = False
        
        # Now sum up totals from the aggregated user stats
        total_commits_from_tracked = sum(u["commits"] for u in user_stats.values())
        total_prs_opened = sum(u["prs_opened"] for u in user_stats.values())
        total_prs_merged = sum(u["prs_merged"] for u in user_stats.values())
        total_issues_closed = sum(u["issues_closed"] for u in user_stats.values())
        
        # Internal commits = commits by internal contributors to tracked repos
        internal_commits = sum(u["commits"] for u in user_stats.values() if u["is_internal"])
        
        # External commits to tracked repos = commits by external contributors to tracked repos
        external_commits_to_tracked = sum(u["commits"] for u in user_stats.values() if not u["is_internal"])
        
        # Get external commits from ExternalCommit table (commits to non-tracked repos)
        external_commit_count = ExternalCommit.query.filter(
            ExternalCommit.commit_date >= since,
            ExternalCommit.commit_date <= until
        ).count()
        
        external_commits_to_non_tracked = external_commit_count
        
        # Total external commits = external commits to tracked repos + external commits to non-tracked repos
        external_commits = external_commits_to_tracked + external_commits_to_non_tracked
        
        # Total commits = internal commits + all external commits
        total_commits = internal_commits + external_commits
        
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
        
        # CRITICAL: Fill in missing days with zeros to ensure trend calculation covers full time period
        # Convert since/until to date objects for comparison
        since_date = since.date() if isinstance(since, datetime) else since
        until_date = until.date() if isinstance(until, datetime) else until
        
        # Generate all dates in the range (inclusive)
        current_date = since_date
        all_dates = []
        while current_date <= until_date:
            all_dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Fill in missing days with 0.0
        for date in all_dates:
            if date not in daily_weighted_scores:
                daily_weighted_scores[date] = 0.0
        
        # Sort by date and extract scores - ensure chronological order (oldest to newest)
        sorted_dates = sorted(daily_weighted_scores.keys())
        daily_scores = [daily_weighted_scores[date] for date in sorted_dates]
        
        # CRITICAL: Verify data is in correct chronological order
        # If last date < first date, dates are reversed (should never happen with sorted(), but double-check)
        if len(sorted_dates) > 1:
            if sorted_dates[0] > sorted_dates[-1]:
                logger.error(
                    f"CRITICAL: Dates are in reverse order! First date {sorted_dates[0]} > Last date {sorted_dates[-1]}. "
                    f"Reversing data for trend calculation."
                )
                sorted_dates = list(reversed(sorted_dates))
                daily_scores = list(reversed(daily_scores))
        
        # Additional validation: Check if data direction suggests reversal
        # If data shows clear upward trend (last > first) but we're about to calculate negative trend,
        # the data might be in wrong order despite date sorting
        if len(daily_scores) > 2:
            first_score = daily_scores[0]
            last_score = daily_scores[-1]
            score_change = last_score - first_score
            
            # Pre-calculate to check direction
            temp_trend = MetricsService._calculate_trendline_slope(daily_scores)
            temp_direction = "up" if temp_trend > 0 else "down" if temp_trend < 0 else "flat"
            data_direction = "up" if score_change > 0.1 else "down" if score_change < -0.1 else "flat"
            
            # If data clearly goes up but trend is negative (or vice versa), reverse data
            if data_direction == "up" and temp_direction == "down" and abs(temp_trend) > 0.01:
                logger.warning(
                    f"PRE-CALCULATION CHECK: Data shows upward (first={first_score:.2f}, last={last_score:.2f}, "
                    f"change={score_change:.2f}) but preliminary trend is {temp_trend:.4f}. "
                    f"Reversing data before final calculation."
                )
                daily_scores = list(reversed(daily_scores))
            elif data_direction == "down" and temp_direction == "up" and abs(temp_trend) > 0.01:
                logger.warning(
                    f"PRE-CALCULATION CHECK: Data shows downward (first={first_score:.2f}, last={last_score:.2f}, "
                    f"change={score_change:.2f}) but preliminary trend is {temp_trend:.4f}. "
                    f"Reversing data before final calculation."
                )
                daily_scores = list(reversed(daily_scores))
        
        # Log for debugging
        if len(daily_scores) > 0:
            first_score = daily_scores[0]
            last_score = daily_scores[-1]
            score_change = last_score - first_score
            logger.debug(
                f"Team summary trend calculation: {len(daily_scores)} days, "
                f"date range: {sorted_dates[0] if sorted_dates else 'N/A'} to {sorted_dates[-1] if sorted_dates else 'N/A'}, "
                f"first_score={first_score:.2f}, last_score={last_score:.2f}, change={score_change:.2f}, "
                f"scores: {daily_scores[:5]}... (showing first 5)"
            )
        else:
            logger.debug("Team summary trend calculation: No daily scores found")
        
        # Calculate trendline slope with validated data order
        # At this point, data should be in correct chronological order (oldest to newest)
        average_trend = MetricsService._calculate_trendline_slope(daily_scores)
        
        # Final validation: Double-check that trend direction matches data direction
        # This is a safety check in case pre-calculation check missed something
        if len(daily_scores) > 2:
            first_score = daily_scores[0]
            last_score = daily_scores[-1]
            score_change = last_score - first_score
            
            data_direction = "up" if score_change > 0.1 else "down" if score_change < -0.1 else "flat"
            trend_direction = "up" if average_trend > 0 else "down" if average_trend < 0 else "flat"
            
            # If there's still a mismatch after pre-calculation check, flip the sign
            # (This should rarely happen if pre-calculation check worked)
            if data_direction != trend_direction and data_direction != "flat" and abs(average_trend) > 0.01:
                logger.warning(
                    f"POST-CALCULATION VALIDATION: Data shows {data_direction}ward trend "
                    f"(first={first_score:.2f}, last={last_score:.2f}, change={score_change:.2f}), "
                    f"but calculated trend is {trend_direction}ward (slope={average_trend:.4f}). "
                    f"Flipping sign as final correction."
                )
                average_trend = -average_trend
                logger.info(f"Final corrected trend: {average_trend:.4f}")
        
        # Calculate percentages - they will naturally add up to 100% since total_commits = internal_commits + external_commits
        # Total commits now includes both tracked repo commits and external commits
        if total_commits > 0:
            internal_pct = (internal_commits / total_commits * 100)
            external_pct = (external_commits / total_commits * 100)
        else:
            internal_pct = 0
            external_pct = 0
        
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
        
        # CRITICAL: Fill in missing days with zeros to ensure trend calculation covers full time period
        # Convert since/until to date objects for comparison
        since_date = since.date() if isinstance(since, datetime) else since
        until_date = until.date() if isinstance(until, datetime) else until
        
        # Generate all dates in the range (inclusive)
        current_date = since_date
        all_dates = []
        while current_date <= until_date:
            all_dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Fill in missing days with 0.0
        for date in all_dates:
            if date not in daily_weighted_scores:
                daily_weighted_scores[date] = 0.0
        
        # Sort by date and extract scores - ensure chronological order (oldest to newest)
        sorted_dates = sorted(daily_weighted_scores.keys())
        daily_scores = [daily_weighted_scores[date] for date in sorted_dates]
        
        # CRITICAL: Verify data is in correct chronological order
        if len(sorted_dates) > 1:
            if sorted_dates[0] > sorted_dates[-1]:
                logger.error(
                    f"CRITICAL: Dates are in reverse order! First date {sorted_dates[0]} > Last date {sorted_dates[-1]}. "
                    f"Reversing data for trend calculation."
                )
                sorted_dates = list(reversed(sorted_dates))
                daily_scores = list(reversed(daily_scores))
        
        # Pre-calculation validation: Check if data direction suggests reversal
        if len(daily_scores) > 2:
            first_score = daily_scores[0]
            last_score = daily_scores[-1]
            score_change = last_score - first_score
            
            temp_trend = MetricsService._calculate_trendline_slope(daily_scores)
            temp_direction = "up" if temp_trend > 0 else "down" if temp_trend < 0 else "flat"
            data_direction = "up" if score_change > 0.1 else "down" if score_change < -0.1 else "flat"
            
            if data_direction == "up" and temp_direction == "down" and abs(temp_trend) > 0.01:
                logger.warning(
                    f"PRE-CALCULATION CHECK for repo {repo.full_name}: Data shows upward but preliminary trend is {temp_trend:.4f}. "
                    f"Reversing data before final calculation."
                )
                daily_scores = list(reversed(daily_scores))
            elif data_direction == "down" and temp_direction == "up" and abs(temp_trend) > 0.01:
                logger.warning(
                    f"PRE-CALCULATION CHECK for repo {repo.full_name}: Data shows downward but preliminary trend is {temp_trend:.4f}. "
                    f"Reversing data before final calculation."
                )
                daily_scores = list(reversed(daily_scores))
        
        # Calculate trendline slope with validated data order
        average_trend = MetricsService._calculate_trendline_slope(daily_scores)
        
        # Final validation: Double-check trend direction
        if len(daily_scores) > 2:
            first_score = daily_scores[0]
            last_score = daily_scores[-1]
            score_change = last_score - first_score
            
            data_direction = "up" if score_change > 0.1 else "down" if score_change < -0.1 else "flat"
            trend_direction = "up" if average_trend > 0 else "down" if average_trend < 0 else "flat"
            
            if data_direction != trend_direction and data_direction != "flat" and abs(average_trend) > 0.01:
                logger.warning(
                    f"POST-CALCULATION VALIDATION for repo {repo.full_name}: Data shows {data_direction}ward but trend is {trend_direction}ward. "
                    f"Flipping sign as final correction."
                )
                average_trend = -average_trend
        
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
            
            # Check if this user is explicitly marked as external contributor
            is_external_contributor = ExternalContributor.query.filter_by(
                github_login=contributor.login,
                is_active=True
            ).first() is not None
            
            # If explicitly marked as external contributor, always mark as external
            if is_external_contributor:
                user_stats[github_id]["is_internal"] = False
            else:
                # Otherwise, use normal internal/external logic
                is_internal = MetricsService._is_internal_contributor(contributor.login, repo_full_name, team_logins, internal_orgs_config)
                # Mark as internal if ANY of their work is internal
                if is_internal:
                    user_stats[github_id]["is_internal"] = True
            
            user_stats[github_id]["commits"] += stat.commits_count
            user_stats[github_id]["prs_opened"] += stat.prs_opened
            user_stats[github_id]["prs_merged"] += stat.prs_merged
            user_stats[github_id]["issues_closed"] += stat.issues_closed
            user_stats[github_id]["login"] = contributor.login
            user_stats[github_id]["name"] = contributor.name
            user_stats[github_id]["avatar_url"] = contributor.avatar_url
            
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
        
        # ----------------------------------------------------------------------------------
        # Include contributors that ONLY have external commits (ExternalCommit records)
        # ----------------------------------------------------------------------------------
        # This allows users like external collaborators (e.g. MiltonHeYan) whose commits
        # are stored in ExternalCommit but who don't appear in DailyStats/Contributor
        # to still show up in the dashboard contributors list and be selectable in the UI.
        external_commits = ExternalCommit.query.filter(
            ExternalCommit.commit_date >= since,
            ExternalCommit.commit_date <= until
        ).all()
        
        for ext_commit in external_commits:
            github_id = ext_commit.github_user_id
            login = ext_commit.github_user_login
            
            # Check if this user is explicitly marked as external contributor
            is_external_contributor = ExternalContributor.query.filter_by(
                github_login=login,
                is_active=True
            ).first() is not None
            
            # Increment commit count for this user
            user_stats[github_id]["commits"] += 1
            
            # ExternalCommit records are ALWAYS external (commits to non-tracked repos)
            # If user is explicitly marked as external contributor, ensure they're marked as external
            if is_external_contributor:
                user_stats[github_id]["is_internal"] = False
            # If user is a team member, they might have both internal and external commits
            # But ExternalCommit records themselves are always external, so don't mark as internal
            # Only mark as internal if they have internal commits from DailyStats
            # (which is already handled above in the DailyStats processing loop)
            
            # Preserve login if not already set from internal stats
            if not user_stats[github_id]["login"]:
                user_stats[github_id]["login"] = login
            
            # Add to daily scores for trend calculation (1 commit, no PRs/issues)
            date_key = ext_commit.commit_date.date() if hasattr(ext_commit.commit_date, "date") else ext_commit.commit_date
            daily_score = weights["commits"]  # Single commit with commit weight
            user_stats[github_id]["daily_scores"][date_key] += daily_score
        
        # Build result
        results = []
        
        # Fetch social links for all contributors (get from any contributor record with matching github_id)
        contributor_logins = [metrics["login"] for metrics in user_stats.values()]
        contributors_with_links = Contributor.query.filter(
            Contributor.github_id.in_(list(user_stats.keys()))
        ).all()
        
        # Create a map of github_id to social links (use first non-null value found)
        social_links_map = {}
        for contrib in contributors_with_links:
            if contrib.github_id not in social_links_map:
                social_links_map[contrib.github_id] = {
                    "linkedin_url": contrib.linkedin_url,
                    "twitter_url": contrib.twitter_url,
                    "website_url": contrib.website_url
                }
            else:
                # Update with non-null values
                existing = social_links_map[contrib.github_id]
                if not existing["linkedin_url"] and contrib.linkedin_url:
                    existing["linkedin_url"] = contrib.linkedin_url
                if not existing["twitter_url"] and contrib.twitter_url:
                    existing["twitter_url"] = contrib.twitter_url
                if not existing["website_url"] and contrib.website_url:
                    existing["website_url"] = contrib.website_url
        
        # CRITICAL: Prepare date range for filling missing days
        # Convert since/until to date objects for comparison
        since_date = since.date() if isinstance(since, datetime) else since
        until_date = until.date() if isinstance(until, datetime) else until
        
        # Generate all dates in the range (inclusive) - used for filling missing days
        current_date = since_date
        all_dates = []
        while current_date <= until_date:
            all_dates.append(current_date)
            current_date += timedelta(days=1)
        
        for github_id, metrics in user_stats.items():
            # Fill in missing days with zeros to ensure trend calculation covers full time period
            for date in all_dates:
                if date not in metrics["daily_scores"]:
                    metrics["daily_scores"][date] = 0.0
            
            # Calculate average trend using least squares regression
            sorted_dates = sorted(metrics["daily_scores"].keys())
            daily_scores = [metrics["daily_scores"][date] for date in sorted_dates]
            
            # CRITICAL: Verify data is in correct chronological order
            if len(sorted_dates) > 1:
                if sorted_dates[0] > sorted_dates[-1]:
                    logger.error(
                        f"CRITICAL: Dates are in reverse order for contributor {metrics['login']}! "
                        f"First date {sorted_dates[0]} > Last date {sorted_dates[-1]}. "
                        f"Reversing data for trend calculation."
                    )
                    sorted_dates = list(reversed(sorted_dates))
                    daily_scores = list(reversed(daily_scores))
            
            # Pre-calculation validation: Check if data direction suggests reversal
            if len(daily_scores) > 2:
                first_score = daily_scores[0]
                last_score = daily_scores[-1]
                score_change = last_score - first_score
                
                temp_trend = MetricsService._calculate_trendline_slope(daily_scores)
                temp_direction = "up" if temp_trend > 0 else "down" if temp_trend < 0 else "flat"
                data_direction = "up" if score_change > 0.1 else "down" if score_change < -0.1 else "flat"
                
                if data_direction == "up" and temp_direction == "down" and abs(temp_trend) > 0.01:
                    logger.warning(
                        f"PRE-CALCULATION CHECK for contributor {metrics['login']}: Data shows upward but preliminary trend is {temp_trend:.4f}. "
                        f"Reversing data before final calculation."
                    )
                    daily_scores = list(reversed(daily_scores))
                elif data_direction == "down" and temp_direction == "up" and abs(temp_trend) > 0.01:
                    logger.warning(
                        f"PRE-CALCULATION CHECK for contributor {metrics['login']}: Data shows downward but preliminary trend is {temp_trend:.4f}. "
                        f"Reversing data before final calculation."
                    )
                    daily_scores = list(reversed(daily_scores))
            
            # Calculate trendline slope with validated data order
            average_trend = MetricsService._calculate_trendline_slope(daily_scores)
            
            # Final validation: Double-check trend direction
            if len(daily_scores) > 2:
                first_score = daily_scores[0]
                last_score = daily_scores[-1]
                score_change = last_score - first_score
                
                data_direction = "up" if score_change > 0.1 else "down" if score_change < -0.1 else "flat"
                trend_direction = "up" if average_trend > 0 else "down" if average_trend < 0 else "flat"
                
                if data_direction != trend_direction and data_direction != "flat" and abs(average_trend) > 0.01:
                    logger.warning(
                        f"POST-CALCULATION VALIDATION for contributor {metrics['login']}: Data shows {data_direction}ward but trend is {trend_direction}ward. "
                        f"Flipping sign as final correction."
                    )
                    average_trend = -average_trend
            
            # Get social links for this contributor
            social_links = social_links_map.get(github_id, {
                "linkedin_url": None,
                "twitter_url": None,
                "website_url": None
            })
            
            # Final check: If user is explicitly marked as external contributor, ensure they're external
            login = metrics["login"]
            if login:
                is_external_contributor = ExternalContributor.query.filter_by(
                    github_login=login,
                    is_active=True
                ).first() is not None
                if is_external_contributor:
                    metrics["is_internal"] = False
            
            results.append({
                "login": metrics["login"],
                "name": metrics["name"],
                "avatar_url": metrics["avatar_url"],
                "is_internal": metrics["is_internal"],
                "commits": metrics["commits"],
                "prs_opened": metrics["prs_opened"],
                "prs_merged": metrics["prs_merged"],
                "issues_closed": metrics["issues_closed"],
                "average_trend": round(average_trend, 2),
                "linkedin_url": social_links["linkedin_url"],
                "twitter_url": social_links["twitter_url"],
                "website_url": social_links["website_url"]
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
        # If range_days is None, use 5 years ago as limit (to reduce query load)
        if range_days is None:
            since = until - timedelta(days=365 * 5)  # 5 years max
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
            
            # Check if this user is explicitly marked as external contributor
            is_external_contributor = ExternalContributor.query.filter_by(
                github_login=contributor.login,
                is_active=True
            ).first() is not None
            
            # If explicitly marked as external contributor, always mark as external
            if is_external_contributor:
                is_internal = False
            else:
                # Otherwise, use normal internal/external logic
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
        
        # Get external commits from ExternalCommit table (needed for both split and contributions)
        external_commits_query = ExternalCommit.query.filter(
            ExternalCommit.commit_date >= since,
            ExternalCommit.commit_date <= until
        )
        
        # If filtering by contributor, only show their external commits
        if contributor_login:
            external_commits_query = external_commits_query.filter_by(github_user_login=contributor_login)
        # When all contributors are selected, show external commits from all contributors
        # (sync_external_commits tracks for all contributors to tracked repos, not just team members)
        
        external_commits_list = external_commits_query.all()
        external_commits_count = len(external_commits_list)
        
        # Add external commits to daily_data by date
        # Note: ALL ExternalCommit records are external by definition (commits to non-tracked repos)
        for ext_commit in external_commits_list:
            # Format date as YYYY-MM-DD
            date_str = ext_commit.commit_date.strftime("%Y-%m-%d")
            daily_data[date_str]["total"] += 1
            # ExternalCommit records are ALWAYS external, regardless of user classification
            daily_data[date_str]["external"] += 1
        
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
        # Include external commits from tracked repos (by external contributors) 
        # AND external commits from ExternalCommit table (to non-tracked repos)
        # Note: external commits from ExternalCommit are now included in daily_commits
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
        
        # Build repository contribution list (internal repos only)
        repo_contributions = []
        
        for repo_name, counts in sorted(repo_breakdown.items()):
            if counts["internal"] > 0:
                repo_contributions.append({
                    "name": repo_name,
                    "value": counts["internal"],
                    "type": "internal"
                })
        
        # Group external commits by repository
        external_repo_breakdown = defaultdict(int)
        for ext_commit in external_commits_list:
            external_repo_breakdown[ext_commit.repo_full_name] += 1
        
        # Add external repos to contributions
        for repo_name, count in sorted(external_repo_breakdown.items(), key=lambda x: x[1], reverse=True):
            repo_contributions.append({
                "name": repo_name,
                "value": count,
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

        total_commits = summary.get("total_commits", 0) or 0
        total_prs_merged = summary.get("total_prs_merged", 0) or 0
        total_prs_opened = summary.get("total_prs_opened", 0) or 0
        total_issues_closed = summary.get("total_issues_closed", 0) or 0
        avg_trend = summary.get("average_trend", 0) or 0.0
        internal_pct = summary.get("internal_percentage", 0.0) or 0.0
        external_pct = summary.get("external_percentage", 0.0) or 0.0

        if avg_trend > 0.2:
            trend_label = "upward"
        elif avg_trend < -0.2:
            trend_label = "downward"
        else:
            trend_label = "flat"

        internal_flags = [f for f in flags if f.get("severity") in ("high", "medium")]
        high_flags = [f for f in flags if f.get("severity") == "high"]
        medium_flags = [f for f in flags if f.get("severity") == "medium"]

        # Find top contributors
        top_contributors = sorted(
            [c for c in contributors if c.get("is_internal", False)],
            key=lambda x: x.get("average_trend", 0.0) or 0.0,
            reverse=True
        )[:3]

        # Find top repos
        top_repos = sorted(
            repos,
            key=lambda r: (r.get("average_trend", 0.0) or 0.0),
            reverse=True
        )[:3]

        lines: List[str] = []
        lines.append(f"Weekly Engineering Summary ({range_days_label})")
        lines.append("")
        
        # Activity Summary
        lines.append("Activity Summary")
        lines.append("As shown in the Daily Commits chart above:")
        lines.append(f"• {total_commits} total commits")
        lines.append(f"• {total_prs_opened} pull requests opened")
        lines.append(f"• {total_prs_merged} pull requests merged")
        lines.append(f"• {total_issues_closed} issues closed")
        lines.append("")
        
        # Trend Analysis
        lines.append("Trend Analysis")
        lines.append("Based on the trend indicators in the dashboard:")
        lines.append(f"• Overall momentum: {trend_label} (score: {avg_trend:.2f})")
        if top_contributors:
            top_contrib = top_contributors[0]
            lines.append(f"• Top performer: {top_contrib['login']} (trend: {top_contrib.get('average_trend', 0.0) or 0.0:.2f})")
        lines.append("")
        
        # Contribution Mix
        lines.append("Contribution Mix")
        lines.append("As illustrated in the Contribution Split pie chart:")
        lines.append(f"• Internal: {internal_pct:.1f}%")
        lines.append(f"• External: {external_pct:.1f}%")
        lines.append("")
        
        # Repository Focus
        if top_repos:
            lines.append("Repository Focus")
            lines.append("Top repositories by activity (see Contribution Split chart):")
            for repo in top_repos[:2]:
                repo_trend = repo.get("average_trend", 0.0) or 0.0
                lines.append(f"• {repo['full_name']} (trend: {repo_trend:.2f})")
            lines.append("")
        
        # Risk Assessment
        lines.append("Risk Assessment")
        if internal_flags:
            lines.append(f"As highlighted in the Risk Flags section ({len(high_flags)} high, {len(medium_flags)} medium):")
            if high_flags:
                lines.append(f"• {high_flags[0].get('title', 'High priority issue detected')}")
            if medium_flags and not high_flags:
                lines.append(f"• {medium_flags[0].get('title', 'Medium priority issue detected')}")
        else:
            lines.append("• No high or medium risk flags detected this period")

        return "\n".join(lines)

