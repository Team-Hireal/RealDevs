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
    def get_dashboard_data(range_days: int = 7) -> Dict:
        """Get all dashboard data including metrics and risk flags."""
        until = datetime.now(timezone.utc)
        since = until - timedelta(days=range_days)
        
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
        
        # Compute team summary
        team_summary = MetricsService._compute_team_summary(repos, since, until, team_logins)
        
        # Compute per-repo summaries
        repo_summaries = [
            MetricsService._compute_repo_summary(repo, since, until, team_logins)
            for repo in repos
        ]
        
        # Compute risk flags
        risk_flags = MetricsService._compute_risk_flags(repos, since, until, team_logins)
        
        # Get contributor breakdown
        contributors = MetricsService._get_contributor_breakdown(repos, since, until, team_logins)
        
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
            "range_days": range_days
        }
    
    @staticmethod
    def _compute_team_summary(repos: List[Repository], since: datetime, until: datetime, team_logins: set) -> Dict:
        """Compute team-level summary metrics."""
        repo_ids = [r.id for r in repos]
        
        # Query aggregated stats
        stats = DailyStats.query.filter(
            DailyStats.repo_id.in_(repo_ids),
            DailyStats.date >= since,
            DailyStats.date <= until
        ).all()
        
        total_commits = 0
        total_prs_opened = 0
        total_prs_merged = 0
        total_issues_closed = 0
        
        internal_commits = 0
        external_commits = 0
        
        for stat in stats:
            contributor = Contributor.query.get(stat.contributor_id)
            is_internal = contributor.login in team_logins if contributor else False
            
            total_commits += stat.commits_count
            total_prs_opened += stat.prs_opened
            total_prs_merged += stat.prs_merged
            total_issues_closed += stat.issues_closed
            
            if is_internal:
                internal_commits += stat.commits_count
            else:
                external_commits += stat.commits_count
        
        # Calculate momentum score
        weights = MetricsService.get_weights()
        momentum_score = (
            total_commits * weights["commits"] +
            total_prs_opened * weights["prs_opened"] +
            total_prs_merged * weights["prs_merged"] +
            total_issues_closed * weights["issues_closed"]
        )
        
        # Calculate percentages
        internal_pct = (internal_commits / total_commits * 100) if total_commits > 0 else 0
        external_pct = (external_commits / total_commits * 100) if total_commits > 0 else 0
        
        return {
            "total_commits": total_commits,
            "total_prs_opened": total_prs_opened,
            "total_prs_merged": total_prs_merged,
            "total_issues_closed": total_issues_closed,
            "momentum_score": round(momentum_score, 2),
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
        
        weights = MetricsService.get_weights()
        momentum_score = (
            total_commits * weights["commits"] +
            total_prs_opened * weights["prs_opened"] +
            total_prs_merged * weights["prs_merged"] +
            total_issues_closed * weights["issues_closed"]
        )
        
        return {
            "repo_id": repo.id,
            "full_name": repo.full_name,
            "commits": total_commits,
            "prs_opened": total_prs_opened,
            "prs_merged": total_prs_merged,
            "issues_closed": total_issues_closed,
            "momentum_score": round(momentum_score, 2),
            "last_synced": repo.last_synced_at.isoformat() if repo.last_synced_at else None
        }
    
    @staticmethod
    def _get_contributor_breakdown(repos: List[Repository], since: datetime, until: datetime, team_logins: set) -> List[Dict]:
        """Get per-contributor stats."""
        repo_ids = [r.id for r in repos]
        
        # Group stats by contributor
        contributor_stats = defaultdict(lambda: {
            "commits": 0,
            "prs_opened": 0,
            "prs_merged": 0,
            "issues_closed": 0
        })
        
        stats = DailyStats.query.filter(
            DailyStats.repo_id.in_(repo_ids),
            DailyStats.date >= since,
            DailyStats.date <= until
        ).all()
        
        for stat in stats:
            contributor_stats[stat.contributor_id]["commits"] += stat.commits_count
            contributor_stats[stat.contributor_id]["prs_opened"] += stat.prs_opened
            contributor_stats[stat.contributor_id]["prs_merged"] += stat.prs_merged
            contributor_stats[stat.contributor_id]["issues_closed"] += stat.issues_closed
        
        # Build result
        weights = MetricsService.get_weights()
        results = []
        
        for contributor_id, metrics in contributor_stats.items():
            contributor = Contributor.query.get(contributor_id)
            if not contributor:
                continue
            
            is_internal = contributor.login in team_logins
            
            momentum_score = (
                metrics["commits"] * weights["commits"] +
                metrics["prs_opened"] * weights["prs_opened"] +
                metrics["prs_merged"] * weights["prs_merged"] +
                metrics["issues_closed"] * weights["issues_closed"]
            )
            
            results.append({
                "login": contributor.login,
                "name": contributor.name,
                "avatar_url": contributor.avatar_url,
                "is_internal": is_internal,
                "commits": metrics["commits"],
                "prs_opened": metrics["prs_opened"],
                "prs_merged": metrics["prs_merged"],
                "issues_closed": metrics["issues_closed"],
                "momentum_score": round(momentum_score, 2)
            })
        
        # Sort by momentum score
        results.sort(key=lambda x: x["momentum_score"], reverse=True)
        
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
        for repo in repos:
            stats = DailyStats.query.filter(
                DailyStats.repo_id == repo.id,
                DailyStats.date >= since
            ).all()
            
            if not stats or all(s.commits_count == 0 and s.prs_merged == 0 for s in stats):
                flags.append({
                    "type": "no_activity",
                    "severity": "high",
                    "title": f"No activity in {repo.full_name}",
                    "description": f"No commits or merged PRs in the last {(until - since).days} days",
                    "repo": repo.full_name
                })
        
        # Check for single point of failure (one person doing most work)
        for repo in repos:
            stats = DailyStats.query.filter(
                DailyStats.repo_id == repo.id,
                DailyStats.date >= since
            ).all()
            
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
                    recent_stats = DailyStats.query.filter(
                        DailyStats.repo_id == repo.id,
                        DailyStats.contributor_id == contrib.id,
                        DailyStats.date >= since
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
    def get_weekly_recap(range_days: int = 7) -> str:
        """Generate weekly recap text."""
        data = MetricsService.get_dashboard_data(range_days)
        
        summary = data["team_summary"]
        repos = data["repo_summaries"]
        flags = data["risk_flags"]
        contributors = data["contributors"]
        
        # Build text
        lines = []
        lines.append(f"📊 Weekly Recap ({range_days} days)")
        lines.append("=" * 50)
        lines.append("")
        
        # Team summary
        lines.append("🔹 Team Activity:")
        lines.append(f"  • {summary.get('total_commits', 0)} commits")
        lines.append(f"  • {summary.get('total_prs_merged', 0)} PRs merged")
        lines.append(f"  • {summary.get('total_prs_opened', 0)} PRs opened")
        lines.append(f"  • {summary.get('total_issues_closed', 0)} issues closed")
        lines.append(f"  • Momentum Score: {summary.get('momentum_score', 0)}")
        lines.append("")
        
        # Internal vs External
        lines.append("🔹 Contribution Split:")
        lines.append(f"  • Internal: {summary.get('internal_percentage', 0):.1f}%")
        lines.append(f"  • External: {summary.get('external_percentage', 0):.1f}%")
        lines.append("")
        
        # Top repos
        if repos:
            top_repos = sorted(repos, key=lambda r: r['momentum_score'], reverse=True)[:3]
            lines.append("🔹 Most Active Repos:")
            for repo in top_repos:
                lines.append(f"  • {repo['full_name']} (score: {repo['momentum_score']})")
            lines.append("")
        
        # Top contributors
        if contributors:
            top_contributors = [c for c in contributors if c['is_internal']][:5]
            if top_contributors:
                lines.append("🔹 Top Contributors:")
                for contrib in top_contributors:
                    lines.append(f"  • {contrib['login']} (score: {contrib['momentum_score']})")
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

