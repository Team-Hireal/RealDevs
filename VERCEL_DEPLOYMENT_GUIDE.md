# Vercel Deployment Guide - RealDevs Monorepo

## Overview

This guide explains how to deploy the RealDevs monorepo (Flask backend + Next.js frontend) to a single Vercel project.

## Architecture

```
RealDevs/
├── apps/
│   ├── api/          # Flask backend (Python)
│   ├── web/          # Next.js frontend
├── app.py            # Vercel entry point for Flask
├── package.json      # Root package.json for build orchestration
├── requirements.txt  # Python dependencies
└── vercel.json       # Vercel configuration
```

## Deployment Options

### Option 1: Separate Vercel Projects (Recommended by Vercel)

Deploy frontend and backend as separate Vercel projects sharing the same Git repository.

**Pros:**
- Native Vercel support for each framework
- Easier debugging and logs separation
- Better performance (optimized builds)
- Simpler configuration

**Steps:**
1. Import repository to Vercel twice
2. Project 1: Root Directory = `apps/web`, Framework = Next.js
3. Project 2: Root Directory = `apps/api`, Framework = Other
4. Configure environment variables for each project
5. Set up custom domains (e.g., `app.yourdomain.com` and `api.yourdomain.com`)

### Option 2: Single Vercel Project (Current Setup)

Deploy both frontend and backend to the same Vercel project with unified routing.

**Pros:**
- Single deployment
- Same origin (no CORS issues)
- Unified domain

**Cons:**
- More complex configuration
- Harder to debug
- May have performance limitations

## Current Setup Configuration

### 1. Root `package.json`

```json
{
  "scripts": {
    "vercel-build": "cd apps/web && npm install && npm run build",
    "build": "npm install --prefix apps/web && npm run build --prefix apps/web"
  }
}
```

The `vercel-build` script is automatically run by Vercel during deployment.

### 2. Root `requirements.txt`

Contains all Flask dependencies. Vercel automatically installs these.

### 3. `vercel.json`

Routes `/api/*` to Flask and everything else to Next.js:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build"
    },
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/app.py"
    },
    {
      "handle": "filesystem"
    },
    {
      "src": "/(.*)",
      "dest": "/apps/web/.next/$1"
    }
  ]
}
```

### 4. `app.py`

Vercel entry point that handles all API requests and serves frontend files.

## Environment Variables

### Backend (Flask)
Set these in Vercel Dashboard → Project Settings → Environment Variables:

```
FLASK_ENV=production
HIDEVS_SECRET_KEY=<your-secret-key>
DATABASE_URL=<your-database-url>
PYTHONPATH=.
```

### Frontend (Next.js)
No environment variables needed if using same domain (API is at `/api`).

For development (`.env.local` in `apps/web/`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Deployment Steps

### Initial Setup

1. **Install Vercel CLI** (optional):
   ```bash
   npm install -g vercel
   ```

2. **Connect to GitHub**:
   - Push your repository to GitHub
   - Go to https://vercel.com
   - Import your repository

3. **Configure Project**:
   - Root Directory: leave as `.` (project root)
   - Framework Preset: Other
   - Build Command: `npm run vercel-build`
   - Output Directory: `apps/web/.next`

4. **Set Environment Variables**:
   Add all required environment variables in Project Settings

5. **Deploy**:
   - Click "Deploy"
   - Vercel will automatically detect changes and redeploy on future commits

### Testing Deployment

After deployment:

1. Visit your Vercel URL (e.g., `your-project.vercel.app`)
2. Frontend should load
3. Test API endpoint: `https://your-project.vercel.app/api/health`

## Troubleshooting

### Issue: Frontend Not Loading

**Solution 1:** Verify build output
```bash
cd apps/web
npm run build
# Check if .next directory is created
```

**Solution 2:** Check Vercel logs
- Go to Vercel Dashboard → Deployments → Select deployment → View logs

### Issue: API Routes Not Working

**Solution 1:** Verify Python app loads
```bash
python app.py
# Should start Flask app
```

**Solution 2:** Check `app.py` paths are correct

### Issue: Build Failures

**Common causes:**
1. Missing dependencies in `requirements.txt` or `package.json`
2. Python version mismatch (Vercel uses Python 3.9 by default)
3. Node.js version mismatch

**Solutions:**
- Add `runtime.txt` with Python version:
  ```
  python-3.9
  ```
- Specify Node.js version in `package.json`:
  ```json
  {
    "engines": {
      "node": "18.x"
    }
  }
  ```

### Issue: Environment Variables Not Working

- Ensure variables are set in Vercel Dashboard
- Redeploy after adding variables
- For frontend variables, use `NEXT_PUBLIC_` prefix

## Alternative: Using Vercel CLI for Manual Deploy

```bash
# From project root
vercel

# For production
vercel --prod
```

## Monitoring

- View logs: Vercel Dashboard → Deployments → Logs
- Check function performance: Dashboard → Analytics
- Monitor errors: Dashboard → Logs → Filter by "Error"

## Custom Domain Setup

1. Go to Project Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. SSL certificates are automatically provisioned

## Database Considerations

For production, use a managed database service:
- **PostgreSQL**: Neon, Supabase, Railway
- **MongoDB**: MongoDB Atlas
- **SQLite**: Not recommended for Vercel (ephemeral filesystem)

Update `DATABASE_URL` environment variable accordingly.

## Best Practices

1. **Use environment variables** for all secrets and configuration
2. **Test locally** before deploying
3. **Monitor logs** after deployment
4. **Set up preview deployments** for branches
5. **Use production database** separate from development

## Support

- Vercel Documentation: https://vercel.com/docs
- Vercel Discord: https://vercel.com/discord
- GitHub Issues: Report issues in your repository

---

**Note**: For Phase 1 (local-first use), consider whether cloud deployment is necessary. If deploying, implement additional security measures for PAT storage and encryption.

