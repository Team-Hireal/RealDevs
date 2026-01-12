# External Commits Feature

## Overview

The External Commits feature tracks contributions made by your team members to repositories that are **not** in your tracked repository list. This helps you understand the full scope of your team's work, including contributions to open source projects, client repositories, or other external codebases.

## How It Works

### What are External Commits?

- **Internal Commits**: Commits made to repositories you have selected for tracking in RealDevs
- **External Commits**: Commits made by your team members to repositories **outside** your tracked list

### Data Collection

External commit data is collected through GitHub's Events API, which provides recent activity for GitHub users. The system:

1. Fetches recent push events for each configured team member
2. Filters out commits to tracked repositories
3. Stores the remaining commits as "external commits"
4. Displays them in the dashboard's contribution breakdown

### Limitations

- **Recency**: GitHub's Events API only provides the last ~90 days of activity
- **Public Activity**: Only public repositories and activities are captured
- **Rate Limits**: External commit sync is subject to GitHub API rate limits

## Setup

### 1. Configure Team Members

External commits are only tracked for users you've explicitly marked as team members. To configure team members:

**Via API:**
```bash
curl -X POST http://localhost:8000/api/team-members \
  -H "Content-Type: application/json" \
  -d '{
    "github_logins": ["username1", "username2", "username3"]
  }'
```

**Via Settings Page:**
1. Navigate to the Settings page in the web interface
2. Add team member GitHub usernames
3. Save settings

### 2. Run Initial Sync

After configuring team members, run a sync to fetch both internal and external commits:

**Via API:**
```bash
curl -X POST http://localhost:8000/api/sync \
  -H "Content-Type: application/json" \
  -d '{"range_days": 30}'
```

**Via Dashboard:**
1. Open the Dashboard page
2. Click the "Sync" button
3. The system will sync both internal repositories and external commits

### 3. View External Commits

External commits appear in the dashboard in two places:

1. **Contribution Split Chart**: Shows breakdown by repository, with external repos labeled
2. **Team Summary**: External commit count is included in the overall metrics

## Database Migration

If you're upgrading from an older version of RealDevs, you need to run the migration to add the `external_commits` table:

```bash
cd apps/api
source venv/bin/activate  # or use the full path to venv/bin/python
python migrate_add_external_commits.py
```

Or simply restart your application - the table will be created automatically on startup.

## API Endpoints

### Get Dashboard with External Commits

```bash
GET /api/dashboard?range_days=7
```

Response includes external commit counts in `team_summary.external_commits`.

### Get Daily Commits with External Breakdown

```bash
GET /api/dashboard/daily-commits?range_days=7
```

Response includes `repo_contributions` array with both internal and external repositories:

```json
{
  "repo_contributions": [
    {
      "name": "your-org/internal-repo",
      "type": "internal",
      "value": 45
    },
    {
      "name": "external-org/open-source-project",
      "type": "external",
      "value": 12
    }
  ]
}
```

### Sync External Commits

External commits are automatically synced when you run the main sync endpoint:

```bash
POST /api/sync
Content-Type: application/json

{
  "range_days": 30
}
```

The response will include an `external_commits` section:

```json
{
  "ok": true,
  "synced_repos": ["repo1", "repo2"],
  "external_commits": {
    "ok": true,
    "synced_members": ["user1", "user2"],
    "external_commits_synced": 47
  }
}
```

## Troubleshooting

### No External Commits Showing

1. **Check Team Members**: Ensure you have team members configured
   ```bash
   curl http://localhost:8000/api/team-members
   ```

2. **Verify Sync Ran**: Check that external commit sync completed successfully
   ```bash
   curl -X POST http://localhost:8000/api/sync -H "Content-Type: application/json" -d '{"range_days": 30}'
   ```

3. **Check Database**: Verify external commits are stored
   ```bash
   # In Python shell with app context
   from app.models import ExternalCommit
   print(ExternalCommit.query.count())
   ```

### External Commits Not Updating

- External commit data is fetched during sync operations
- Run sync regularly to keep data up-to-date
- Consider the 90-day limitation of GitHub's Events API

### Rate Limit Issues

If you hit GitHub API rate limits:

1. Reduce the frequency of syncs
2. Reduce the number of team members being tracked
3. Check your rate limit status:
   ```bash
   curl -H "Authorization: Bearer YOUR_PAT" https://api.github.com/rate_limit
   ```

## Privacy Considerations

- Only **public** GitHub activity is tracked
- Private repository commits are not visible unless your PAT has access
- Team members should be aware they're being tracked
- Consider your organization's privacy policies

## Future Enhancements

Potential improvements to this feature:

- Support for private repository tracking
- More detailed external commit analysis
- Notifications for external work
- Time allocation reports (internal vs external)
- Integration with time tracking systems

## Technical Details

### Database Schema

The `external_commits` table stores:

```sql
CREATE TABLE external_commits (
    id INTEGER PRIMARY KEY,
    github_user_login VARCHAR(255) NOT NULL,
    github_user_id INTEGER NOT NULL,
    repo_full_name VARCHAR(255) NOT NULL,
    repo_owner VARCHAR(255) NOT NULL,
    commit_sha VARCHAR(40) NOT NULL UNIQUE,
    commit_date DATETIME NOT NULL,
    commit_message TEXT,
    created_at DATETIME,
    updated_at DATETIME
);
```

### Sync Process

1. For each team member:
   - Fetch recent events from GitHub (`/users/{username}/events`)
   - Filter for PushEvents within date range
   - Extract commits from each push
   - Skip commits to tracked repositories
   - Store unique commits (by SHA) in database

2. Metrics calculation:
   - External commits are counted separately from internal commits
   - They appear in the contribution breakdown chart
   - They're included in team summary metrics

### Code References

- **Sync Service**: `apps/api/app/services/sync_service.py::sync_external_commits()`
- **Metrics Service**: `apps/api/app/services/metrics_service.py::get_daily_commits()`
- **Model**: `apps/api/app/models/__init__.py::ExternalCommit`
- **GitHub Client**: `apps/api/app/utils/github_client.py::get_user_events()`

## Summary

The External Commits feature provides visibility into your team's full workload, not just the repositories you're actively tracking. This is particularly useful for:

- Understanding team capacity and allocation
- Identifying open source contributions
- Tracking work on client projects
- Ensuring balanced workload distribution

To get started, simply configure your team members in the Settings page and run a sync!

