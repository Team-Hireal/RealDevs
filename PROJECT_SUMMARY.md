# RealDevs Phase 1 - Project Summary

## Overview

**RealDevs** is a local-first team momentum analytics tool that provides insights into GitHub activity without surveillance. Built for engineering teams who value transparency and trust.

**Status**: ✅ Phase 1 MVP Complete

---

## ✨ Features Implemented

### 1. Dashboard (Homepage)
- **4 Key Metric Cards:**
  - Total Code Commitment Trend with sparkline chart
  - Internal vs External Commitment Split with pie chart
  - Top Contributor showcase with avatar and stats
  - Risk Flags counter with severity indicators
  
- **Visualizations:**
  - Area charts for commit trends
  - Pie charts for contribution split
  - Color-coded badges for risk severity
  
- **Risk Flags Section:**
  - No activity alerts
  - Single point of failure warnings
  - External contributor notifications
  - Stale repository flags
  
- **Contributors Table:**
  - Sortable by momentum score
  - Shows commits, PRs, issues for each person
  - Avatar display
  - Internal/external distinction
  
- **Weekly Recap:**
  - Auto-generated neutral summary
  - Highlights, bottlenecks, and recommendations
  - Copy-to-clipboard functionality
  
- **Interactive Controls:**
  - Date range selector (7/14/30 days)
  - Sync button with loading state
  - Last synced timestamp

### 2. Credentials Page
- **GitHub PAT Management:**
  - Secure PAT input with show/hide toggle
  - Real-time validation against GitHub API
  - Encrypted storage in local SQLite
  - Memory-only mode option
  - Complete data reset capability
  
- **Team Members Configuration:**
  - Add/remove team members by GitHub username
  - Visual list with avatars
  - Instant updates to dashboard
  - Used for internal vs external classification

### 3. Settings Page
- **Risk Flag Thresholds:**
  - No activity threshold (days)
  - Stale PR threshold (days)
  - Single contributor risk percentage
  - Increment/decrement controls
  - Min/max/default value display
  
- **Momentum Score Weights:**
  - Commits weight
  - PRs opened weight
  - PRs merged weight
  - Issues closed weight
  - Visual formula explanation
  
- **Controls:**
  - Save changes button
  - Reset to defaults
  - Real-time preview of formula

### 4. Backend API
- **Authentication:**
  - PAT submission and validation
  - Encrypted storage with Fernet
  - Auth status checking
  
- **Repository Management:**
  - List all accessible repos
  - Select repos for monitoring
  - View selected repos
  
- **Data Synchronization:**
  - Fetch commits, PRs, issues from GitHub
  - Pagination handling
  - Rate limit monitoring
  - Incremental sync support
  
- **Metrics & Analytics:**
  - Team momentum calculations
  - Per-repo summaries
  - Contributor breakdowns
  - Risk flag detection
  - Weekly recap generation
  
- **Configuration:**
  - Settings CRUD operations
  - Team member management

---

## 🏗️ Architecture

### Tech Stack

**Frontend:**
- Next.js 15 with App Router
- React 19.0 with TypeScript
- TanStack Query for data fetching
- Tailwind CSS with custom design system
- shadcn/ui components
- Recharts for visualizations

**Backend:**
- Flask 3.1.2
- SQLAlchemy 2 ORM
- SQLite database
- Pydantic validation
- httpx for GitHub API
- cryptography (Fernet encryption)
- pytest for testing

**Infrastructure:**
- Docker & Docker Compose
- Makefile for common commands
- GitHub REST API integration

### Project Structure

```
RealDevs/
├── apps/
│   ├── api/                    # Flask backend
│   │   ├── app/
│   │   │   ├── api/           # REST endpoints
│   │   │   ├── models/        # SQLAlchemy models
│   │   │   ├── services/      # Business logic
│   │   │   └── utils/         # Helpers
│   │   ├── tests/             # pytest tests
│   │   ├── config.py
│   │   ├── run.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── web/                    # Next.js frontend
│       ├── src/
│       │   ├── app/           # Pages (App Router)
│       │   ├── components/    # React components
│       │   ├── lib/           # API client & utils
│       │   └── types/         # TypeScript types
│       ├── package.json
│       └── Dockerfile
│
├── docs/
│   ├── API.md                 # API documentation
│   ├── ARCHITECTURE.md        # System design
│   ├── DEPLOYMENT.md          # Hosting guide
│   └── CONTRIBUTING.md        # Contribution guide
│
├── docker-compose.yml
├── Makefile
├── setup.sh
├── README.md
├── QUICKSTART.md
└── PROJECT_SUMMARY.md (this file)
```

---

## 🎨 Design System

