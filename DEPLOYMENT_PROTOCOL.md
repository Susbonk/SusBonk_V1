# 🚀 Deployment Protocol - SusBonk Full Stack

## Pre-Deployment Checklist

### Backend Verification
- [ ] Backend API running: `curl http://localhost:8000/health`
- [ ] Database migrations applied
- [ ] JWT_SECRET configured in .env
- [ ] All 16 API endpoints tested
- [ ] Docker containers healthy
- [ ] OpenSearch cluster operational

### Frontend Verification
- [ ] Frontend dev server running: http://localhost:5173
- [ ] API client connecting to backend
- [ ] Registration flow working
- [ ] Login flow working
- [ ] Auto-login on reload working
- [ ] All CRUD operations functional

### Integration Tests
- [ ] Register new user → success
- [ ] Login with credentials → dashboard loads
- [ ] Fetch chats → displays in dropdown
- [ ] View whitelist → shows trusted users
- [ ] Create custom prompt → appears in list
- [ ] Delete custom prompt → removed from list
- [ ] Page reload → stays logged in

## Deployment Steps

### Step 1: Code Review & Quality Check
```bash
# Frontend type checking
cd frontend
npm run check

# Backend tests
cd ../backend
pytest tests/ -v

# Check for console errors
# Open browser DevTools → Console → No errors
```

### Step 2: Build Frontend for Production
```bash
cd frontend

# Create production build
npm run build

# Preview production build
npm run preview

# Verify build output
ls -lh dist/
```

### Step 3: Configure Production Environment

**Backend `.env`:**
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/susbonk

# JWT
JWT_SECRET=<production-secret-64-chars>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# CORS
CORS_ORIGINS=["https://susbonk.com"]

# OpenSearch
OPENSEARCH_URL=http://os01:9200
```

**Frontend `.env.production`:**
```bash
VITE_API_URL=https://api.susbonk.com
```

### Step 4: Deploy Backend

**Option A: Docker Compose (Recommended)**
```bash
cd backend

# Build images
docker-compose build

# Start services
docker-compose up -d

# Check health
curl https://api.susbonk.com/health

# View logs
docker-compose logs -f api-backend
```

**Option B: AWS/DigitalOcean**
```bash
# Build Docker image
docker build -t susbonk-api:latest .

# Push to registry
docker tag susbonk-api:latest registry.example.com/susbonk-api:latest
docker push registry.example.com/susbonk-api:latest

# Deploy to cloud
# (Use cloud provider's deployment tools)
```

### Step 5: Deploy Frontend

**Option A: Static Hosting (Vercel/Netlify)**
```bash
cd frontend

# Vercel
vercel --prod

# Netlify
netlify deploy --prod --dir=dist
```

**Option B: Nginx**
```bash
# Build frontend
npm run build

