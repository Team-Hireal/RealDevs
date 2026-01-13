# Storage Alternatives: Can You Avoid PostgreSQL on Vercel?

## TL;DR: The Reality

**Short Answer**: For **persistent data** on Vercel, you **need external storage**. JSON files won't work.

**Why?**
- Vercel's filesystem is **read-only** (except `/tmp`)
- `/tmp` is **ephemeral** (cleared between function invocations)
- Serverless functions are **stateless** (no shared memory)
- Each request may hit a **different server instance**

---

## Why JSON Files Won't Work on Vercel

### The Problem

```python
# ❌ This WON'T work on Vercel
with open('data.json', 'w') as f:
    json.dump(data, f)  # Error: Read-only filesystem!
```

**Vercel's Filesystem:**
- ✅ **Read-only** - You can read files from your codebase
- ❌ **Cannot write** - No file writes allowed (except `/tmp`)
- ❌ **No persistence** - `/tmp` is cleared after each function execution

### What Happens If You Try

1. **Write to project directory**: `PermissionError` or `Read-only filesystem`
2. **Write to `/tmp`**: Works temporarily, but data is **lost** when function ends
3. **Next request**: Data is gone (different server instance, cleared `/tmp`)

---

## Why In-Memory Storage Won't Work

### The Problem

```python
# ❌ This WON'T persist on Vercel
data_store = {}  # In-memory dictionary

@app.route('/save', methods=['POST'])
def save():
    data_store['key'] = request.json  # Only exists in THIS function instance
    return {"ok": True}

@app.route('/get', methods=['GET'])
def get():
    return data_store  # Empty! Different function instance
```

**Serverless Functions Are Stateless:**
- Each request may hit a **different server**
- Each function instance has its **own memory**
- No shared state between requests
- Functions are **destroyed** after execution (or after idle timeout)

### What Happens

1. **Request 1**: Save data to memory → Works
2. **Request 2**: Try to read data → **Empty!** (Different server instance)
3. **Data is lost** between requests

---

## Your Current Data Requirements

Looking at your models, you need to store:

1. **AuthToken** - Encrypted GitHub PATs (persistent, secure)
2. **Repository** - Selected repositories (persistent)
3. **Contributor** - Contributors with relationships (persistent, relational)
4. **DailyStats** - Daily aggregated stats (persistent, time-series)
5. **TeamMember** - Team members (persistent)
6. **Settings** - User preferences (persistent)
7. **ExternalCommit** - External commits (persistent, large volume)
8. **ExternalContributor** - External contributors (persistent)

**Characteristics:**
- ✅ **Relational data** (foreign keys, relationships)
- ✅ **Complex queries** (joins, aggregations)
- ✅ **Persistence required** (data must survive between requests)
- ✅ **Concurrent access** (multiple users, multiple requests)

**This requires a proper database.**

---

## Alternatives to PostgreSQL (That Actually Work)

### Option 1: Vercel KV (Redis-like) ⚡

**Best for**: Simple key-value storage, sessions, caching

```python
# Install: pip install @vercel/kv
from vercel_kv import kv

# Store
await kv.set('user:123', json.dumps(data))

# Retrieve
data = await kv.get('user:123')
```

**Pros:**
- ✅ Integrated with Vercel
- ✅ Fast (in-memory)
- ✅ Simple API

**Cons:**
- ❌ No complex queries (key-value only)
- ❌ No relationships
- ❌ Limited data structure
- ❌ **Not suitable for your relational data**

**Verdict**: ❌ Not suitable for your use case (too complex data model)

---

### Option 2: Vercel Blob Storage 📦

**Best for**: File storage, images, documents

```python
from vercel import blob

# Store
await blob.put('data.json', json.dumps(data))

# Retrieve
data = await blob.get('data.json')
```

**Pros:**
- ✅ Integrated with Vercel
- ✅ Persistent storage
- ✅ Good for files

**Cons:**
- ❌ No querying (file-based)
- ❌ No relationships
- ❌ Need to load entire file to read
- ❌ **Not suitable for relational data**

