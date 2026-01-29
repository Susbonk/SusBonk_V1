# Security Configuration Guide

## ⚠️ IMPORTANT: Before First Deployment

This guide walks you through securing your SusBonk deployment.

## Step 1: Generate Secrets (5 minutes)

### PostgreSQL Password
```bash
openssl rand -base64 32
# Example output: xK9mP2vL8nQ4rT6wY1zB3cD5fG7hJ9kM0nP2qR4sT6u=
```

### Redis Password
```bash
openssl rand -hex 16
# Example output: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### OpenSearch Password
```bash
openssl rand -base64 32
# Example output: yL0mN2oP4qR6sT8uV0wX2yZ4aB6cD8eF0gH2iJ4kL6m=
```

### Backend Secret Key
```bash
openssl rand -base64 32
# Example output: zM1nO3pQ5rS7tU9vW1xY3zA5bC7dE9fG1hI3jK5lM7n=
```

### Django Secret Key
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Example output: django-insecure-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

### Django Superuser Password
Use a password manager to generate a strong password:
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- Example: `Tr0ng!P@ssw0rd#2026`

## Step 2: Create .env File

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and replace all `CHANGE_ME_*` values with the secrets you generated:

```bash
# Database
POSTGRES_DB=susbonk
POSTGRES_USER=susbonk
POSTGRES_PASSWORD=xK9mP2vL8nQ4rT6wY1zB3cD5fG7hJ9kM0nP2qR4sT6u=

# Redis
REDIS_PASSWORD=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

# OpenSearch
OPENSEARCH_PASSWORD=yL0mN2oP4qR6sT8uV0wX2yZ4aB6cD8eF0gH2iJ4kL6m=

# Backend
SECRET_KEY=zM1nO3pQ5rS7tU9vW1xY3zA5bC7dE9fG1hI3jK5lM7n=
ENVIRONMENT=production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Django Admin
DJANGO_SECRET_KEY=django-insecure-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
DJANGO_SUPERUSER_PASSWORD=Tr0ng!P@ssw0rd#2026

# Telegram Bot
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Frontend
VITE_API_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com

# Logging
RUST_LOG=info

# AI Service
MODEL_PATH=/models
```

## Step 3: Secure .env File

```bash
# Set restrictive permissions
chmod 600 .env

# Verify it's in .gitignore
grep -q "^\.env$" .gitignore || echo ".env" >> .gitignore

# Never commit .env
git status  # Should NOT show .env
```

## Step 4: Production Environment Variables

For production deployments, use environment-specific secrets:

### AWS Secrets Manager
```bash
aws secretsmanager create-secret \
  --name susbonk/postgres-password \
  --secret-string "xK9mP2vL8nQ4rT6wY1zB3cD5fG7hJ9kM0nP2qR4sT6u="

aws secretsmanager create-secret \
  --name susbonk/redis-password \
  --secret-string "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"

# ... repeat for all secrets
```

### Docker Secrets
```bash
echo "xK9mP2vL8nQ4rT6wY1zB3cD5fG7hJ9kM0nP2qR4sT6u=" | docker secret create postgres_password -
echo "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6" | docker secret create redis_password -
```

### Kubernetes Secrets
```bash
kubectl create secret generic susbonk-secrets \
  --from-literal=postgres-password='xK9mP2vL8nQ4rT6wY1zB3cD5fG7hJ9kM0nP2qR4sT6u=' \
  --from-literal=redis-password='a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6' \
  --from-literal=opensearch-password='yL0mN2oP4qR6sT8uV0wX2yZ4aB6cD8eF0gH2iJ4kL6m=' \
  --from-literal=secret-key='zM1nO3pQ5rS7tU9vW1xY3zA5bC7dE9fG1hI3jK5lM7n=' \
  --from-literal=django-secret-key='django-insecure-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6'
```

## Step 5: Verify Security Settings

### Check Django Settings
```bash
docker-compose exec admin python manage.py check --deploy
```

Expected output:
```
System check identified no issues (0 silenced).
```

### Test Redis Authentication
```bash
# Should fail without password
docker-compose exec redis redis-cli ping
# Error: NOAUTH Authentication required

# Should succeed with password
docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping
# PONG
```

