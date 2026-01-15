#!/bin/bash
set -e

echo "🚀 Starting Postal Mail Server..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start services
echo "📦 Starting Postal services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

# Initialize database if needed
echo "🗄️ Initializing database..."
docker-compose exec postal-web postal initialize || echo "Database already initialized"

# Create admin user if needed
echo "👤 Creating admin user..."
docker-compose exec postal-web postal make-user || echo "Admin user may already exist"

echo "✅ Postal is ready!"
echo "🌐 Web UI: http://localhost:5000"
echo "📧 SMTP: localhost:2525"
echo ""
echo "Next steps:"
echo "1. Visit http://localhost:5000 to access the web interface"
echo "2. Create a mail server and domain"
echo "3. Generate SMTP credentials"
echo "4. Update your .env file with the new SMTP settings"