**Verdict**: ❌ Not suitable (you'd need to implement your own database logic)

---

### Option 3: External JSON Storage Services 🌐

**Services**: AWS S3, Google Cloud Storage, Cloudflare R2

```python
import boto3

s3 = boto3.client('s3')

# Store
s3.put_object(Bucket='my-bucket', Key='data.json', Body=json.dumps(data))

# Retrieve
response = s3.get_object(Bucket='my-bucket', Key='data.json')
data = json.loads(response['Body'].read())
```

**Pros:**
- ✅ Persistent storage
- ✅ Can store JSON files
- ✅ Works on Vercel

**Cons:**
- ❌ **You'd need to implement:**
  - Full database logic (CRUD operations)
  - Querying/filtering
  - Relationships/joins
  - Transactions
  - Indexing
  - Concurrency handling
- ❌ Performance issues (load entire file for each query)
- ❌ No ACID guarantees
- ❌ Complex to implement correctly

**Verdict**: ⚠️ **Technically possible but NOT recommended** - You'd essentially be building your own database

---

### Option 4: MongoDB Atlas (NoSQL) 🍃

**Best for**: Document-based data, flexible schemas

```python
from pymongo import MongoClient

client = MongoClient(MONGODB_URI)
db = client.realdevs

# Store
db.repositories.insert_one(repo_data)

# Query
repos = db.repositories.find({'owner': 'username'})
```

**Pros:**
- ✅ Cloud-hosted (works on Vercel)
- ✅ Free tier available
- ✅ Document-based (can store JSON-like structures)
- ✅ Querying support
- ✅ Relationships possible (embedded documents or references)

**Cons:**
- ⚠️ Different data model (document-based, not relational)
- ⚠️ Would require refactoring your SQLAlchemy models
- ⚠️ No SQL joins (need to handle relationships differently)

**Verdict**: ✅ **Possible but requires significant refactoring**

---

### Option 5: PostgreSQL (Recommended) 🐘

**Best for**: Relational data, complex queries, ACID transactions

**Pros:**
- ✅ Perfect fit for your current data model
- ✅ Relational (foreign keys, joins)
- ✅ Complex queries (SQL)
- ✅ ACID transactions
- ✅ Many free tier options
- ✅ **No code changes needed** (you're already using SQLAlchemy)

**Cons:**
- ⚠️ Requires external service (but many free options)

**Verdict**: ✅ **Best option - designed for your use case**

---

## Comparison Table

| Solution | Persistent | Queryable | Relationships | Complexity | Cost | Verdict |
|----------|-----------|-----------|---------------|------------|------|---------|
| **JSON Files** | ❌ No | ❌ No | ❌ No | Low | Free | ❌ Won't work |
| **In-Memory** | ❌ No | ❌ No | ❌ No | Low | Free | ❌ Won't work |
| **Vercel KV** | ✅ Yes | ⚠️ Limited | ❌ No | Low | Free tier | ❌ Too simple |
| **Vercel Blob** | ✅ Yes | ❌ No | ❌ No | Low | Free tier | ❌ Too simple |
| **S3/Cloud Storage** | ✅ Yes | ❌ No* | ❌ No* | High | Free tier | ⚠️ Too complex |
| **MongoDB Atlas** | ✅ Yes | ✅ Yes | ⚠️ Limited | Medium | Free tier | ⚠️ Requires refactor |
| **PostgreSQL** | ✅ Yes | ✅ Yes | ✅ Yes | Low | Free tier | ✅ **Best fit** |

*Would require implementing yourself

---

## Can You Make It Work Without PostgreSQL?

### Scenario 1: Single-User, Session-Based (Temporary)

**If you only need data for a single session:**

```python
# Store in browser (localStorage/sessionStorage)
# Backend just processes requests, doesn't store data
```

**Limitations:**
- ❌ Data lost on browser close (sessionStorage)
- ❌ Data lost if user clears browser (localStorage)
- ❌ No sharing between devices
- ❌ No persistence across sessions

**Verdict**: ⚠️ Only works for temporary, single-session use

---

### Scenario 2: Client-Side Only (No Backend Storage)

**Store everything in the frontend:**

```typescript
// Next.js - Store in browser
localStorage.setItem('repos', JSON.stringify(repos));
```

**Limitations:**
- ❌ No backend processing
- ❌ No server-side sync
- ❌ No GitHub API calls from backend
- ❌ Security issues (tokens in browser)
- ❌ Data lost if user clears browser

**Verdict**: ❌ Doesn't match your architecture (you need backend for GitHub API)

---

### Scenario 3: Hybrid Approach (Some Data in Browser)

**Store non-sensitive data in browser, sensitive in database:**

```python
# Backend: Store only auth tokens in database
# Frontend: Store repos, settings in localStorage
```

**What you'd need:**
- ✅ Database for: AuthToken (security requirement)
- ✅ Browser for: Repos, Settings (if acceptable to lose)

**Limitations:**
- ⚠️ Still need database for auth tokens
- ⚠️ Data loss risk for browser-stored data
- ⚠️ No sync across devices

**Verdict**: ⚠️ **Still requires database** (for auth tokens at minimum)

---

## Recommended Approach

### For Your Use Case: PostgreSQL is Unavoidable

**Why?**
1. **Security**: Auth tokens must be stored server-side (encrypted)
2. **Relational Data**: Your models have complex relationships
3. **Persistence**: Data must survive between requests
4. **Concurrency**: Multiple users, multiple requests
5. **Complex Queries**: Daily stats, aggregations, joins

**But Good News:**
- ✅ Many **free PostgreSQL options** available
- ✅ Your code is **already set up** for PostgreSQL
- ✅ **No code changes needed** (just set `DATABASE_URL`)
- ✅ **Easy to set up** (5-10 minutes)

---

## Free PostgreSQL Options (No Credit Card Required)

### 1. Supabase (Recommended for Free Tier)
- **Free**: 500MB database, unlimited API requests
- **Setup**: 2 minutes
- **URL**: supabase.com

### 2. Neon (Serverless PostgreSQL)
- **Free**: 3GB storage, serverless
- **Setup**: 2 minutes
- **URL**: neon.tech

### 3. Railway
- **Free**: $5 credit/month
- **Setup**: 3 minutes
- **URL**: railway.app

### 4. Render
- **Free**: 90-day trial, then $7/month
- **Setup**: 3 minutes
- **URL**: render.com

**All of these work perfectly with your existing code!**

---

## If You Really Want to Avoid PostgreSQL

### Option A: Refactor to MongoDB

**What you'd need to do:**
1. Replace SQLAlchemy with MongoDB driver
2. Refactor all models (document-based)
3. Rewrite all queries
4. Handle relationships differently
5. Test everything

**Time**: 2-3 days of work  
**Complexity**: High  
**Benefit**: Minimal (MongoDB still requires external service)

---

### Option B: Client-Side Only (Major Architecture Change)

**What you'd need to do:**
1. Remove all backend storage
2. Store everything in browser
3. Move GitHub API calls to frontend (security risk)
4. Handle auth differently
5. Accept data loss risk

**Time**: 1-2 weeks of work  
**Complexity**: Very High  
**Benefit**: None (worse architecture, security issues)

---

## Conclusion

### The Reality Check

**Question**: Can you avoid PostgreSQL?  
**Answer**: **Technically yes, but practically no.**

**Why PostgreSQL is the Right Choice:**
1. ✅ Your code is **already designed** for it
2. ✅ **Free options** available (Supabase, Neon)
3. ✅ **5-minute setup** (just get connection string)
4. ✅ **No code changes** needed
5. ✅ **Best fit** for your relational data model

**Why Alternatives Don't Work:**
- ❌ JSON files: Read-only filesystem on Vercel
- ❌ In-memory: Stateless serverless functions
- ❌ Other storage: Either too simple or too complex

**Recommendation**: Use PostgreSQL (Supabase or Neon free tier). It's the path of least resistance and best fit for your use case.

---

## Quick Setup (5 Minutes)

```bash
# 1. Sign up for Supabase (free)
# 2. Create project
# 3. Get connection string
# 4. Set environment variable
export DATABASE_URL="postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres?sslmode=require"

# 5. Initialize database
python apps/api/init_db.py

# Done! No code changes needed.
```

**That's it!** Your existing code will work immediately.

---

## Summary

| Approach | Works? | Effort | Recommendation |
|----------|--------|--------|----------------|
| JSON Files | ❌ No | Low | Don't use |
| In-Memory | ❌ No | Low | Don't use |
| PostgreSQL | ✅ Yes | **Very Low** | ✅ **Use this** |
| MongoDB | ⚠️ Yes* | High | Only if you want NoSQL |
| Client-Side Only | ⚠️ Yes* | Very High | Not recommended |

*Requires significant refactoring

**Bottom Line**: PostgreSQL is the practical choice. It's free, easy, and your code is already ready for it.

