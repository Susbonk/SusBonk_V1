#!/bin/bash
# Test script for Django Admin Panel deployment

set -e

echo "=== SusBonk Django Admin Panel - Deployment Test ==="
echo ""

# Check directory structure
echo "✓ Checking directory structure..."
test -d admin/core || { echo "✗ Missing admin/core directory"; exit 1; }
test -d admin/db_admin || { echo "✗ Missing admin/db_admin directory"; exit 1; }
test -d admin/core/migrations || { echo "✗ Missing migrations directory"; exit 1; }
echo "  ✓ Directory structure OK"

# Check required files
echo ""
echo "✓ Checking required files..."
test -f admin/pyproject.toml || { echo "✗ Missing pyproject.toml"; exit 1; }
test -f admin/manage.py || { echo "✗ Missing manage.py"; exit 1; }
test -f admin/start.sh || { echo "✗ Missing start.sh"; exit 1; }
test -f admin/Dockerfile || { echo "✗ Missing Dockerfile"; exit 1; }
test -f admin/core/models.py || { echo "✗ Missing models.py"; exit 1; }
test -f admin/core/admin.py || { echo "✗ Missing admin.py"; exit 1; }
test -f admin/db_admin/settings.py || { echo "✗ Missing settings.py"; exit 1; }
test -f admin/core/migrations/0001_initial.py || { echo "✗ Missing initial migration"; exit 1; }
test -f admin/core/migrations/0002_default_data.py || { echo "✗ Missing default data migration"; exit 1; }
echo "  ✓ All required files present"

# Check docker-compose configuration
echo ""
echo "✓ Checking docker-compose configuration..."
grep -q "pg-database:" backend/docker-compose.yml || { echo "✗ Missing pg-database service"; exit 1; }
grep -q "admin:" backend/docker-compose.yml || { echo "✗ Missing admin service"; exit 1; }
grep -q "db-net:" backend/docker-compose.yml || { echo "✗ Missing db-net network"; exit 1; }
echo "  ✓ Docker-compose configuration OK"

# Check environment variables
echo ""
echo "✓ Checking environment variables..."
test -f .env || { echo "✗ Missing .env file"; exit 1; }
grep -q "POSTGRES_DB" .env || { echo "✗ Missing POSTGRES_DB in .env"; exit 1; }
grep -q "POSTGRES_USER" .env || { echo "✗ Missing POSTGRES_USER in .env"; exit 1; }
grep -q "POSTGRES_PASSWORD" .env || { echo "✗ Missing POSTGRES_PASSWORD in .env"; exit 1; }
echo "  ✓ Environment variables configured"

# Check file permissions
echo ""
echo "✓ Checking file permissions..."
test -x admin/start.sh || { echo "✗ start.sh is not executable"; exit 1; }
echo "  ✓ File permissions OK"

echo ""
echo "=== All checks passed! ==="
echo ""
echo "Next steps:"
echo "1. Start Docker daemon"
echo "2. Build and start services:"
echo "   cd backend"
echo "   docker-compose up -d pg-database"
echo "   docker-compose up -d admin"
echo ""
echo "3. Check logs:"
echo "   docker logs -f susbonk-admin"
echo ""
echo "4. Access admin panel:"
echo "   http://localhost:5000/admin"
echo "   Username: \$DJANGO_ADMIN_USER (from .env)"
echo "   Password: \$DJANGO_ADMIN_PASSWORD (from .env)"
echo ""
echo "5. Verify database:"
echo "   docker exec -it susbonk-postgres psql -U postgres -d postgres -c '\\dt'"
echo ""
