"""Service for syncing GitHub data."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from app.models import db, Repository, Contributor, DailyStats, TeamMember
from app.utils.github_client import GitHubClient
from app.services.auth_service import AuthService
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class SyncService:
    """Handles GitHub data synchronization."""
    
    @staticmethod
    def fetch_available_repos() -> List[Dict]:
        """Fetch all repos accessible to the user."""
        pat = AuthService.get_stored_pat()
        if not pat:
            raise ValueError("No PAT stored")
        
        with GitHubClient(pat) as client:
            repos = client.list_repos()
        
        return [
            {
                "id": repo['id'],
                "full_name": repo['full_name'],
                "owner": repo['owner']['login'],
                "name": repo['name'],
                "private": repo.get('private', False),
                "default_branch": repo.get('default_branch', 'main'),
                "updated_at": repo.get('updated_at')
            }
            for repo in repos
        ]
    
    @staticmethod
    def select_repos(repo_full_names: List[str]) -> Dict:
        """Mark repos as selected for syncing. Removes repos not in the list."""
        pat = AuthService.get_stored_pat()
        if not pat:
            raise ValueError("No PAT stored")
        
        with GitHubClient(pat) as client:
            all_repos = client.list_repos()
        
        # Create a lookup
        repo_map = {repo['full_name']: repo for repo in all_repos}
        
        # Get currently selected repos
        current_repos = Repository.query.all()
        current_full_names = {r.full_name for r in current_repos}
        
        # Convert new selection to a set for easier comparison
        new_full_names = set(repo_full_names)
        
        # Find repos to remove (in DB but not in new selection)
        repos_to_remove = current_full_names - new_full_names
        if repos_to_remove:
            repos_to_delete = Repository.query.filter(
                Repository.full_name.in_(repos_to_remove)
            ).all()
            for repo in repos_to_delete:
                db.session.delete(repo)
            logger.info(f"Removing {len(repos_to_delete)} repo(s) from selection")
        
        # Find repos to add (in new selection but not in DB)
        repos_to_add = new_full_names - current_full_names
        
        # Process repos to add
        selected = []
        for full_name in repo_full_names:
            if full_name not in repo_map:
                logger.warning(f"Repo not found: {full_name}")
                continue
            
            repo_data = repo_map[full_name]
            
            # Check if already exists
            existing = Repository.query.filter_by(github_id=repo_data['id']).first()
            if existing:
                selected.append(existing)
                continue
            
            # Create new
            repo = Repository(
                github_id=repo_data['id'],
                full_name=repo_data['full_name'],
                owner=repo_data['owner']['login'],
                name=repo_data['name'],
                private=repo_data.get('private', False),
                default_branch=repo_data.get('default_branch', 'main')
            )
            db.session.add(repo)
            selected.append(repo)
        
        db.session.commit()
        
        # Get final list of selected repos
        final_selected = Repository.query.all()
        
        return {
            "ok": True,
            "selected_count": len(final_selected),
            "repos": [{"id": r.id, "full_name": r.full_name} for r in final_selected]
        }
    
    @staticmethod
    def sync_repos(range_days: int = 7) -> Dict:
        """Sync data for all selected repos."""
        pat = AuthService.get_stored_pat()
        if not pat:
            raise ValueError("No PAT stored")
        
        repos = Repository.query.all()
        if not repos:
            logger.warning("Sync attempted but no repos selected")
            return {
                "ok": False, 
                "error": "No repos selected. Please select repositories first.",
                "stats": {
                    "repos_synced": 0,
                    "total_commits": 0,
                    "total_prs": 0
                }
            }
        
        until = datetime.now(timezone.utc)
        since = until - timedelta(days=range_days)
        
        synced_repos = []
        failed_repos = []
        total_commits = 0
        total_prs = 0
        total_issues = 0
        
        logger.info(f"Starting sync for {len(repos)} repo(s), range: {range_days} days")
        
        with GitHubClient(pat) as client:
            for repo in repos:
                try:
                    logger.info(f"Syncing {repo.full_name}...")
                    
                    # Fetch commits
                    commits = client.get_commits(repo.owner, repo.name, since=since, until=until)
                    logger.info(f"  Fetched {len(commits)} commits from {repo.full_name}")
                    total_commits += len(commits)
                    
                    # Fetch PRs
                    prs = client.get_pull_requests(repo.owner, repo.name, state="all")
                    # Filter by date
                    prs = [pr for pr in prs if pr.get('updated_at') and 
                           SyncService._parse_github_date(pr['updated_at']) >= since]
                    logger.info(f"  Fetched {len(prs)} PRs from {repo.full_name}")
                    total_prs += len(prs)
                    
                    # Fetch issues (optional)
                    issues = client.get_issues(repo.owner, repo.name, state="closed", since=since)
                    logger.info(f"  Fetched {len(issues)} issues from {repo.full_name}")
                    total_issues += len(issues)
                    
                    # Process data
                    SyncService._process_commits(repo, commits, since, until)
                    SyncService._process_prs(repo, prs, since, until)
                    SyncService._process_issues(repo, issues, since, until)
                    
                    # Update last synced
                    repo.last_synced_at = datetime.now(timezone.utc)
                    synced_repos.append(repo.full_name)
                    logger.info(f"  Successfully synced {repo.full_name}")
                
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error syncing {repo.full_name}: {error_msg}", exc_info=True)
                    failed_repos.append({
                        "repo": repo.full_name,
                        "error": error_msg
                    })
        
        db.session.commit()
        
        result = {
            "ok": len(failed_repos) == 0,
            "synced_repos": synced_repos,
            "failed_repos": failed_repos,
            "stats": {
                "repos_synced": len(synced_repos),
                "total_commits": total_commits,
                "total_prs": total_prs,
                "total_issues": total_issues
            }
        }
        
        logger.info(f"Sync completed: {len(synced_repos)} successful, {len(failed_repos)} failed")
        return result
    
    @staticmethod
    def _parse_github_date(date_str: str) -> datetime:
        """Parse GitHub ISO date string."""
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    
    @staticmethod
    def _process_commits(repo: Repository, commits: List[Dict], since: datetime, until: datetime):
        """Process commits and aggregate by contributor and day."""
        # Group by contributor and date
        commit_counts = defaultdict(lambda: defaultdict(int))
        
        skipped_no_author = 0
        skipped_no_id_login = 0
        processed_count = 0
        
        for commit in commits:
            if not commit.get('author'):
                skipped_no_author += 1
                logger.debug(f"Skipping commit {commit.get('sha', 'unknown')[:8]}: no author field")
                continue
            
            author = commit['author']
            if not author:
                skipped_no_author += 1
                logger.debug(f"Skipping commit {commit.get('sha', 'unknown')[:8]}: author is null")
                continue
            
            commit_date_str = commit['commit']['author']['date']
            commit_date = SyncService._parse_github_date(commit_date_str)
            
            # Filter commits by date range (GitHub API may return commits slightly outside range)
            if commit_date < since or commit_date > until:
                skipped_no_id_login += 1
                logger.debug(f"Skipping commit {commit.get('sha', 'unknown')[:8]}: outside date range ({commit_date.date()})")
                continue
            
            day = commit_date.date()
            
            github_id = author.get('id')
            login = author.get('login')
            
            if not github_id or not login:
                skipped_no_id_login += 1
                logger.debug(f"Skipping commit {commit.get('sha', 'unknown')[:8]}: missing github_id or login (id={github_id}, login={login})")
                continue
            
            processed_count += 1
            
            # Ensure contributor exists
            contributor = Contributor.query.filter_by(
                repo_id=repo.id,
                github_id=github_id
            ).first()
            
            if not contributor:
                contributor = Contributor(
                    github_id=github_id,
                    login=login,
                    name=commit['commit']['author']['name'],
                    avatar_url=author.get('avatar_url'),
                    repo_id=repo.id
                )
                db.session.add(contributor)
                db.session.flush()
            
            commit_counts[contributor.id][day] += 1
        
        logger.info(f"  Processed {processed_count} commits, skipped {skipped_no_author + skipped_no_id_login} (no author: {skipped_no_author}, no id/login: {skipped_no_id_login})")
        
        # Update or create daily stats
        for contributor_id, day_counts in commit_counts.items():
            for day, count in day_counts.items():
                day_datetime = datetime.combine(day, datetime.min.time()).replace(tzinfo=timezone.utc)
                
                stat = DailyStats.query.filter_by(
                    date=day_datetime,
                    repo_id=repo.id,
                    contributor_id=contributor_id
                ).first()
                
                if not stat:
                    stat = DailyStats(
                        date=day_datetime,
                        repo_id=repo.id,
                        contributor_id=contributor_id,
                        commits_count=count
                    )
                    db.session.add(stat)
                else:
                    stat.commits_count = count
    
    @staticmethod
    def _process_prs(repo: Repository, prs: List[Dict], since: datetime, until: datetime):
        """Process pull requests."""
        pr_opened = defaultdict(lambda: defaultdict(int))
        pr_merged = defaultdict(lambda: defaultdict(int))
        
        for pr in prs:
            if not pr.get('user'):
                continue
            
            user = pr['user']
            github_id = user.get('id')
            login = user.get('login')
            
            if not github_id or not login:
                continue
            
            # Ensure contributor exists
            contributor = Contributor.query.filter_by(
                repo_id=repo.id,
                github_id=github_id
            ).first()
            
            if not contributor:
                contributor = Contributor(
                    github_id=github_id,
                    login=login,
                    avatar_url=user.get('avatar_url'),
                    repo_id=repo.id
                )
                db.session.add(contributor)
                db.session.flush()
            
            # Count opened PRs
            if pr.get('created_at'):
                created_date = SyncService._parse_github_date(pr['created_at'])
                if since <= created_date <= until:
                    day = created_date.date()
                    pr_opened[contributor.id][day] += 1
            
            # Count merged PRs
            if pr.get('merged_at'):
                merged_date = SyncService._parse_github_date(pr['merged_at'])
                if since <= merged_date <= until:
                    day = merged_date.date()
                    pr_merged[contributor.id][day] += 1
        
        # Update daily stats
        for contributor_id, day_counts in pr_opened.items():
            for day, count in day_counts.items():
                day_datetime = datetime.combine(day, datetime.min.time()).replace(tzinfo=timezone.utc)
                
                stat = DailyStats.query.filter_by(
                    date=day_datetime,
                    repo_id=repo.id,
                    contributor_id=contributor_id
                ).first()
                
                if not stat:
                    stat = DailyStats(
                        date=day_datetime,
                        repo_id=repo.id,
                        contributor_id=contributor_id,
                        prs_opened=count
                    )
                    db.session.add(stat)
                else:
                    stat.prs_opened = count
        
        for contributor_id, day_counts in pr_merged.items():
            for day, count in day_counts.items():
                day_datetime = datetime.combine(day, datetime.min.time()).replace(tzinfo=timezone.utc)
                
                stat = DailyStats.query.filter_by(
                    date=day_datetime,
                    repo_id=repo.id,
                    contributor_id=contributor_id
                ).first()
                
                if stat:
                    stat.prs_merged = count
                else:
                    stat = DailyStats(
                        date=day_datetime,
                        repo_id=repo.id,
                        contributor_id=contributor_id,
                        prs_merged=count
                    )
                    db.session.add(stat)
    
    @staticmethod
    def _process_issues(repo: Repository, issues: List[Dict], since: datetime, until: datetime):
        """Process closed issues."""
        issues_closed = defaultdict(lambda: defaultdict(int))
        
        for issue in issues:
            if not issue.get('user') or not issue.get('closed_at'):
                continue
            
            user = issue['user']
            github_id = user.get('id')
            login = user.get('login')
            
            if not github_id or not login:
                continue
            
            closed_date = SyncService._parse_github_date(issue['closed_at'])
            if not (since <= closed_date <= until):
                continue
            
            # Ensure contributor exists
            contributor = Contributor.query.filter_by(
                repo_id=repo.id,
                github_id=github_id
            ).first()
            
            if not contributor:
                contributor = Contributor(
                    github_id=github_id,
                    login=login,
                    avatar_url=user.get('avatar_url'),
                    repo_id=repo.id
                )
                db.session.add(contributor)
                db.session.flush()
            
            day = closed_date.date()
            issues_closed[contributor.id][day] += 1
        
        # Update daily stats
        for contributor_id, day_counts in issues_closed.items():
            for day, count in day_counts.items():
                day_datetime = datetime.combine(day, datetime.min.time()).replace(tzinfo=timezone.utc)
                
                stat = DailyStats.query.filter_by(
                    date=day_datetime,
                    repo_id=repo.id,
                    contributor_id=contributor_id
                ).first()
                
                if stat:
                    stat.issues_closed = count
                else:
                    stat = DailyStats(
                        date=day_datetime,
                        repo_id=repo.id,
                        contributor_id=contributor_id,
                        issues_closed=count
                    )
                    db.session.add(stat)

