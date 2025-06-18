#!/bin/bash

# Discord Bot Docker Quickstart Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🐳 Discord Socket Listener - Docker Quickstart       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check prerequisites
print_status "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_success "Prerequisites check passed!"

# Setup environment
print_status "Setting up environment..."

if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        print_success "Created .env file from template"
    else
        print_error ".env.example file not found!"
        exit 1
    fi
else
    print_warning ".env file already exists, skipping creation"
fi

# Check if bot token is configured
if grep -q "your_discord_bot_token_here" .env || grep -q "your_bot_token_here" .env; then
    print_warning "Discord bot token not configured!"
    echo ""
    echo -e "${YELLOW}Please edit .env file and set your Discord bot token:${NC}"
    echo "DISCORD_BOT_TOKEN=your_actual_bot_token_here"
    echo ""
    read -p "Press Enter after configuring the bot token, or Ctrl+C to exit..."
fi

# Create necessary directories
print_status "Creating directories..."
mkdir -p logs data backups
print_success "Directories created"

# Build images
print_status "Building Docker images... (this may take a few minutes)"
if command -v make &> /dev/null; then
    make build
else
    docker-compose build
fi
print_success "Docker images built successfully!"

# Start services
print_status "Starting services..."
if command -v make &> /dev/null; then
    make up
else
    docker-compose up -d discord-bot redis
fi

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 10

# Check service status
print_status "Checking service status..."
if command -v make &> /dev/null; then
    make status
else
    docker-compose ps
fi

# Verify bot is running
if docker-compose ps discord-bot | grep -q "Up"; then
    print_success "Discord bot is running!"
else
    print_error "Discord bot failed to start. Check logs:"
    docker-compose logs discord-bot
    exit 1
fi

# Show success message
echo ""
print_success "🎉 Discord Socket Listener is now running!"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Invite your bot to a Discord server"
echo "2. Use bot commands:"
echo "   • !listen    - Start monitoring current channel"
echo "   • !status    - Check monitoring status"
echo "   • !unlisten  - Stop monitoring current channel"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
if command -v make &> /dev/null; then
    echo "• make logs     - View bot logs"
    echo "• make client   - Start socket client for testing"
    echo "• make status   - Check service status"
    echo "• make down     - Stop services"
else
    echo "• docker-compose logs -f discord-bot  - View bot logs"
    echo "• docker-compose --profile client up socket-client  - Start socket client"
    echo "• docker-compose ps  - Check service status"
    echo "• docker-compose down  - Stop services"
fi
echo ""
echo -e "${BLUE}Service endpoints:${NC}"
echo "• Socket Server: localhost:8888"
echo "• Redis: localhost:6379"
echo ""
echo -e "${YELLOW}View logs:${NC}"
if command -v make &> /dev/null; then
    make logs
else
    docker-compose logs --tail=20 discord-bot
fi
