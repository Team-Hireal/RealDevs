# Quick Fix Guide - Get RealDevs Running in 15 Minutes

🎯 **Goal:** Fix database connectivity and get the app fully functional

---

## Current Status

✅ **WORKING:**
- Frontend fully functional
- Navigation and UI working
- GitHub integration code ready
- API endpoints responding

❌ **NOT WORKING:**
- Database endpoints returning 500 errors
- Cannot save/retrieve data
- Team members, contributors, settings cannot be stored

---

## The Problem

**Missing:** PostgreSQL database connection

The app needs these environment variables in Vercel:
- `POSTGRES_URL_NON_POOLING` (preferred)
- `POSTGRES_URL` (alternative)
- `DATABASE_URL` (fallback)

---

## The Solution (15 minutes)

### Step 1: Create Database (5 min)

#### Option A: Neon (Recommended - Easiest)

1. Go to https://neon.tech
2. Sign up (GitHub SSO available)
3. Click "Create Project"
4. Name it: `realdevs`
5. Region: Choose closest to you
6. Click "Create Project"
7. Copy the **Connection string** (non-pooling)

#### Option B: Supabase

1. Go to https://supabase.com
2. Sign up
3. Create new project
4. Name: `realdevs`
5. Set database password (save it!)
6. Wait for provisioning (~2 min)
7. Go to Settings → Database
8. Copy "Connection string" (Transaction mode)

---

### Step 2: Initialize Database (3 min)

#### If you have `psql` installed:

```bash
# Navigate to project directory
cd ~/Desktop/Hireal/RealDevs

# Run the initialization script
psql "YOUR_CONNECTION_STRING_HERE" < init_supabase.sql

# Verify tables were created
psql "YOUR_CONNECTION_STRING_HERE" -c "\dt"
```

#### If you DON'T have `psql`:

**For Neon:**
1. Install Neon CLI: `npm i -g neonctl`
2. Run: `neonctl sql < init_supabase.sql`

**For Supabase:**
1. Go to your project dashboard
2. Click "SQL Editor" in left sidebar
3. Click "New Query"
4. Open `init_supabase.sql` in a text editor
5. Copy all contents
6. Paste into Supabase SQL Editor
7. Click "Run"
8. Verify success: You should see "SUCCESS! ✓" message

---

### Step 3: Configure Vercel (5 min)

#### Option A: Via Vercel Dashboard (Easiest)

1. Go to https://vercel.com/hireal-projects/real-devs
2. Click "Settings" tab
3. Click "Environment Variables"
4. Click "Add New"
5. Set:
   - **Key:** `POSTGRES_URL_NON_POOLING`
   - **Value:** (paste your connection string)
   - **Environments:** Production, Preview, Development (select all)
6. Click "Save"

#### Option B: Via CLI

```bash
# Navigate to project
cd ~/Desktop/Hireal/RealDevs

# Add environment variable
vercel env add POSTGRES_URL_NON_POOLING
# When prompted: paste your connection string
# When asked for environments: select all (a)

# Verify it was added
vercel env ls
```

---

### Step 4: Redeploy (2 min)

```bash
# Deploy with new environment variable
vercel --prod

# Wait for deployment to complete (~2-3 minutes)
# You'll get a new URL or confirmation
```

---

## Verification

Test that everything works:

### 1. Test API Endpoints

```bash
# Health check (should work)
curl https://real-devs-oo4m2788k-hireal-projects.vercel.app/api/health

# Team members (should now return 200 with empty array)
curl https://real-devs-oo4m2788k-hireal-projects.vercel.app/api/team-members

# Should see: {"members":[]}
```

### 2. Test in Browser

1. Go to: https://real-devs-oo4m2788k-hireal-projects.vercel.app
2. Click "Credentials"
3. Click "Username (Public Only)" tab
4. Enter a GitHub username (e.g., "torvalds")
5. Click "Submit"
6. Should see success message
7. Refresh page - username should persist!

