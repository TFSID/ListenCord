# Discord Socket Listener - Modular Version

Versi modular dari Discord Bot yang memonitor channel dan broadcast pesan melalui socket server.


## Bot Permission

| Permission                    | Keterangan                                                  |
| ----------------------------- | ----------------------------------------------------------- |
| `Read Messages/View Channels` | Untuk membaca pesan di channel                              |
| `Send Messages`               | Untuk merespon perintah `!listen`, `!status`, dll           |
| `Read Message History`        | Untuk mengakses pesan yang diedit/dihapus                   |
| `Manage Messages` (opsional)  | Jika bot perlu menghapus pesan atau mengelola pesan lainnya |
| `Connect` dan `Speak`         | **Tidak perlu** jika bot tidak menggunakan audio            |


## Bot Command

| Command                  | Deskripsi                                               |
| ------------------------ | ------------------------------------------------------- |
| `!listen [channel_id]`   | Mulai memonitor channel tertentu (opsional: ID channel) |
| `!unlisten [channel_id]` | Berhenti memonitor channel tertentu                     |
| `!status`                | Menampilkan status monitoring dan socket server         |


# Docker compose guide

# Basic (paling umum)
```
docker-compose up -d --build
```

# Development dengan hot reload
```
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

# Production dengan resource limits
```  
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

# Full stack dengan database & monitoring
```
docker-compose --profile database --profile monitoring up -d --build
```

# Force rebuild (jika ada masalah cache)
```
docker-compose build --no-cache && docker-compose up -d
```

# 🐳 Docker Quickstart Guide

Panduan cepat untuk menjalankan Discord Socket Listener menggunakan Docker.

## 📋 Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)
- Discord Bot Token

## ⚡ Quick Start (5 menit)

### 1. Clone & Setup

