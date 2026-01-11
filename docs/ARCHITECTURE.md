# RealDevs Architecture

## Overview

RealDevs is a **local-first** web application built with a clear separation between frontend and backend.

```
┌─────────────────────────────────────────────────────┐
│                    Browser                          │
│  ┌──────────────────────────────────────────────┐   │
│  │         Next.js Frontend (Port 3000)         │   │
│  │  • React 19 + TypeScript                     │   │
│  │  • TanStack Query for data fetching          │   │
│  │  • shadcn/ui components                      │   │
│  │  • Tailwind CSS styling                      │   │
│  └────────────────┬─────────────────────────────┘   │
└───────────────────┼─────────────────────────────────┘
                    │ HTTP API Calls
                    ▼
┌─────────────────────────────────────────────────────┐
│         Flask Backend (Port 8000)                   │
│  ┌──────────────────────────────────────────────┐   │
│  │              REST API Layer                  │   │
│  │  • Flask 3.1.2 + CORS                        │   │
│  │  • Pydantic request/response validation      │   │
│  └────────────────┬─────────────────────────────┘   │
│                   │                                  │
│  ┌────────────────▼─────────────────────────────┐   │
│  │           Service Layer                      │   │
│  │  • AuthService (PAT management)              │   │
│  │  • SyncService (GitHub data ingestion)       │   │
│  │  • MetricsService (calculations & flags)     │   │
│  └────────────────┬─────────────────────────────┘   │
│                   │                                  │
│  ┌────────────────▼─────────────────────────────┐   │
│  │           Data Layer                         │   │
│  │  • SQLAlchemy 2 ORM                          │   │
│  │  • SQLite database                           │   │
│  │  • Fernet encryption for PAT                 │   │
│  └────────────────┬─────────────────────────────┘   │
└───────────────────┼─────────────────────────────────┘
                    │ GitHub API Client (httpx)
                    ▼
┌─────────────────────────────────────────────────────┐
│              GitHub REST API                        │
│  • Commits, PRs, Issues                             │
│  • Pagination & rate limit handling                 │
└─────────────────────────────────────────────────────┘
```

## Frontend Architecture

### Directory Structure

```
apps/web/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── page.tsx         # Dashboard (/)
│   │   ├── credentials/     # Credentials page
│   │   ├── settings/        # Settings page
│   │   ├── layout.tsx       # Root layout
│   │   └── globals.css      # Global styles
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── navigation.tsx   # Sidebar navigation
│   │   └── providers.tsx    # React Query provider
│   ├── lib/
│   │   ├── api.ts           # API client
│   │   └── utils.ts         # Utility functions
│   └── types/               # TypeScript types
└── public/                  # Static assets
```

### Key Technologies

- **Next.js 15** with App Router
- **React 19** with TypeScript
- **TanStack Query** for server state management
- **shadcn/ui** for accessible components
- **Tailwind CSS** for styling with custom design system

### Design Principles

1. **Responsive**: Works on all screen sizes
2. **Dark Mode First**: Developer-oriented aesthetic
3. **Glass Morphism**: Frosted glass effects with gradients
4. **Accessibility**: Semantic HTML + ARIA attributes
5. **Performance**: Code splitting, lazy loading, optimized assets

## Backend Architecture

### Directory Structure

```
apps/api/
├── app/
│   ├── api/
│   │   ├── routes.py        # API endpoints
│   │   └── schemas.py       # Pydantic models
│   ├── models/
│   │   └── __init__.py      # SQLAlchemy models
│   ├── services/
│   │   ├── auth_service.py  # PAT management
│   │   ├── sync_service.py  # GitHub sync
│   │   └── metrics_service.py # Calculations
│   ├── utils/
│   │   ├── encryption.py    # Fernet encryption
│   │   └── github_client.py # GitHub API wrapper
│   └── __init__.py          # App factory
├── tests/                   # pytest tests
├── config.py                # Configuration
└── run.py                   # Entry point
```

### Key Technologies

- **Flask 3.1.2** for REST API
- **SQLAlchemy 2** for ORM
- **Pydantic** for validation
- **httpx** for async HTTP
- **cryptography** for PAT encryption
- **pytest** for testing

### Design Principles

1. **Clean Architecture**: Separation of concerns (API → Service → Data)
2. **Security First**: Encrypted PAT storage, no logging of secrets
3. **Stateless API**: Each request is independent
4. **Error Handling**: Graceful degradation, clear error messages
5. **Testability**: Pure functions, dependency injection

## Data Model

### Core Entities

