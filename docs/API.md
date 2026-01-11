# RealDevs API Documentation

Base URL: `http://localhost:8000/api`

## Authentication

Phase 1 uses GitHub Personal Access Token (PAT) submitted by the user. The PAT is stored encrypted locally.

## Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "service": "RealDevs API"
}
```

---

### Submit PAT

Submit and validate GitHub Personal Access Token.

```http
POST /auth/pat
```

**Request Body:**
```json
{
  "pat": "ghp_xxxxxxxxxxxxx",
  "store_mode": "encrypted"  // or "memory"
}
```

**Response:**
```json
{
  "ok": true,
  "user": {
    "login": "username",
    "id": 12345,
    "name": "User Name",
    "avatar_url": "https://..."
  }
}
```

---

### Check Auth Status

Check if PAT is configured.

```http
GET /auth/status
```

**Response:**
```json
{
  "ok": true,
  "configured": true,
  "user": {
    "login": "username",
    "id": 12345,
    "store_mode": "encrypted"
  }
}
```

---

### List Repositories

Get all repositories accessible to the user.

```http
GET /repos
```

**Response:**
```json
{
  "repos": [
    {
      "id": 123,
      "full_name": "owner/repo",
      "owner": "owner",
      "name": "repo",
      "private": false,
      "default_branch": "main",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### Get Selected Repositories

Get repositories currently selected for syncing.

```http
GET /repos/selected
```

**Response:**
```json
{
  "repos": [
    {
      "id": 1,
      "full_name": "owner/repo",
      "owner": "owner",
      "name": "repo",
      "private": false,
      "last_synced_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

---

### Select Repositories

Mark repositories for syncing.

```http
POST /repos/select
```

**Request Body:**
```json
{
  "repo_full_names": ["owner/repo1", "owner/repo2"]
}
```

**Response:**
```json
{
  "ok": true,
  "selected_count": 2,
  "repos": [
    {"id": 1, "full_name": "owner/repo1"},
    {"id": 2, "full_name": "owner/repo2"}
  ]
}
```

---

### Sync Repositories

Sync data from GitHub for selected repositories.

```http
POST /sync
```

**Request Body:**
```json
{
  "range_days": 7  // optional, defaults to 7
}
```

**Response:**
```json
{
  "ok": true,
  "synced_repos": ["owner/repo1", "owner/repo2"],
  "stats": {
    "repos_synced": 2,
    "total_commits": 150,
    "total_prs": 25
  }
}
```

---

### Get Dashboard Data

Get all metrics, risk flags, and contributor stats.

```http
GET /dashboard?range_days=7
```

**Query Parameters:**
- `range_days` (optional): Number of days to analyze (default: 7)

**Response:**
```json
{
  "team_summary": {
    "total_commits": 150,
    "total_prs_opened": 25,
    "total_prs_merged": 20,
    "total_issues_closed": 10,
    "momentum_score": 245.5,
    "internal_commits": 120,
    "external_commits": 30,
    "internal_percentage": 80.0,
    "external_percentage": 20.0
  },
  "repo_summaries": [
    {
      "repo_id": 1,
      "full_name": "owner/repo",
      "commits": 75,
      "prs_opened": 12,
      "prs_merged": 10,
      "issues_closed": 5,
      "momentum_score": 122.5,
      "last_synced": "2024-01-01T12:00:00Z"
    }
  ],
  "risk_flags": [
    {
      "type": "no_activity",
      "severity": "high",
      "title": "No activity in owner/repo",
      "description": "No commits or merged PRs in the last 7 days",
      "repo": "owner/repo"
    }
  ],
  "contributors": [
    {
      "login": "developer1",
      "name": "Developer One",
      "avatar_url": "https://...",
      "is_internal": true,
      "commits": 50,
      "prs_opened": 8,
      "prs_merged": 7,
      "issues_closed": 3,
      "momentum_score": 89.0
    }
  ],
  "last_synced": "2024-01-01T12:00:00Z",
  "range_days": 7
}
```

---

### Get Weekly Report

Get auto-generated text summary.

```http
GET /report/weekly?range_days=7
```

**Query Parameters:**
- `range_days` (optional): Number of days to analyze (default: 7)

**Response:**
```json
{
  "text": "📊 Weekly Recap (7 days)\n==================================================\n\n🔹 Team Activity:\n  • 150 commits\n  • 20 PRs merged\n..."
}
```

---

### Get Team Members

Get configured team members.

```http
GET /team-members
```

**Response:**
```json
{
  "members": [
    {
      "id": 1,
      "github_login": "developer1",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### Update Team Members

Replace team members list.

```http
POST /team-members
```

**Request Body:**
```json
{
  "github_logins": ["developer1", "developer2"]
}
```

**Response:**
```json
{
  "ok": true,
  "message": "Updated 2 team members"
}
```

---

### Get Settings

Get all configuration settings.

```http
GET /settings
```

**Response:**
```json
{
  "settings": {
    "threshold_no_activity_days": "3",
    "threshold_stale_pr_days": "7",
    "weight_commits": "1.0",
    "weight_prs_merged": "2.0"
  }
}
```

---

### Update Setting

Update a single setting.

```http
POST /settings
```

**Request Body:**
```json
{
  "key": "threshold_no_activity_days",
  "value": "5"
}
```

**Response:**
```json
{
  "ok": true,
  "message": "Setting updated"
}
```

---

### Reset All Data

Delete all local data including PAT.

```http
POST /reset
```

**Response:**
```json
{
  "ok": true,
  "message": "All data cleared successfully"
}
```

---

## Error Responses

All endpoints may return errors in this format:

```json
{
  "ok": false,
  "error": "Error message description"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad request (validation error)
- `401`: Unauthorized (PAT not configured or invalid)
- `500`: Internal server error

---

## Rate Limiting

The backend respects GitHub's rate limits:
- Authenticated requests: 5,000/hour
- The client monitors rate limits and logs warnings when low

---

## Data Privacy

- PAT is encrypted at rest using Fernet encryption
- PAT is never returned in API responses after initial submission
- All data is stored locally in SQLite
- No external data transmission except to GitHub API