---

## Troubleshooting

### ❌ Still getting 500 errors?

**Check environment variable:**
```bash
vercel env ls
```
Should show `POSTGRES_URL_NON_POOLING` in the list.

**Check database connection string format:**
Should look like:
```
postgresql://[user]:[password]@[host]/[database]?sslmode=require
```

**Check database tables:**
```bash
psql "YOUR_CONNECTION_STRING" -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
```
Should show 8 tables:
- auth_tokens
- contributors  
- daily_stats
- external_commits
- external_contributors
- repositories
- settings
- team_members

---

### ❌ Can't connect to database?

**Verify connection string works:**
```bash
psql "YOUR_CONNECTION_STRING" -c "SELECT 1;"
```
Should output: `1`

If it fails:
- Check password is correct
- Check host is accessible
- Check SSL mode is set (`sslmode=require`)

---

### ❌ Vercel CLI not working?

**Install/update:**
```bash
npm i -g vercel@latest
vercel login
```

**Or use dashboard:** All steps can be done via Vercel web interface

---

## After Fix - What to Test

✅ **Frontend:**
- [ ] Dashboard loads
- [ ] Can navigate to Credentials
- [ ] Can navigate to Settings

✅ **GitHub Integration:**
- [ ] Can enter GitHub username
- [ ] Can submit username
- [ ] Username persists after refresh
- [ ] User info fetched from GitHub

✅ **API Endpoints:**
- [ ] `/api/health` returns 200
- [ ] `/api/team-members` returns 200
- [ ] `/api/external-contributors` returns 200
- [ ] `/api/internal-orgs` returns 200
- [ ] `/api/auth/status` returns user info

✅ **Data Persistence:**
- [ ] Can add team members
- [ ] Team members saved to database
- [ ] Can add external contributors
- [ ] Settings can be configured
- [ ] Data survives page refresh

---

## Quick Reference

### Connection Strings

**Neon:**
```
postgresql://[user]:[password]@[host]/[database]?sslmode=require
```

**Supabase:**
```
postgresql://postgres.[project-id]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
```

**Railway:**
```
postgresql://postgres:[password]@[host].railway.app:[port]/railway
```

---

### Important Files

- **Database Schema:** `init_supabase.sql`
- **API Endpoints:** `apps/web/api/*.py`
- **Frontend:** `apps/web/src/`
- **Vercel Config:** `vercel.json`

---

### Environment Variables Needed

| Variable | Required | Purpose |
|----------|----------|---------|
| `POSTGRES_URL_NON_POOLING` | ✅ Yes | Database connection |
| `HIDEVS_SECRET_KEY` | ⚠️ Optional | PAT encryption (auto-generated) |
| `FLASK_ENV` | ⚠️ Optional | Set to `production` |

---

## Success Criteria

✅ You're done when:
1. No 500 errors in API responses
2. Can add GitHub username via frontend
3. Username persists after page refresh
4. `/api/team-members` returns 200
5. Dashboard shows UI (even if no data yet)

---

## Need Help?

1. **Check Vercel logs:**
   - Go to: https://vercel.com/hireal-projects/real-devs
   - Click "Deployments"
   - Click latest deployment
   - Check "Function Logs"

2. **Check database connection:**
   ```bash
   psql "YOUR_CONNECTION_STRING" -c "\dt"
   ```

3. **Test endpoints individually:**
   ```bash
   # Test each endpoint
   curl https://real-devs-oo4m2788k-hireal-projects.vercel.app/api/health
   curl https://real-devs-oo4m2788k-hireal-projects.vercel.app/api/team-members
   curl https://real-devs-oo4m2788k-hireal-projects.vercel.app/api/auth/status
   ```

---

**Estimated Time:** 15 minutes  
**Difficulty:** Easy  
**Cost:** $0 (Free tiers available for all database providers)

🎉 **After these steps, your RealDevs app will be fully functional!**

