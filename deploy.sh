#!/bin/bash

echo "🚀 Deploying RealDevs with Database Fixes..."
echo ""
echo "Changes:"
echo "  ✅ Fixed psycopg2 version mismatch"
echo "  ✅ All endpoints use raw SQL (no import errors)"
echo "  ✅ 12/12 functions (within Vercel limit)"
echo ""

# Add all changes
git add .

# Commit with descriptive message
git commit -m "Fix: Use psycopg2-binary for database connectivity

- Changed psycopg[binary]>=3 to psycopg2-binary>=2.9
- All endpoints now use raw SQL with psycopg2
- Fixes 500 errors on /api/auth/pat and other endpoints
- Stays within 12-function Vercel limit"

# Push to trigger deployment
echo ""
echo "Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Deploy triggered!"
echo ""
echo "Next steps:"
echo "  1. Wait ~2 minutes for Vercel deployment"
echo "  2. Initialize database: Run init_supabase.sql in Supabase"
echo "  3. Test: Visit https://www.realdevs.pro/credentials"
echo ""
echo "Watch deployment: https://vercel.com/dashboard"

