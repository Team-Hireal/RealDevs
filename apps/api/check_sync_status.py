#!/usr/bin/env python3
"""Diagnostic script to check sync status and test GitHub connectivity."""
import sys
from app import create_app
from app.models import db, Repository, Contributor, DailyStats, AuthToken, TeamMember
from app.services.auth_service import AuthService
from app.services.sync_service import SyncService
from app.utils.github_client import GitHubClient

def main():
    app = create_app()
    with app.app_context():
        print("=" * 60)
        print("RealDevs Sync Status Diagnostic")
        print("=" * 60)
        print()
        
        # Check PAT
        auth = AuthToken.query.first()
        if not auth:
            print("❌ PAT not configured")
            print("   → Please configure your PAT first via the credentials page")
            return 1
        else:
            print(f"✅ PAT configured for user: {auth.github_user_login}")
        
        # Check repos
        repos = Repository.query.all()
        print(f"\n📦 Repositories selected: {len(repos)}")
        if repos:
            for r in repos:
                synced = "✅" if r.last_synced_at else "⏳"
                print(f"   {synced} {r.full_name}")
                if r.last_synced_at:
                    print(f"      Last synced: {r.last_synced_at}")
        else:
            print("   ⚠️  No repositories selected!")
            print("   → You need to select repositories before syncing")
            print()
            print("   To select repos, you can:")
            print("   1. Use the API: POST /api/repos/select with repo_full_names")
            print("   2. Or use this script with --select-repos flag")
        
        # Check data
        contributors = Contributor.query.all()
        stats = DailyStats.query.all()
        print(f"\n📊 Data in database:")
        print(f"   Contributors: {len(contributors)}")
        print(f"   Daily stats records: {len(stats)}")
        
        # Test GitHub connectivity
        print(f"\n🔗 Testing GitHub connectivity...")
        try:
            pat = AuthService.get_stored_pat()
            if pat:
                with GitHubClient(pat) as client:
                    user_info = client.validate_token()
                    print(f"   ✅ Connected as: {user_info.get('login')}")
                    
                    # Try to list repos
                    available_repos = SyncService.fetch_available_repos()
                    print(f"   ✅ Can access {len(available_repos)} repositories")
                    if available_repos:
                        print(f"   Sample repos:")
                        for repo in available_repos[:5]:
                            print(f"      - {repo['full_name']}")
        except Exception as e:
            print(f"   ❌ Error connecting to GitHub: {e}")
            return 1
        
        # Summary
        print(f"\n{'=' * 60}")
        if repos:
            print("✅ Ready to sync! Run sync from the dashboard or API.")
        else:
            print("⚠️  Not ready: Select repositories first")
        print("=" * 60)
        
        return 0 if repos else 1

if __name__ == "__main__":
    sys.exit(main())

