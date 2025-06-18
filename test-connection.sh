#!/bin/bash

# Test connection script
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

echo -e "${BLUE}"
echo "🧪 Testing Discord Socket Listener Connection"
echo "=============================================="
echo -e "${NC}"

# Test 1: Check if services are running
print_test "Checking if services are running..."
if docker-compose ps discord-bot | grep -q "Up"; then
    print_pass "Discord bot service is running"
else
    print_fail "Discord bot service is not running"
    echo "Run: make up"
    exit 1
fi

if docker-compose ps redis | grep -q "Up"; then
    print_pass "Redis service is running"
else
    print_fail "Redis service is not running"
fi

# Test 2: Check socket connectivity
print_test "Testing socket server connectivity..."
if timeout 5 bash -c "</dev/tcp/localhost/8888"; then
    print_pass "Socket server is accepting connections on port 8888"
else
    print_fail "Cannot connect to socket server on port 8888"
    echo "Check logs: make logs"
fi

# Test 3: Check Redis connectivity
print_test "Testing Redis connectivity..."
if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
    print_pass "Redis is responding"
else
    print_fail "Redis is not responding"
fi

# Test 4: Check bot logs for errors
print_test "Checking bot logs for errors..."
if docker-compose logs discord-bot 2>&1 | grep -i error | tail -5; then
    print_fail "Found errors in bot logs (showing last 5):"
    docker-compose logs discord-bot 2>&1 | grep -i error | tail -5
else
    print_pass "No recent errors found in bot logs"
fi

# Test 5: Test socket client connection
print_test "Testing socket client connection..."
timeout 10 docker-compose run --rm socket-client python -c "
import socket
import sys
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect(('discord-bot', 8888))
    print('Socket client can connect successfully')
    s.close()
    sys.exit(0)
except Exception as e:
    print(f'Socket client connection failed: {e}')
    sys.exit(1)
" && print_pass "Socket client connection test passed" || print_fail "Socket client connection test failed"

echo ""
echo -e "${GREEN}Connection test completed!${NC}"
echo ""
echo -e "${YELLOW}If any tests failed:${NC}"
echo "1. Check service status: make status"
echo "2. View logs: make logs"
echo "3. Restart services: make restart"
echo "4. Check configuration: cat .env"
