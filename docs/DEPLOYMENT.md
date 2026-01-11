# Deployment Guide

This guide covers deploying RealDevs to various platforms. **Note**: Phase 1 is designed for local-first use. Deploying to hosted platforms requires additional security considerations.

## ⚠️ Security Warning

RealDevs Phase 1 handles GitHub Personal Access Tokens (PATs). When self-hosting:

- Never expose your backend API publicly without proper authentication
- Use HTTPS/TLS for all connections
- Rotate PATs regularly
- Consider implementing additional authentication layers
- Monitor access logs

## Local Development

### Docker Compose (Recommended)

```bash
# Start all services
docker compose up --build

# Access:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
```

### Manual Setup

**Backend:**
```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp env.example .env
# Edit .env and set HIDEVS_SECRET_KEY

# Run
python run.py
```

**Frontend:**
```bash
cd apps/web
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local

# Run
npm run dev
```

## Self-Hosting Options

### Option 1: Docker on VPS (DigitalOcean, Linode, etc.)

1. **Provision a VPS** with Docker installed

2. **Clone repository:**
   ```bash
   git clone <your-repo>
   cd RealDevs
   ```

3. **Configure environment:**
   ```bash
   # Backend
   cd apps/api
   cp env.example .env
   nano .env  # Set HIDEVS_SECRET_KEY to a secure random string
   
   # Frontend
   cd ../web
   echo "NEXT_PUBLIC_API_URL=https://your-domain.com/api" > .env.local
   ```

4. **Set up reverse proxy (Nginx):**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Enable HTTPS with Let's Encrypt:**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

6. **Start services:**
   ```bash
   docker compose up -d
   ```

### Option 2: Separate Hosting (Vercel + Render/Railway)

⚠️ **Not recommended for Phase 1** due to PAT security concerns.

If you must deploy separately:

**Backend (Render/Railway):**

1. Create new Web Service
2. Build command: `pip install -r requirements.txt`
3. Start command: `python run.py`
4. Environment variables:
   - `HIDEVS_SECRET_KEY`: Generate secure random key
   - `DATABASE_URL`: Use PostgreSQL instead of SQLite for production
   - `FLASK_ENV`: production
   - `CORS_ORIGINS`: Your Vercel frontend URL

**Frontend (Vercel):**

1. Import repository
2. Framework preset: Next.js
3. Root directory: `apps/web`
4. Environment variables:
   - `NEXT_PUBLIC_API_URL`: Your backend API URL

## Production Considerations

### Database

Phase 1 uses SQLite, which works for single-user local setups. For production:

1. **Migrate to PostgreSQL:**
   ```bash
   pip install psycopg2-binary
   
   # Update DATABASE_URL in .env
   DATABASE_URL=postgresql://user:pass@host:5432/realdevs
   ```

2. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

### Secrets Management

Never hardcode secrets. Use:

- **Docker Secrets** for Docker Swarm
- **Kubernetes Secrets** for K8s
- **Environment variables** from hosting platform
- **Vault** for enterprise deployments

### Scaling

For multi-user scenarios (future phases):

1. **Horizontal scaling:**
   - Deploy multiple backend instances behind load balancer
   - Use Redis for shared session storage
   - Implement job queue for GitHub sync operations

2. **Database:**
   - Use managed PostgreSQL (AWS RDS, DigitalOcean Databases)
   - Enable connection pooling
   - Set up read replicas for heavy loads

### Monitoring

Implement monitoring for:

- API response times
- GitHub API rate limits
- Database query performance
- Error rates
- User activity

**Recommended tools:**
- Prometheus + Grafana
- Sentry for error tracking
- Uptime monitoring (UptimeRobot, Pingdom)

## Backup & Recovery

### Backup Strategy

```bash
# Backup SQLite database
cp apps/api/realdevs.db backups/realdevs-$(date +%Y%m%d).db

# Automate with cron
0 0 * * * /path/to/backup-script.sh
```

### Disaster Recovery

1. Keep encrypted PAT backups separate from database
2. Document restoration procedures
3. Test recovery process regularly
4. Maintain offsite backups

## Security Checklist

- [ ] HTTPS/TLS enabled
- [ ] Secure secret key (32+ random characters)
- [ ] PAT encryption verified
- [ ] CORS configured correctly
- [ ] Rate limiting implemented
- [ ] Firewall rules configured
- [ ] Regular security updates
- [ ] Access logs monitored
- [ ] Backup strategy tested

## Support

For issues or questions:
- GitHub Issues: [your-repo/issues]
- Documentation: [your-docs-url]

---

**Remember**: RealDevs Phase 1 is designed for local-first, single-user use. Multi-user SaaS deployment is planned for future phases with proper authentication and security measures.

