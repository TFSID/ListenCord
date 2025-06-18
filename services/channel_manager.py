from typing import Set
from utils.logger import Logger
import json
from pathlib import Path

class ChannelManager:
    """Service untuk manage monitored channels"""
    
    def __init__(self, channels_file: str = "monitored_channels.json"):
        self.channels_file = channels_file
        self.logger = Logger.get_logger(self.__class__.__name__)
        self.monitored_channels: Set[int] = set()
        
        # Load channels dari file jika ada
        self._load_channels()
    
    def add_channel(self, channel_id: int) -> bool:
        """Tambah channel untuk monitoring"""
        if channel_id in self.monitored_channels:
            return False
        
        self.monitored_channels.add(channel_id)
        self._save_channels()
        self.logger.info(f"Added channel {channel_id} to monitoring")
        return True
    
    def remove_channel(self, channel_id: int) -> bool:
        """Hapus channel dari monitoring"""
        if channel_id not in self.monitored_channels:
            return False
        
        self.monitored_channels.remove(channel_id)
        self._save_channels()
        self.logger.info(f"Removed channel {channel_id} from monitoring")
        return True
    
    def is_monitored(self, channel_id: int) -> bool:
        """Check apakah channel dimonitor"""
        return channel_id in self.monitored_channels
    
    def get_monitored_channels(self) -> Set[int]:
        """Get semua monitored channels"""
        return self.monitored_channels.copy()
    
    def _load_channels(self) -> None:
        """Load channels dari file"""
        try:
            if Path(self.channels_file).exists():
                with open(self.channels_file, 'r') as f:
                    channels_list = json.load(f)
                    self.monitored_channels = set(channels_list)
                    self.logger.info(f"Loaded {len(self.monitored_channels)} monitored channels")
        except Exception as e:
            self.logger.error(f"Error loading channels: {e}")
            self.monitored_channels = set()
    
    def _save_channels(self) -> None:
        """Save channels ke file"""
        try:
            with open(self.channels_file, 'w') as f:
                json.dump(list(self.monitored_channels), f)
        except Exception as e:
            self.logger.error(f"Error saving channels: {e}")
