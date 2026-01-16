# RealDevs - Complete Project Structure Diagram

## Project Structure Overview

```
RealDevs/
│
├── 📁 Root Configuration Files
│   ├── app.py                          # Vercel entry point
│   ├── docker-compose.yml              # Docker Compose configuration
│   ├── vercel.json                     # Vercel deployment config
│   ├── Makefile                        # Build automation commands
│   ├── requirements.txt                # Root Python dependencies
│   ├── setup.sh                        # Setup script
│   ├── LICENSE                         # MIT License
│   ├── README.md                       # Main documentation
│   ├── QUICKSTART.md                   # Quick start guide
│   ├── SOLUTION_SUMMARY.md             # Solution summary
│   ├── VERIFICATION_RESULTS.md         # Verification results
│   ├── .dockerignore                   # Docker ignore patterns
│   └── .vercelignore                   # Vercel ignore patterns
│
├── 📁 api/                             # Legacy/Alternative API (Vercel)
│   ├── index.py                        # Vercel handler
│   ├── vercel_handler.py               # Vercel handler implementation
│   ├── requirements.txt                # API dependencies
│   └── test_index.py                   # API tests
│
├── 📁 apps/                            # Main application code
│   │
│   ├── 📁 api/                         # Flask Backend (Port 8000)
│   │   ├── 📁 app/                     # Application package
│   │   │   ├── __init__.py             # Flask app factory
│   │   │   │
│   │   │   ├── 📁 api/                 # API Layer
│   │   │   │   ├── __init__.py
│   │   │   │   ├── routes.py           # REST API endpoints
│   │   │   │   └── schemas.py          # Pydantic request/response models
│   │   │   │
│   │   │   ├── 📁 models/              # Data Models (SQLAlchemy)
│   │   │   │   ├── __init__.py         # Database models
│   │   │   │   └── (AuthToken, Repository, Contributor, DailyStats, etc.)
│   │   │   │
│   │   │   ├── 📁 services/            # Business Logic Layer
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth_service.py     # PAT management & encryption
│   │   │   │   ├── sync_service.py     # GitHub data synchronization
│   │   │   │   └── metrics_service.py  # Metrics calculations & risk flags
│   │   │   │
│   │   │   └── 📁 utils/               # Utility Functions
│   │   │       ├── __init__.py
│   │   │       ├── encryption.py       # Fernet encryption for PAT
│   │   │       └── github_client.py    # GitHub API client wrapper
│   │   │
│   │   ├── 📁 tests/                   # Test Suite
│   │   │   ├── __init__.py
│   │   │   ├── test_encryption.py      # Encryption tests
│   │   │   └── test_metrics.py         # Metrics calculation tests
│   │   │
│   │   ├── 📁 venv/                    # Python virtual environment
│   │   │   └── (Python packages)
│   │   │
│   │   ├── 📄 Configuration Files
│   │   │   ├── config.py               # Flask configuration
│   │   │   ├── run.py                  # Development server entry point
│   │   │   ├── index.py                # Production entry point
│   │   │   ├── vercel_handler.py       # Vercel serverless handler
│   │   │   ├── init_db.py              # Database initialization
│   │   │   ├── pytest.ini              # Pytest configuration
│   │   │   ├── env.example             # Environment variables template
│   │   │   ├── requirements.txt        # Python dependencies
│   │   │   ├── Dockerfile              # Docker image definition
│   │   │   └── realdevs.db             # SQLite database file
│   │   │
│   │   ├── 📄 Migration Scripts
│   │   │   ├── migrate_add_external_commits.py
│   │   │   ├── migrate_add_external_contributors.py
│   │   │   └── migrate_add_social_links.py
│   │   │
│   │   ├── 📄 Utility Scripts
│   │   │   ├── check_sync_status.py    # Sync status checker
│   │   │   └── clear_test_data.py      # Test data cleanup
│   │   │
│   │   └── 📄 Test Files
│   │       ├── test_app.py             # Application tests
│   │       ├── test_external_commits.py
│   │       ├── test_imports.py
│   │       └── TREND_CALCULATION_VERIFICATION.md
│   │
│   └── 📁 web/                         # Next.js Frontend (Port 3000)
│       ├── 📁 src/                     # Source code
│       │   │
│       │   ├── 📁 app/                 # Next.js App Router
│       │   │   ├── layout.tsx          # Root layout component
│       │   │   ├── page.tsx            # Dashboard page (/)
│       │   │   ├── globals.css         # Global styles
│       │   │   ├── icon.png            # App icon
│       │   │   │
│       │   │   ├── 📁 credentials/    # Credentials page
│       │   │   │   └── page.tsx        # PAT management page
│       │   │   │
│       │   │   └── 📁 settings/       # Settings page
│       │   │       └── page.tsx        # Settings configuration page
│       │   │
│       │   ├── 📁 components/         # React Components
│       │   │   ├── navigation.tsx      # Sidebar navigation
│       │   │   ├── providers.tsx       # React Query provider
│       │   │   ├── theme-selector.tsx  # Theme switcher
│       │   │   │
│       │   │   └── 📁 ui/              # shadcn/ui components
│       │   │       ├── badge.tsx       # Badge component
│       │   │       ├── button.tsx      # Button component
│       │   │       ├── card.tsx        # Card component
│       │   │       ├── input.tsx        # Input component
│       │   │       ├── select.tsx      # Select component
│       │   │       ├── skeleton.tsx   # Loading skeleton
│       │   │       └── tabs.tsx        # Tabs component
│       │   │
│       │   ├── 📁 contexts/            # React Contexts
│       │   │   └── theme-context.tsx   # Theme context provider
│       │   │
│       │   ├── 📁 lib/                 # Library/Utility Code
│       │   │   ├── api.ts              # API client (TanStack Query)
│       │   │   └── utils.ts            # Utility functions
│       │   │
│       │   ├── 📁 types/               # TypeScript Type Definitions
│       │   │   └── index.ts            # Shared types/interfaces
│       │   │
│       │   └── 📁 public/              # Static Assets
│       │       ├── contributors.png    # Contributors page image
│       │       ├── dashboard.png       # Dashboard preview image
│       │       └── logo.png            # Application logo
│       │
│       ├── 📁 public/                  # Public static files
│       │   └── logo.png                # Public logo
│       │
│       ├── 📁 node_modules/            # NPM dependencies
│       │
│       ├── 📄 Configuration Files
│       │   ├── package.json            # NPM dependencies & scripts
│       │   ├── package-lock.json       # Locked dependency versions
│       │   ├── next.config.js          # Next.js configuration
│       │   ├── tsconfig.json           # TypeScript configuration
│       │   ├── tailwind.config.ts      # Tailwind CSS configuration
│       │   ├── postcss.config.js       # PostCSS configuration
│       │   ├── next-env.d.ts           # Next.js TypeScript definitions
│       │   └── Dockerfile              # Docker image definition
│
└── 📁 docs/                            # Documentation
    ├── API.md                          # API documentation
    ├── ARCHITECTURE.md                 # Architecture overview
    ├── CONTRIBUTING.md                 # Contribution guidelines
    ├── VERCEL_COMPLETE_GUIDE.md       # Vercel deployment guide
    ├── VERCEL_QUICK_START.md          # Vercel quick start
    └── VERCEL_TROUBLESHOOTING.md      # Vercel troubleshooting
```

