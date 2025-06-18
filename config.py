import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BotConfig:
    """Konfigurasi untuk Discord Bot"""
    bot_token: str
    command_prefix: str = '!'
    log_level: str = 'INFO'
    log_file: str = 'discord_bot.log'
    message_log_file: str = 'discord_messages.txt'

@dataclass
class SocketConfig:
    """Konfigurasi untuk Socket Server"""
    host: str = 'localhost'
    port: int = 8888
    max_connections: int = 5
    heartbeat_interval: int = 30

class Config:
    """Kelas utama untuk manajemen konfigurasi"""
    
    @staticmethod
    def from_env() -> tuple[BotConfig, SocketConfig]:
        """Load konfigurasi dari environment variables"""
        bot_token = os.getenv('DISCORD_BOT_TOKEN')
        if not bot_token:
            raise ValueError("DISCORD_BOT_TOKEN environment variable is required")
        
        bot_config = BotConfig(
            bot_token=bot_token,
            command_prefix=os.getenv('BOT_PREFIX', '!'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_file=os.getenv('LOG_FILE', 'discord_bot.log'),
            message_log_file=os.getenv('MESSAGE_LOG_FILE', 'discord_messages.txt')
        )
        
        socket_config = SocketConfig(
            host=os.getenv('SOCKET_HOST', 'localhost'),
            port=int(os.getenv('SOCKET_PORT', '8888')),
            max_connections=int(os.getenv('MAX_CONNECTIONS', '5')),
            heartbeat_interval=int(os.getenv('HEARTBEAT_INTERVAL', '30'))
        )
        
        return bot_config, socket_config
