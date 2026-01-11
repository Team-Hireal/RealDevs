# RealDevs Quick Start Guide

Get up and running with RealDevs in 5 minutes.

## Prerequisites

- Docker & Docker Compose (recommended) OR
- Node.js 24+ and Python 3.14.2+ (manual setup)

## Quick Start with Docker

1. **Clone and navigate:**
   ```bash
   git clone <your-repo-url>
   cd RealDevs
   ```

2. **Start services:**
   ```bash
   docker compose up --build
   ```

3. **Open in browser:**
   ```
   http://localhost:3000
   ```

That's it! 🎉

## Quick Start without Docker

### Terminal 1 - Backend

```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create environment file
cat > .env << EOF
FLASK_ENV=development
HIDEVS_SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///./realdevs.db
FLASK_APP=run.py
EOF

# Start server
python run.py
```

### Terminal 2 - Frontend

```bash
cd apps/web
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local

# Start server
npm run dev
```

Open http://localhost:3000

## First-Time Setup

1. **Create GitHub PAT:**
   - Go to GitHub → Settings → Developer settings
   - Personal access tokens → Fine-grained tokens
   - Generate new token with **read-only** permissions:
     - ✅ Repository contents
     - ✅ Pull requests
     - ✅ Issues
     - ✅ Metadata

2. **Configure RealDevs:**
   - Navigate to Credentials page
   - Paste your PAT
   - Click "Submit"

3. **Select Repositories:**
   - Choose repos to monitor
   - Click "Select"

4. **Add Team Members:**
   - In Credentials page
   - Add GitHub usernames of your team
   - This distinguishes internal vs external contributions

5. **Sync & View Dashboard:**
   - Go to Dashboard
   - Click "Sync" button
   - View your team's momentum metrics!

## Common Commands

```bash
# Start all services (Docker)
make docker-up

# Stop all services
make docker-down

# View logs
make docker-logs

# Run tests
make test

# Clean up
make clean
```

## Troubleshooting

### Port already in use

```bash
# Find and kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### PAT validation fails

- Check token has correct permissions
- Verify token hasn't expired
- Try generating a new token

### No data showing

- Click "Sync" button to fetch data
- Check selected repositories
- Verify team members are added

### Docker issues

```bash
# Rebuild from scratch
docker compose down -v
docker compose build --no-cache
docker compose up
```

## Next Steps

- 📖 Read [README.md](README.md) for full documentation
- 🏗️ Check [ARCHITECTURE.md](docs/ARCHITECTURE.md) to understand the system
- 🚀 See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for hosting options
- 🤝 Read [CONTRIBUTING.md](docs/CONTRIBUTING.md) to contribute

## Support

- GitHub Issues: [your-repo/issues]
- Discussions: [your-repo/discussions]

---

**Tip**: RealDevs is local-first. Your PAT never leaves your machine, and all data is stored locally.

