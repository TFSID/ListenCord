import asyncio
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure
from datetime import datetime

@dataclass
class MongoDBConfig:
    """Configuration untuk MongoDB"""
    uri: str
    database_name: str = "discord_bot"
    collection_name: str = "messages"
    timeout: int = 5000
    enable_mongodb: bool = True
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'MongoDBConfig':
        """Create config dari dictionary"""
        return cls(
            uri=config_dict.get('mongodb_uri', 'mongodb://localhost:27017/'),
            database_name=config_dict.get('database_name', 'discord_bot'),
            collection_name=config_dict.get('collection_name', 'messages'),
            timeout=config_dict.get('timeout', 5000),
            enable_mongodb=config_dict.get('enable_mongodb', True)
        )

class MongoDBService:
    """Service untuk mengelola MongoDB operations"""
    
    def __init__(self, config: MongoDBConfig):
        """
        Initialize MongoDB service
        
        Args:
            config: MongoDBConfig object
        """
        self.config = config
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.collection = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self._connection_failed = False
        self._is_connected = False
        
        # Stats tracking
        self._messages_saved = 0
        self._connection_attempts = 0
        self._last_error = None
    
    async def initialize(self) -> bool:
        """
        Initialize MongoDB connection
        
        Returns:
            bool: True jika berhasil initialize, False jika gagal
        """
        if not self.config.enable_mongodb:
            self.logger.info("MongoDB disabled in configuration")
            return False
        
        self.logger.info(f"Initializing MongoDB service...")
        return await self._connect()
    
    async def _connect(self) -> bool:
        """
        Establish connection ke MongoDB
        
        Returns:
            bool: True jika berhasil connect, False jika gagal
        """
        try:
            self._connection_attempts += 1
            
            # Create client dengan timeout settings
            self.client = AsyncIOMotorClient(
                self.config.uri,
                serverSelectionTimeoutMS=self.config.timeout,
                connectTimeoutMS=self.config.timeout,
                socketTimeoutMS=self.config.timeout
            )
            
            # Test connection
            await self.client.admin.command('ping')
            
            # Setup database dan collection
            self.db = self.client[self.config.database_name]
            self.collection = self.db[self.config.collection_name]
            
            # Create indexes untuk optimasi query
            await self._create_indexes()
            
            self.logger.info(f"Successfully connected to MongoDB: {self.config.database_name}.{self.config.collection_name}")
            self._connection_failed = False
            self._is_connected = True
            self._last_error = None
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self._last_error = str(e)
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            self._connection_failed = True
            self._is_connected = False
            return False
        except Exception as e:
            self._last_error = str(e)
            self.logger.error(f"Unexpected error connecting to MongoDB: {e}")
            self._connection_failed = True
            self._is_connected = False
            return False
    
    async def _create_indexes(self):
        """Create indexes untuk optimasi performance"""
        try:
            # Index untuk timestamp (untuk sorting berdasarkan waktu)
            await self.collection.create_index("timestamp")
            
            # Index untuk server_id dan channel_id (untuk filtering)
            await self.collection.create_index([("server_id", 1), ("channel_id", 1)])
            
            # Index untuk author_id (untuk filtering berdasarkan user)
            await self.collection.create_index("author_id")
            
            # Compound index untuk queries yang sering digunakan
            await self.collection.create_index([
                ("server_id", 1), 
                ("channel_id", 1), 
                ("timestamp", -1)
            ])
            
            self.logger.info("Database indexes created successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to create indexes: {e}")
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self._is_connected = False
            self.logger.info("MongoDB connection closed")
    
    async def _ensure_connection(self) -> bool:
        """
        Ensure connection masih aktif, reconnect jika perlu
        
        Returns:
            bool: True jika connection ready, False jika gagal
        """
        if not self.config.enable_mongodb:
            return False
            
        if self.client is None or self._connection_failed:
            return await self._connect()
        
        try:
            # Test connection dengan ping
            await self.client.admin.command('ping')
            if not self._is_connected:
                self._is_connected = True
                self.logger.info("MongoDB connection restored")
            return True
        except Exception as e:
            if self._is_connected:
                self.logger.warning(f"Connection lost: {e}, attempting to reconnect...")
            self._is_connected = False
            return await self._connect()
    
    async def save_message(self, message_data: 'DiscordMessage') -> bool:
        """
        Save Discord message ke MongoDB
        
        Args:
            message_data: DiscordMessage object
            
        Returns:
            bool: True jika berhasil save, False jika gagal
        """
        try:
            # Ensure connection aktif
            if not await self._ensure_connection():
                return False
            
            # Convert message data ke dict
            message_dict = message_data.to_dict()
            
            # Add metadata
            message_dict['created_at'] = datetime.utcnow()
            message_dict['_id'] = f"{message_data.channel_id}_{message_data.timestamp}_{message_data.author_id}"
            
            # Insert ke MongoDB
            result = await self.collection.insert_one(message_dict)
            
            if result.inserted_id:
                self._messages_saved += 1
                self.logger.debug(f"Message saved to MongoDB: {result.inserted_id}")
                return True
            else:
                self.logger.error("Failed to save message: No document inserted")
                return False
                
        except OperationFailure as e:
            self._last_error = str(e)
            self.logger.error(f"MongoDB operation failed: {e}")
            return False
        except Exception as e:
            self._last_error = str(e)
            self.logger.error(f"Unexpected error saving message: {e}")
            return False
    
    async def get_message_count(self) -> int:
        """Get total jumlah messages dalam database"""
        try:
            if not await self._ensure_connection():
                return -1
            
            count = await self.collection.count_documents({})
            return count
            
        except Exception as e:
            self.logger.error(f"Error getting message count: {e}")
            return -1
    
    async def get_recent_messages(self, limit: int = 10) -> list:
        """Get recent messages dari database"""
        try:
            if not await self._ensure_connection():
                return []
            
            cursor = self.collection.find().sort("timestamp", -1).limit(limit)
            messages = await cursor.to_list(length=limit)
            
            return messages
            
        except Exception as e:
            self.logger.error(f"Error getting recent messages: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "enabled": self.config.enable_mongodb,
            "connected": self._is_connected,
            "connection_attempts": self._connection_attempts,
            "messages_saved": self._messages_saved,
            "last_error": self._last_error,
            "database": self.config.database_name,
            "collection": self.config.collection_name
        }
    
    @property
    def is_available(self) -> bool:
        """Check if MongoDB service is available"""
        return self.config.enable_mongodb and self._is_connected

