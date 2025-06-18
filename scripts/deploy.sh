#!/bin/bash

# Discord Bot Deployment Script
set -e

echo "🚀 Starting Discord Bot deployment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Parse command line arguments
ENVIRONMENT=${1:-production}
PROFILE=${2:-basic}

echo "📋 Deployment Configuration:"
echo "   Environment: $ENVIRONMENT"
echo "   Profile: $PROFILE"

# Build images
echo "🔨 Building Docker images..."
docker-compose build

# Deploy based on environment
case $ENVIRONMENT in
    "development"|"dev")
        echo "🔧 Starting development environment..."
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
        ;;
    "production"|"prod")
        echo "🏭 Starting production environment..."
        case $PROFILE in
            "full")
                docker-compose -f docker-compose.yml -f docker-compose.prod.yml --profile database --profile monitoring up -d
                ;;
            "database")
                docker-compose -f docker-compose.yml -f docker-compose.prod.yml --profile database up -d
                ;;
            *)
                docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
                ;;
        esac
        ;;
    *)
        echo "❌ Unknown environment: $ENVIRONMENT"
        echo "Available environments: development, production"
        exit 1
        ;;
esac

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose ps

# Show logs
echo "📝 Recent logs:"
docker-compose logs --tail=20 discord-bot

echo "✅ Deployment completed!"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose logs -f discord-bot"
echo "   Check status: docker-compose ps"
echo "   Stop services: docker-compose down"
echo "   Start client: docker-compose --profile client up socket-client"

if [[ $PROFILE == *"monitoring"* ]]; then
    echo ""
    echo "🔍 Monitoring URLs:"
    echo "   Prometheus: http://localhost:9090"
    echo "   Grafana: http://localhost:3000 (admin/admin)"
fi