### Verify Environment
```bash
# Check ENVIRONMENT is set correctly
docker-compose exec backend env | grep ENVIRONMENT
# ENVIRONMENT=production

# Check DEBUG is disabled
docker-compose exec admin python manage.py shell -c "from django.conf import settings; print(f'DEBUG={settings.DEBUG}')"
# DEBUG=False
```

## Step 6: Security Checklist

Before going live, verify:

- [ ] All secrets generated with strong randomness
- [ ] `.env` file has 600 permissions
- [ ] `.env` is in `.gitignore` and not committed
- [ ] `ENVIRONMENT=production` in production
- [ ] `DEBUG=False` verified in Django
- [ ] `ALLOWED_HOSTS` set to actual domain(s)
- [ ] `CORS_ORIGINS` set to actual frontend URL(s)
- [ ] Redis requires authentication
- [ ] All default passwords changed
- [ ] HTTPS/TLS configured (see next section)

## Step 7: Enable HTTPS (Production Only)

### Option A: Using Traefik (Recommended)

Add to `docker-compose.yml`:
```yaml
services:
  traefik:
    image: traefik:v2.10
    container_name: susbonk-traefik
    command:
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=${ACME_EMAIL}"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "letsencrypt:/letsencrypt"
    networks:
      - susbonk-net

  backend:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`api.yourdomain.com`)"
      - "traefik.http.routers.backend.entrypoints=websecure"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
      - "traefik.http.services.backend.loadbalancer.server.port=8000"

volumes:
  letsencrypt:
    driver: local
```

### Option B: Using Nginx + Certbot

See `docs/nginx-ssl-setup.md` for detailed instructions.

## Step 8: Rotate Secrets Regularly

Set up a reminder to rotate secrets every 90 days:

```bash
# Add to crontab
0 0 1 */3 * /path/to/rotate-secrets.sh
```

Create `rotate-secrets.sh`:
```bash
#!/bin/bash
# Generate new secrets
NEW_POSTGRES_PW=$(openssl rand -base64 32)
NEW_REDIS_PW=$(openssl rand -hex 16)

# Update database password
docker-compose exec postgres psql -U postgres -c "ALTER USER susbonk PASSWORD '$NEW_POSTGRES_PW';"

# Update Redis password
docker-compose exec redis redis-cli CONFIG SET requirepass "$NEW_REDIS_PW"

# Update .env file
sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$NEW_POSTGRES_PW/" .env
sed -i "s/^REDIS_PASSWORD=.*/REDIS_PASSWORD=$NEW_REDIS_PW/" .env

# Restart services
docker-compose restart backend telegram-bot ai-service
```

## Troubleshooting

### "NOAUTH Authentication required" Error
Redis password not configured correctly. Check:
1. `REDIS_PASSWORD` in `.env`
2. `REDIS_URL` includes password: `redis://:password@redis:6379`
3. Redis container restarted after password change

### "ImproperlyConfigured: DJANGO_SECRET_KEY must be set"
Django secret key missing. Check:
1. `DJANGO_SECRET_KEY` in `.env`
2. Environment variable passed to admin container
3. No typos in variable name

### "DisallowedHost" Error
Domain not in ALLOWED_HOSTS. Check:
1. `ALLOWED_HOSTS` includes your domain
2. No trailing slashes in domain names
3. Both www and non-www versions included if needed

## Security Best Practices

1. **Never commit secrets** - Use `.gitignore` and verify with `git status`
2. **Use strong passwords** - Minimum 32 characters for service passwords
3. **Rotate regularly** - Change secrets every 90 days
4. **Limit access** - Use firewall rules to restrict database/Redis access
5. **Monitor logs** - Set up alerts for authentication failures
6. **Enable 2FA** - For Django admin and any user accounts
7. **Backup secrets** - Store encrypted backups in secure location
8. **Audit access** - Review who has access to secrets regularly

## Emergency: Secrets Compromised

If secrets are compromised:

1. **Immediately rotate all secrets**
2. **Revoke all active sessions**
3. **Review access logs for unauthorized access**
4. **Notify affected users if data breach occurred**
5. **Update incident response documentation**

```bash
# Emergency rotation script
./scripts/emergency-rotate-all-secrets.sh

# Revoke all JWT tokens (restart backend)
docker-compose restart backend

# Check for suspicious activity
docker-compose logs --since 24h | grep -i "failed\|unauthorized\|error"
```

## Support

For security issues, contact: security@susbonk.com  
For general support: support@susbonk.com

**Last Updated**: 2026-01-29
