# Step-by-Step: Deploying Flask + SQL Database on Vercel

## ✅ Yes, You Can Deploy Flask + SQL on Vercel!

**Important Requirements:**
- ✅ Flask works perfectly on Vercel as serverless functions
- ⚠️ **SQLite will NOT work** (Vercel has a read-only filesystem)
- ✅ **PostgreSQL is required** (or other cloud databases like MySQL, etc.)

---

## Prerequisites

Before starting, ensure you have:

1. **Vercel Account**: [Sign up at vercel.com](https://vercel.com/signup) (free tier available)
2. **PostgreSQL Database**: Choose one:
   - [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres) (integrated, recommended)
   - [Supabase](https://supabase.com) (free tier: 500MB)
   - [Neon](https://neon.tech) (free tier: 3GB, serverless)
   - [Railway](https://railway.app) (free tier: $5 credit)
   - [Render](https://render.com) (free tier available)
3. **Vercel CLI**: Install with `npm i -g vercel`
4. **Git Repository**: Your code should be in GitHub/GitLab/Bitbucket

---

## Step 1: Set Up PostgreSQL Database

### Option A: Vercel Postgres (Easiest)

1. Go to your Vercel Dashboard
2. Navigate to **Storage** → **Create Database** → **Postgres**
3. Choose a name and region
4. Copy the connection string (you'll need this in Step 3)

### Option B: Supabase (Free Tier)

1. Go to [supabase.com](https://supabase.com) and sign up
2. Create a new project
3. Go to **Settings** → **Database**
4. Copy the connection string (format: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`)

### Option C: Neon (Serverless PostgreSQL)

1. Go to [neon.tech](https://neon.tech) and sign up
2. Create a new project
3. Copy the connection string from the dashboard

**Save your connection string** - you'll need it in Step 3!

---

## Step 2: Verify Project Configuration

Your project already has the necessary files configured:

✅ **`vercel.json`** - Already configured  
✅ **`apps/api/vercel_handler.py`** - Serverless entry point exists  
✅ **`apps/api/config.py`** - Already supports PostgreSQL  
✅ **`apps/api/requirements.txt`** - Already includes `psycopg2-binary`  

**No code changes needed!** Your project is already set up for Vercel.

---

## Step 3: Generate Secret Key

Generate a secure secret key for encryption:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Save this key** - you'll need it in the next step.

---

## Step 4: Install Vercel CLI and Login

```bash
# Install Vercel CLI (if not already installed)
npm i -g vercel

# Login to Vercel
vercel login
```

Follow the prompts to authenticate.

---

## Step 5: Link Your Project to Vercel

Navigate to your project root and link it:

```bash
cd /Users/test/Desktop/Hireal/RealDevs

# Link project to Vercel (first time only)
vercel link
```

When prompted:
- **Set up and develop?** → Yes
- **Which scope?** → Select your account
- **Link to existing project?** → No (or Yes if you already created one)
- **Project name?** → Enter a name (e.g., `realdevs-api`)
- **Directory?** → Press Enter (use current directory)

---

## Step 6: Set Environment Variables

Set all required environment variables:

```bash
# Set secret key
vercel env add HIDEVS_SECRET_KEY
# Paste the secret key you generated in Step 3
# Select: Production, Preview, Development (all three)

# Set database URL
vercel env add DATABASE_URL
# Paste your PostgreSQL connection string from Step 1
# Format: postgresql://user:password@host:port/database?sslmode=require
# Select: Production, Preview, Development (all three)

# Set Flask environment
vercel env add FLASK_ENV production
# Select: Production, Preview, Development (all three)

# Set CORS origins (replace with your frontend URL)
vercel env add CORS_ORIGINS
# Enter: https://your-frontend.vercel.app,https://yourdomain.com
# (No trailing slashes, comma-separated)
# Select: Production, Preview, Development (all three)
```

**Important Notes:**
- For each variable, select **all three environments** (Production, Preview, Development)
- The `DATABASE_URL` should include `?sslmode=require` at the end
- `CORS_ORIGINS` should be comma-separated URLs without trailing slashes

---

## Step 7: Initialize Database Tables

Before deploying, initialize your database tables. You have two options:

### Option A: Run Locally (Recommended)

```bash
# Set DATABASE_URL locally
export DATABASE_URL="your-postgres-connection-string-here"

# Run initialization script
cd apps/api
python init_db.py
```

### Option B: Create Tables After Deployment

After deployment, you can create an API endpoint to initialize tables, or run migrations.

---

## Step 8: Deploy to Vercel

Deploy your application:

```bash
# Make sure you're in the project root
cd /Users/test/Desktop/Hireal/RealDevs

# Deploy to production
vercel --prod
```

The deployment will:
1. Build your Flask application
2. Package dependencies
3. Deploy as serverless functions
4. Provide you with a deployment URL

**Save the deployment URL** - it will look like: `https://your-project.vercel.app`

---

## Step 9: Verify Deployment

Test that your API is working:

```bash
# Health check
curl https://your-project.vercel.app/api/health

# Should return: {"status": "ok", "service": "RealDevs API"}
```

If you get an error, check the logs:

```bash
# View deployment logs
vercel logs [your-deployment-url]
```

Or check in the Vercel Dashboard:
- Go to **Deployments** → Click on your deployment → **Functions** → **View Logs**

---

## Step 10: Update Frontend (If Applicable)

If you have a frontend (Next.js app), update it to use the Vercel backend:

1. **In Vercel Dashboard** (for your frontend project):
   - Go to **Settings** → **Environment Variables**
   - Add: `NEXT_PUBLIC_API_URL` = `https://your-backend.vercel.app/api`

2. **Or in your frontend code** (`apps/web/.env.production`):
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.vercel.app/api
   ```

---

## Step 11: Test All Endpoints

Test your critical API endpoints:

```bash
# Health check
curl https://your-project.vercel.app/api/health

# Auth status
curl https://your-project.vercel.app/api/auth/status

# Diagnostics (if available)
curl https://your-project.vercel.app/api/diagnostics
```

---

## Troubleshooting Common Issues

### Issue 1: "Module not found" errors

**Solution:**
- Verify `requirements.txt` is in `apps/api/` directory
- Check build logs in Vercel Dashboard
- Ensure all dependencies are listed

### Issue 2: Database connection fails

**Solutions:**
- Verify `DATABASE_URL` format is correct
- Ensure connection string includes `?sslmode=require`
- Check database allows external connections
- Test connection string locally:
  ```bash
  psql "your-connection-string"
  ```

### Issue 3: CORS errors

**Solution:**
- Update `CORS_ORIGINS` to include exact frontend URL
- No trailing slashes in URLs
- Format: `https://app1.vercel.app,https://app2.vercel.app`

### Issue 4: Timeout errors

**Solutions:**
- Hobby plan: 10-second timeout
- Pro plan: 60-second timeout
- Optimize slow endpoints
- Consider background jobs for long operations

### Issue 5: SQLite errors

**Solution:**
- **You MUST use PostgreSQL** - SQLite won't work on Vercel
- Ensure `DATABASE_URL` is set correctly
- Remove any SQLite fallback code in production

---

## Testing Locally with Vercel

Before deploying, test locally:

```bash
# Test with Vercel's local development server
vercel dev
```

This simulates the Vercel environment locally. Access your API at `http://localhost:3000`

---

## Viewing Logs

### Via CLI:
```bash
# View logs for a deployment
vercel logs [deployment-url] --follow

# List all deployments
vercel ls
```

### Via Dashboard:
1. Go to **Deployments**
2. Click on a deployment
3. Click **Functions**
4. Click **View Logs**

---

## Environment Variables Summary

| Variable | Required | Example | Notes |
|----------|----------|---------|-------|
| `HIDEVS_SECRET_KEY` | ✅ | `abc123...` | 32+ character secret key |
| `DATABASE_URL` | ✅ | `postgresql://...` | Must include `?sslmode=require` |
| `FLASK_ENV` | ✅ | `production` | Set to `production` for prod |
| `CORS_ORIGINS` | ✅ | `https://app.vercel.app` | Comma-separated, no trailing slashes |

---

## Deployment Checklist

Before deploying, verify:

- [ ] PostgreSQL database created and connection string obtained
- [ ] Secret key generated (`HIDEVS_SECRET_KEY`)
- [ ] Vercel CLI installed and logged in
- [ ] Project linked to Vercel (`vercel link`)
- [ ] All environment variables set (4 variables)
- [ ] Database tables initialized (if needed)
- [ ] Tested locally with `vercel dev` (optional but recommended)
- [ ] Frontend API URL updated (if applicable)

---

## Post-Deployment

### Automatic Deployments

Once connected to Git:
- **Every push to main** → Auto-deploys to production
- **Every PR** → Creates preview deployment

### Custom Domain

1. Go to **Settings** → **Domains**
2. Add your domain
3. Update DNS records as instructed

### Monitoring

- **Vercel Analytics**: Built-in in dashboard
- **Function Logs**: Available in dashboard
- **Error Tracking**: Consider adding Sentry

---

## Important Notes

1. **SQLite Won't Work**: Vercel's filesystem is read-only. You **must** use PostgreSQL or another cloud database.

2. **Serverless Functions**: Your Flask app runs as serverless functions. Each request may hit a different instance.

3. **Cold Starts**: First request after inactivity may be slower (1-3 seconds). Subsequent requests are fast.

4. **Timeout Limits**:
   - Hobby (Free): 10 seconds
   - Pro: 60 seconds
   - Enterprise: 300 seconds

5. **Connection Pooling**: Your config already includes connection pooling settings for PostgreSQL, which is essential for serverless.

---

## Next Steps

After successful deployment:

1. ✅ Set up monitoring (optional)
2. ✅ Configure custom domain (optional)
3. ✅ Set up CI/CD (automatic with Git integration)
4. ✅ Optimize performance (caching, etc.)

---

## Quick Reference Commands

```bash
# Deploy
vercel --prod

# Deploy preview
vercel

# Test locally
vercel dev

# View logs
vercel logs [url]

# List deployments
vercel ls

# View environment variables
vercel env ls

# Pull environment variables locally
vercel env pull .env.local
```

---

## Need More Help?

- **Detailed Guide**: See [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md)
- **Quick Start**: See [VERCEL_QUICKSTART.md](./VERCEL_QUICKSTART.md)
- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)

---

**Last Updated**: 2024  
**Status**: ✅ Ready for deployment

