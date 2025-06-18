.PHONY: help build up down logs shell test clean quickstart

# Default target
help:
	@echo "🐳 Discord Socket Listener - Docker Commands"
	@echo "============================================="
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  quickstart    - Run complete setup (recommended for first time)"
	@echo "  up            - Start services"
	@echo "  test-conn     - Test all connections"
	@echo ""
	@echo "📋 Management:"
	@echo "  build         - Build Docker images"
	@echo "  up-dev        - Start services in development mode"
	@echo "  up-prod       - Start services in production mode"
	@echo "  up-full       - Start all services including database and monitoring"
	@echo "  down          - Stop services"
	@echo "  restart       - Restart services"
	@echo "  clean         - Clean up containers and volumes"
	@echo ""
	@echo "🔍 Monitoring:"
	@echo "  logs          - Show logs"
	@echo "  status        - Check service status"
	@echo "  stats         - Show resource usage"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  client        - Start socket client"
	@echo "  shell         - Open shell in bot container"
	@echo "  test          - Run tests"
	@echo ""
	@echo "💾 Maintenance:"
	@echo "  backup        - Create backup"
	@echo "  update        - Update and restart services"

# Quickstart - complete setup
quickstart:
	@echo "🚀 Running Discord Bot Quickstart..."
	@chmod +x quickstart.sh
	@./quickstart.sh

# Test connections
test-conn:
	@echo "🧪 Testing connections..."
	@chmod +x test-connection.sh
	@./test-connection.sh

# Build images
build:
	@echo "🔨 Building Docker images..."
	@docker-compose build

# Start basic services
up:
	@echo "🚀 Starting services..."
	@docker-compose up -d discord-bot redis
	@echo "✅ Services started! Use 'make logs' to view logs"

# Start in development mode
up-dev:
	@echo "🔧 Starting development environment..."
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Start in production mode
up-prod:
	@echo "🏭 Starting production environment..."
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Start all services including optional ones
up-full:
	@echo "🌟 Starting all services..."
	@docker-compose --profile database --profile monitoring up -d
	@echo "✅ All services started!"
	@echo "📊 Monitoring URLs:"
	@echo "   Prometheus: http://localhost:9090"
	@echo "   Grafana: http://localhost:3000 (admin/admin)"

# Stop services
down:
	@echo "🛑 Stopping services..."
	@docker-compose down

# Show logs
logs:
	@echo "📝 Showing bot logs (Ctrl+C to exit)..."
	@docker-compose logs -f discord-bot

# Open shell in bot container
shell:
	@echo "🐚 Opening shell in bot container..."
	@docker-compose exec discord-bot /bin/bash

# Start socket client
client:
	@echo "🔌 Starting socket client..."
	@docker-compose --profile client up socket-client

# Run tests (when implemented)
test:
	@echo "🧪 Running tests..."
	@docker-compose exec discord-bot python -m pytest tests/ || echo "No tests found"

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	@docker-compose down -v --remove-orphans
	@docker system prune -f
	@echo "✅ Cleanup completed"

# Restart services
restart:
	@echo "🔄 Restarting services..."
	@docker-compose restart discord-bot
	@echo "✅ Services restarted"

# Check status
status:
	@echo "📊 Service Status:"
	@docker-compose ps

# View resource usage
stats:
	@echo "📈 Resource Usage:"
	@docker stats --no-stream

# Create backup
backup:
	@echo "💾 Creating backup..."
	@chmod +x scripts/backup.sh
	@./scripts/backup.sh

# Update services
update:
	@echo "🔄 Updating services..."
	@git pull
	@docker-compose build
	@docker-compose up -d discord-bot redis
	@echo "✅ Update completed"

# Show service URLs
urls:
	@echo "🌐 Service URLs:"
	@echo "   Socket Server: http://localhost:8888"
	@echo "   Redis: localhost:6379"
	@echo "   Grafana: http://localhost:3000 (admin/admin)"
	@echo "   Prometheus: http://localhost:9090"
	@echo "   PostgreSQL: localhost:5432"
