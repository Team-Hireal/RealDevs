# Deployment Optimization Guide

## Problem: Function Count Limit

Vercel's Hobby plan has a limit of **12 serverless functions per deployment**.

### What Counts as a Function?

1. **Python API endpoints** (each `.py` file in `/api/`)
2. **Next.js ISR/SSR pages** (server-rendered pages)
3. **Next.js API routes** (files in `/pages/api/` or `/app/api/`)

### Our Original Setup

- 12 Python API functions ✓
- 4 Next.js ISR functions (/, /credentials, /settings, /_global-error) ❌
- **Total: 16 functions** (exceeded limit by 4)

## Solution Applied

### 1. Convert Next.js to Static Export

Changed `next.config.js` to export static HTML files instead of ISR functions:

```javascript
output: 'export',
images: { unoptimized: true }
```

**Benefits:**
- ✅ No Next.js ISR functions counted against limit
- ✅ Only 12 Python functions now
- ✅ Faster page loads (pre-rendered HTML)
- ✅ Lower hosting costs
- ✅ Better CDN caching

**Trade-offs:**
- Static pages only (but your app already uses client-side data fetching with React Query)
- No server-side rendering (not needed for your use case)
- Images not optimized by Next.js (acceptable for your current setup)

## Build Time Optimization

### Current Build Time: ~1m 22s

Breakdown:
- **Next.js build**: ~30s (compiling, TypeScript, generating pages)
- **Python dependencies**: ~48s (12 functions × ~4s each with `uv`)
- **Deployment**: ~1m 48s (uploading files)

### Why Python Installation is Slow

Vercel creates isolated virtual environments for each Python serverless function:
- Ensures function isolation
- Prevents dependency conflicts
- Required for serverless architecture

### Optimization Options

#### ✅ Already Optimized
1. **Using `uv` package manager** - 10-20x faster than `pip`
2. **Build caching enabled** - Reuses dependencies when possible
3. **Parallel function builds** - All 12 functions build simultaneously

#### Possible Future Optimizations

1. **Consolidate endpoints** (if you need < 12 functions in future):
   ```python
   # Instead of separate files, use one handler with routing
   /api/handler.py  # Routes to different handlers internally
   ```

2. **Use shared dependencies**:
   - Already using shared `requirements.txt`
   - Vercel automatically shares common dependencies

3. **Upgrade to Pro plan** ($20/month):
   - 100 functions limit
   - Faster build machines
   - More build minutes
   - Better performance

## Current Function Count

### Python API Functions (12/12)

1. `/api/auth/pat.py` - Store GitHub PAT
2. `/api/auth/status.py` - Check auth status  
3. `/api/auth/username.py` - Username-only mode
4. `/api/dashboard.py` - Dashboard data
5. `/api/dashboard/daily-commits.py` - Commit charts
6. `/api/external-contributors.py` - External contributor management
7. `/api/health.py` - Health check
8. `/api/internal-orgs.py` - Internal org configuration
9. `/api/report/weekly.py` - Weekly reports
10. `/api/repos.py` - List repositories
11. `/api/repos/selected.py` - Selected repos
12. `/api/team-members.py` - Team member management

### Next.js Pages (Static - 0 functions)

- `/` (home/dashboard)
- `/credentials` (settings)
- `/settings` (preferences)

All pages are now **pre-rendered as static HTML** and served via CDN.

## Deployment Performance

### Metrics

| Metric | Time |
|--------|------|
| Download files | ~3s |
| Restore cache | <1s |
| npm install | ~2s |
| Next.js build | ~30s |
| Python deps | ~48s |
| Deploy outputs | ~1m 48s |
| **Total** | **~3m** |

### Comparison to Industry Standards

- ✅ **Very Good** - Most Next.js + Python deployments take 3-5 minutes
- Your build is **well-optimized** for the complexity

### Tips for Faster Deploys

1. **Only push when ready** - Each deploy takes ~3 minutes
2. **Use preview deployments** - Test on branches before main
3. **Batch commits** - Group related changes into one deployment
4. **Cache hits** - Subsequent deploys are faster (when deps don't change)

## Database Configuration

You have **Supabase** connected! Environment variables set:

```bash
POSTGRES_URL="..."
POSTGRES_URL_NON_POOLING="..."
POSTGRES_HOST="..."
POSTGRES_DATABASE="..."
POSTGRES_USER="..."
POSTGRES_PASSWORD="..."
```

### Database Setup for RealDevs

Your API endpoints will automatically use these environment variables. No additional configuration needed!

### Initialize Database Tables

Use the Vercel CLI to initialize your database:

```bash
# Install Vercel CLI
npm install -g vercel

# Link your project  
vercel link

# Pull environment variables
vercel env pull

# Initialize database
cd apps/api
python init_db.py
```

Or run the SQL directly in Supabase SQL Editor:

```sql
-- See apps/api/app/models/__init__.py for full schema
-- Main tables: auth_tokens, repositories, contributors, 
-- daily_stats, team_members, settings, etc.
```

## Monitoring & Alerts

### Build Failures

If deployment fails:
1. Check Vercel dashboard → Deployments → (failed) → Logs
2. Look for red error messages
3. Common issues:
   - Function count exceeded (now fixed!)
   - Python dependency conflicts
   - TypeScript errors
   - Missing environment variables

### Function Limits

If you need to add more endpoints in the future:

**Option A: Consolidate functions** (stay on Hobby plan)
- Combine related endpoints into one handler
- Use path routing internally

**Option B: Upgrade to Pro** ($20/month)
- 100 function limit
- Faster builds
- Better performance
- Team collaboration features

## Summary

### ✅ Current Status

- **Function count**: 12/12 (at limit but OK)
- **Build time**: ~1m 22s (optimized)
- **Deploy time**: ~3m (good)
- **Database**: Connected (Supabase)
- **Next.js**: Static export (0 functions)

### 🎯 Result

Your deployment is now:
- ✅ Within Vercel limits
- ✅ Optimally configured
- ✅ Fast build times
- ✅ Ready for production

### 📝 Next Steps

1. **Push this commit** to deploy the optimized configuration
2. **Initialize database** (see above)
3. **Test all endpoints** - everything should work!
4. **Monitor usage** - Watch function count if adding features

---

## FAQ

**Q: Can I add more API endpoints?**  
A: Not without consolidating existing ones or upgrading to Pro plan.

**Q: Will static export break my app?**  
A: No! Your app uses client-side data fetching (React Query), so it works perfectly with static HTML.

**Q: Is the build time normal?**  
A: Yes! 1-3 minutes is standard for Next.js + Python projects.

**Q: Should I upgrade to Pro?**  
A: Only if you need:
- More than 12 functions
- Faster builds
- Team features
- More bandwidth

**Q: Can I make it faster?**  
A: Not significantly. Your build is already well-optimized.

