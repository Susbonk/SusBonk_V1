# Postal Quick Reference

## Start Postal
```bash
cd postal && ./start.sh
```

## Stop Postal
```bash
cd postal && docker-compose down
```

## View Logs
```bash
cd postal && docker-compose logs -f
```

## Test Email
```bash
cd postal && ./test-email.sh
```

## Access Web UI
http://localhost:5000

## SMTP Endpoint
- Host: `postal-smtp` (from Docker) or `localhost` (from host)
- Port: `2525`

## Run Integration Test
```bash
cd log-platform
cargo test --test email_integration -- --ignored
```

## Rebuild alertd with new config
```bash
cd backend
docker-compose build alert-engine
docker-compose up -d alert-engine
```

## Check alertd logs
```bash
docker logs -f susbonk-alertd
```

## Environment Variables (.env)
```bash
SMTP_SERVER=postal-smtp
SMTP_PORT=2525
SMTP_USER=<from-postal-ui>
SMTP_PASSWORD=<from-postal-ui>
ALERT_EMAIL_FROM=alerts@postal.localhost
ALERT_EMAIL_TO=admin@postal.localhost
```

## Troubleshooting Commands
```bash
# Check if services are running
docker ps | grep postal

# Check network connectivity
docker network inspect susbonk-network

# Test SMTP port
nc -zv localhost 2525

# Reinitialize database
docker-compose exec postal-web postal initialize

# Create new admin user
docker-compose exec postal-web postal make-user
```
