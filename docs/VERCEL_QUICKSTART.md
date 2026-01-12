# Vercel Deployment Quick Start

This is a condensed checklist for deploying the Flask backend to Vercel. For detailed instructions, see [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md).

## Prerequisites Checklist

- [ ] Vercel account created
- [ ] PostgreSQL database provisioned (Supabase, Neon, Railway, etc.)
- [ ] Vercel CLI installed: `npm i -g vercel`

## Quick Deployment Steps

### 1. Set Up Database

Get your PostgreSQL connection string:
```
postgresql://user:password@host:port/database?sslmode=require
```

### 2. Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Deploy via CLI

```bash
# Navigate to project root
cd /Users/test/Desktop/Hireal/RealDevs

# Login to Vercel
vercel login

# Link project (first time)
vercel link

# Set environment variables
vercel env add HIDEVS_SECRET_KEY
vercel env add DATABASE_URL
vercel env add FLASK_ENV production
vercel env add CORS_ORIGINS "https://your-frontend.vercel.app"

# Deploy
vercel --prod
```

### 4. Initialize Database

```bash
# Set DATABASE_URL locally
export DATABASE_URL="your-postgres-connection-string"

# Run initialization script
python apps/api/init_db.py
```

### 5. Test Deployment

```bash
# Health check
curl https://your-project.vercel.app/api/health

# Should return: {"status": "ok", "service": "RealDevs API"}
```

## Environment Variables Summary

| Variable | Required | Example |
|----------|----------|---------|
| `HIDEVS_SECRET_KEY` | ✅ | `your-32-char-secret-key` |
| `DATABASE_URL` | ✅ | `postgresql://user:pass@host/db` |
| `FLASK_ENV` | ✅ | `production` |
| `CORS_ORIGINS` | ✅ | `https://your-app.vercel.app` |

## Files Created for Vercel

- ✅ `vercel.json` - Vercel configuration
- ✅ `apps/api/vercel_handler.py` - Serverless entry point
- ✅ `.vercelignore` - Files to exclude
- ✅ `apps/api/init_db.py` - Database initialization script
- ✅ Updated `config.py` - PostgreSQL support
- ✅ Updated `requirements.txt` - Added `psycopg2-binary`

## Common Issues

**Database connection fails:**
- Verify `DATABASE_URL` format
- Check database allows external connections
- Ensure SSL is enabled (`?sslmode=require`)

**CORS errors:**
- Update `CORS_ORIGINS` with exact frontend URL
- No trailing slashes

**Module not found:**
- Check `requirements.txt` is in `apps/api/`
- Review build logs in Vercel Dashboard

## Next Steps

1. Update frontend `NEXT_PUBLIC_API_URL` to point to Vercel backend
2. Test all API endpoints
3. Set up monitoring (optional)
4. Configure custom domain (optional)

## Full Documentation

For detailed instructions, troubleshooting, and best practices, see:
- [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md) - Complete guide
- [DEPLOYMENT.md](./DEPLOYMENT.md) - General deployment info

---

**Need help?** Check the troubleshooting section in [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md)

