import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure
from typing import Optional, Dict, Any
from models.message import DiscordMessage
import logging
from datetime import datetime
from config import MongoDBConfig

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
                f'{self.config.uri}?authSource=admin',
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
                self.logger.error("MongoDB connection not available, cannot save message")
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
