# Vercel Deployment Troubleshooting

## Issue: Build Succeeds But Backend Not Working

### Symptoms
- ✅ Build completes successfully
- ✅ Dependencies install correctly
- ❌ API endpoints return 404 or don't work
- ❌ `/api/health` doesn't respond

### Solution 1: Verify vercel.json Configuration

Your `vercel.json` must include the `builds` section for Python functions:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/vercel_handler.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/vercel_handler.py"
    }
  ],
  "functions": {
    "api/vercel_handler.py": {
      "maxDuration": 60
    }
  }
}
```

**Key Points:**
- ✅ `builds` section is **required** for Python functions
- ✅ `src` must point to your handler file
- ✅ `use` must be `@vercel/python`
- ✅ Routes must match the handler path

### Solution 2: Check Handler File Location

Vercel expects Python handlers in the `api/` directory at the root:

```
project-root/
├── api/
│   ├── vercel_handler.py  ← Handler must be here
│   └── requirements.txt  ← Dependencies here
├── apps/
│   └── api/
│       └── ... (your Flask app)
└── vercel.json
```

### Solution 3: Verify Handler Exports

Your `api/vercel_handler.py` must export the Flask app:

```python
from run import app

# Export for Vercel
handler = app
# OR
# app  # Vercel will detect this too
```

### Solution 4: Check Function Logs

1. **Go to Vercel Dashboard** → Your Project → **Deployments**
2. **Click on your deployment**
3. **Click "Functions"**
4. **Click on `api/vercel_handler.py`**
5. **Click "View Logs"**

Look for:
- Import errors
- Path errors
- Database connection errors
- Any Python exceptions

### Solution 5: Test Locally with Vercel Dev

Test your configuration locally:

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Test locally
vercel dev
```

Then visit `http://localhost:3000/api/health`

If this works locally but not in production, check:
- Environment variables
- Database connection
- Path issues

### Solution 6: Verify Routes Are Working

Test the endpoint:

```bash
# Health check
curl https://your-project.vercel.app/api/health

# Should return:
# {"status": "ok", "service": "RealDevs API"}
```

If you get 404:
- Check `vercel.json` routes configuration
- Verify handler path matches route `dest`

If you get 500:
- Check function logs (see Solution 4)
- Verify environment variables are set
- Check database connection

---

## Common Errors and Fixes

### Error: "Cannot find module 'run'"

**Problem**: Handler can't find the Flask app

**Fix**: Update `api/vercel_handler.py`:

```python
import os
import sys

# Add apps/api to path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
apps_api_path = os.path.join(root_dir, 'apps', 'api')
sys.path.insert(0, os.path.abspath(apps_api_path))

from run import app
handler = app
```

### Error: "No module named 'app'"

**Problem**: Python path not set correctly

**Fix**: Ensure `sys.path.insert(0, ...)` comes before imports

### Error: 404 Not Found

**Problem**: Routes not configured correctly

**Fix**: 
1. Check `vercel.json` routes match your API paths
2. Verify handler path in `dest` matches actual file location
3. Ensure `builds` section is present

### Error: "Application error"

**Problem**: Runtime error in handler

**Fix**:
1. Check function logs in Vercel Dashboard
2. Verify all environment variables are set
3. Check database connection string
4. Ensure all dependencies are in `requirements.txt`

### Error: Database connection fails

**Problem**: `DATABASE_URL` not set or incorrect

**Fix**:
1. Go to **Settings** → **Environment Variables**
2. Verify `DATABASE_URL` is set
3. Check connection string format: `postgresql://...?sslmode=require`
4. Ensure database is running in Storage dashboard

---

## Debugging Steps

### Step 1: Check Build Output

In Vercel Dashboard → Deployments → Build Logs:
- ✅ Python version detected
- ✅ Virtual environment created
- ✅ Dependencies installed
- ✅ Build completed

### Step 2: Check Function Logs

In Vercel Dashboard → Deployments → Functions → Logs:
- Look for import errors
- Look for runtime errors
- Check if handler is being called

### Step 3: Test Endpoints

```bash
# Health check (should work)
curl https://your-project.vercel.app/api/health

# Auth status (tests database)
curl https://your-project.vercel.app/api/auth/status

# Check response
# - 200 = Working
# - 404 = Routes not configured
# - 500 = Runtime error (check logs)
```

### Step 4: Verify Configuration

```bash
# Check vercel.json syntax
cat vercel.json | python -m json.tool

# Verify handler exists
ls -la api/vercel_handler.py

# Check requirements.txt
cat api/requirements.txt
```

---

## Quick Fixes Checklist

- [ ] `vercel.json` has `builds` section
- [ ] Handler file is in `api/vercel_handler.py`
- [ ] Handler exports `app` or `handler = app`
- [ ] Routes in `vercel.json` match API paths
- [ ] `requirements.txt` is in `api/` directory
- [ ] All environment variables are set
- [ ] Database connection string is correct
- [ ] Tested locally with `vercel dev`

---

## Still Not Working?

1. **Check Vercel Documentation**: [vercel.com/docs/functions/serverless-functions/runtimes/python](https://vercel.com/docs/functions/serverless-functions/runtimes/python)

2. **Review Function Logs**: Most issues show up in logs

3. **Test Minimal Example**: Create a simple handler to verify setup:
   ```python
   # api/test.py
   def handler(request):
       return {"status": "ok"}
   ```

4. **Contact Support**: Vercel has excellent support in their dashboard

---

**Last Updated**: 2024

