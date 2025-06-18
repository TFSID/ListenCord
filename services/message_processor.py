import asyncio
from pathlib import Path
from typing import Set, List, Callable, Awaitable
from models.message import DiscordMessage
from utils.logger import Logger

class MessageProcessor:
    """Service untuk memproses dan mendistribusikan pesan Discord"""
    
    def __init__(self, message_log_file: str):
        self.message_log_file = message_log_file
        self.logger = Logger.get_logger(self.__class__.__name__)
        self.broadcasters: List[Callable[[DiscordMessage], Awaitable[None]]] = []
        
        # Ensure log directory exists
        Path(message_log_file).parent.mkdir(parents=True, exist_ok=True)
    
    def add_broadcaster(self, broadcaster: Callable[[DiscordMessage], Awaitable[None]]):
        """Tambah broadcaster function"""
        self.broadcasters.append(broadcaster)
    
    def remove_broadcaster(self, broadcaster: Callable[[DiscordMessage], Awaitable[None]]):
        """Hapus broadcaster function"""
        if broadcaster in self.broadcasters:
            self.broadcasters.remove(broadcaster)
    
    async def process_message(self, discord_message, message_type: str = "NEW") -> None:
        """Process pesan Discord dan distribute ke semua broadcaster"""
        try:
            # Create message model
            message_data = DiscordMessage.from_discord_message(discord_message, message_type)
            
            # Log ke file
            await self._log_to_file(message_data)
            
            # Broadcast ke semua broadcaster
            await self._broadcast_message(message_data)
            
            # Log ke console
            self.logger.info(
                f"[{message_type}] {message_data.server} #{message_data.channel} - "
                f"{message_data.author}: {message_data.content[:50]}..."
            )
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    async def _log_to_file(self, message_data: DiscordMessage) -> None:
        """Log message data ke file"""
        try:
            with open(self.message_log_file, 'a', encoding='utf-8') as f:
                f.write(f"{message_data.to_json()}\n{'='*50}\n")
        except Exception as e:
            self.logger.error(f"Error writing to file: {e}")
    
    async def _broadcast_message(self, message_data: DiscordMessage) -> None:
        """Broadcast message ke semua broadcaster"""
        if not self.broadcasters:
            return
        
        # Run semua broadcaster secara concurrent
        broadcast_tasks = [
            broadcaster(message_data) 
            for broadcaster in self.broadcasters
        ]
        
        # Jalankan semua task dan handle errors
        results = await asyncio.gather(*broadcast_tasks, return_exceptions=True)
        
        # Log errors jika ada
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Broadcaster {i} error: {result}")
