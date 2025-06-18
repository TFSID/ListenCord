#!/bin/bash

# Backup script for Discord Bot data
set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="discord_bot_backup_$TIMESTAMP"

echo "📦 Creating backup: $BACKUP_NAME"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup logs
echo "📝 Backing up logs..."
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_logs.tar.gz" logs/

# Backup data
echo "💾 Backing up data..."
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_data.tar.gz" data/ monitored_channels.json

# Backup database if running
if docker-compose ps postgres | grep -q "Up"; then
    echo "🗄️ Backing up database..."
    docker-compose exec -T postgres pg_dump -U discord_user discord_bot > "$BACKUP_DIR/${BACKUP_NAME}_database.sql"
fi

# Backup Redis if running
if docker-compose ps redis | grep -q "Up"; then
    echo "🔴 Backing up Redis..."
    docker-compose exec -T redis redis-cli BGSAVE
    docker cp discord-redis:/data/dump.rdb "$BACKUP_DIR/${BACKUP_NAME}_redis.rdb"
fi

echo "✅ Backup completed: $BACKUP_DIR/$BACKUP_NAME*"
echo "📋 Backup files:"
ls -la "$BACKUP_DIR/${BACKUP_NAME}"*
