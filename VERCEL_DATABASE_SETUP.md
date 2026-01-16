# Vercel Database Setup Guide

This guide will help you set up a PostgreSQL database for your RealDevs application deployed on Vercel.

## Table of Contents
1. [Option 1: Vercel Postgres (Recommended)](#option-1-vercel-postgres-recommended)
2. [Option 2: External PostgreSQL (Railway, Neon, etc.)](#option-2-external-postgresql)
3. [Database Initialization](#database-initialization)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

---

## Option 1: Vercel Postgres (Recommended)

Vercel offers a managed PostgreSQL database that integrates seamlessly with your deployment.

### Step 1: Create Vercel Postgres Database

1. Go to your Vercel Dashboard: https://vercel.com/dashboard
2. Select your RealDevs project
3. Navigate to the **Storage** tab
4. Click **Create Database**
5. Select **Postgres**
6. Choose a database name (e.g., `realdevs-db`)
7. Select a region (choose closest to your users)
8. Click **Create**

### Step 2: Connect Database to Project

1. After creation, Vercel will show you the database details
2. Click **Connect Project**
3. Select your RealDevs project
4. Choose which environments to connect:
   - ✅ Production
   - ✅ Preview
   - ✅ Development
5. Click **Connect**

### Step 3: Verify Environment Variables

Vercel automatically adds these environment variables to your project:

```bash
POSTGRES_URL="postgres://..."              # Full connection string
POSTGRES_PRISMA_URL="postgres://..."       # Connection pooling URL
POSTGRES_URL_NON_POOLING="postgres://..."  # Direct connection URL
POSTGRES_USER="..."
POSTGRES_HOST="..."
POSTGRES_PASSWORD="..."
POSTGRES_DATABASE="..."
```

Your application will automatically use `POSTGRES_URL_NON_POOLING` for serverless functions.

---

## Option 2: External PostgreSQL

If you prefer to use an external PostgreSQL provider:

### Recommended Providers

1. **Railway** - https://railway.app
   - Free tier available
   - Easy PostgreSQL setup
   - Good for development

2. **Neon** - https://neon.tech
   - Serverless PostgreSQL
   - Free tier available
   - Built for serverless

3. **Supabase** - https://supabase.com
   - Free tier available
   - Includes auth and storage
   - PostgreSQL + extras

### Setup Steps (Railway Example)

1. Go to https://railway.app and sign up
2. Click **New Project** → **Provision PostgreSQL**
3. Once created, click on the PostgreSQL service
4. Go to **Variables** tab
5. Copy the `DATABASE_URL` value

### Add to Vercel

1. Go to your Vercel project
2. Navigate to **Settings** → **Environment Variables**
3. Add a new variable:
   - **Key**: `DATABASE_URL`
   - **Value**: `postgresql://user:pass@host:port/database`
   - **Environments**: Production, Preview, Development
4. Click **Save**

---

## Database Initialization

After setting up your database, you need to create the necessary tables.

### Method 1: Using the Database Initialization Endpoint (Easiest)

1. Wait for your Vercel deployment to complete
2. Visit: `https://your-app.vercel.app/api/_db_init`
   - This will show you the database status
3. If tables are missing, send a POST request:
   ```bash
   curl -X POST https://your-app.vercel.app/api/_db_init
   ```
4. Verify the response shows all tables created

### Method 2: Using Vercel CLI

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Link your project:
   ```bash
   vercel link
   ```

3. Pull environment variables:
   ```bash
   vercel env pull
   ```

4. Run the initialization script:
   ```bash
   cd apps/api
   python init_db.py
   ```

### Method 3: Direct Database Access

If you have direct access to your database:

```sql
-- Run the following SQL to create tables
-- (Or use a PostgreSQL client like pgAdmin or DBeaver)

-- See apps/api/app/models/__init__.py for full schema
```

---

## Verification

### Check Database Status

Visit: `https://your-app.vercel.app/api/_db_init` (GET request)

You should see:

```json
{
  "ok": true,
  "configured": true,
  "connected": true,
  "database_type": "PostgreSQL",
  "tables_found": [
    "auth_tokens",
    "contributors",
    "daily_stats",
    "external_commits",
    "external_contributors",
    "internal_orgs",
    "repositories",
    "settings",
    "team_members"
  ],
  "tables_missing": [],
  "initialized": true
}
```

### Test API Endpoints

1. **Health Check**:
   ```bash
   curl https://your-app.vercel.app/api/health
   ```

2. **Auth Status**:
   ```bash
   curl https://your-app.vercel.app/api/auth/status
   ```

3. **Team Members**:
   ```bash
   curl https://your-app.vercel.app/api/team-members
   ```

All should return proper JSON responses without errors.

---

## Troubleshooting

### Error: "Database URL not configured"

**Solution**: Ensure one of these environment variables is set in Vercel:
- `DATABASE_URL`
- `POSTGRES_URL_NON_POOLING`
- `POSTGRES_URL`

Check in: Vercel Dashboard → Project → Settings → Environment Variables

### Error: "Database connection failed"

**Possible causes**:

1. **Wrong connection string format**
   - Make sure it starts with `postgresql://` (not `postgres://`)
   - The application automatically converts `postgres://` to `postgresql://`

2. **SSL mode not configured**
   - The application automatically adds `?sslmode=require`
   - Some providers require specific SSL settings

3. **Firewall/IP restrictions**
   - Vercel functions run from dynamic IPs
   - Ensure your database allows connections from any IP (0.0.0.0/0)
   - Or use Vercel Postgres which handles this automatically

### Error: "Tables missing" after initialization

**Solution**: Run the POST request to create tables:

```bash
curl -X POST https://your-app.vercel.app/api/_db_init
```

### Error: "Module import failed"

**Solution**: Ensure `requirements.txt` includes all dependencies:

```txt
Flask==3.1.2
Flask-CORS==5.0.0
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.36
psycopg2-binary==2.9.9
httpx==0.28.1
cryptography==44.0.0
```

### Database is slow or timing out

**Solutions**:

1. **Use connection pooling URL**:
   - Change environment variable from `POSTGRES_URL_NON_POOLING` to `POSTGRES_URL`

2. **Increase timeout**:
   - Add to environment variables: `SQLALCHEMY_POOL_TIMEOUT=30`

3. **Choose closer region**:
   - Recreate database in a region closer to your users

### Data not persisting

**Check**:

1. Are you using the production database?
   - Preview/branch deployments use preview environment variables
   - Make sure you're testing on the production URL

2. Are commits being made?
   ```python
   session.commit()  # Must be called after changes
   ```

---

## Security Best Practices

1. **Secret Key**: Generate a strong secret key:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Add as `HIDEVS_SECRET_KEY` in Vercel environment variables

2. **Database Credentials**: Never commit database URLs to git

3. **Database Backups**: 
   - Vercel Postgres: Automatic backups included
   - External providers: Enable automatic backups

4. **Remove initialization endpoint**: After setup, consider removing or protecting `/api/_db_init`

---

## Next Steps

After database setup:

1. ✅ Visit your deployed site
2. ✅ Go to **Credentials** page
3. ✅ Add your GitHub PAT or username
4. ✅ Configure team members
5. ✅ Select repositories to track
6. ✅ Sync data
7. ✅ View dashboard

---

## Need Help?

- Check Vercel logs: Dashboard → Project → Deployments → (select deployment) → Function Logs
- Check database logs: Storage → (select database) → Logs
- Review error messages in browser console (F12)

---

## Reference Links

- Vercel Postgres Docs: https://vercel.com/docs/storage/vercel-postgres
- SQLAlchemy Docs: https://docs.sqlalchemy.org/
- PostgreSQL Docs: https://www.postgresql.org/docs/

