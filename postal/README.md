# Postal Mail Server Setup

Production-quality self-hosted SMTP server for SusBonk alert notifications.

## Architecture

- **Separate microservice**: Postal runs independently from backend services
- **SMTP relay**: EmailNotifier connects via SMTP (port 2525)
- **Local development**: Uses `postal.localhost` domain (no DNS required)
- **Docker Compose**: MariaDB + Web UI + SMTP Server + Worker

## Quick Start

### 1. Start Postal Services

```bash
cd postal
./start.sh
```

This will:
- Start MariaDB, Postal web, SMTP, and worker containers
- Initialize the database
- Create an admin user (follow prompts)

### 2. Configure Postal

1. Visit http://localhost:5000
2. Log in with admin credentials
3. Create a new **Mail Server** (e.g., "SusBonk Alerts")
4. Add a **Domain** (use `postal.localhost` for local dev)
5. Create **SMTP Credentials** in the Credentials section
6. Note the username and password

### 3. Update Environment Variables

Update `.env` in project root:

```bash
SMTP_SERVER=postal-smtp
SMTP_PORT=2525
SMTP_USER=<your-postal-smtp-username>
SMTP_PASSWORD=<your-postal-smtp-password>
ALERT_EMAIL_FROM=alerts@postal.localhost
ALERT_EMAIL_TO=admin@postal.localhost
```

### 4. Test Email Sending

```bash
cd postal
./test-email.sh
```

This runs automated integration tests and provides manual verification steps.

## Service Endpoints

- **Web UI**: http://localhost:5000
- **SMTP Server**: localhost:2525
- **MariaDB**: localhost:3306 (internal only)

## Integration with Backend

The `backend/docker-compose.yml` has been updated to:
- Load `.env` file for alertd service
- Connect alertd to `susbonk-network` (shared with Postal SMTP)
- Override SMTP settings to point to Postal

## Testing

### Automated Test

```bash
cd log-platform
cargo test --test email_integration -- --ignored
```

### Manual Test

1. Start Postal: `cd postal && docker-compose up -d`
2. Start backend: `cd backend && docker-compose up -d alert-engine`
3. Trigger an alert (disk threshold, error logs, etc.)
4. Check Postal web UI for delivered messages

## Environment Variable Mapping

| .env Variable | Rust Code | Purpose |
|---------------|-----------|---------|
| `SMTP_SERVER` | `cfg.smtp_host` | SMTP hostname |
| `SMTP_PORT` | `cfg.smtp_port` | SMTP port |
| `SMTP_USER` | `cfg.smtp_user` | SMTP username (optional) |
| `SMTP_PASSWORD` | `cfg.smtp_password` | SMTP password (optional) |
| `ALERT_EMAIL_FROM` | `cfg.alert_email_from` | Sender address |
| `ALERT_EMAIL_TO` | `cfg.alert_email_to` | Recipient address |

## Troubleshooting

### Postal services won't start

```bash
# Check logs
docker-compose logs postal-mariadb
docker-compose logs postal-web

# Restart services
docker-compose down
docker-compose up -d
```

### Database initialization fails

```bash
# Manually initialize
docker-compose exec postal-web postal initialize
docker-compose exec postal-web postal make-user
```

### Emails not sending

1. Check SMTP credentials in Postal web UI
2. Verify domain is configured and verified
3. Check worker logs: `docker logs postal-worker`
4. Ensure `from` address matches configured domain

### Connection refused from alertd

1. Verify both services are on `susbonk-network`:
   ```bash
   docker network inspect susbonk-network
   ```
2. Check SMTP server is listening:
   ```bash
   docker logs postal-smtp
   ```
3. Test connection from alertd container:
   ```bash
   docker exec susbonk-alertd nc -zv postal-smtp 2525
   ```

## Production Considerations

For production deployment:

1. **Use real domain**: Replace `postal.localhost` with your domain
2. **Configure DNS**: Set up MX, SPF, DKIM, and DMARC records
3. **Enable TLS**: Configure SSL certificates for SMTP
4. **Secure credentials**: Use Docker secrets or vault
5. **Persistent storage**: Ensure volumes are backed up
6. **IP reputation**: Warm up your sending IP gradually
7. **Rate limiting**: Configure sending limits in Postal
8. **Monitoring**: Set up alerts for Postal service health

## Files Structure

```
postal/
├── docker-compose.yml      # Service definitions
├── config/
│   ├── postal.yml          # Postal configuration
│   └── signing.key         # RSA key for signing
├── start.sh                # Startup script
├── test-email.sh           # Testing script
└── README.md               # This file
```

## References

- [Postal Documentation](https://docs.postalserver.io/)
- [Postal GitHub](https://github.com/postalserver/postal)
- [Docker Hub](https://github.com/postalserver/postal/pkgs/container/postal)
