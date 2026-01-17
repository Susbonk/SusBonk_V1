#!/bin/bash

# SusBonk API - Quick Start Script
# This script helps you get the API up and running quickly

set -e

echo "🐕 SusBonk API - Quick Start"
echo "============================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "⚠️  .env file not found in parent directory"
    echo "Creating from .env.example..."
    if [ -f "../.env.example" ]; then
        cp ../.env.example ../.env
        echo "✓ Created .env file"
    else
        echo "❌ .env.example not found. Please create .env manually."
        exit 1
    fi
fi

echo "✓ Environment file exists"
echo ""

# Start the services
echo "🚀 Starting SusBonk API services..."
echo ""
docker-compose up -d pg-database
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

docker-compose up -d pg-init
echo "⏳ Waiting for database initialization..."
sleep 3

docker-compose up -d api-backend
echo "⏳ Waiting for API to start..."
sleep 5

# Check if API is healthy
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo ""
    echo "✅ SusBonk API is running!"
    echo ""
    echo "📚 Access the API documentation:"
    echo "   Swagger UI: http://localhost:8000/docs"
    echo "   ReDoc:      http://localhost:8000/redoc"
    echo "   Health:     http://localhost:8000/health"
    echo ""
    echo "🧪 Test the API:"
    echo "   ./test-api.sh"
    echo ""
    echo "📊 View logs:"
    echo "   docker-compose logs -f api-backend"
    echo ""
    echo "🛑 Stop the API:"
    echo "   docker-compose down"
    echo ""
else
    echo ""
    echo "⚠️  API might not be ready yet. Check logs:"
    echo "   docker-compose logs api-backend"
    echo ""
fi