class MessageProcessor:
    """Updated message processor dengan MongoDB integration"""
    
    def __init__(self, message_log_file: str, mongodb_service: Optional[MongoDBService] = None):
        """
        Initialize message processor
        
        Args:
            message_log_file: Path untuk file log
            mongodb_service: Optional MongoDB service instance
        """
        self.message_log_file = message_log_file
        self.mongodb_service = mongodb_service
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Stats tracking
        self._messages_processed = 0
        self._file_saves = 0
        self._db_saves = 0
        self._errors = 0
    
    async def initialize(self):
        """Initialize message processor"""
        self.logger.info("Initializing message processor...")
        
        if self.mongodb_service:
            await self.mongodb_service.initialize()
            if self.mongodb_service.is_available:
                self.logger.info("MongoDB service initialized successfully")
            else:
                self.logger.warning("MongoDB service not available, using file logging only")
        else:
            self.logger.info("No MongoDB service provided, using file logging only")
    
    async def _log_to_database(self, message_data: 'DiscordMessage') -> bool:
        """Log message data ke MongoDB"""
        if not self.mongodb_service or not self.mongodb_service.is_available:
            return False
            
        try:
            success = await self.mongodb_service.save_message(message_data)
            if success:
                self._db_saves += 1
            return success
            
        except Exception as e:
            self.logger.error(f"Error saving to database: {e}")
            self._errors += 1
            return False
    
    async def _log_to_file(self, message_data: 'DiscordMessage') -> bool:
        """Log message data ke file"""
        try:
            with open(self.message_log_file, 'a', encoding='utf-8') as f:
                f.write(f"{message_data.to_json()}\n{'='*50}\n")
            self._file_saves += 1
            return True
        except Exception as e:
            self.logger.error(f"Error writing to file: {e}")
            self._errors += 1
            return False
    
    async def process_message(self, discord_message, message_type: str = "NEW") -> None:
        """Process pesan Discord dan save ke database/file"""
        try:
            self._messages_processed += 1
            
            # Create message model
            message_data = DiscordMessage.from_discord_message(discord_message, message_type)
            
            # Try to save ke database first
            database_success = await self._log_to_database(message_data)
            
            # Jika database gagal, fallback ke file
            if not database_success:
                await self._log_to_file(message_data)
            
            # Broadcast ke semua broadcaster (jika ada)
            await self._broadcast_message(message_data)
            
            # Log ke console
            storage_type = "DB" if database_success else "FILE"
            self.logger.info(
                f"[{message_type}][{storage_type}] {message_data.server} #{message_data.channel} - "
                f"{message_data.author}: {message_data.content[:50]}..."
            )
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            self._errors += 1
    
    async def _broadcast_message(self, message_data: 'DiscordMessage'):
        """Placeholder untuk broadcast functionality"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics"""
        stats = {
            "messages_processed": self._messages_processed,
            "file_saves": self._file_saves,
            "db_saves": self._db_saves,
            "errors": self._errors
        }
        
        if self.mongodb_service:
            stats["mongodb"] = self.mongodb_service.get_stats()
        
        return stats