### Color Palette
- **Background**: Dark navy (#1a1f2e)
- **Primary**: Electric blue (#3b82f6)
- **Secondary**: Dark slate (#2d3748)
- **Accent**: Cyan (#06b6d4)
- **Success**: Green (#10b981)
- **Warning**: Yellow (#f59e0b)
- **Danger**: Red (#ef4444)

### Visual Features
- **Frosted Glass Effects**: Backdrop blur with transparency
- **Gradients**: Smooth color transitions
- **Shadows**: Subtle glows for depth
- **Dark Mode**: Default and optimized
- **Responsive**: Works on all screen sizes

### Typography
- Font: Inter
- Headings: Bold, gradient text effects
- Body: Clear, readable sizes
- Code: Monospace for technical content

---

## 🔒 Security

### PAT Protection
- ✅ Encrypted at rest with Fernet
- ✅ Never logged anywhere
- ✅ Never returned in API responses
- ✅ Derived key from environment variable
- ✅ Memory-only mode available

### Data Privacy
- ✅ Local-first architecture
- ✅ No external data transmission (except GitHub API)
- ✅ SQLite stored locally
- ✅ Complete data wipe capability

### Best Practices
- ✅ CORS configured
- ✅ Input validation (Pydantic)
- ✅ Error handling
- ✅ Rate limit monitoring

---

## 📊 Metrics & Algorithms

### Momentum Score
```
Score = (Commits × W₁) + (PRs Opened × W₂) + (PRs Merged × W₃) + (Issues Closed × W₄)

Default Weights:
W₁ (Commits) = 1.0
W₂ (PRs Opened) = 1.5
W₃ (PRs Merged) = 2.0
W₄ (Issues Closed) = 1.0
```

### Risk Flags

1. **No Activity**
   - Trigger: No commits/merges in X days
   - Default: 3 days
   - Severity: High

2. **Single Point of Failure**
   - Trigger: One person accounts for Y% of work
   - Default: 70%
   - Severity: Medium

3. **External Contributor**
   - Trigger: Non-team member making commits
   - Severity: Low

4. **Stale Repository**
   - Trigger: No activity in recent period
   - Severity: High

---

## 📦 Deliverables

### Code
- ✅ Complete backend (Flask)
- ✅ Complete frontend (Next.js)
- ✅ Database models with migrations
- ✅ API client with TypeScript types
- ✅ UI components (shadcn/ui)
- ✅ Docker setup
- ✅ Tests (pytest)

### Documentation
- ✅ README with setup instructions
- ✅ QUICKSTART for 5-minute setup
- ✅ API documentation
- ✅ Architecture guide
- ✅ Deployment guide
- ✅ Contributing guidelines

### Infrastructure
- ✅ docker-compose.yml
- ✅ Dockerfiles for both services
- ✅ Makefile with common commands
- ✅ Setup script (setup.sh)
- ✅ Environment templates

---

## 🚀 Getting Started

### Quick Start (Docker)
```bash
docker compose up --build
# Open http://localhost:3000
```

### Manual Setup
```bash
./setup.sh
# Then run backend and frontend in separate terminals
```

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

---

## 🔄 Development Workflow

1. **Setup**: Run `./setup.sh` or `docker compose up`
2. **Code**: Make changes to `apps/api` or `apps/web`
3. **Test**: `make test` for backend tests
4. **Commit**: Git commit with clear messages
5. **Deploy**: See [DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## 📈 Future Roadmap

### Phase 2
- [ ] GitHub OAuth integration
- [ ] Multi-user support
- [ ] PostgreSQL migration
- [ ] Background job queue
- [ ] Real-time updates (WebSockets)

### Phase 3
- [ ] LLM-powered insights
- [ ] Slack/Discord integration
- [ ] Advanced analytics
- [ ] Custom dashboards
- [ ] Team comparison views

### Phase 4
- [ ] SaaS offering
- [ ] Organization management
- [ ] Billing integration
- [ ] Enterprise features
- [ ] Mobile app

---

## 🎯 Success Metrics

**Phase 1 MVP is considered successful if:**
- ✅ Runs locally with Docker or manual setup
- ✅ Securely stores GitHub PAT
- ✅ Syncs data from multiple repos
- ✅ Displays team momentum metrics
- ✅ Shows risk flags accurately
- ✅ UI is modern and pleasant to use
- ✅ Documentation is clear and complete

**All criteria met! ✅**

---

## 🤝 Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

---

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:
- Next.js by Vercel
- Flask by Pallets
- shadcn/ui by shadcn
- TanStack Query by TanStack
- And many other open-source projects

---

**Built with ❤️ for engineering teams who value transparency over surveillance.**

For questions or support, open an issue on GitHub.