\`\`\`bash
# Clone repository
git clone <your-repo-url>
cd discord-socket-listener

# Copy environment template
cp .env.example .env
\`\`\`

### 2. Configure Bot Token

Edit file `.env` dan masukkan Discord bot token:

\`\`\`env
DISCORD_BOT_TOKEN=your_actual_bot_token_here
\`\`\`

### 3. Start Services

\`\`\`bash
# Build dan start (satu command!)
make up

# Atau tanpa Makefile:
docker-compose up -d discord-bot redis
\`\`\`

### 4. Verify Running

\`\`\`bash
# Check status
make status

# View logs
make logs
\`\`\`

**🎉 Done! Bot sudah running di background.**

## 🧪 Test Connection

### Start Socket Client

\`\`\`bash
# Terminal baru
make client

# Atau manual:
docker-compose --profile client up socket-client
\`\`\`

### Test Bot Commands

Di Discord server:
1. Invite bot ke server
2. Ketik: `!listen` (mulai monitor channel)
3. Ketik: `!status` (check status)
4. Kirim pesan → lihat di client terminal

## 🛠️ Common Commands

\`\`\`bash
# Start services
make up              # Basic (bot + redis)
make up-dev          # Development mode
make up-prod         # Production mode
make up-full         # All services (db + monitoring)

# Management
make logs            # View logs
make shell           # Open bot shell
make restart         # Restart bot
make down            # Stop all
make clean           # Clean everything

# Testing
make client          # Start test client
make status          # Check services
\`\`\`

## 📊 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| Socket Server | `localhost:8888` | Main socket endpoint |
| Redis | `localhost:6379` | Cache server |
| Grafana | `localhost:3000` | Monitoring dashboard |
| Prometheus | `localhost:9090` | Metrics server |
| PostgreSQL | `localhost:5432` | Database |

## 🔧 Configuration

### Environment Variables

Edit `.env` file:

\`\`\`env
# Required
DISCORD_BOT_TOKEN=your_token_here

# Optional
BOT_PREFIX=!
LOG_LEVEL=INFO
SOCKET_PORT=8888
MAX_CONNECTIONS=10
\`\`\`

### Service Profiles

\`\`\`bash
# Basic services only
docker-compose up -d

# With database
docker-compose --profile database up -d

# With monitoring
docker-compose --profile monitoring up -d

# Everything
docker-compose --profile database --profile monitoring up -d
\`\`\`

## 🚨 Troubleshooting

### Bot tidak connect ke Discord

\`\`\`bash
# Check logs
make logs

# Common issues:
# 1. Invalid bot token
# 2. Bot tidak di-invite ke server
# 3. Missing permissions
\`\`\`

### Socket client tidak connect

\`\`\`bash
# Check bot status
make status

# Check if port is open
docker-compose ps discord-bot

# Restart if needed
make restart
\`\`\`

### Permission errors

\`\`\`bash
# Fix file permissions
sudo chown -R $USER:$USER logs/ data/

# Or run with sudo (not recommended)
sudo make up
\`\`\`

## 📁 File Structure

\`\`\`
discord-socket-listener/
├── .env                 # Your configuration
├── docker-compose.yml   # Main compose file
├── Makefile            # Easy commands
├── logs/               # Application logs
├── data/               # Persistent data
└── monitored_channels.json  # Channel config
\`\`\`

## 🔄 Updates

\`\`\`bash
# Pull latest changes
git pull

# Rebuild and restart
make down
make build
make up
\`\`\`

## 🧹 Cleanup

\`\`\`bash
# Stop services
make down

# Remove everything (including data!)
make clean

# Remove only containers (keep data)
docker-compose down
\`\`\`

## 📞 Need Help?

1. Check logs: `make logs`
2. Check status: `make status`
3. Restart services: `make restart`
4. Clean start: `make clean && make up`

---

**Next Steps:**
- [Full Documentation](README.md)
- [Production Deployment](PRODUCTION.md)
- [Development Guide](DEVELOPMENT.md)
\`\`\`

Buat script quickstart otomatis:


## Quickstart

### Setup awal
```
cp .env.example .env
```
### Edit .env dengan Discord bot token

### Build dan start basic services
```
make build
make up
```

### Start dengan database
```
make up-full
```

### Start client untuk testing
```
make client
```
### View logs
```
make logs
```
### Production deployment
```
./scripts/deploy.sh production full
```


## Struktur Project

\`\`\`
├── app.py                 # Main application orchestrator
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── run_client.py        # Client runner script
├── client/
│   └── socket_client.py # Socket client implementation
├── models/
│   └── message.py       # Data models
├── services/
│   ├── channel_manager.py    # Channel monitoring management
│   ├── discord_bot.py        # Discord bot service
│   ├── message_processor.py  # Message processing service
│   └── socket_server.py      # Socket server service
└── utils/
    └── logger.py        # Logging utilities
\`\`\`

## Setup

1. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. Set environment variables:
\`\`\`bash
export DISCORD_BOT_TOKEN="your_bot_token_here"
export SOCKET_HOST="localhost"  # optional, default: localhost
export SOCKET_PORT="8888"       # optional, default: 8888
\`\`\`

## Docker Setup

### Prerequisites
- Docker
- Docker Compose

### Quick Start

1. Clone repository dan masuk ke directory:
\`\`\`bash
git clone <repository-url>
cd discord-socket-listener
\`\`\`

2. Copy dan edit environment file:
\`\`\`bash
cp .env.example .env
# Edit .env file dengan Discord bot token Anda
\`\`\`

3. Build dan start services:
\`\`\`bash
# Using Makefile (recommended)
make build
make up

# Or using docker-compose directly
docker-compose build
docker-compose up -d discord-bot redis
\`\`\`

4. Check logs:
\`\`\`bash
make logs
# Or
docker-compose logs -f discord-bot
\`\`\`

### Available Commands

\`\`\`bash
# Build images
make build

# Start basic services (bot + redis)
make up

# Start in development mode with hot reload
make up-dev

# Start in production mode with resource limits
make up-prod

# Start all services including database and monitoring
make up-full

# Start socket client for testing
make client

# View logs
make logs

# Open shell in bot container
make shell

# Stop services
make down

# Clean up everything
make clean

# Check status
make status
\`\`\`

### Service Profiles

The docker-compose setup includes several service profiles:

- **Default**: Discord bot + Redis
- **client**: Socket client for testing
- **database**: PostgreSQL database
- **monitoring**: Prometheus + Grafana

Start specific profiles:
\`\`\`bash
# Start with database
docker-compose --profile database up -d

# Start with monitoring
docker-compose --profile monitoring up -d

# Start everything
docker-compose --profile database --profile monitoring --profile client up -d
\`\`\`

### Environment Variables

All configuration is done via environment variables in `.env` file:

\`\`\`env
DISCORD_BOT_TOKEN=your_bot_token_here
SOCKET_HOST=0.0.0.0
SOCKET_PORT=8888
LOG_LEVEL=INFO
\`\`\`

### Volumes and Persistence

- `./logs` - Application logs
- `./data` - Application data
- `redis_data` - Redis data
- `postgres_data` - PostgreSQL data (if using database profile)

### Health Checks

All services include health checks:
- Discord bot: Socket server connectivity
- Redis: Redis ping
- PostgreSQL: Database connectivity

### Monitoring (Optional)

When using monitoring profile:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## Usage

### Menjalankan Bot

\`\`\`bash
python app.py
\`\`\`

### Menjalankan Client Listener

\`\`\`bash
python run_client.py [host] [port]
\`\`\`

Contoh:
\`\`\`bash
python run_client.py localhost 8888
\`\`\`

## Bot Commands

- `!listen [channel_id]` - Mulai monitor channel (default: channel saat ini)
- `!unlisten [channel_id]` - Stop monitor channel (default: channel saat ini)  
- `!status` - Tampilkan status monitoring

## Features

### Modular Architecture
- **Config Management**: Centralized configuration dengan environment variables
- **Channel Manager**: Service untuk manage monitored channels dengan persistence
- **Message Processor**: Service untuk process dan distribute pesan
- **Socket Server**: Service untuk broadcast ke clients
- **Discord Bot**: Service untuk handle Discord events dan commands
- **Logger Utility**: Centralized logging management

### Improvements dari Versi Monolith
- ✅ Separation of concerns
- ✅ Dependency injection
- ✅ Configuration management
- ✅ Error handling improvements
- ✅ Graceful shutdown
- ✅ Persistent channel monitoring
- ✅ Concurrent message broadcasting
- ✅ Better logging system

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_BOT_TOKEN` | Discord bot token | Required |
| `BOT_PREFIX` | Bot command prefix | `!` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FILE` | Bot log file | `discord_bot.log` |
| `MESSAGE_LOG_FILE` | Message log file | `discord_messages.txt` |
| `SOCKET_HOST` | Socket server host | `localhost` |
| `SOCKET_PORT` | Socket server port | `8888` |
| `MAX_CONNECTIONS` | Max socket connections | `5` |
| `HEARTBEAT_INTERVAL` | Heartbeat interval (seconds) | `30` |

## Architecture Benefits

1. **Maintainability**: Setiap modul memiliki tanggung jawab yang jelas
2. **Testability**: Mudah untuk unit testing karena dependencies diinjected
3. **Scalability**: Mudah untuk menambah broadcaster atau processor baru
4. **Configuration**: Centralized config dengan environment variables
5. **Error Handling**: Better error isolation dan recovery
6. **Monitoring**: Comprehensive logging across all modules