# Configuration helper untuk environment variables
class Config:
    """Configuration helper class"""
    
    @staticmethod
    def get_mongodb_config() -> MongoDBConfig:
        """Get MongoDB configuration dari environment variables"""
        import os
        
        return MongoDBConfig(
            uri=os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'),
            database_name=os.getenv('MONGODB_DATABASE', 'discord_bot'),
            collection_name=os.getenv('MONGODB_COLLECTION', 'messages'),
            timeout=int(os.getenv('MONGODB_TIMEOUT', '5000')),
            enable_mongodb=os.getenv('ENABLE_MONGODB', 'true').lower() == 'true'
        )

# Example untuk integration dengan app.py
class DiscordBotApp:
    """Example aplikasi Discord bot dengan MongoDB integration"""
    
    def __init__(self):
        # Load configuration
        self.bot_config, self.socket_config = Config.from_env()
        self.mongodb_config = Config.get_mongodb_config()
        
        self.logger = Logger.get_logger(self.__class__.__name__, 
                                       self.bot_config.log_file, 
                                       self.bot_config.log_level)
        
        # Initialize services
        self.channel_manager = ChannelManager()
        self.mongodb_service = MongoDBService(self.mongodb_config)
        self.message_processor = MessageProcessor(
            self.bot_config.message_log_file,
            self.mongodb_service
        )
        self.socket_server = SocketServer(self.socket_config)
        
        self.discord_bot = DiscordBot(
            self.bot_config,
            self.channel_manager,
            self.message_processor,
            self.socket_server
        )
    
    async def initialize(self):
        """Initialize all services"""
        self.logger.info("Initializing Discord Bot App...")
        
        # Initialize message processor (yang akan initialize MongoDB service)
        await self.message_processor.initialize()
        
        # Initialize other services
        # await self.socket_server.initialize()
        # await self.discord_bot.initialize()
        
        self.logger.info("All services initialized successfully")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get application statistics"""
        return {
            "processor": self.message_processor.get_stats(),
            "mongodb": self.mongodb_service.get_stats() if self.mongodb_service else None
        }
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Shutting down services...")
        
        if self.mongodb_service:
            await self.mongodb_service.disconnect()
        
        # Shutdown other services
        # await self.socket_server.shutdown()
        # await self.discord_bot.shutdown()
        
        self.logger.info("All services shut down successfully")