## Architecture Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Next.js Frontend (Port 3000)                     │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │  Pages:                                            │ │  │
│  │  │  • / (Dashboard)                                   │ │  │
│  │  │  • /credentials (PAT Management)                   │ │  │
│  │  │  • /settings (Configuration)                      │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │  Components:                                        │ │  │
│  │  │  • Navigation, UI Components (shadcn/ui)           │ │  │
│  │  │  • Theme Context, Providers (TanStack Query)      │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │  Libraries:                                         │ │  │
│  │  │  • api.ts (API client)                             │ │  │
│  │  │  • utils.ts (Helper functions)                     │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  └───────────────────────┬───────────────────────────────────┘  │
└───────────────────────────┼─────────────────────────────────────┘
                            │ HTTP REST API (JSON)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              Flask Backend API (Port 8000)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Layer (routes.py, schemas.py)                      │  │
│  │  • /api/auth/* (Authentication)                         │  │
│  │  • /api/repos/* (Repository management)                 │  │
│  │  • /api/sync/* (Data synchronization)                  │  │
│  │  • /api/dashboard/* (Dashboard data)                   │  │
│  │  • /api/metrics/* (Metrics & risk flags)               │  │
│  └───────────────────────┬───────────────────────────────────┘  │
│                          │                                       │
│  ┌───────────────────────▼───────────────────────────────────┐  │
│  │  Service Layer                                           │  │
│  │  • auth_service.py (PAT encryption/decryption)          │  │
│  │  • sync_service.py (GitHub data ingestion)              │  │
│  │  • metrics_service.py (Calculations & risk detection)   │  │
│  └───────────────────────┬───────────────────────────────────┘  │
│                          │                                       │
│  ┌───────────────────────▼───────────────────────────────────┐  │
│  │  Data Layer                                               │  │
│  │  • SQLAlchemy ORM (models/)                              │  │
│  │  • SQLite Database (realdevs.db)                         │  │
│  │  • Fernet Encryption (utils/encryption.py)               │  │
│  └───────────────────────┬───────────────────────────────────┘  │
└───────────────────────────┼─────────────────────────────────────┘
                            │ GitHub API Client (httpx)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub REST API                              │
│  • Commits, Pull Requests, Issues                              │
│  • Repository metadata, Contributors                           │
│  • Pagination & rate limit handling                            │
└─────────────────────────────────────────────────────────────────┘
```

## Key Technologies Stack

### Frontend (apps/web/)
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **UI Library**: React 19.2
- **State Management**: TanStack Query (React Query)
- **UI Components**: shadcn/ui
- **Styling**: Tailwind CSS
- **Build Tool**: Next.js built-in

### Backend (apps/api/)
- **Framework**: Flask 3.1.2
- **Language**: Python 3.12+
- **ORM**: SQLAlchemy 2
- **Database**: SQLite
- **Validation**: Pydantic
- **HTTP Client**: httpx (async)
- **Encryption**: cryptography (Fernet)
- **Testing**: pytest

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Deployment**: Vercel (serverless)
- **Package Management**: 
  - Python: pip, requirements.txt
  - Node.js: npm, package.json

## Data Models

```
AuthToken
├── encrypted_token (Fernet encrypted PAT)
├── github_user_login
├── github_user_id
└── store_mode

Repository
├── github_id
├── full_name (owner/repo)
├── last_synced_at
└── contributors (1:N)

Contributor
├── github_id
├── login
├── is_team_member (user-marked)
├── repo_id (FK)
└── daily_stats (1:N)

DailyStats
├── date
├── repo_id (FK)
├── contributor_id (FK)
├── commits_count
├── prs_opened/merged/closed
├── issues_closed
└── reviews_count

TeamMember
├── github_login
└── is_active

Settings
├── key
└── value
```

## Deployment Architecture

### Local Development
```
Docker Compose
├── api (Flask on :8000)
└── web (Next.js on :3000)
```

### Vercel Deployment
```
Vercel Platform
├── Serverless Functions (app.py → apps/api/)
└── Static Assets (apps/web/)
```

## File Count Summary

- **Backend**: ~20 Python files (excluding __pycache__)
- **Frontend**: ~15 TypeScript/TSX files
- **Configuration**: ~15 config files
- **Documentation**: ~10 markdown files
- **Tests**: ~5 test files

---

**Note**: This diagram represents the complete project structure as of the current state. The project follows a monorepo structure with clear separation between frontend (Next.js) and backend (Flask) applications.

