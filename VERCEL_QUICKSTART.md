# Vercel Deployment Quickstart

## Overview

This monorepo contains:
- **Frontend**: Next.js app in `apps/web/`
- **Backend**: Flask API in `apps/api/`

Both deploy to the same Vercel project with unified routing.

## How It Works

```
User Request
    ↓
/api/* → Flask Backend (app.py)
/* → Next.js Frontend (apps/web/)
```

## Prerequisites

- GitHub account
- Vercel account (free tier works)
- Repository pushed to GitHub

## Deployment Steps

### 1. Import to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New..." → "Project"
3. Select your repository
4. Configure:
   - **Root Directory**: `.` (leave as default)
   - **Framework Preset**: Next.js (auto-detected)
   - Leave build settings as default

### 2. Set Environment Variables

In Vercel Dashboard → Settings → Environment Variables, add:

**Required for Backend:**
```
FLASK_ENV=production
HIDEVS_SECRET_KEY=<generate-a-strong-secret>
PYTHONPATH=.
```

**Optional:**
```
DATABASE_URL=<your-database-url-if-using-postgres>
```

**Frontend Environment Variables:**
No additional variables needed! API calls to `/api/*` automatically route to your Flask backend on the same domain.

### 3. Deploy

Click "Deploy" - Vercel will:
1. Install Python dependencies from `requirements.txt`
2. Build Next.js frontend
3. Configure routing automatically from `vercel.json`

## Project Structure

```
RealDevs/
├── apps/
│   ├── api/           # Flask backend
│   │   ├── app/
│   │   └── requirements.txt
│   └── web/           # Next.js frontend
│       ├── src/
│       ├── package.json
│       └── next.config.js
├── app.py             # Flask entry point for Vercel
├── package.json       # Root package.json
├── requirements.txt   # Python dependencies
└── vercel.json        # Deployment configuration
```

## Configuration Files

### vercel.json
Routes API requests to Flask and frontend requests to Next.js:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "apps/web/package.json",
      "use": "@vercel/next"
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
      "src": "/(.*)",
      "dest": "/apps/web/$1"
    }
  ]
}
```

### app.py
Vercel entry point that loads the Flask application:
```python
from app import create_app
app = create_app()
```

## Local Development

### Terminal 1 - Backend:
```bash
cd apps/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=8000
```

### Terminal 2 - Frontend:
```bash
cd apps/web
npm install
npm run dev
```

Frontend runs on `http://localhost:3000` and proxies API calls to `http://localhost:8000`.

## Testing Deployment

After deployment:

1. **Test Frontend**: Visit `https://your-project.vercel.app`
2. **Test API**: Visit `https://your-project.vercel.app/api/health`

Expected API response:
```json
{
  "status": "ok",
  "service": "RealDevs API"
}
```

## Troubleshooting

### Build Fails

**Issue**: Python dependencies installation fails

**Solution**: Check `requirements.txt` is at project root

**Issue**: Next.js build fails

**Solution**: Ensure `apps/web/package.json` has all dependencies

### API Not Working

**Issue**: 404 on `/api/*` routes

**Solution**: 
- Check `app.py` is at project root
- Verify `PYTHONPATH=.` in environment variables
- Check Vercel logs for Python errors

### Frontend Not Loading

**Issue**: Blank page or 404

**Solution**:
- Check build logs for Next.js errors
- Verify `apps/web/package.json` has `build` script
- Check browser console for errors

## Environment Variables Best Practices

1. **Never commit secrets** - Use Vercel dashboard
2. **Different values per environment**:
   - Use "Preview" for staging
   - Use "Production" for live deployment
3. **Regenerate PAT** for production use
4. **Use managed database** (not SQLite) for production

## Monitoring

- **Build Logs**: Deployments → Select deployment → View logs
- **Runtime Logs**: Project → Functions → Select function → Logs
- **Analytics**: Project → Analytics

## Updating Deployment

Vercel auto-deploys on every push to your main branch:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

## Custom Domain

1. Go to Project Settings → Domains
2. Add your domain
3. Update DNS records as instructed
4. SSL certificate auto-provisioned

## Cost Considerations

**Vercel Free Tier Includes:**
- 100 GB bandwidth/month
- Serverless function execution
- Automatic SSL
- Preview deployments

**May Need Paid Plan For:**
- High traffic (>100GB/month)
- Long-running serverless functions (>10s)
- Team collaboration features

## Alternative: Separate Projects

For better isolation, deploy as two separate Vercel projects:

**Project 1 - Frontend:**
- Root Directory: `apps/web`
- Framework: Next.js
- Domain: `app.yourdomain.com`

**Project 2 - Backend:**
- Root Directory: `apps/api`
- Framework: Other
- Domain: `api.yourdomain.com`

Then configure CORS and update frontend API URL.

## Support

- **Vercel Docs**: https://vercel.com/docs
- **Next.js Docs**: https://nextjs.org/docs
- **Flask Docs**: https://flask.palletsprojects.com/

## Security Notes

⚠️ **Important for Production:**
1. Use strong `HIDEVS_SECRET_KEY`
2. Implement rate limiting
3. Use managed PostgreSQL (not SQLite)
4. Set up proper CORS policies
5. Review PAT permissions
6. Enable Vercel authentication if needed

---

**Ready to Deploy?** Push to GitHub and import to Vercel!

