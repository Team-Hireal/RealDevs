# Vercel Quick Start Guide

Quick reference for deploying everything on Vercel.

## 🚀 5-Minute Setup

### 1. Create Vercel Account
- Go to [vercel.com](https://vercel.com) → Sign up with GitHub

### 2. Create Database (2 minutes)
```
Vercel Dashboard → Storage → Create Database → Postgres
- Name: realdevs-db
- Region: Choose closest
- Plan: Hobby (free) or Pro
- Copy connection string from .env.local tab
```

### 3. Deploy Backend (2 minutes)
```
Vercel Dashboard → Add New Project → Import Git Repository
- Framework: Other
- Root: . (root)
- Deploy!
```

### 4. Connect Database (1 minute)
```
Project → Settings → Environment Variables
- Add DATABASE_URL (from Step 2)
- Add HIDEVS_SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
- Add FLASK_ENV = production
- Add CORS_ORIGINS = https://your-frontend.vercel.app
```

### 5. Initialize Database
```bash
# Pull env vars
vercel env pull .env.local

# Initialize
cd apps/api
export DATABASE_URL=$(grep DATABASE_URL ../.env.local | cut -d '=' -f2-)
python init_db.py
```

### 6. Test
```bash
curl https://your-project.vercel.app/api/health
```

**Done!** ✅

---

## 📋 Environment Variables

| Variable | Value | Where to Get |
|----------|-------|--------------|
| `DATABASE_URL` | `postgresql://...` | Storage → Database → .env.local |
| `HIDEVS_SECRET_KEY` | `your-key-here` | Generate with Python |
| `FLASK_ENV` | `production` | Set manually |
| `CORS_ORIGINS` | `https://app.vercel.app` | Your frontend URL |

---

## 🔧 Common Commands

```bash
# Deploy
vercel --prod

# Test locally
vercel dev

# View logs
vercel logs [url] --follow

# Pull env vars
vercel env pull .env.local
```

---

## 🐛 Quick Troubleshooting

**Database connection fails?**
- Check `DATABASE_URL` includes `?sslmode=require`
- Verify database is running in Storage dashboard

**CORS errors?**
- Update `CORS_ORIGINS` with exact frontend URL (no trailing slash)
- Redeploy after updating

**Module not found?**
- Check `requirements.txt` is in `apps/api/`
- Review build logs in dashboard

---

## 📚 Full Guide

For detailed instructions, see [VERCEL_COMPLETE_GUIDE.md](./VERCEL_COMPLETE_GUIDE.md)

---

**Status**: ✅ Ready to deploy