```
AuthToken
├─ encrypted_token (Fernet encrypted)
├─ github_user_login
├─ github_user_id
└─ store_mode (encrypted|memory)

Repository
├─ github_id
├─ full_name (owner/repo)
├─ last_synced_at
└─ contributors []

Contributor
├─ github_id
├─ login
├─ is_team_member (marked by user)
├─ repo_id (FK)
└─ daily_stats []

DailyStats (aggregated metrics)
├─ date
├─ repo_id (FK)
├─ contributor_id (FK)
├─ commits_count
├─ prs_opened
├─ prs_merged
├─ prs_closed
├─ issues_closed
└─ reviews_count

TeamMember (user-configured)
├─ github_login
└─ is_active

Settings (key-value store)
├─ key
└─ value
```

### Relationships

- Repository → Contributor (1:N)
- Contributor → DailyStats (1:N)
- Repository → DailyStats (1:N)

## Data Flow

### 1. PAT Configuration

```
User submits PAT
  ↓
Frontend → POST /auth/pat
  ↓
Backend validates with GitHub API
  ↓
Encrypt PAT with Fernet
  ↓
Store in SQLite
  ↓
Return user info (without PAT)
```

### 2. Repository Selection

```
User clicks "Select Repos"
  ↓
Frontend → GET /repos
  ↓
Backend fetches from GitHub API
  ↓
User selects repos
  ↓
Frontend → POST /repos/select
  ↓
Backend stores selected repos
```

### 3. Data Sync

```
User clicks "Sync"
  ↓
Frontend → POST /sync
  ↓
Backend for each repo:
  ├─ Fetch commits (paginated)
  ├─ Fetch pull requests
  ├─ Fetch issues
  ├─ Process & aggregate by contributor/day
  └─ Update DailyStats
  ↓
Return sync summary
```

### 4. Dashboard Display

```
Frontend → GET /dashboard?range_days=7
  ↓
Backend:
  ├─ Query DailyStats for date range
  ├─ Calculate team_summary
  ├─ Calculate per-repo summaries
  ├─ Calculate contributor breakdown
  ├─ Compute risk flags
  └─ Return dashboard data
  ↓
Frontend renders charts & tables
```

## Security Architecture

### PAT Storage

1. User submits PAT
2. Derive Fernet key from `HIDEVS_SECRET_KEY`
3. Encrypt PAT with Fernet
4. Store encrypted blob in SQLite
5. Never log or return PAT after storage

### Encryption Flow

```python
# Encryption
secret_key → SHA256 → Base64 → Fernet key
PAT → Fernet.encrypt() → Encrypted blob → SQLite

# Decryption
SQLite → Encrypted blob → Fernet.decrypt() → PAT → GitHub API
```

### Security Measures

- ✅ Encrypted at rest (Fernet)
- ✅ HTTPS in production (via reverse proxy)
- ✅ CORS configured
- ✅ No PAT in logs
- ✅ No PAT in API responses
- ✅ Local-first (no external data transmission)

## Performance Optimizations

### Frontend

1. **Code Splitting**: Next.js automatic chunking
2. **Caching**: TanStack Query with 1-minute stale time
3. **Lazy Loading**: Components loaded on demand
4. **Optimized Images**: Next.js Image component

### Backend

1. **Database Indexes**: On frequently queried columns
2. **Pagination**: GitHub API pagination handled
3. **Connection Pooling**: SQLAlchemy connection reuse
4. **Rate Limit Monitoring**: Respects GitHub limits

## Extensibility

### Adding New Metrics

1. Add column to `DailyStats` model
2. Update sync logic in `SyncService`
3. Update calculation in `MetricsService`
4. Add to frontend dashboard

### Adding New Risk Flags

1. Add logic to `MetricsService._compute_risk_flags()`
2. Define threshold in `Settings`
3. Display in frontend risk flags section

### Adding New Endpoints

1. Define Pydantic schema in `schemas.py`
2. Add route in `routes.py`
3. Implement service logic
4. Add TypeScript types in `lib/api.ts`
5. Use in frontend with TanStack Query

## Future Architecture (Phase 2+)

- **Multi-user**: PostgreSQL + user authentication
- **OAuth**: GitHub OAuth instead of PAT
- **Background Jobs**: Celery for async sync
- **Real-time Updates**: WebSockets for live data
- **LLM Integration**: AI-powered insights
- **Multi-tenant**: Isolated data per organization

## Monitoring & Observability

Planned for future phases:

- Structured logging (JSON)
- Metrics (Prometheus)
- Tracing (OpenTelemetry)
- Error tracking (Sentry)
- Performance monitoring (New Relic / DataDog)

---

**Philosophy**: Local-first, privacy-focused, transparent architecture that puts the user in control.

