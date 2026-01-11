"""GitHub API client with pagination and rate limit handling."""
import httpx
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class GitHubClient:
    """Client for GitHub REST API."""
    
    def __init__(self, pat: str, base_url: str = "https://api.github.com"):
        """Initialize with Personal Access Token."""
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {pat}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.client = httpx.Client(headers=self.headers, timeout=30.0)
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.client.close()
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def _get_paginated(self, url: str, params: Optional[Dict] = None, max_pages: int = 10) -> List[Dict]:
        """Fetch all pages of a paginated endpoint."""
        all_results = []
        current_url = url
        page_count = 0
        
        if params is None:
            params = {}
        
        params.setdefault('per_page', 100)
        
        while current_url and page_count < max_pages:
            try:
                response = self.client.get(current_url, params=params if page_count == 0 else None)
                response.raise_for_status()
                
                data = response.json()
                if isinstance(data, list):
                    all_results.extend(data)
                else:
                    all_results.append(data)
                
                # Check rate limit
                remaining = int(response.headers.get('X-RateLimit-Remaining', 999))
                if remaining < 10:
                    logger.warning(f"GitHub rate limit low: {remaining} requests remaining")
                
                # Get next page URL from Link header
                link_header = response.headers.get('Link', '')
                next_url = None
                for link in link_header.split(','):
                    if 'rel="next"' in link:
                        next_url = link[link.index('<')+1:link.index('>')]
                        break
                
                current_url = next_url
                page_count += 1
                params = None  # Clear params for subsequent pages
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching {current_url}: {e}")
                break
            except Exception as e:
                logger.error(f"Error fetching {current_url}: {e}")
                break
        
        return all_results
    
    def validate_token(self) -> Dict[str, Any]:
        """Validate PAT and get user info."""
        response = self.client.get(f"{self.base_url}/user")
        response.raise_for_status()
        return response.json()
    
    def list_repos(self, visibility: str = "all", affiliation: str = "owner,collaborator,organization_member") -> List[Dict]:
        """List repositories accessible to the user."""
        params = {
            "visibility": visibility,
            "affiliation": affiliation,
            "sort": "updated",
            "per_page": 100
        }
        return self._get_paginated(f"{self.base_url}/user/repos", params, max_pages=20)
    
    def get_commits(self, owner: str, repo: str, since: Optional[datetime] = None, until: Optional[datetime] = None) -> List[Dict]:
        """Get commits for a repository in a date range."""
        params = {}
        if since:
            params['since'] = since.isoformat()
        if until:
            params['until'] = until.isoformat()
        
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        return self._get_paginated(url, params, max_pages=50)
    
    def get_pull_requests(self, owner: str, repo: str, state: str = "all") -> List[Dict]:
        """Get pull requests for a repository."""
        params = {
            "state": state,
            "sort": "updated",
            "direction": "desc",
            "per_page": 100
        }
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        return self._get_paginated(url, params, max_pages=20)
    
    def get_issues(self, owner: str, repo: str, state: str = "closed", since: Optional[datetime] = None) -> List[Dict]:
        """Get issues for a repository (excludes PRs)."""
        params = {
            "state": state,
            "sort": "updated",
            "direction": "desc",
            "per_page": 100
        }
        if since:
            params['since'] = since.isoformat()
        
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        all_issues = self._get_paginated(url, params, max_pages=20)
        
        # Filter out pull requests (issues with pull_request field)
        return [issue for issue in all_issues if 'pull_request' not in issue]
    
    def get_contributors(self, owner: str, repo: str) -> List[Dict]:
        """Get contributors for a repository."""
        url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
        return self._get_paginated(url, max_pages=10)
    
    def get_rate_limit(self) -> Dict:
        """Get current rate limit status."""
        response = self.client.get(f"{self.base_url}/rate_limit")
        response.raise_for_status()
        return response.json()

