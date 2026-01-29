# Code Review Action Plan
**Date**: January 29, 2026  
**Priority**: CRITICAL SECURITY FIXES REQUIRED

## 🔴 CRITICAL - Fix Immediately (Before Any Deployment)

### 1. Django Secret Key (5 minutes)
```python
# admin/db_admin/settings.py
import os
from django.core.exceptions import ImproperlyConfigured

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured('DJANGO_SECRET_KEY must be set')
```

### 2. Django DEBUG Mode (2 minutes)
```python
# admin/db_admin/settings.py
DEBUG = os.environ.get('ENVIRONMENT', 'production') != 'production'
```

### 3. Django ALLOWED_HOSTS (2 minutes)
```python
# admin/db_admin/settings.py
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')
```

### 4. Update .env.example (5 minutes)
```bash
# Add to .env.example
DJANGO_SECRET_KEY=CHANGE_ME_RUN_python_manage_py_shell_-c_"from_django.core.management.utils_import_get_random_secret_key;_print(get_random_secret_key())"

# Update weak passwords
POSTGRES_PASSWORD=CHANGE_ME_GENERATE_RANDOM_32_CHARS
OPENSEARCH_PASSWORD=CHANGE_ME_GENERATE_RANDOM_32_CHARS
DJANGO_SUPERUSER_PASSWORD=CHANGE_ME_USE_STRONG_PASSWORD_MIN_12_CHARS
REDIS_PASSWORD=CHANGE_ME_GENERATE_RANDOM_32_CHARS
```

### 5. Redis Authentication (10 minutes)
```yaml
# docker-compose.yml
redis:
  image: redis:7-alpine
  container_name: susbonk-redis
  command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-redis_dev_password}
  environment:
    - REDIS_PASSWORD=${REDIS_PASSWORD:-redis_dev_password}
```

Update all Redis clients:
```python
# backend/settings.py
REDIS_URL: str = f"redis://:{os.environ.get('REDIS_PASSWORD', '')}@redis:6379"
```

```rust
// ai-service/src/main.rs, telegram-bot/config/src/lib.rs
redis_url: env_string("REDIS_URL", "redis://:password@localhost:6379"),
```

**Total Time**: ~30 minutes  
**Impact**: Prevents 5 critical security vulnerabilities

---

## 🟠 HIGH PRIORITY - Fix This Week

### 6. Backend Reload Flag (1 minute)
```python
# backend/main.py
reload=os.environ.get('ENVIRONMENT') == 'development',
```

### 7. Rate Limiting (30 minutes)
```bash
# Add to backend/pyproject.toml
dependencies = [
    "slowapi>=0.1.9",
]
```

```python
# backend/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
main_app.state.limiter = limiter
main_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# backend/api/handlers/auth.py
from slowapi import Limiter
from fastapi import Request

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    ...
```

### 8. AI Service Timeout (15 minutes)
```rust
// ai-service/src/main.rs
use tokio::time::timeout;

match timeout(
    Duration::from_secs(cfg.ai_timeout_s),
    llm.classify(&task_data.text, &task_data.prompt)
).await {
    Ok(Ok(result)) => result,
    Ok(Err(e)) => {
        error!("LLM error: {}", e);
        continue;
    }
    Err(_) => {
        error!("LLM timeout after {}s", cfg.ai_timeout_s);
        continue;
    }
}
```

### 9. Input Validation (20 minutes)
```rust
// telegram-bot/app/services.rs
fn sanitize_text(text: &str) -> String {
    text.chars()
        .filter(|c| !c.is_control() || c.is_whitespace())
        .take(4096)
        .collect()
}

// Use in message handlers
let clean_text = sanitize_text(&message.text);
```

### 10. HTTPS Setup (2 hours)
```yaml
# docker-compose.yml - Add Traefik
traefik:
  image: traefik:v2.10
  container_name: susbonk-traefik
  command:
    - "--api.insecure=false"
    - "--providers.docker=true"
    - "--providers.docker.exposedbydefault=false"
    - "--entrypoints.web.address=:80"
    - "--entrypoints.websecure.address=:443"
    - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
    - "--certificatesresolvers.letsencrypt.acme.email=admin@susbonk.com"
    - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - "/var/run/docker.sock:/var/run/docker.sock:ro"
    - "letsencrypt:/letsencrypt"
  networks:
    - susbonk-net

# Update backend service
backend:
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.backend.rule=Host(`api.susbonk.com`)"
    - "traefik.http.routers.backend.entrypoints=websecure"
    - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
```

**Total Time**: ~4 hours  
**Impact**: Prevents DDoS, improves security posture

---

## 🟡 MEDIUM PRIORITY - Fix This Month

### 11. Database Connection Pooling
```python
# backend/settings.py
DB_POOL_SIZE: int = int(os.environ.get('DB_POOL_SIZE', '50'))
DB_POOL_RECYCLE: int = 3600
DB_POOL_PRE_PING: bool = True
```

