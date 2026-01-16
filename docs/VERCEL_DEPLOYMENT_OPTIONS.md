# Vercel Deployment Options Comparison

## Option 1: Single Project (Current Setup) ✅ CONFIGURED

### What It Is
Deploy both frontend and backend to one Vercel project with unified routing.

### Pros
- ✅ Single deployment process
- ✅ Same origin (no CORS issues)
- ✅ Unified domain
- ✅ Simpler for small teams

### Cons
- ⚠️ More complex configuration
- ⚠️ Harder to debug (mixed logs)
- ⚠️ Coupled deployment (both deploy together)

### When to Use
- Small projects
- MVP/prototype stage
- Single domain requirement
- Simple deployment workflow

### Configuration Files
```
RealDevs/
├── vercel.json        # Routes /api/* to Flask, /* to Next.js
├── app.py             # Flask entry point
├── package.json       # Root package.json
├── requirements.txt   # Python dependencies
└── apps/
    ├── api/           # Flask backend
    └── web/           # Next.js frontend
```

### Deployment Command
```bash
git push origin main
```
Vercel automatically detects changes and deploys both.

---

## Option 2: Separate Projects

### What It Is
Deploy frontend and backend as two separate Vercel projects from the same repository.

### Pros
- ✅ Clean separation of concerns
- ✅ Independent deployments
- ✅ Easier debugging (separate logs)
- ✅ Better scalability
- ✅ Native framework support

### Cons
- ⚠️ Requires CORS configuration
- ⚠️ Two separate deployments
- ⚠️ Need to manage two URLs (or use custom domains)

### When to Use
- Production applications
- Team with separate frontend/backend developers
- Need independent scaling
- Long-term project

### Setup Steps

#### Project 1: Frontend
1. Import repository to Vercel
2. Configure:
   - **Root Directory**: `apps/web`
   - **Framework**: Next.js
   - **Environment Variables**:
     ```
     NEXT_PUBLIC_API_URL=https://your-api.vercel.app
     ```

#### Project 2: Backend
1. Import same repository to Vercel (second time)
2. Configure:
   - **Root Directory**: `apps/api`
   - **Framework**: Other
   - **Build Command**: `pip install -r requirements.txt`
   - **Install Command**: (leave empty)
   - **Environment Variables**:
     ```
     FLASK_ENV=production
     HIDEVS_SECRET_KEY=<secret>
     CORS_ORIGINS=https://your-frontend.vercel.app
     ```

#### Update Flask CORS Configuration
In `apps/api/app/__init__.py`:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://your-frontend.vercel.app",
            "https://your-frontend-*.vercel.app",  # Preview deployments
            "http://localhost:3000"  # Local development
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

#### Update Frontend API Client
In `apps/web/src/lib/api.ts`:
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api';
```

---

## Comparison Matrix

| Feature | Single Project | Separate Projects |
|---------|---------------|-------------------|
| **Setup Complexity** | Medium | Low |
| **CORS Issues** | None | Need Configuration |
| **Independent Deployment** | No | Yes |
| **Debugging** | Mixed Logs | Separate Logs |
| **Scaling** | Coupled | Independent |
| **Cost (Free Tier)** | 1 Project | 2 Projects |
| **Custom Domains** | 1 Domain | 2 Subdomains |
| **Best For** | MVP, Prototypes | Production |

---

## Recommended Path

### For Your Current Stage (RealDevs Phase 1)

**Use Option 1 (Single Project)** ✅

**Reasons:**
1. You're in MVP/local-first phase
2. Simpler deployment for quick iterations
3. Single domain for ease of use
4. No CORS complexity

**When to Switch to Option 2:**
- Moving to Phase 2 (multi-user)
- Experiencing deployment conflicts
- Need independent scaling
- Team grows (separate frontend/backend teams)

---

## Migration Path (Option 1 → Option 2)

When you're ready to switch:

### Step 1: Prepare Backend
1. Add CORS configuration in Flask
2. Test locally with CORS enabled
3. Update environment variables

### Step 2: Deploy Backend Separately
1. Import repository to Vercel
2. Set Root Directory to `apps/api`
3. Configure environment variables
4. Note the deployment URL

### Step 3: Update & Deploy Frontend
1. Add `NEXT_PUBLIC_API_URL` environment variable
2. Update API client to use environment variable
3. Import repository to Vercel (new project)
4. Set Root Directory to `apps/web`
5. Deploy

### Step 4: Test & Validate
1. Test all API endpoints
2. Verify CORS working
3. Check authentication flow
4. Test on preview deployments

### Step 5: Cleanup
1. Delete original combined project (optional)
2. Update documentation
3. Update team documentation

---

## Domain Configuration Examples

### Option 1 (Single Project)
```
https://realdevs.vercel.app/          → Frontend (Next.js)
https://realdevs.vercel.app/api/*     → Backend (Flask)
```

### Option 2 (Separate Projects)
```
https://realdevs.vercel.app/          → Frontend (Next.js)
https://api-realdevs.vercel.app/api/* → Backend (Flask)
```

### Option 2 with Custom Domain
```
https://app.realdevs.com/             → Frontend (Next.js)
https://api.realdevs.com/api/*        → Backend (Flask)
```

---

## Quick Decision Guide

**Choose Option 1 if:**
- ✅ You're building an MVP
- ✅ You want simplest deployment
- ✅ You're a solo developer or small team
- ✅ You don't need independent scaling

**Choose Option 2 if:**
- ✅ You're building for production
- ✅ You have separate frontend/backend developers
- ✅ You need independent deployment cycles
- ✅ You want easier debugging

---

## Current Setup Status

✅ **Configured for Option 1 (Single Project)**

### Files Configured:
- ✅ `vercel.json` - Routing configuration
- ✅ `app.py` - Flask entry point
- ✅ `package.json` - Root package.json
- ✅ `requirements.txt` - Python dependencies
- ✅ `apps/web/next.config.js` - Next.js configuration

### Ready to Deploy:
1. Push to GitHub
2. Import to Vercel
3. Add environment variables
4. Deploy!

See `VERCEL_QUICKSTART.md` for detailed deployment steps.

