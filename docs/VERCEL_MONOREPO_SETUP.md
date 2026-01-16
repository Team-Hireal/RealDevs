# Vercel Monorepo Setup: Next.js + Flask in One Project

This guide covers deploying both your Next.js frontend and Flask backend inside **ONE Vercel project** using the monorepo structure.

## Overview

**Key Setup:**
- **Vercel Project Root Directory** = `apps/web` (Vercel detects and builds Next.js normally)
- **Flask Function entrypoint** = `apps/web/api/index.py` (Vercel Python serverless functions)
- **Backend code** = `apps/api/**` (reused via imports)

## Prerequisites

- ✅ GitHub repository with your code
- ✅ Vercel account (sign up at [vercel.com](https://vercel.com))
- ✅ Supabase account (for PostgreSQL database)
- ✅ All code changes from this setup committed to Git

---

## Step 1: Set Vercel Root Directory to `apps/web`

1. **Import your Git repository in Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New..." → "Project"
   - Import your GitHub repository

2. **Configure Root Directory:**
   - In Project Settings → **Build & Development Settings**
   - Set **Root Directory** = `apps/web`
   - Click "Save"

This makes Vercel treat `apps/web` as the app it builds and deploys.

---

## Step 2: Enable "Include Files Outside Root Directory"

Because your Vercel Root Directory is `apps/web`, but backend code is in `apps/api`, you need to enable this setting:

1. In Vercel Project Settings → **Monorepo** section
2. Enable **"Include files outside Root Directory"** or similar setting
3. This allows Vercel to access `apps/api/**` when building Python functions

**Alternative (if setting not available):** Move backend code inside `apps/web`:
- Move `apps/api/app` → `apps/web/backend/app`
- Update imports in `apps/web/api/index.py` accordingly

---

## Step 3: Configure Environment Variables

In Vercel Project → **Settings** → **Environment Variables**, add:

### Required Variables

- `DATABASE_URL` - Your Supabase PostgreSQL connection string
  - Get this from Supabase Dashboard → Project Settings → Database → Connection String
  - **Important:** Use the **pooler URL** (not direct) for serverless to avoid connection limits
  - Format: `postgresql://user:password@host:port/database?sslmode=require`

- `HIDEVS_SECRET_KEY` - Secret key for encryption (generate a secure random string)
  - You can generate one: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### Optional Variables

- `CORS_ORIGINS` - Comma-separated list of allowed origins (defaults to Vercel URL + localhost)
- `FLASK_ENV` - Set to `production` for production deployments
- `GITHUB_TOKEN` - If you need GitHub API access from serverless functions

**Apply to:** Production, Preview, and Development environments

---

## Step 4: Initialize Database

Vercel serverless functions are not suitable for running one-time init scripts. Initialize your database schema using one of these methods:

### Option A: Run Locally (Recommended)

1. Set `DATABASE_URL` in your local `.env` file to point to Supabase
2. Run the init script:
   ```bash
   cd apps/api
   python init_db.py
   ```

### Option B: Use Supabase SQL Editor

1. Go to Supabase Dashboard → SQL Editor
2. Run the SQL schema creation commands manually
3. Or export schema from local SQLite and adapt for PostgreSQL

---

## Step 5: Deploy

1. **Commit all changes:**
   ```bash
   git add .
   git commit -m "Setup Vercel monorepo deployment"
   git push
   ```

2. **Vercel will auto-build:**
   - Next.js from `apps/web`
   - Python function(s) from `apps/web/api/*`
   - Automatic deployment on every push to main branch

3. **Verify deployment:**
   - Frontend: `https://<your-domain>/` should load Next.js dashboard
   - Backend: `https://<your-domain>/api/health` should respond from Flask

---

## Step 6: Local Development

For local development, the setup automatically handles routing:

- **Frontend:** `npm run dev` in `apps/web` (runs on port 3000)
- **Backend:** Run Flask server in `apps/api` (runs on port 8000)
- **Next.js rewrites:** Automatically proxy `/api/*` to `http://127.0.0.1:8000/api/*` in development

The `next.config.js` is configured to only rewrite in development mode, so production uses Vercel's serverless functions.

---

## Project Structure

```
RealDevs/
├── apps/
│   ├── api/                    # Backend code (Flask app)
│   │   ├── app/
│   │   │   ├── __init__.py     # Flask factory (create_app)
│   │   │   ├── api/
│   │   │   ├── models/
│   │   │   └── services/
│   │   ├── config.py
│   │   └── requirements.txt
│   │
│   └── web/                    # Frontend (Next.js) - VERCEL ROOT
│       ├── api/                # Vercel Python Functions entrypoint
│       │   ├── index.py        # Flask app entrypoint
│       │   └── requirements.txt # Python deps for functions
│       ├── src/
│       │   ├── app/
│       │   └── lib/
│       │       └── api.ts      # API client (uses /api route)
│       └── next.config.js      # Dev-only rewrites
│
└── vercel.json                 # (Not used when root is apps/web)
```

---

## Important Notes

### Function Bundle Size

Vercel Python Functions have size limits. To keep bundles small:

- ✅ `.vercelignore` already excludes `venv/`, `node_modules/`, `*.db`
- ✅ Don't commit large test files or artifacts
- ✅ Use `apps/web/api/requirements.txt` (not the full `apps/api/requirements.txt`)

### Database Connection

- ✅ **Use PostgreSQL** (Supabase) - SQLite won't work on serverless
- ✅ **Use connection pooling** - Prefer Supabase pooler URL over direct connection
- ✅ **Configure SSL** - The config automatically adds `sslmode=require` for PostgreSQL

### Long-Running Operations

Serverless functions have execution time limits (~10s on Hobby, ~60s on Pro). If sync operations take too long:

- Break into smaller paginated calls
- Move heavy sync to Vercel Cron Jobs
- Store results in database for quick retrieval

### CORS

CORS is automatically configured:
- Production: Allows requests from your Vercel domain
- Development: Allows `localhost:3000-3003`
- Override with `CORS_ORIGINS` env var if needed

---

## Troubleshooting

### "Module not found" errors

- **Problem:** Vercel can't find `apps/api` modules
- **Solution:** Enable "Include files outside Root Directory" in Vercel settings

### Database connection errors

- **Problem:** Can't connect to Supabase
- **Solution:** 
  - Verify `DATABASE_URL` is set correctly
  - Use pooler URL (not direct connection)
  - Check Supabase firewall settings

### Function timeout

- **Problem:** Requests timing out
- **Solution:** 
  - Break long operations into smaller chunks
  - Use background jobs (Vercel Cron) for heavy syncs
  - Upgrade Vercel plan for longer timeouts

### CORS errors

- **Problem:** Frontend can't call `/api` endpoints
- **Solution:** 
  - Verify `CORS_ORIGINS` includes your Vercel domain
  - Check that frontend uses relative `/api` URLs (not absolute)

---

## Next Steps

1. ✅ Deploy and verify both frontend and backend work
2. ✅ Test authentication flow
3. ✅ Test GitHub sync functionality
4. ✅ Set up Vercel Cron Jobs for periodic syncs (if needed)
5. ✅ Configure custom domain (optional)

---

## References

- [Vercel: Python and JavaScript in the same app](https://vercel.com/kb/guide/how-to-use-python-and-javascript-in-the-same-application)
- [Vercel: Flask on Vercel](https://vercel.com/docs/frameworks/backend/flask)
- [Vercel: Python Runtime](https://vercel.com/docs/functions/runtimes/python)
- [Vercel: Monorepo Guide](https://vercel.com/docs/monorepos)

