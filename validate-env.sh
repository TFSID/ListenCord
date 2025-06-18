#!/bin/bash

# Environment validation script
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🔍 Validating Environment Configuration${NC}"
echo "========================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Run: cp .env.example .env"
    exit 1
fi

# Load .env
source .env

# Validate required variables
REQUIRED_VARS=("DISCORD_BOT_TOKEN")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ] || [ "${!var}" = "your_discord_bot_token_here" ] || [ "${!var}" = "your_bot_token_here" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo -e "${RED}❌ Missing or invalid required variables:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Please edit .env file and set proper values"
    exit 1
fi

# Validate optional variables with defaults
echo -e "${GREEN}✅ Required variables configured${NC}"
echo ""
echo -e "${YELLOW}Configuration Summary:${NC}"
echo "BOT_PREFIX: ${BOT_PREFIX:-!}"
echo "LOG_LEVEL: ${LOG_LEVEL:-INFO}"
echo "SOCKET_HOST: ${SOCKET_HOST:-localhost}"
echo "SOCKET_PORT: ${SOCKET_PORT:-8888}"
echo "MAX_CONNECTIONS: ${MAX_CONNECTIONS:-10}"
echo ""
echo -e "${GREEN}✅ Environment validation passed!${NC}"
