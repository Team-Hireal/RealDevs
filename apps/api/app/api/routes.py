"""API routes."""
from flask import jsonify, request
from app.api import api_bp
from app.api.schemas import (
    PatSubmission, RepoSelection, SyncRequest, TeamMemberUpdate, SettingsUpdate,
    InternalOrgsUpdate
)
from app.services.auth_service import AuthService
from app.services.sync_service import SyncService
from app.services.metrics_service import MetricsService
from app.models import db, TeamMember, Settings
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


def validate_request(schema_class):
    """Decorator to validate request JSON with Pydantic."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                data = request.get_json()
                validated = schema_class(**data)
                return func(validated, *args, **kwargs)
            except ValidationError as e:
                return jsonify({"ok": False, "error": str(e)}), 400
            except Exception as e:
                logger.error(f"Validation error: {e}")
                return jsonify({"ok": False, "error": "Invalid request data"}), 400
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator


@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "RealDevs API"
    })


@api_bp.route('/auth/pat', methods=['POST'])
@validate_request(PatSubmission)
def submit_pat(data: PatSubmission):
    """Validate and store GitHub PAT."""
    try:
        result = AuthService.validate_and_store_pat(data.pat, data.store_mode)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in submit_pat: {e}")
        return jsonify({"ok": False, "error": str(e)}), 400


@api_bp.route('/auth/status', methods=['GET'])
def auth_status():
    """Check if PAT is configured."""
    user_info = AuthService.get_user_info()
    if user_info:
        return jsonify({
            "ok": True,
            "configured": True,
            "user": user_info
        })
    return jsonify({
        "ok": True,
        "configured": False
    })


@api_bp.route('/repos', methods=['GET'])
def list_repos():
    """List all repos accessible to the user."""
    try:
        repos = SyncService.fetch_available_repos()
        return jsonify({"repos": repos})
    except Exception as e:
        logger.error(f"Error listing repos: {e}")
        return jsonify({"ok": False, "error": str(e)}), 400


@api_bp.route('/repos/select', methods=['POST'])
@validate_request(RepoSelection)
def select_repos(data: RepoSelection):
    """Select repos for syncing."""
    try:
        result = SyncService.select_repos(data.repo_full_names)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error selecting repos: {e}")
        return jsonify({"ok": False, "error": str(e)}), 400


@api_bp.route('/repos/selected', methods=['GET'])
def get_selected_repos():
    """Get currently selected repos."""
    from app.models import Repository
    repos = Repository.query.all()
    return jsonify({
        "repos": [
            {
                "id": r.id,
                "full_name": r.full_name,
                "owner": r.owner,
                "name": r.name,
                "private": r.private,
                "last_synced_at": r.last_synced_at.isoformat() if r.last_synced_at else None
            }
            for r in repos
        ]
    })


@api_bp.route('/sync', methods=['POST'])
def sync_repos():
    """Sync selected repos."""
    try:
        data = request.get_json() or {}
        range_days_param = data.get('range_days', 7)
        # Handle "all" for all-time sync (use a large number like 3650 days ~10 years)
        if range_days_param == 'all':
            range_days = 3650  # ~10 years, effectively all time
        else:
            range_days = int(range_days_param)
        
        result = SyncService.sync_repos(range_days=range_days)
        # Return 200 even if some repos failed, but include error info
        status_code = 200 if result.get("ok") or result.get("synced_repos") else 400
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error syncing repos: {e}", exc_info=True)
        return jsonify({"ok": False, "error": str(e)}), 500


@api_bp.route('/diagnostics', methods=['GET'])
def diagnostics():
    """Get diagnostic information about the current state."""
    from app.models import Repository, Contributor, DailyStats, AuthToken, TeamMember
    
    repos = Repository.query.all()
    contributors = Contributor.query.all()
    stats = DailyStats.query.all()
    auth = AuthToken.query.first()
    team_members = TeamMember.query.filter_by(is_active=True).all()
    
    # Get recent stats
    from datetime import datetime, timedelta, timezone
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_stats = DailyStats.query.filter(DailyStats.date >= week_ago).all()
    
    return jsonify({
        "pat_configured": auth is not None,
        "github_user": auth.github_user_login if auth else None,
        "repos_selected": len(repos),
        "repos": [
            {
                "full_name": r.full_name,
                "last_synced": r.last_synced_at.isoformat() if r.last_synced_at else None
            }
            for r in repos
        ],
        "contributors_count": len(contributors),
        "daily_stats_count": len(stats),
        "recent_stats_count": len(recent_stats),
        "team_members_count": len(team_members),
        "ready_to_sync": len(repos) > 0 and auth is not None
    })


@api_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """Get dashboard data."""
    try:
        range_days_param = request.args.get('range_days', default='7')
        # Handle "all" for all-time data
        if range_days_param == 'all':
            range_days = None
        else:
            range_days = int(range_days_param)
        data = MetricsService.get_dashboard_data(range_days)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@api_bp.route('/dashboard/daily-commits', methods=['GET'])
def daily_commits():
    """Get daily commit data for charts."""
    try:
        range_days_param = request.args.get('range_days', default='7')
        contributor_login = request.args.get('contributor_login', default=None)
        # Handle "all" for all-time data
        if range_days_param == 'all':
            range_days = None
        else:
            range_days = int(range_days_param)
        data = MetricsService.get_daily_commits(range_days, contributor_login)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting daily commits: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@api_bp.route('/report/weekly', methods=['GET'])
def weekly_report():
    """Get weekly recap text."""
    try:
        range_days_param = request.args.get('range_days', default='7')
        # Handle "all" for all-time data
        if range_days_param == 'all':
            range_days = None
        else:
            range_days = int(range_days_param)
        text = MetricsService.get_weekly_recap(range_days)
        return jsonify({"text": text})
    except Exception as e:
        logger.error(f"Error generating recap: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@api_bp.route('/team-members', methods=['GET'])
def get_team_members():
    """Get configured team members."""
    members = TeamMember.query.filter_by(is_active=True).all()
    return jsonify({
        "members": [
            {
                "id": m.id,
                "github_login": m.github_login,
                "created_at": m.created_at.isoformat()
            }
            for m in members
        ]
    })


@api_bp.route('/team-members', methods=['POST'])
@validate_request(TeamMemberUpdate)
def update_team_members(data: TeamMemberUpdate):
    """Update team members list."""
    try:
        # Clear existing
        TeamMember.query.delete()
        
        # Add new
        for login in data.github_logins:
            member = TeamMember(github_login=login, is_active=True)
            db.session.add(member)
        
        db.session.commit()
        
        return jsonify({
            "ok": True,
            "message": f"Updated {len(data.github_logins)} team members"
        })
    except Exception as e:
        logger.error(f"Error updating team members: {e}")
        db.session.rollback()
        return jsonify({"ok": False, "error": str(e)}), 500


@api_bp.route('/settings', methods=['GET'])
def get_settings():
    """Get all settings."""
    settings = Settings.query.all()
    return jsonify({
        "settings": {s.key: s.value for s in settings}
    })


@api_bp.route('/settings', methods=['POST'])
@validate_request(SettingsUpdate)
def update_setting(data: SettingsUpdate):
    """Update a setting."""
    try:
        setting = Settings.query.filter_by(key=data.key).first()
        if setting:
            setting.value = data.value
        else:
            setting = Settings(key=data.key, value=data.value)
            db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({"ok": True, "message": "Setting updated"})
    except Exception as e:
        logger.error(f"Error updating setting: {e}")
        db.session.rollback()
        return jsonify({"ok": False, "error": str(e)}), 500


@api_bp.route('/reset', methods=['POST'])
def reset_all():
    """Reset all data including PAT."""
    try:
        AuthService.clear_all_data()
        return jsonify({
            "ok": True,
            "message": "All data cleared successfully"
        })
    except Exception as e:
        logger.error(f"Error resetting data: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@api_bp.route('/internal-orgs', methods=['GET'])
def get_internal_orgs():
    """Get internal organizations and repos configuration."""
    try:
        import json
        
        # Get from settings
        orgs_setting = Settings.query.filter_by(key='internal_organizations').first()
        repos_setting = Settings.query.filter_by(key='internal_repos').first()
        
        organizations = json.loads(orgs_setting.value) if orgs_setting else []
        repos = json.loads(repos_setting.value) if repos_setting else []
        
        return jsonify({
            "organizations": organizations,
            "repos": repos
        })
    except Exception as e:
        logger.error(f"Error getting internal orgs: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@api_bp.route('/internal-orgs', methods=['POST'])
@validate_request(InternalOrgsUpdate)
def update_internal_orgs(data: InternalOrgsUpdate):
    """Update internal organizations and repos configuration."""
    try:
        import json
        
        # Update organizations
        orgs_setting = Settings.query.filter_by(key='internal_organizations').first()
        if orgs_setting:
            orgs_setting.value = json.dumps(data.organizations)
        else:
            orgs_setting = Settings(key='internal_organizations', value=json.dumps(data.organizations))
            db.session.add(orgs_setting)
        
        # Update repos
        repos_setting = Settings.query.filter_by(key='internal_repos').first()
        if repos_setting:
            repos_setting.value = json.dumps(data.repos)
        else:
            repos_setting = Settings(key='internal_repos', value=json.dumps(data.repos))
            db.session.add(repos_setting)
        
        db.session.commit()
        
        return jsonify({
            "ok": True,
            "message": f"Updated {len(data.organizations)} internal organizations and {len(data.repos)} specific repos"
        })
    except Exception as e:
        logger.error(f"Error updating internal orgs: {e}")
        db.session.rollback()
        return jsonify({"ok": False, "error": str(e)}), 500

# https://github.com/SimonSaysGiveMeSmile

