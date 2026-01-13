# External Contributors Feature

## Overview

This feature allows you to track specific external contributors to your repositories. When you add an external contributor by their GitHub username, the system will:

1. Look them up on GitHub
2. Fetch all their commit history to your selected repositories
3. Display them as "External" in the dashboard
4. Track their contributions separately from internal team members

There is **no limit** on the number of external contributors you can add.

## How It Works

### Database Schema

A new table `external_contributors` has been added with the following fields:
- `id`: Primary key
- `github_login`: GitHub username (unique)
- `github_user_id`: GitHub user ID (auto-populated during sync)
- `is_active`: Whether this contributor is actively tracked
- `last_synced_at`: Last time their commits were synced
- `created_at`: When they were added
- `updated_at`: Last update timestamp

### Backend Implementation

#### Models (`apps/api/app/models/__init__.py`)
- **ExternalContributor**: New model to store external contributors

#### API Endpoints (`apps/api/app/api/routes.py`)
- `GET /api/external-contributors`: Get list of external contributors
- `POST /api/external-contributors`: Update external contributors list

#### Sync Service (`apps/api/app/services/sync_service.py`)
- **`sync_external_contributors()`**: New method that:
  - Fetches all configured external contributors
  - For each contributor, fetches their commits to all selected repositories
  - Processes commits using the standard commit processing pipeline
  - Updates the `last_synced_at` timestamp

#### Metrics Service (`apps/api/app/services/metrics_service.py`)
- **Updated `_is_internal_contributor()`**: Now checks if a contributor is in the `ExternalContributor` table and explicitly marks them as external

### Frontend Implementation

#### API Client (`apps/web/src/lib/api.ts`)
- Added `getExternalContributors()` method
- Added `updateExternalContributors()` method
- Added `ExternalContributor` TypeScript interface

#### Credentials Page (`apps/web/src/app/credentials/page.tsx`)
- **Internal Team Members Section**: Renamed from "External Members" for clarity
  - Used to track internal team members
  - Helps determine internal vs external classification
  
- **External Contributors Section**: New section added
  - Input field to add GitHub usernames
  - List of added external contributors with "External" badge
  - Remove button for each contributor
  - Success/error feedback messages

## Usage Guide

### Adding External Contributors

1. Navigate to the **Credentials** page
2. Scroll to the **External Contributors** section (at the bottom)
3. Enter a GitHub username in the input field
4. Click "Add" or press Enter
5. The contributor will be added to the list with an "External" badge

### Syncing External Contributor Data

After adding external contributors, you need to sync to fetch their commits:

1. Go to the **Dashboard** or **Credentials** page
2. Click the sync button (or run automatic sync)
3. The system will:
   - Fetch commits from each external contributor to your selected repositories
   - Process and store their contribution data
   - Label them as "External" in the dashboard

### Viewing External Contributors in the Dashboard

External contributors will appear in the dashboard with:
- Their commits, PRs, and other contributions to your repositories
- An "External" label or indicator
- Their profile information (avatar, name, social links if available)

### Removing External Contributors

1. Go to the **Credentials** page
2. Find the contributor in the **External Contributors** section
3. Click the trash icon next to their name
4. The contributor will be removed (their historical data remains but they won't be tracked going forward)

## Internal vs External Classification

The system determines if a contributor is "Internal" or "External" based on:

1. **External Contributors Table** (highest priority): If explicitly added as external → External
2. **Team Members Table**: If added as internal team member → Internal
3. **Internal Organizations**: If repo owner is in configured internal orgs → Internal
4. **Internal Repos**: If repo is explicitly marked as internal → Internal
5. **Default**: Otherwise → External

This means external contributors are **always** labeled as external, even if they contribute to internal repositories.

## API Reference

### Get External Contributors
```http
GET /api/external-contributors
```

**Response:**
```json
{
  "contributors": [
    {
      "id": 1,
      "github_login": "username",
      "github_user_id": 12345,
      "last_synced_at": "2026-01-13T10:30:00Z",
      "created_at": "2026-01-13T09:00:00Z"
    }
  ]
}
```

### Update External Contributors
```http
POST /api/external-contributors
Content-Type: application/json

{
  "github_logins": ["username1", "username2", "username3"]
}
```

**Response:**
```json
{
  "ok": true,
  "message": "Updated 3 external contributors"
}
```

### Sync External Contributors

External contributors are automatically synced when you run a sync operation:

```http
POST /api/sync
Content-Type: application/json

{
  "range_days": 7
}
```

The sync response will include an `external_contributors` field with sync results.

## Technical Details

### GitHub API Integration

The sync service uses the GitHub Commits API with author filtering:
```python
commits = client.get_commits(
    repo_owner, 
    repo_name, 
    author=login,  # Filter by external contributor
    since=since, 
    until=until
)
```

This efficiently fetches only commits from the specific contributor without fetching all repository commits.

### Performance Considerations

- Commits are fetched per repository, per contributor
- The GitHub API is rate-limited (5000 requests/hour for authenticated requests)
- For repositories with many external contributors and long histories, initial sync may take time
- Subsequent syncs are faster as they only fetch new commits

### Database Migration

A migration script is provided at `apps/api/migrate_add_external_contributors.py` to create the `external_contributors` table. The migration:
- Creates the table with all required fields
- Adds indexes on `github_login` and `github_user_id` for performance
- Checks if the table already exists to avoid duplicate creation

## Troubleshooting

### External contributors not showing in dashboard
- Ensure you've run a sync after adding contributors
- Check that the repositories are selected in the Credentials page
- Verify the GitHub username is correct

### Sync takes too long
- Reduce the sync range (e.g., 7 days instead of "all time")
- Limit the number of repositories being tracked
- Consider syncing external contributors separately during off-peak hours

### Contributors showing as "Internal" instead of "External"
- Verify they are added in the "External Contributors" section
- Check that they're not also added as "Internal Team Members"
- Run a fresh sync after making changes

## Future Enhancements

Potential improvements for this feature:
- Bulk import from CSV file
- Automatic contributor discovery based on PR/commit patterns
- Per-contributor sync schedules
- Contributor groups/tags for better organization
- Detailed contribution analytics per external contributor

## Files Modified

### Backend
- `apps/api/app/models/__init__.py` - Added ExternalContributor model
- `apps/api/app/api/schemas.py` - Added ExternalContributorUpdate schema
- `apps/api/app/api/routes.py` - Added API endpoints for external contributors
- `apps/api/app/services/sync_service.py` - Added sync_external_contributors() method
- `apps/api/app/services/metrics_service.py` - Updated _is_internal_contributor() method
- `apps/api/migrate_add_external_contributors.py` - Database migration script (NEW)

### Frontend
- `apps/web/src/lib/api.ts` - Added API client methods
- `apps/web/src/app/credentials/page.tsx` - Added UI for managing external contributors

## Summary

This feature provides a powerful way to explicitly track external contributors to your projects. By adding their GitHub usernames, you can monitor their contributions separately from your internal team, gaining better visibility into external collaboration and open-source contributions to your repositories.

