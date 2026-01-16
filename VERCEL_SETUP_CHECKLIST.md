# Vercel Deployment Checklist

## Pre-Deployment Verification

### ✅ Project Files
- [ ] `vercel.json` exists at project root
- [ ] `package.json` exists at project root
- [ ] `requirements.txt` exists at project root
- [ ] `app.py` exists at project root
- [ ] `apps/web/package.json` exists
- [ ] `apps/web/next.config.js` exists
- [ ] `apps/api/requirements.txt` exists

### ✅ Git Repository
- [ ] Project pushed to GitHub/GitLab/Bitbucket
- [ ] Remote repository URL: `________________`
- [ ] Main branch name: `________________`

### ✅ Local Testing
- [ ] Backend runs locally: `cd apps/api && flask run`
- [ ] Frontend runs locally: `cd apps/web && npm run dev`
- [ ] API responds: `http://localhost:8000/api/health`
- [ ] Frontend loads: `http://localhost:3000`
- [ ] Frontend can call API endpoints

---

## Vercel Account Setup

### ✅ Account Creation
- [ ] Created Vercel account at [vercel.com/signup](https://vercel.com/signup)
- [ ] Connected GitHub/GitLab/Bitbucket account
- [ ] Verified email address
- [ ] Account type: `________________` (Personal/Team)

---

## Environment Variables Preparation

### ✅ Required Variables
Generate and save these BEFORE importing project:

**Flask Backend:**
```bash
# Generate secret key (run in terminal):
# python -c "import secrets; print(secrets.token_urlsafe(32))"
```

- [ ] `FLASK_ENV=production`
- [ ] `HIDEVS_SECRET_KEY=________________`
- [ ] `PYTHONPATH=.`

**Database (if using PostgreSQL):**
- [ ] `DATABASE_URL=________________`

**GitHub PAT (optional for testing):**
- [ ] `GITHUB_TOKEN=________________`

---

## Vercel Project Import

### ✅ Step 1: Import Repository
- [ ] Go to [vercel.com/new](https://vercel.com/new)
- [ ] Click "Import Git Repository"
- [ ] Select your RealDevs repository
- [ ] Click "Import"

### ✅ Step 2: Configure Project Settings
**Framework Preset:**
- [ ] Framework: `Next.js` (should auto-detect)

**Root Directory:**
- [ ] Root Directory: `.` (leave as default)
- [ ] Do NOT change root directory

**Build Settings:**
- [ ] Build Command: `Auto` (leave as default)
- [ ] Output Directory: `Auto` (leave as default)
- [ ] Install Command: `Auto` (leave as default)

### ✅ Step 3: Environment Variables
Add ALL variables from preparation section:

- [ ] Click "Environment Variables" section
- [ ] Add `FLASK_ENV` = `production` → All Environments
- [ ] Add `HIDEVS_SECRET_KEY` = `<your-secret>` → All Environments
- [ ] Add `PYTHONPATH` = `.` → All Environments
- [ ] Add `DATABASE_URL` (if applicable) → Production only
- [ ] Add any other custom variables

### ✅ Step 4: Deploy
- [ ] Click "Deploy" button
- [ ] Wait for deployment (2-5 minutes)
- [ ] Deployment URL: `https://________________.vercel.app`

---

## Post-Deployment Testing

### ✅ Frontend Tests
- [ ] Homepage loads: `https://your-project.vercel.app`
- [ ] Navigation works (Dashboard, Credentials, Settings)
- [ ] No console errors in browser DevTools
- [ ] Styling renders correctly
- [ ] Dark mode/theme works

### ✅ Backend API Tests
- [ ] Health endpoint: `https://your-project.vercel.app/api/health`
  - Expected: `{"status": "ok", "service": "RealDevs API"}`
- [ ] Auth status: `https://your-project.vercel.app/api/auth/status`
- [ ] Dashboard: `https://your-project.vercel.app/api/dashboard`

### ✅ Integration Tests
- [ ] Can navigate between pages
- [ ] Can configure GitHub PAT
- [ ] Can sync repositories
- [ ] Dashboard displays data
- [ ] No CORS errors in console
- [ ] API calls work from frontend

### ✅ Log Verification
In Vercel Dashboard:
- [ ] Go to Deployments → Latest deployment
- [ ] Check Build logs for errors
- [ ] Go to Functions → app.py
- [ ] Check Runtime logs for errors
- [ ] No critical errors in logs

---

## Domain Configuration (Optional)

### ✅ Custom Domain Setup
- [ ] Go to Project Settings → Domains
- [ ] Add domain: `________________`
- [ ] Update DNS records:
  - [ ] Type: `A` → Value: `76.76.21.21`
  - [ ] Type: `CNAME` → Value: `cname.vercel-dns.com`
- [ ] Wait for DNS propagation (5-60 minutes)
- [ ] SSL certificate auto-issued
- [ ] Test custom domain works

---

## Production Database Setup (Recommended)

### ✅ PostgreSQL Setup
Choose one provider:

**Option A: Neon**
- [ ] Sign up at [neon.tech](https://neon.tech)
- [ ] Create new project
- [ ] Copy connection string
- [ ] Add to Vercel: `DATABASE_URL=postgresql://...`

**Option B: Supabase**
- [ ] Sign up at [supabase.com](https://supabase.com)
- [ ] Create new project
- [ ] Go to Settings → Database
- [ ] Copy connection string
- [ ] Add to Vercel: `DATABASE_URL=postgresql://...`

**Option C: Railway**
- [ ] Sign up at [railway.app](https://railway.app)
- [ ] Create PostgreSQL database
- [ ] Copy connection string
- [ ] Add to Vercel: `DATABASE_URL=postgresql://...`

### ✅ Database Migration
- [ ] Add `DATABASE_URL` to Vercel environment variables
- [ ] Redeploy project
- [ ] Verify database connection in logs
- [ ] Test data persistence

---

## Security Hardening

### ✅ Environment Variables Security
- [ ] All secrets stored in Vercel (not in code)
- [ ] Production secrets different from development
- [ ] `HIDEVS_SECRET_KEY` is strong (32+ characters)
- [ ] No secrets committed to Git
- [ ] `.env` files in `.gitignore`

### ✅ GitHub PAT Security
- [ ] Using fine-grained token (not classic)
- [ ] Read-only permissions only
- [ ] Token expiration set (max 90 days)
- [ ] Separate tokens for dev/prod

### ✅ Vercel Security Settings
- [ ] Go to Project Settings → Security
- [ ] Enable "Deployment Protection" (if on Pro plan)
- [ ] Review "Vercel Authentication"
- [ ] Check "Secure Compute" settings

---

## Monitoring Setup

### ✅ Vercel Analytics
- [ ] Go to Project → Analytics
- [ ] Enable Web Analytics (if desired)
- [ ] Note: Free tier includes basic analytics

### ✅ Error Monitoring
- [ ] Check Functions logs regularly
- [ ] Set up external monitoring (optional):
  - [ ] Sentry integration
  - [ ] LogRocket integration
  - [ ] Custom monitoring

### ✅ Uptime Monitoring
External services (optional):
- [ ] Set up [UptimeRobot](https://uptimerobot.com) (free)
- [ ] Monitor: `https://your-project.vercel.app/api/health`
- [ ] Alert email: `________________`

---

## Team Configuration (If Applicable)

### ✅ Team Setup
- [ ] Create Vercel team (if needed)
- [ ] Invite team members
- [ ] Set member roles:
  - [ ] Member 1: `________________` (role: `________`)
  - [ ] Member 2: `________________` (role: `________`)
- [ ] Configure team billing

### ✅ Git Integration
- [ ] Enable preview deployments
- [ ] Configure branch deployments
- [ ] Set up deployment notifications:
  - [ ] Slack integration
  - [ ] Email notifications
  - [ ] Discord webhook

---

## Continuous Deployment

### ✅ Automatic Deployments
- [ ] Push to main branch triggers production deploy
- [ ] Pull requests trigger preview deployments
- [ ] Preview URL format: `https://project-git-branch.vercel.app`

### ✅ Deployment Branches
Configure which branches deploy:
- [ ] Production branch: `________________` (usually `main`)
- [ ] Preview branches: `All branches` or `Specific: ________`

---

## Performance Optimization

### ✅ Vercel Settings
- [ ] Go to Project Settings → Functions
- [ ] Check region settings (default: All regions)
- [ ] Review function timeout (default: 10s)

### ✅ Next.js Optimizations
- [ ] Images use Next.js `<Image>` component
- [ ] Enable image optimization
- [ ] Check bundle size in build logs

### ✅ API Optimizations
- [ ] Database connection pooling enabled
- [ ] API responses cached where appropriate
- [ ] Large responses paginated

---

## Documentation Updates

### ✅ Project Documentation
- [ ] Update README with deployment URL
- [ ] Document environment variables needed
- [ ] Add deployment status badge (optional)
- [ ] Update team documentation

### ✅ Internal Documentation
- [ ] Document deployment process for team
- [ ] Document rollback procedure
- [ ] Document environment variable locations
- [ ] Create runbook for common issues

---

## Backup & Recovery

### ✅ Backup Strategy
- [ ] Database backups configured
- [ ] Backup frequency: `________________`
- [ ] Backup retention: `________________`
- [ ] Test restore procedure

### ✅ Rollback Plan
- [ ] Know how to rollback deployment:
  1. Go to Deployments
  2. Select previous deployment
  3. Click "Promote to Production"
- [ ] Document rollback procedure
- [ ] Test rollback process

---

## Final Verification

### ✅ Complete System Test
- [ ] User flow test: Sign in → Configure PAT → Sync → View Dashboard
- [ ] Mobile responsiveness check
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Performance check (< 3s load time)
- [ ] No JavaScript errors
- [ ] No console warnings

### ✅ Production Readiness
- [ ] All environment variables set
- [ ] Database properly configured
- [ ] SSL certificate active
- [ ] Monitoring enabled
- [ ] Team notified of deployment
- [ ] Documentation updated

---

## Go-Live Checklist

### ✅ Pre-Launch
- [ ] All tests passing
- [ ] No critical issues in logs
- [ ] Performance acceptable
- [ ] Security review complete
- [ ] Backup strategy in place

### ✅ Launch
- [ ] Announce to team
- [ ] Monitor for first 24 hours
- [ ] Check error rates
- [ ] Verify user reports

### ✅ Post-Launch
- [ ] Document any issues encountered
- [ ] Update runbooks with solutions
- [ ] Schedule regular health checks
- [ ] Plan next iteration

---

## Troubleshooting Reference

### Build Failures
- [ ] Check Python version: `runtime.txt` if needed
- [ ] Verify `requirements.txt` syntax
- [ ] Check `package.json` dependencies
- [ ] Review build logs

### Runtime Errors
- [ ] Check environment variables set correctly
- [ ] Review function logs
- [ ] Verify database connection
- [ ] Check API endpoint paths

### Performance Issues
- [ ] Check function execution time
- [ ] Review database query performance
- [ ] Check bundle size
- [ ] Enable caching

---

## Maintenance Schedule

### Daily
- [ ] Check deployment status
- [ ] Review error logs

### Weekly
- [ ] Review analytics
- [ ] Check for dependency updates
- [ ] Review function performance

### Monthly
- [ ] Security audit
- [ ] Performance review
- [ ] Backup verification
- [ ] Cost review

---

## Contact & Support

### Vercel Support
- [ ] Support tier: `________________`
- [ ] Support email: support@vercel.com
- [ ] Discord: [vercel.com/discord](https://vercel.com/discord)

### Internal Contacts
- [ ] DevOps lead: `________________`
- [ ] On-call person: `________________`
- [ ] Emergency contact: `________________`

---

## Completion Sign-Off

**Deployment completed by:** `________________`

**Date:** `________________`

**Deployment URL:** `https://________________.vercel.app`

**Status:** ✅ Production Ready

**Notes:**
```
[Add any additional notes, known issues, or future improvements]
```

---

## Quick Reference Commands

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from CLI
vercel --prod

# View logs
vercel logs

# Check environment variables
vercel env ls

# Pull environment variables locally
vercel env pull .env.local
```

---

**Checklist Version:** 1.0  
**Last Updated:** 2026-01-16  
**Project:** RealDevs

