# Complete Vercel Deployment Guide

This guide walks you through deploying your entire RealDevs application on Vercel - both the Flask backend and PostgreSQL database.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Create Vercel Account](#step-1-create-vercel-account)
3. [Step 2: Set Up Vercel Postgres Database](#step-2-set-up-vercel-postgres-database)
4. [Step 3: Prepare Your Project](#step-3-prepare-your-project)
5. [Step 4: Deploy Backend to Vercel](#step-4-deploy-backend-to-vercel)
6. [Step 5: Connect Database to Backend](#step-5-connect-database-to-backend)
7. [Step 6: Initialize Database Tables](#step-6-initialize-database-tables)
8. [Step 7: Configure Environment Variables](#step-7-configure-environment-variables)
9. [Step 8: Test Your Deployment](#step-8-test-your-deployment)
10. [Step 9: Deploy Frontend (Optional)](#step-9-deploy-frontend-optional)
11. [Troubleshooting](#troubleshooting)
12. [Next Steps](#next-steps)

---

## Prerequisites

Before starting, ensure you have:

- ✅ **GitHub account** (or GitLab/Bitbucket)
- ✅ **Your code pushed to a Git repository**
- ✅ **Node.js installed** (for Vercel CLI - optional but recommended)
- ✅ **Python 3.12** (for local testing)

---

## Step 1: Create Vercel Account

1. **Go to [vercel.com](https://vercel.com)**

2. **Click "Sign Up"** (top right)

3. **Sign up with GitHub** (recommended):
   - Click "Continue with GitHub"
   - Authorize Vercel to access your repositories
   - This enables automatic deployments

4. **Complete your profile** (optional):
   - Choose a team name or use personal account
   - You can skip this and do it later

**✅ You now have a Vercel account!**

---

## Step 2: Set Up Vercel Postgres Database

### 2.1 Create Database

1. **Go to Vercel Dashboard**: [vercel.com/dashboard](https://vercel.com/dashboard)

2. **Click "Storage"** in the left sidebar (or go to [vercel.com/storage](https://vercel.com/storage))

3. **Click "Create Database"**

4. **Select "Postgres"**

5. **Configure Database**:
   - **Name**: `realdevs-db` (or any name you prefer)
   - **Region**: Choose closest to your users
     - `Washington, D.C., USA (iad1)` - US East
     - `San Francisco, USA (sfo1)` - US West
     - `Frankfurt, Germany (fra1)` - Europe
   - **Plan**: 
     - **Hobby** (Free): Good for development/testing
     - **Pro**: $20/month - For production

6. **Click "Create"**

7. **Wait for provisioning** (takes 1-2 minutes)

### 2.2 Get Connection String

Once your database is created:

1. **Click on your database** (`realdevs-db`)

2. **Go to ".env.local" tab**

3. **Copy the connection string** - It will look like:
   ```
   postgres://default:xxxxx@ep-xxxxx.us-east-1.postgres.vercel-storage.com:5432/verceldb
   ```

   **Important**: Vercel Postgres uses a different format. You may need to convert it to standard PostgreSQL format:
   ```
   postgresql://default:xxxxx@ep-xxxxx.us-east-1.postgres.vercel-storage.com:5432/verceldb?sslmode=require
   ```

4. **Save this connection string** - You'll need it in Step 5!

### 2.3 Alternative: Use Vercel Environment Variables

Vercel Postgres can automatically inject connection variables. You'll see:
- `POSTGRES_URL`
- `POSTGRES_PRISMA_URL`
- `POSTGRES_URL_NON_POOLING`

**For SQLAlchemy, use `POSTGRES_URL`** (or convert to `DATABASE_URL` format).

---

## Step 3: Prepare Your Project

Your project is already configured for Vercel! Let's verify:

### 3.1 Verify Configuration Files

✅ **`vercel.json`** - Already exists and configured  
✅ **`apps/api/vercel_handler.py`** - Serverless entry point exists  
✅ **`apps/api/config.py`** - Already supports PostgreSQL  
✅ **`apps/api/requirements.txt`** - Already includes `psycopg2-binary`  

**No code changes needed!**

### 3.2 Generate Secret Key

Generate a secure secret key for encryption:

```bash
# Option 1: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: OpenSSL
openssl rand -hex 32
```

**Save this key** - You'll need it in Step 7.

### 3.3 Ensure Code is in Git

Make sure your code is committed and pushed to GitHub:

```bash
# Check git status
git status

# If not committed, commit and push
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

---

## Step 4: Deploy Backend to Vercel

You have three options. Choose the easiest for you:

### Option A: Deploy via Vercel Dashboard (Easiest)

1. **Go to Vercel Dashboard**: [vercel.com/dashboard](https://vercel.com/dashboard)

2. **Click "Add New..."** → **"Project"**

3. **Import Git Repository**:
   - If you signed up with GitHub, you'll see your repositories
   - Click **"Import"** next to your RealDevs repository
   - If you don't see it, click **"Adjust GitHub App Permissions"** and grant access

4. **Configure Project**:
   - **Project Name**: `realdevs-api` (or any name)
   - **Framework Preset**: **Other** (or leave as "Other")
   - **Root Directory**: Leave as root (`.`)
   - **Build Command**: Leave empty (Vercel auto-detects Python)
   - **Output Directory**: Leave empty
   - **Install Command**: Leave empty

5. **Click "Deploy"**

6. **Wait for deployment** (2-5 minutes)

7. **Note your deployment URL**: `https://your-project.vercel.app`

### Option B: Deploy via Vercel CLI (Recommended for Developers)

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```
   Follow the prompts to authenticate.

3. **Navigate to project root**:
   ```bash
   cd /Users/test/Desktop/Hireal/RealDevs
   ```

4. **Link project** (first time only):
   ```bash
   vercel link
   ```
   - **Set up and develop?** → Yes
   - **Which scope?** → Select your account
   - **Link to existing project?** → No (or Yes if you created one in dashboard)
   - **Project name?** → `realdevs-api`
   - **Directory?** → Press Enter (use current directory)

5. **Deploy to production**:
   ```bash
   vercel --prod
   ```

6. **Note your deployment URL** from the output

### Option C: Automatic Deployments (After Initial Setup)

Once connected to Git:
- **Every push to `main` branch** → Auto-deploys to production
- **Every pull request** → Creates preview deployment

**✅ Your backend is now deployed!**

---

## Step 5: Connect Database to Backend

Now connect your Vercel Postgres database to your deployed backend:

### 5.1 Get Database Connection String

1. **Go to Vercel Dashboard** → **Storage** → Click on `realdevs-db`

2. **Go to ".env.local" tab**

3. **Copy `POSTGRES_URL`** or convert to standard format:
   ```
   postgresql://default:password@ep-xxxxx.us-east-1.postgres.vercel-storage.com:5432/verceldb?sslmode=require
   ```

### 5.2 Set Environment Variable in Vercel Project

1. **Go to Vercel Dashboard** → **Your Project** (`realdevs-api`)

2. **Go to Settings** → **Environment Variables**

3. **Add `DATABASE_URL`**:
   - Click **"Add New"**
   - **Key**: `DATABASE_URL`
   - **Value**: Paste your PostgreSQL connection string
   - **Environments**: Select all three:
     - ✅ Production
     - ✅ Preview
     - ✅ Development
   - Click **"Save"**

4. **Alternative**: If Vercel Postgres provides `POSTGRES_URL`, you can use that instead:
   - **Key**: `POSTGRES_URL` (or keep as `DATABASE_URL` and map it)
   - **Value**: The `POSTGRES_URL` from your database

**Note**: Your `config.py` reads `DATABASE_URL`, so make sure to use that key name.

---

## Step 6: Initialize Database Tables

Now initialize your database schema:

### Option A: Via Vercel CLI (Recommended)

1. **Pull environment variables locally**:
   ```bash
   cd /Users/test/Desktop/Hireal/RealDevs
   vercel env pull .env.local
   ```

2. **Set DATABASE_URL** (if not in .env.local):
   ```bash
   # Check .env.local
   cat .env.local
   
   # If DATABASE_URL is not there, add it:
   echo 'DATABASE_URL=your-postgres-connection-string' >> .env.local
   ```

3. **Initialize database**:
   ```bash
   cd apps/api
   export DATABASE_URL=$(grep DATABASE_URL ../.env.local | cut -d '=' -f2-)
   python init_db.py
   ```

### Option B: Via Python Script (Direct)

1. **Set environment variable**:
   ```bash
   export DATABASE_URL="postgresql://default:password@ep-xxxxx.us-east-1.postgres.vercel-storage.com:5432/verceldb?sslmode=require"
   ```

2. **Initialize database**:
   ```bash
   cd apps/api
   python init_db.py
   ```

   **Expected output**:
   ```
   Database tables created successfully!
   ```

### Option C: Via Vercel Function (If init_db.py doesn't work)

Create a temporary endpoint to initialize:

1. **Add to `apps/api/app/api/routes.py`** (temporary):
   ```python
   @api_bp.route('/init-db', methods=['POST'])
   def init_database():
       """Initialize database tables (one-time use)."""
       try:
           from app.models import db
           db.create_all()
           return jsonify({"ok": True, "message": "Database initialized"})
       except Exception as e:
           return jsonify({"ok": False, "error": str(e)}), 500
   ```

2. **Deploy and call once**:
   ```bash
   curl -X POST https://your-project.vercel.app/api/init-db
   ```

3. **Remove the endpoint** after use (security)

**✅ Your database is now initialized!**

---

## Step 7: Configure Environment Variables

Set all required environment variables in Vercel:

### 7.1 Go to Environment Variables

**Vercel Dashboard** → **Your Project** → **Settings** → **Environment Variables**

### 7.2 Add Required Variables

Add each of these:

#### 1. `HIDEVS_SECRET_KEY`
- **Key**: `HIDEVS_SECRET_KEY`
- **Value**: The secret key you generated in Step 3.2
- **Environments**: Production, Preview, Development

#### 2. `DATABASE_URL` (Already done in Step 5)
- ✅ Already set

#### 3. `FLASK_ENV`
- **Key**: `FLASK_ENV`
- **Value**: `production`
- **Environments**: Production, Preview, Development

#### 4. `CORS_ORIGINS`
- **Key**: `CORS_ORIGINS`
- **Value**: Your frontend URL(s), comma-separated:
  - For production: `https://your-frontend.vercel.app`
  - For local dev: `http://localhost:3000`
  - Example: `https://your-frontend.vercel.app,http://localhost:3000`
- **Important**: No trailing slashes!
- **Environments**: Production, Preview, Development

### 7.3 Verify All Variables

You should now have:
- ✅ `DATABASE_URL`
- ✅ `HIDEVS_SECRET_KEY`
- ✅ `FLASK_ENV`
- ✅ `CORS_ORIGINS`

### 7.4 Redeploy (If Needed)

After adding environment variables, Vercel may auto-redeploy. If not:

```bash
vercel --prod
```

Or trigger redeploy from dashboard: **Deployments** → **Redeploy**

**✅ Environment variables configured!**

---

## Step 8: Test Your Deployment

Test that everything is working:

### 8.1 Health Check

```bash
curl https://your-project.vercel.app/api/health
```

**Expected response**:
```json
{
  "status": "ok",
  "service": "RealDevs API"
}
```

### 8.2 Test Database Connection

```bash
# Auth status (tests database connection)
curl https://your-project.vercel.app/api/auth/status
```

**Expected response**:
```json
{
  "ok": true,
  "configured": false
}
```

### 8.3 Check Logs

If something doesn't work, check logs:

**Via CLI**:
```bash
vercel logs [your-deployment-url] --follow
```

**Via Dashboard**:
1. Go to **Deployments**
2. Click on your deployment
3. Click **"Functions"**
4. Click on function → **"View Logs"**

### 8.4 Test Full Flow

1. **Submit PAT**:
   ```bash
   curl -X POST https://your-project.vercel.app/api/auth/pat \
     -H "Content-Type: application/json" \
     -d '{"pat": "your-github-token", "store_mode": "encrypted"}'
   ```

2. **Check auth status**:
   ```bash
   curl https://your-project.vercel.app/api/auth/status
   ```

**✅ Your backend is working!**

---

## Step 9: Deploy Frontend (Optional)

If you want to deploy your Next.js frontend on Vercel too:

### 9.1 Deploy Frontend

1. **Go to Vercel Dashboard** → **Add New Project**

2. **Import your repository** (same repo or separate frontend repo)

3. **Configure**:
   - **Framework Preset**: **Next.js** (auto-detected)
   - **Root Directory**: `apps/web` (if monorepo)
   - **Build Command**: Leave default
   - **Output Directory**: Leave default

4. **Add Environment Variable**:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-backend.vercel.app/api`
   - **Environments**: All

5. **Click "Deploy"**

### 9.2 Update Backend CORS

Update `CORS_ORIGINS` in your backend to include frontend URL:

1. **Go to Backend Project** → **Settings** → **Environment Variables**

2. **Edit `CORS_ORIGINS`**:
   - Add your frontend URL: `https://your-frontend.vercel.app`
   - Example: `https://your-frontend.vercel.app,http://localhost:3000`

3. **Redeploy backend**

**✅ Full stack deployed on Vercel!**

---

## Troubleshooting

### Issue 1: "Module not found" errors

**Problem**: Python dependencies not installed

**Solution**:
- Verify `requirements.txt` is in `apps/api/`
- Check build logs in Vercel Dashboard
- Ensure all dependencies are listed

### Issue 2: Database connection fails

**Problem**: Cannot connect to Vercel Postgres

**Solutions**:
- Verify `DATABASE_URL` is set correctly
- Ensure connection string includes `?sslmode=require`
- Check database is running in Vercel Dashboard → Storage
- Verify you're using the correct connection string format

### Issue 3: CORS errors

**Problem**: Frontend can't access API

**Solution**:
- Update `CORS_ORIGINS` to include exact frontend URL
- No trailing slashes in URLs
- Format: `https://app1.vercel.app,https://app2.vercel.app`
- Redeploy after updating

### Issue 4: Timeout errors

**Problem**: Requests timing out

**Solutions**:
- **Hobby plan**: 10-second timeout
- **Pro plan**: 60-second timeout
- Optimize slow endpoints (GitHub API calls)
- Consider background jobs for long operations

### Issue 5: "Application error" on first request

**Problem**: Cold start or import error

**Solutions**:
- Check function logs in Vercel Dashboard
- Verify `vercel_handler.py` exports `app` correctly
- Test locally with `vercel dev`

### Issue 6: Database tables not found

**Problem**: `relation "repositories" does not exist`

**Solution**:
- Run `init_db.py` with correct `DATABASE_URL`
- Verify database initialization completed successfully
- Check database in Vercel Dashboard → Storage → Your DB → Data

---

## Next Steps

After successful deployment:

### 1. Set Up Custom Domain (Optional)

1. **Vercel Dashboard** → **Your Project** → **Settings** → **Domains**
2. **Add your domain**
3. **Update DNS records** as instructed

### 2. Set Up Monitoring

- **Vercel Analytics**: Built-in in dashboard
- **Function Logs**: Available in dashboard
- **Error Tracking**: Consider adding Sentry

### 3. Optimize Performance

- Add caching where possible
- Optimize database queries
- Reduce cold starts (keep functions warm)

### 4. Set Up Automatic Deployments

- Already enabled if connected to Git
- Every push to `main` → Production
- Every PR → Preview deployment

---

## Quick Reference

### Vercel Dashboard URLs

- **Dashboard**: [vercel.com/dashboard](https://vercel.com/dashboard)
- **Storage**: [vercel.com/storage](https://vercel.com/storage)
- **Documentation**: [vercel.com/docs](https://vercel.com/docs)

### Important Commands

```bash
# Deploy
vercel --prod

# Deploy preview
vercel

# Test locally
vercel dev

# View logs
vercel logs [url] --follow

# List deployments
vercel ls

# View environment variables
vercel env ls

# Pull environment variables
vercel env pull .env.local
```

### Environment Variables Summary

| Variable | Required | Example |
|----------|----------|---------|
| `DATABASE_URL` | ✅ | `postgresql://...` |
| `HIDEVS_SECRET_KEY` | ✅ | `your-32-char-key` |
| `FLASK_ENV` | ✅ | `production` |
| `CORS_ORIGINS` | ✅ | `https://app.vercel.app` |

---

## Deployment Checklist

Before going live, verify:

- [ ] Vercel account created
- [ ] Vercel Postgres database created
- [ ] Backend deployed to Vercel
- [ ] Database connection string configured
- [ ] Database tables initialized
- [ ] All environment variables set (4 variables)
- [ ] Health check endpoint working
- [ ] Database connection working
- [ ] CORS configured correctly
- [ ] Frontend deployed (if applicable)
- [ ] Frontend connected to backend
- [ ] Tested full flow (auth, repos, etc.)

---

## Summary

You now have:

✅ **Backend**: Deployed on Vercel as serverless functions  
✅ **Database**: Vercel Postgres (managed PostgreSQL)  
✅ **Frontend**: Can be deployed on Vercel (optional)  
✅ **Everything in one place**: Single dashboard for all services  

**Your RealDevs application is now fully deployed on Vercel!** 🎉

---

**Last Updated**: 2024  
**Status**: ✅ Complete deployment guide

