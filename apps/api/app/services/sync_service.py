"""Service for syncing GitHub data."""
# https://github.com/SimonSaysGiveMeSmile
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from app.models import db, Repository, Contributor, DailyStats, TeamMember, ExternalCommit
from app.utils.github_client import GitHubClient
from app.services.auth_service import AuthService
from collections import defaultdict
import logging
import re

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
                    SyncService._process_commits(repo, commits, since, until, client)
                    SyncService._process_prs(repo, prs, since, until, client)
                    SyncService._process_issues(repo, issues, since, until, client)
                    
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
    def _extract_social_links(user_data: Dict) -> Dict[str, Optional[str]]:
        """Extract social links from GitHub user profile data.
        
        Returns dict with linkedin_url, twitter_url, website_url.
        """
        links = {
            'linkedin_url': None,
            'twitter_url': None,
            'website_url': None
        }
        
        # Extract website/blog URL
        blog = user_data.get('blog')
        if blog:
            # Normalize URL (add https:// if missing)
            if not blog.startswith(('http://', 'https://')):
                blog = f'https://{blog}'
            links['website_url'] = blog
        
        # Extract Twitter handle
        twitter_username = user_data.get('twitter_username')
        if twitter_username:
            # Remove @ if present and construct URL
            username = twitter_username.lstrip('@')
            links['twitter_url'] = f'https://twitter.com/{username}'
        
        # Extract LinkedIn from bio or blog
        bio = user_data.get('bio', '')
        blog_url = user_data.get('blog', '')
        
        # Check bio for LinkedIn patterns
        linkedin_patterns = [
            r'linkedin\.com/in/([a-zA-Z0-9\-]+)',
            r'in/([a-zA-Z0-9\-]+)',  # Short form like "in/simon-tian-1333a3156"
        ]
        
        for pattern in linkedin_patterns:
            match = re.search(pattern, bio, re.IGNORECASE)
            if match:
                linkedin_id = match.group(1)
                links['linkedin_url'] = f'https://www.linkedin.com/in/{linkedin_id}'
                break
        
        # Also check blog URL for LinkedIn
        if not links['linkedin_url']:
            for pattern in linkedin_patterns:
                match = re.search(pattern, blog_url, re.IGNORECASE)
                if match:
                    linkedin_id = match.group(1)
                    links['linkedin_url'] = f'https://www.linkedin.com/in/{linkedin_id}'
                    break
        
        return links
    
    @staticmethod
    def _update_contributor_profile(contributor: Contributor, client: GitHubClient):
        """Fetch and update contributor profile with social links."""
        try:
            user_data = client.get_user(contributor.login)
            if not user_data:
                return
            
            # Extract social links
            links = SyncService._extract_social_links(user_data)
            
            # Update contributor with profile data
            if user_data.get('name') and not contributor.name:
                contributor.name = user_data.get('name')
            if user_data.get('avatar_url') and not contributor.avatar_url:
                contributor.avatar_url = user_data.get('avatar_url')
            
            # Update social links (only if not already set, to avoid overwriting manual updates)
            if links['linkedin_url'] and not contributor.linkedin_url:
                contributor.linkedin_url = links['linkedin_url']
            if links['twitter_url'] and not contributor.twitter_url:
                contributor.twitter_url = links['twitter_url']
            if links['website_url'] and not contributor.website_url:
                contributor.website_url = links['website_url']
            
        except Exception as e:
            logger.debug(f"Error updating profile for {contributor.login}: {e}")
    
    @staticmethod
    def _process_commits(repo: Repository, commits: List[Dict], since: datetime, until: datetime, client: GitHubClient):
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
                # Fetch user profile data for new contributors
                SyncService._update_contributor_profile(contributor, client)
            
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
    def _process_prs(repo: Repository, prs: List[Dict], since: datetime, until: datetime, client: GitHubClient):
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
                # Fetch user profile data for new contributors
                SyncService._update_contributor_profile(contributor, client)
            
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
    def _process_issues(repo: Repository, issues: List[Dict], since: datetime, until: datetime, client: GitHubClient):
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
                # Fetch user profile data for new contributors
                SyncService._update_contributor_profile(contributor, client)
            
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
    
    @staticmethod
    def sync_external_commits(range_days: int = 7) -> Dict:
        """Sync external commits (commits by contributors to non-tracked repos).
        
        This function tracks ALL contributors to tracked repositories and fetches
        their complete contribution history across GitHub, filtering out commits
        to tracked repos to show only external work.
        """
        pat = AuthService.get_stored_pat()
        if not pat:
            raise ValueError("No PAT stored")
        
        # Get ALL unique contributors from tracked repositories
        # This automatically includes everyone who has contributed to your projects
        contributors = db.session.query(Contributor.github_id, Contributor.login).distinct().all()
        
        if not contributors:
            logger.info("No contributors found in tracked repositories")
            return {
                "ok": True,
                "message": "No contributors found - sync repositories first",
                "external_commits_synced": 0
            }
        
        # Also include manually configured team members if any
        team_members = TeamMember.query.filter_by(is_active=True).all()
        team_member_logins = {tm.github_login for tm in team_members}
        
        # Combine: all contributors + team members
        all_users = {}
        for github_id, login in contributors:
            all_users[login] = github_id
        for tm in team_members:
            if tm.github_login not in all_users:
                all_users[tm.github_login] = None  # We'll get github_id from events
        
        logger.info(f"Tracking {len(all_users)} user(s): {len(contributors)} from repos + {len(team_member_logins)} configured team members")
        
        # Get tracked repository full names
        tracked_repos = Repository.query.all()
        tracked_repo_names = {repo.full_name for repo in tracked_repos}
        
        until = datetime.now(timezone.utc)
        since = until - timedelta(days=range_days)
        
        total_external_commits = 0
        synced_members = []
        failed_members = []
        
        logger.info(f"Starting external commit sync for {len(all_users)} contributor(s)")
        
        with GitHubClient(pat) as client:
            for login, github_id in all_users.items():
                try:
                    logger.info(f"Fetching external commits for {login}...")
                    
                    # Method 1: Use GitHub Events API (recent activity, up to 300 events)
                    events = client.get_user_events(login, per_page=100)
                    
                    # Method 2: Use GitHub Search API for comprehensive history
                    # This searches ALL commits by the user across GitHub
                    try:
                        search_results = client.search_commits(login, since=since, until=until)
                        logger.info(f"  Found {len(search_results)} commits via search for {login}")
                    except Exception as e:
                        logger.warning(f"  Search API failed for {login}: {e}")
                        search_results = []
                    
                    commits_processed = 0
                    
                    # Process events first
                    for event in events:
                        # Only process PushEvents (commits)
                        if event.get('type') != 'PushEvent':
                            continue
                        
                        # Check event date
                        created_at_str = event.get('created_at')
                        if not created_at_str:
                            continue
                        
                        event_date = SyncService._parse_github_date(created_at_str)
                        if event_date < since or event_date > until:
                            continue
                        
                        # Get repository info
                        repo_info = event.get('repo', {})
                        repo_full_name = repo_info.get('name')
                        
                        if not repo_full_name:
                            continue
                        
                        # Skip if this is a tracked repo
                        if repo_full_name in tracked_repo_names:
                            continue
                        
                        # Extract repo owner
                        repo_owner = repo_full_name.split('/')[0] if '/' in repo_full_name else ''
                        
                        # Process commits in the push event
                        payload = event.get('payload', {})
                        commits = payload.get('commits', [])
                        
                        for commit_data in commits:
                            commit_sha = commit_data.get('sha')
                            if not commit_sha:
                                continue
                            
                            # Check if we already have this commit
                            existing = ExternalCommit.query.filter_by(commit_sha=commit_sha).first()
                            if existing:
                                continue
                            
                            # Get github_user_id from the actor or use cached value
                            actor = event.get('actor', {})
                            user_github_id = actor.get('id') or github_id
                            
                            if not user_github_id:
                                continue
                            
                            # Create external commit record
                            external_commit = ExternalCommit(
                                github_user_login=login,
                                github_user_id=user_github_id,
                                repo_full_name=repo_full_name,
                                repo_owner=repo_owner,
                                commit_sha=commit_sha,
                                commit_date=event_date,
                                commit_message=commit_data.get('message', '')[:500]  # Truncate long messages
                            )
                            db.session.add(external_commit)
                            commits_processed += 1
                            total_external_commits += 1
                    
                    # Process search results for more comprehensive coverage
                    for commit_result in search_results:
                        try:
                            # Extract commit info from search result
                            commit_sha = commit_result.get('sha')
                            if not commit_sha:
                                continue
                            
                            # Check if we already have this commit
                            existing = ExternalCommit.query.filter_by(commit_sha=commit_sha).first()
                            if existing:
                                continue
                            
                            # Get repository info
                            repo_info = commit_result.get('repository', {})
                            repo_full_name = repo_info.get('full_name')
                            
                            if not repo_full_name or repo_full_name in tracked_repo_names:
                                continue
                            
                            # Extract repo owner
                            repo_owner = repo_full_name.split('/')[0] if '/' in repo_full_name else ''
                            
                            # Get commit date
                            commit_info = commit_result.get('commit', {})
                            author_info = commit_info.get('author', {})
                            commit_date_str = author_info.get('date')
                            
                            if not commit_date_str:
                                continue
                            
                            commit_date = SyncService._parse_github_date(commit_date_str)
                            
                            # Verify date is in range
                            if commit_date < since or commit_date > until:
                                continue
                            
                            # Get github_user_id - use cached or from commit author
                            author = commit_result.get('author', {})
                            user_github_id = author.get('id') or github_id
                            
                            if not user_github_id:
                                continue
                            
                            # Create external commit record
                            external_commit = ExternalCommit(
                                github_user_login=login,
                                github_user_id=user_github_id,
                                repo_full_name=repo_full_name,
                                repo_owner=repo_owner,
                                commit_sha=commit_sha,
                                commit_date=commit_date,
                                commit_message=commit_info.get('message', '')[:500]
                            )
                            db.session.add(external_commit)
                            commits_processed += 1
                            total_external_commits += 1
                            
                        except Exception as e:
                            logger.debug(f"Error processing search result for {login}: {e}")
                            continue
                    
                    synced_members.append(login)
                    logger.info(f"  Found {commits_processed} external commits for {login}")
                    
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error syncing external commits for {login}: {error_msg}", exc_info=True)
                    failed_members.append({
                        "member": login,
                        "error": error_msg
                    })
        
        db.session.commit()
        
        logger.info(f"External commit sync completed: {len(synced_members)} successful, {len(failed_members)} failed, {total_external_commits} commits")
        
        return {
            "ok": len(failed_members) == 0,
            "synced_members": synced_members,
            "failed_members": failed_members,
            "external_commits_synced": total_external_commits
        }

