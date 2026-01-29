# SusBonk API Backend - Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- `.env` file configured (see below)

### 1. Configure Environment

Create or update `.env` file in project root:

```bash
# Database
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=pg-database
POSTGRES_PORT=5432

# JWT (REQUIRED - Generate a secure random string)
JWT_SECRET=your-secure-random-string-here-change-this
JWT_ALG=HS256
JWT_ACCESS_TTL_MIN=10080

# API
API_HOST=0.0.0.0
API_PORT=8000
```

**⚠️ IMPORTANT**: Generate a secure JWT_SECRET:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Start Services

```bash
cd backend
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- API backend (port 8000)
- OpenSearch (port 9200)
- OpenSearch Dashboards (port 5601)
- Log ingestion service (port 8080)
- Alert engine
- Django admin (port 5050)

### 3. Verify Deployment

```bash
# Check API health
curl http://localhost:8000/health

# Check Swagger docs
open http://localhost:8000/docs

# Check all services
docker-compose ps
```

Expected response from health check:
```json
{"status": "healthy", "service": "susbonk-api"}
```

### 4. Test the API

```bash
# Run test script
cd backend
./test-api.sh
```

Or manually:
```bash
# Register a user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

## 📊 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:8000 | REST API |
| Swagger Docs | http://localhost:8000/docs | Interactive API documentation |
| ReDoc | http://localhost:8000/redoc | Alternative API documentation |
| Health Check | http://localhost:8000/health | Service health status |
| PostgreSQL | localhost:5432 | Database |
| OpenSearch | http://localhost:9200 | Log storage |
| Dashboards | http://localhost:5601 | Log visualization |
| Django Admin | http://localhost:5050 | Admin panel |

## 🔧 Development Setup

### Local Development (without Docker)

1. **Install dependencies:**
```bash
cd backend

# Using uv (recommended)
uv pip install .

# Or using pip
pip install -e .
```

2. **Set up database:**
```bash
# Start PostgreSQL
docker-compose up -d pg-database

# Wait for database to be ready
sleep 5

# Initialize schema
docker-compose up pg-init
```

3. **Run the API:**
```bash
python main.py
```

The API will be available at http://localhost:8000

### Running Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio httpx pytest-cov

# Run all tests
pytest tests/ -v

# Run P0 critical tests only
pytest tests/ -v -m priority_p0

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 🐳 Docker Commands

### Start all services
```bash
docker-compose up -d
```

### Stop all services
```bash
docker-compose down
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api-backend
```

### Rebuild after code changes
```bash
docker-compose up -d --build api-backend
```

### Reset everything (including data)
```bash
docker-compose down -v
docker-compose up -d
```

## 📝 API Usage Examples

### Authentication

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "securepass123"
  }'

# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'

# Get current user
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### System Prompts

```bash
# List system prompts
curl http://localhost:8000/prompts \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Get specific prompt
curl http://localhost:8000/prompts/{prompt_id} \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Custom Prompts

```bash
# Create custom prompt
curl -X POST http://localhost:8000/prompts/custom \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Custom Prompt",
    "prompt_text": "Detect messages about..."
  }'

# List custom prompts
curl http://localhost:8000/prompts/custom \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Update custom prompt
curl -X PATCH http://localhost:8000/prompts/custom/{prompt_id} \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'

# Delete custom prompt
curl -X DELETE http://localhost:8000/prompts/custom/{prompt_id} \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Chats

```bash
# List chats
curl http://localhost:8000/chats \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Get chat settings
curl http://localhost:8000/chats/{chat_id} \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Update chat settings
curl -X PATCH http://localhost:8000/chats/{chat_id} \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "enable_ai_check": true,
    "prompts_threshold": 0.5,
    "cleanup_links": true
  }'
```

## 🔍 Troubleshooting

### API won't start

**Error**: `JWT_SECRET is required`
**Solution**: Set JWT_SECRET in .env file

**Error**: `Cannot connect to database`
**Solution**: Ensure PostgreSQL is running: `docker-compose up -d pg-database`

### Tests failing

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Install dependencies: `pip install -e .`

**Error**: `Connection refused`
**Solution**: Ensure services are running: `docker-compose ps`

### Database issues

**Reset database:**
```bash
docker-compose down -v
docker-compose up -d pg-database
docker-compose up pg-init
docker-compose up -d api-backend
```

### View service logs

```bash
# API logs
docker-compose logs -f api-backend

# Database logs
docker-compose logs -f pg-database

# All logs
docker-compose logs -f
```

## 📊 Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database health
docker-compose exec pg-database pg_isready

# OpenSearch health
curl http://localhost:9200/_cluster/health
```

### Logs

```bash
# View API logs
docker-compose logs -f api-backend

# View structured logs
docker-compose logs api-backend | grep '"level"'
```

## 🔒 Security Checklist

- [ ] JWT_SECRET is set to a secure random string
- [ ] JWT_SECRET is different in production
- [ ] Database password is changed from default
- [ ] CORS origins restricted in production
- [ ] HTTPS enabled in production
- [ ] Rate limiting configured
- [ ] Firewall rules configured
- [ ] Regular security updates applied

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Test Protocol**: TEST_PROTOCOL.md
- **Test Checklist**: TEST_CHECKLIST.md
- **Code Review Fixes**: CODE_REVIEW_FIXES.md
- **Implementation Summary**: IMPLEMENTATION_SUMMARY.md

## 🎯 Production Deployment

### Environment Variables

Update `.env` for production:
```bash
# Use strong passwords
POSTGRES_PASSWORD=strong-random-password

# Use secure JWT secret
JWT_SECRET=secure-random-string-64-chars-minimum

# Restrict CORS (update main.py)
# Change allow_origins from ["*"] to specific domains

# Use production database
POSTGRES_HOST=your-production-db-host
```

### Docker Compose Production

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'
services:
  api-backend:
    restart: always
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

Deploy:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## ✅ Deployment Checklist

- [ ] Environment variables configured
- [ ] JWT_SECRET generated and set
- [ ] Database initialized
- [ ] Services started
- [ ] Health checks passing
- [ ] API accessible
- [ ] Swagger docs accessible
- [ ] Tests passing
- [ ] Logs being generated
- [ ] Monitoring configured

---

**Status**: ✅ Ready for deployment
**Version**: 0.1.0
**Last Updated**: 2026-01-17