# Copy to web server
scp -r dist/* user@server:/var/www/susbonk/

# Nginx config
server {
    listen 80;
    server_name susbonk.com;
    root /var/www/susbonk;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### Step 6: DNS Configuration
```
A     susbonk.com          → Frontend IP
A     api.susbonk.com      → Backend IP
CNAME www.susbonk.com      → susbonk.com
```

### Step 7: SSL/TLS Setup
```bash
# Let's Encrypt
certbot --nginx -d susbonk.com -d www.susbonk.com -d api.susbonk.com
```

### Step 8: Post-Deployment Verification

**Backend Health Check:**
```bash
curl https://api.susbonk.com/health
# Expected: {"status":"healthy","service":"susbonk-api"}

curl https://api.susbonk.com/docs
# Expected: Swagger UI loads
```

**Frontend Verification:**
```bash
curl https://susbonk.com
# Expected: HTML with SusBonk title

# Test in browser:
# 1. Open https://susbonk.com
# 2. Register new account
# 3. Login
# 4. Verify dashboard loads
# 5. Create custom prompt
# 6. Refresh page → still logged in
```

**Integration Test:**
```bash
# Register
curl -X POST https://api.susbonk.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Login
TOKEN=$(curl -X POST https://api.susbonk.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  | jq -r '.access_token')

# Get user
curl https://api.susbonk.com/auth/me \
  -H "Authorization: Bearer $TOKEN"

# List chats
curl https://api.susbonk.com/chats \
  -H "Authorization: Bearer $TOKEN"
```

## Monitoring Setup

### Backend Monitoring
```bash
# Check API logs
docker-compose logs -f api-backend

# Check database connections
docker-compose exec postgres psql -U susbonk -c "SELECT count(*) FROM pg_stat_activity;"

# Check OpenSearch health
curl http://localhost:9200/_cluster/health
```

### Frontend Monitoring
```bash
# Check Nginx access logs
tail -f /var/log/nginx/access.log

# Check error logs
tail -f /var/log/nginx/error.log
```

### Application Monitoring
- Set up error tracking (Sentry)
- Configure uptime monitoring (UptimeRobot)
- Enable performance monitoring (New Relic/DataDog)

## Rollback Procedure

### Backend Rollback
```bash
# Stop current version
docker-compose down

# Checkout previous version
git checkout <previous-commit>

# Rebuild and restart
docker-compose up -d --build

# Verify health
curl http://localhost:8000/health
```

### Frontend Rollback
```bash
# Vercel
vercel rollback

# Netlify
netlify rollback

# Manual
git checkout <previous-commit>
npm run build
# Redeploy dist/
```

## Security Checklist

### Backend Security
- [ ] JWT_SECRET is strong (64+ random chars)
- [ ] CORS restricted to production domain
- [ ] HTTPS enabled everywhere
- [ ] Database credentials secured
- [ ] Rate limiting enabled
- [ ] SQL injection protection (SQLAlchemy ORM)
- [ ] Input validation (Pydantic)
- [ ] Password hashing (bcrypt)

### Frontend Security
- [ ] API URL uses HTTPS
- [ ] No secrets in client code
- [ ] Content Security Policy configured
- [ ] XSS protection enabled
- [ ] CSRF tokens for state-changing operations

## Performance Optimization

### Backend
- [ ] Database connection pooling enabled
- [ ] Query optimization (N+1 prevention)
- [ ] Response caching where appropriate
- [ ] Gzip compression enabled

### Frontend
- [ ] Production build minified
- [ ] Assets compressed
- [ ] Lazy loading implemented
- [ ] CDN for static assets

## Backup Strategy

### Database Backup
```bash
# Daily backup
docker-compose exec postgres pg_dump -U susbonk susbonk > backup-$(date +%Y%m%d).sql

# Automated backup script
0 2 * * * /path/to/backup-script.sh
```

### Configuration Backup
```bash
# Backup .env files
tar -czf config-backup-$(date +%Y%m%d).tar.gz backend/.env frontend/.env.production
```

## Troubleshooting

### Backend Issues
```bash
# Check logs
docker-compose logs api-backend

# Check database connection
docker-compose exec postgres psql -U susbonk -c "SELECT 1;"

# Restart service
docker-compose restart api-backend
```

### Frontend Issues
```bash
# Check build errors
npm run build

# Check API connectivity
curl https://api.susbonk.com/health

# Clear browser cache
# DevTools → Application → Clear storage
```

### Common Issues

**401 Unauthorized:**
- Check JWT_SECRET matches between deployments
- Verify token not expired
- Check CORS configuration

**CORS Errors:**
- Verify CORS_ORIGINS includes frontend domain
- Check protocol (http vs https)
- Verify preflight requests allowed

**Database Connection Failed:**
- Check DATABASE_URL format
- Verify database is running
- Check network connectivity
- Verify credentials

## Success Criteria

✅ Backend API responds to health check
✅ Frontend loads without errors
✅ User can register and login
✅ Dashboard displays real data
✅ All CRUD operations work
✅ Page reload maintains session
✅ HTTPS enabled on all endpoints
✅ Monitoring alerts configured
✅ Backup strategy in place

## Post-Deployment Tasks

- [ ] Monitor error rates for 24 hours
- [ ] Check performance metrics
- [ ] Verify backup jobs running
- [ ] Update documentation
- [ ] Notify team of deployment
- [ ] Schedule post-mortem if issues

## Emergency Contacts

- **DevOps Lead**: [contact]
- **Backend Lead**: [contact]
- **Frontend Lead**: [contact]
- **Database Admin**: [contact]

## Deployment Log

| Date | Version | Deployed By | Status | Notes |
|------|---------|-------------|--------|-------|
| 2026-01-17 | v1.0.0 | Team | ✅ Success | Initial deployment |

---

**Last Updated**: 2026-01-17
**Next Review**: 2026-01-24