### 12. Redis Result Stream Cleanup
```rust
// ai-service/src/main.rs
redis::cmd("XADD")
    .arg(&cfg.results_stream)
    .arg("MAXLEN")
    .arg("~")
    .arg(10000)
    .arg("*")
    .arg(&[("result", result_json)])
    .query_async(&mut conn)
    .await?;
```

### 13. Eager Loading for Queries
```python
# backend/api/handlers/chat.py
from sqlalchemy.orm import selectinload

stmt = select(Chat).options(
    selectinload(Chat.prompts),
    selectinload(Chat.custom_prompts),
    selectinload(Chat.user_states)
).where(Chat.user_id == current_user.id)
```

### 14. Prometheus Metrics
```toml
# ai-service/Cargo.toml
[dependencies]
prometheus = "0.13"
```

```rust
// ai-service/src/main.rs
use prometheus::{Counter, Encoder, TextEncoder, Registry};

let registry = Registry::new();
let requests_total = Counter::new("ai_requests_total", "Total AI requests").unwrap();
registry.register(Box::new(requests_total.clone())).unwrap();

// Metrics endpoint
let metrics_app = Router::new()
    .route("/metrics", get(|| async move {
        let encoder = TextEncoder::new();
        let metric_families = registry.gather();
        let mut buffer = vec![];
        encoder.encode(&metric_families, &mut buffer).unwrap();
        String::from_utf8(buffer).unwrap()
    }));
```

### 15. Error Handling Standardization
```python
# backend/api/exceptions.py
class SusBonkException(Exception):
    """Base exception"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationError(SusBonkException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class AuthorizationError(SusBonkException):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=403)

# backend/main.py
@main_app.exception_handler(SusBonkException)
async def susbonk_exception_handler(request: Request, exc: SusBonkException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )
```

---

## Testing Additions

### Unit Tests
```python
# backend/tests/test_chat_crud.py
import pytest
from api.handlers.chat import get_chats, create_chat

@pytest.mark.asyncio
async def test_get_chats_returns_user_chats_only(client, test_user, test_chat):
    response = await client.get("/api/chats", headers=auth_headers(test_user))
    assert response.status_code == 200
    chats = response.json()
    assert all(chat["user_id"] == test_user.id for chat in chats)

@pytest.mark.asyncio
async def test_create_chat_validates_platform(client, test_user):
    response = await client.post("/api/chats", json={
        "type": "invalid_platform",
        "platform_chat_id": 123
    }, headers=auth_headers(test_user))
    assert response.status_code == 422
```

### Load Tests
```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class SusBonkUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        response = self.client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        self.token = response.json()["access_token"]
    
    @task(3)
    def list_chats(self):
        self.client.get("/api/chats", headers={
            "Authorization": f"Bearer {self.token}"
        })
    
    @task(1)
    def check_message(self):
        self.client.post("/api/messages/check", json={
            "text": "Test spam message",
            "chat_id": 123
        }, headers={
            "Authorization": f"Bearer {self.token}"
        })
```

Run with:
```bash
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] All CRITICAL fixes applied
- [ ] All HIGH priority fixes applied
- [ ] Environment variables configured
- [ ] Secrets generated and stored securely
- [ ] Database migrations tested
- [ ] Load tests passed (1000 concurrent users)
- [ ] Security scan completed (no critical/high issues)

### Deployment
- [ ] Database backup created
- [ ] Blue-green deployment configured
- [ ] Health checks verified
- [ ] Monitoring dashboards created
- [ ] Alerting rules configured
- [ ] Rollback plan documented

### Post-Deployment
- [ ] Smoke tests passed
- [ ] Performance metrics baseline established
- [ ] Error rates monitored (< 0.1%)
- [ ] Response times acceptable (p95 < 500ms)
- [ ] Security monitoring active
- [ ] Incident response team notified

---

## Quick Commands

### Generate Secrets
```bash
# Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Random passwords
openssl rand -base64 32

# Redis password
openssl rand -hex 16
```

### Run Security Scan
```bash
# Python dependencies
pip install safety
safety check

# Rust dependencies
cargo install cargo-audit
cargo audit

# Docker images
docker scan susbonk-backend:latest
```

### Test Deployment
```bash
# Start services
docker-compose up -d

# Wait for health checks
./scripts/wait-for-health.sh

# Run smoke tests
pytest tests/smoke/

# Check logs
docker-compose logs -f backend
```

---

## Estimated Timeline

| Phase | Duration | Effort |
|-------|----------|--------|
| Critical Fixes | 1 day | 4 hours |
| High Priority | 1 week | 16 hours |
| Medium Priority | 2 weeks | 32 hours |
| Testing | 1 week | 24 hours |
| Documentation | 3 days | 12 hours |
| **Total** | **5 weeks** | **88 hours** |

---

## Success Criteria

- ✅ Zero critical security vulnerabilities
- ✅ All services pass health checks
- ✅ Load test: 1000 concurrent users, p95 < 500ms
- ✅ Test coverage > 80%
- ✅ Zero hardcoded secrets
- ✅ HTTPS enabled on all endpoints
- ✅ Rate limiting active
- ✅ Monitoring and alerting configured

---

**Next Action**: Start with critical fixes (30 minutes total)
