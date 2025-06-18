from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional
import json

@dataclass
class DiscordMessage:
    """Model untuk Discord message data"""
    type: str
    timestamp: str
    server: Optional[str]
    server_id: Optional[int]
    channel: str
    channel_id: int
    author: str
    author_id: int
    content: str
    attachments: List[str]
    embeds: int
    reactions: int
    
    @classmethod
    def from_discord_message(cls, message, message_type: str = "NEW") -> 'DiscordMessage':
        """Create DiscordMessage dari discord.Message object"""
        return cls(
            type=message_type,
            timestamp=datetime.utcnow().isoformat(),
            server=message.guild.name if message.guild else "DM",
            server_id=message.guild.id if message.guild else None,
            channel=message.channel.name,
            channel_id=message.channel.id,
            author=str(message.author),
            author_id=message.author.id,
            content=message.content,
            attachments=[att.url for att in message.attachments],
            embeds=len(message.embeds),
            reactions=len(message.reactions)
        )
    
    def to_json(self) -> str:
        """Convert ke JSON string"""
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)
    
    def to_dict(self) -> dict:
        """Convert ke dictionary"""
        return asdict(self)
