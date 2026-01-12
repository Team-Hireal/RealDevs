#!/usr/bin/env python3
"""Test script to verify external commits functionality."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.models import db, TeamMember, ExternalCommit, Repository
from app.services.sync_service import SyncService

def test_external_commits():
    """Test external commits functionality."""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("EXTERNAL COMMITS VERIFICATION")
        print("=" * 60)
        print()
        
        # 1. Check database structure
        print("1. Checking database structure...")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'external_commits' in tables:
            print("   ✅ external_commits table exists")
            columns = [col['name'] for col in inspector.get_columns('external_commits')]
            print(f"   Columns: {', '.join(columns)}")
        else:
            print("   ❌ external_commits table NOT found")
            print("   Run: python migrate_add_external_commits.py")
            return
        print()
        
        # 2. Check team members
        print("2. Checking team members configuration...")
        team_members = TeamMember.query.filter_by(is_active=True).all()
        if team_members:
            print(f"   ✅ {len(team_members)} team member(s) configured:")
            for tm in team_members:
                print(f"      - {tm.github_login}")
        else:
            print("   ⚠️  No team members configured")
            print("   External commits require team members to be configured")
            print("   Add via: POST /api/team-members")
        print()
        
        # 3. Check tracked repos
        print("3. Checking tracked repositories...")
        repos = Repository.query.all()
        if repos:
            print(f"   ✅ {len(repos)} repository(ies) tracked:")
            for repo in repos[:5]:  # Show first 5
                print(f"      - {repo.full_name}")
            if len(repos) > 5:
                print(f"      ... and {len(repos) - 5} more")
        else:
            print("   ⚠️  No repositories tracked")
        print()
        
        # 4. Check external commits
        print("4. Checking external commits data...")
        external_commits = ExternalCommit.query.all()
        if external_commits:
            print(f"   ✅ {len(external_commits)} external commit(s) stored")
            
            # Group by repo
            from collections import defaultdict
            by_repo = defaultdict(int)
            by_user = defaultdict(int)
            
            for ec in external_commits:
                by_repo[ec.repo_full_name] += 1
                by_user[ec.github_user_login] += 1
            
            print(f"   External repos: {len(by_repo)}")
            print(f"   Top external repos:")
            for repo, count in sorted(by_repo.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"      - {repo}: {count} commits")
            
            print(f"   Contributors:")
            for user, count in sorted(by_user.items(), key=lambda x: x[1], reverse=True):
                print(f"      - {user}: {count} commits")
        else:
            print("   ⚠️  No external commits found")
            print("   Run: POST /api/sync to fetch external commits")
        print()
        
        # 5. Test sync function availability
        print("5. Checking sync function...")
        try:
            if hasattr(SyncService, 'sync_external_commits'):
                print("   ✅ sync_external_commits function available")
            else:
                print("   ❌ sync_external_commits function NOT found")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        print()
        
        # 6. Summary and recommendations
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        issues = []
        if 'external_commits' not in tables:
            issues.append("Database table missing - run migration")
        if not team_members:
            issues.append("No team members configured")
        if not external_commits and team_members:
            issues.append("No external commits synced - run sync")
        
        if issues:
            print("⚠️  ISSUES FOUND:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
            print()
            print("RECOMMENDED ACTIONS:")
            if not team_members:
                print("   1. Configure team members:")
                print("      curl -X POST http://localhost:8000/api/team-members \\")
                print("        -H 'Content-Type: application/json' \\")
                print("        -d '{\"github_logins\": [\"username1\", \"username2\"]}'")
            if not external_commits and team_members:
                print("   2. Run sync to fetch external commits:")
                print("      curl -X POST http://localhost:8000/api/sync \\")
                print("        -H 'Content-Type: application/json' \\")
                print("        -d '{\"range_days\": 30}'")
        else:
            print("✅ Everything looks good!")
            print("   External commits feature is fully operational")
        
        print()
        print("For more information, see: docs/EXTERNAL_COMMITS.md")
        print("=" * 60)

if __name__ == '__main__':
    try:
        test_external_commits()
    except Exception as e:
        print(f"\n❌ Error running test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

