import asyncio
from config import Config
from config import MongoDBConfig
from services.mongo_handler import MongoDBService
from services.discord_bot import DiscordBot
from services.channel_manager import ChannelManager
from services.message_processor import MessageProcessor
from services.socket_server import SocketServer
from utils.logger import Logger

class DiscordSocketListener:
    """Main application class yang mengkoordinasi semua services"""
    
    def __init__(self):
        # Load configuration
        self.bot_config, self.socket_config = Config.from_env()
        self.mongodb_config = MongoDBConfig.from_env()
        self.mongodb_service = MongoDBService(self.mongodb_config)
        self.logger = Logger.get_logger(self.__class__.__name__, 
                                       self.bot_config.log_file, 
                                       self.bot_config.log_level)
        
        # Initialize services
        self.channel_manager = ChannelManager()
        self.message_processor = MessageProcessor(self.bot_config.message_log_file, mongodb_service=self.mongodb_service)
        self.socket_server = SocketServer(self.socket_config)
        
        self.discord_bot = DiscordBot(
            self.bot_config,
            self.channel_manager,
            self.message_processor,
            self.socket_server
        )
    # async def ping(self):
    #     print(f"Received message: {message.content}")
    #     """Cek koneksi bot"""
    #     await self.send('Pong!')

    async def start(self):
        """Start aplikasi"""
        try:
            self.logger.info("Starting Discord Socket Listener...")
            await self.discord_bot.start()
        except Exception as e:
            self.logger.error(f"Error starting application: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop aplikasi"""
        self.logger.info("Stopping Discord Socket Listener...")
        
        # Stop socket server
        self.socket_server.stop()
        
        # Stop Discord bot
        self.discord_bot.stop()
        
        self.logger.info("Application stopped")

# Entry point
async def main():
    """Main entry point"""
    app = DiscordSocketListener()
    
    try:
        await app.start()
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
        await app.stop()
    except Exception as e:
        print(f"Error: {e}")
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
