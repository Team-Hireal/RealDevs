# Vercel Deployment Guide for Flask Backend

This comprehensive guide will walk you through deploying your Flask backend to Vercel and preparing your project for production deployment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Understanding Vercel Serverless Functions](#understanding-vercel-serverless-functions)
3. [Project Preparation](#project-preparation)
4. [Database Migration](#database-migration)
5. [Configuration Files](#configuration-files)
6. [Environment Variables](#environment-variables)
7. [Deployment Steps](#deployment-steps)
8. [Post-Deployment Configuration](#post-deployment-configuration)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## Prerequisites

Before starting, ensure you have:

- ✅ A Vercel account ([sign up here](https://vercel.com/signup))
- ✅ Vercel CLI installed (`npm i -g vercel`)
- ✅ A cloud database (PostgreSQL recommended) - SQLite won't work on Vercel
- ✅ GitHub repository with your code
- ✅ All environment variables documented

### Why PostgreSQL?

Vercel's serverless functions have a **read-only filesystem**, which means:
- ❌ SQLite databases cannot be written to
- ❌ File-based storage is not persistent
- ✅ You need a cloud database (PostgreSQL, MySQL, etc.)

**Recommended Providers:**
- [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres) (integrated)
- [Supabase](https://supabase.com) (free tier available)
- [Neon](https://neon.tech) (serverless PostgreSQL)
- [Railway](https://railway.app) (PostgreSQL)
- [Render](https://render.com) (PostgreSQL)

---

## Understanding Vercel Serverless Functions

Vercel runs Flask as **serverless functions**. Key differences from traditional hosting:

1. **Stateless**: Each request may hit a different instance
2. **Cold starts**: First request may be slower
3. **Timeout limits**: 
   - Hobby: 10 seconds
   - Pro: 60 seconds
   - Enterprise: 300 seconds
4. **File system**: Read-only (except `/tmp`)

Your Flask app will be automatically converted to serverless functions based on your routing.

---

## Project Preparation

### Step 1: Create Vercel Configuration

Create a `vercel.json` file in your **project root** (`/Users/test/Desktop/Hireal/RealDevs/`):

```json
{
  "version": 2,
  "builds": [
    {
      "src": "apps/api/run.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "apps/api/run.py"
    },
    {
      "src": "/(.*)",
      "dest": "apps/api/run.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.12"
  }
}
```

### Step 2: Create Serverless Entry Point

Vercel needs a specific entry point. Create `apps/api/vercel_handler.py`:

```python
"""Vercel serverless function entry point."""
import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from run import app

# Export the Flask app for Vercel
# Vercel will automatically detect this as the WSGI application
handler = app
```

### Step 3: Update run.py for Vercel Compatibility

Your current `run.py` should work, but ensure it exports the app correctly:

```python
"""Main entry point for Flask application."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app

app = create_app()

# For Vercel, the app must be accessible
# Vercel will look for 'app' or 'application' variable
if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### Step 4: Update vercel.json to Use Correct Entry Point

Update `vercel.json` to use the handler:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "apps/api/vercel_handler.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "apps/api/vercel_handler.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.12"
  }
}
```

---

## Database Migration

### Step 1: Install PostgreSQL Driver

Add to `apps/api/requirements.txt`:

```txt
psycopg2-binary==2.9.9
```

Or for async support (optional):

```txt
psycopg2-binary==2.9.9
# or
asyncpg==0.29.0  # if using async SQLAlchemy
```

### Step 2: Update Database Configuration

Update `apps/api/config.py` to support PostgreSQL:

```python
"""Configuration for RealDevs API."""
import os
from pathlib import Path

class Config:
    """Base configuration."""
    
    # Flask
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"
    
    # Security
    SECRET_KEY = os.getenv("HIDEVS_SECRET_KEY", "dev-secret-change-in-production")
    
    # Database
    BASE_DIR = Path(__file__).parent
    # Support both SQLite (local) and PostgreSQL (production)
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        # Fallback to SQLite for local development
        DATABASE_URL = f"sqlite:///{BASE_DIR}/realdevs.db"
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # PostgreSQL connection string
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Verify connections before using
        "pool_recycle": 300,    # Recycle connections after 5 minutes
    }
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003").split(",")
    
    # GitHub API
    GITHUB_API_BASE = "https://api.github.com"
    GITHUB_RATE_LIMIT_BUFFER = 100
    
    # Pagination
    MAX_PAGE_SIZE = 100
    DEFAULT_PAGE_SIZE = 30


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


def get_config():
    """Get configuration based on environment."""
    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        return ProductionConfig()
    return DevelopmentConfig()
```

### Step 3: Migrate Existing Data (Optional)

If you have existing SQLite data, export and import:

```bash
# Export from SQLite
cd apps/api
python -c "
from app import create_app
from app.models import db, Repository, Contributor, DailyStats, AuthToken, TeamMember, Settings
import json

app = create_app()
with app.app_context():
    # Export data
    data = {
        'repos': [{'full_name': r.full_name, 'owner': r.owner, 'name': r.name, 'private': r.private} for r in Repository.query.all()],
        'team_members': [{'github_login': m.github_login} for m in TeamMember.query.all()],
        # Add other models as needed
    }
    with open('data_export.json', 'w') as f:
        json.dump(data, f)
    print('Data exported to data_export.json')
"

# Then import to PostgreSQL after deployment
```

---

## Configuration Files

### Complete vercel.json

Create/update `/Users/test/Desktop/Hireal/RealDevs/vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "apps/api/vercel_handler.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "apps/api/vercel_handler.py"
    }
  ],
  "functions": {
    "apps/api/vercel_handler.py": {
      "maxDuration": 60
    }
  },
  "env": {
    "PYTHON_VERSION": "3.12"
  }
}
```

### .vercelignore (Optional)

Create `/Users/test/Desktop/Hireal/RealDevs/.vercelignore` to exclude unnecessary files:

```
apps/api/__pycache__/
apps/api/*.db
apps/api/venv/
apps/api/.env
apps/api/tests/
*.pyc
__pycache__/
.pytest_cache/
.coverage
.env.local
```

---

## Environment Variables

### Required Environment Variables

Set these in Vercel Dashboard → Project → Settings → Environment Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `HIDEVS_SECRET_KEY` | Secret key for encryption | `your-secure-random-key-32-chars-min` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/dbname` |
| `FLASK_ENV` | Environment mode | `production` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `https://your-app.vercel.app,https://yourdomain.com` |
| `GITHUB_API_BASE` | GitHub API base URL | `https://api.github.com` (default) |

### Generating a Secure Secret Key

```python
import secrets
print(secrets.token_urlsafe(32))
```

Or using OpenSSL:

```bash
openssl rand -hex 32
```

### PostgreSQL Connection String Format

```
postgresql://[user]:[password]@[host]:[port]/[database]?sslmode=require
```

**Example (Supabase):**
```
postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres?sslmode=require
```

**Example (Neon):**
```
postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

---

## Deployment Steps

### Method 1: Vercel CLI (Recommended)

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Navigate to project root**:
   ```bash
   cd /Users/test/Desktop/Hireal/RealDevs
   ```

4. **Link project** (first time only):
   ```bash
   vercel link
   ```
   - Follow prompts to select/create project
   - Choose existing project or create new

5. **Set environment variables**:
   ```bash
   vercel env add HIDEVS_SECRET_KEY
   vercel env add DATABASE_URL
   vercel env add FLASK_ENV
   vercel env add CORS_ORIGINS
   ```
   - Enter values for each
   - Select environments (Production, Preview, Development)

6. **Deploy**:
   ```bash
   vercel --prod
   ```

7. **View deployment**:
   ```bash
   vercel ls
   vercel inspect [deployment-url]
   ```

### Method 2: Vercel Dashboard

1. **Go to [Vercel Dashboard](https://vercel.com/dashboard)**

2. **Click "Add New Project"**

3. **Import your Git repository**

4. **Configure project**:
   - **Framework Preset**: Other
   - **Root Directory**: Leave as root (or set to `apps/api` if deploying only backend)
   - **Build Command**: Leave empty (Vercel auto-detects Python)
   - **Output Directory**: Leave empty
   - **Install Command**: Leave empty

5. **Add Environment Variables**:
   - Go to Settings → Environment Variables
   - Add all required variables (see above)

6. **Deploy**

### Method 3: GitHub Integration (Automatic)

1. **Connect GitHub repository** in Vercel Dashboard

2. **Configure project** (same as Method 2)

3. **Set environment variables**

4. **Every push to main branch** will trigger automatic deployment

---

## Post-Deployment Configuration

### Step 1: Verify Deployment

1. **Check health endpoint**:
   ```bash
   curl https://your-project.vercel.app/api/health
   ```
   Should return:
   ```json
   {"status": "ok", "service": "RealDevs API"}
   ```

2. **Check logs**:
   ```bash
   vercel logs [deployment-url]
   ```
   Or in Dashboard → Deployments → [deployment] → Functions → View Logs

### Step 2: Initialize Database

If using a fresh PostgreSQL database, tables need to be created:

**Option A: Via API endpoint** (if you add one):
```bash
curl -X POST https://your-project.vercel.app/api/init-db
```

**Option B: Create initialization script** (`apps/api/init_db.py`):

```python
"""Initialize database tables."""
from app import create_app
from app.models import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
```

Then run locally with production DATABASE_URL:
```bash
export DATABASE_URL="your-postgres-url"
python apps/api/init_db.py
```

**Option C: Use Alembic migrations** (recommended for production):

```bash
# Create migration
cd apps/api
alembic revision --autogenerate -m "Initial migration"

# Apply to production
DATABASE_URL="your-postgres-url" alembic upgrade head
```

### Step 3: Update Frontend API URL

Update your Next.js frontend to point to the Vercel backend:

**In `apps/web/.env.production` or Vercel environment variables**:
```
NEXT_PUBLIC_API_URL=https://your-backend.vercel.app/api
```

### Step 4: Test Endpoints

Test all critical endpoints:

```bash
# Health check
curl https://your-project.vercel.app/api/health

# Auth status
curl https://your-project.vercel.app/api/auth/status

# Diagnostics
curl https://your-project.vercel.app/api/diagnostics
```

---

## Troubleshooting

### Common Issues

#### 1. "Module not found" errors

**Problem**: Python dependencies not installed

**Solution**:
- Ensure `requirements.txt` is in `apps/api/`
- Check build logs in Vercel Dashboard
- Verify all dependencies are listed

#### 2. Database connection errors

**Problem**: Cannot connect to PostgreSQL

**Solutions**:
- Verify `DATABASE_URL` is set correctly
- Check database allows connections from Vercel IPs
- Ensure SSL is enabled (`?sslmode=require`)
- Test connection string locally:
  ```bash
  psql "your-connection-string"
  ```

#### 3. CORS errors

**Problem**: Frontend can't access API

**Solution**:
- Update `CORS_ORIGINS` to include your frontend URL
- Format: `https://your-frontend.vercel.app,https://yourdomain.com`
- No trailing slashes

#### 4. Timeout errors

**Problem**: Requests timing out (>10s for Hobby, >60s for Pro)

**Solutions**:
- Optimize slow endpoints (GitHub API calls)
- Add caching where possible
- Consider background jobs for long operations
- Upgrade Vercel plan for longer timeouts

#### 5. "Application error" on first request

**Problem**: Cold start or import error

**Solutions**:
- Check function logs in Vercel Dashboard
- Verify `vercel_handler.py` exports `app` correctly
- Test locally with `vercel dev`

#### 6. SQLite errors

**Problem**: Trying to write to SQLite on Vercel

**Solution**:
- Must use PostgreSQL or another cloud database
- SQLite is read-only on Vercel's filesystem

### Debugging Commands

```bash
# Test locally with Vercel
vercel dev

# View deployment logs
vercel logs [deployment-url]

# Inspect deployment
vercel inspect [deployment-url]

# Check environment variables
vercel env ls

# Pull environment variables
vercel env pull .env.local
```

### Viewing Logs

1. **Vercel Dashboard**:
   - Go to Deployments → [deployment] → Functions
   - Click on function → View Logs

2. **CLI**:
   ```bash
   vercel logs [deployment-url] --follow
   ```

---

## Best Practices

### 1. Database Connection Pooling

For serverless, use connection pooling:

```python
# In config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_size": 5,
    "max_overflow": 10,
}
```

### 2. Environment-Specific Configuration

Use different configs for different environments:

```python
# In Vercel, set FLASK_ENV=production
# Locally, use FLASK_ENV=development
```

### 3. Error Handling

Ensure all endpoints have proper error handling:

```python
try:
    # Your code
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    return jsonify({"ok": False, "error": str(e)}), 500
```

### 4. Rate Limiting

Consider adding rate limiting for production:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

### 5. Monitoring

Set up monitoring:

- **Vercel Analytics**: Built-in
- **Sentry**: Error tracking
- **Logtail**: Log aggregation
- **Uptime monitoring**: UptimeRobot, Pingdom

### 6. Security

- ✅ Use HTTPS (automatic on Vercel)
- ✅ Never commit secrets
- ✅ Rotate keys regularly
- ✅ Use strong secret keys (32+ characters)
- ✅ Enable database SSL
- ✅ Implement rate limiting
- ✅ Validate all inputs
- ✅ Use parameterized queries (SQLAlchemy does this)

### 7. Performance

- **Cache GitHub API responses** where possible
- **Use background jobs** for long operations
- **Optimize database queries** (add indexes)
- **Minimize cold starts** (keep functions warm with cron)

### 8. Cost Optimization

- **Use connection pooling** to reduce database connections
- **Cache responses** to reduce API calls
- **Monitor function execution time**
- **Use Vercel's free tier** limits wisely

---

## Deployment Checklist

Before deploying:

- [ ] Created `vercel.json` in project root
- [ ] Created `vercel_handler.py` entry point
- [ ] Updated `config.py` for PostgreSQL
- [ ] Added `psycopg2-binary` to `requirements.txt`
- [ ] Set up PostgreSQL database
- [ ] Generated secure `HIDEVS_SECRET_KEY`
- [ ] Configured `DATABASE_URL` environment variable
- [ ] Updated `CORS_ORIGINS` with production URLs
- [ ] Set `FLASK_ENV=production`
- [ ] Tested locally with `vercel dev`
- [ ] Initialized database tables
- [ ] Updated frontend API URL
- [ ] Tested all critical endpoints
- [ ] Set up monitoring/error tracking
- [ ] Documented deployment process

---

## Next Steps

After successful deployment:

1. **Set up custom domain** (optional):
   - Vercel Dashboard → Settings → Domains
   - Add your domain
   - Update DNS records

2. **Configure CI/CD**:
   - Automatic deployments on git push
   - Preview deployments for PRs

3. **Set up monitoring**:
   - Error tracking (Sentry)
   - Uptime monitoring
   - Performance monitoring

4. **Optimize**:
   - Add caching
   - Optimize database queries
   - Reduce cold starts

---

## Additional Resources

- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Flask on Vercel Guide](https://vercel.com/guides/deploying-flask-with-vercel)
- [PostgreSQL Connection Pooling](https://docs.sqlalchemy.org/en/14/core/pooling.html)

---

## Support

If you encounter issues:

1. Check Vercel function logs
2. Test locally with `vercel dev`
3. Verify environment variables
4. Check database connectivity
5. Review this guide's troubleshooting section

For project-specific issues, check the main [README.md](../README.md) or [DEPLOYMENT.md](./DEPLOYMENT.md).

---

**Last Updated**: 2024
**Maintained by**: RealDevs Team

