import asyncio
import discord
from discord.ext import commands
from typing import Optional
from config import BotConfig
from services.channel_manager import ChannelManager
from services.message_processor import MessageProcessor
from services.socket_server import SocketServer
from utils.logger import Logger


class DiscordBot:
    """Discord Bot service yang sederhana"""
    
    def __init__(self, config: BotConfig, channel_manager: ChannelManager, 
                 message_processor: MessageProcessor, socket_server: SocketServer):
        self.config = config
        self.channel_manager = channel_manager
        self.message_processor = message_processor
        self.socket_server = socket_server
        self.logger = Logger.get_logger(self.__class__.__name__, config.log_file, config.log_level)
        
        # Setup bot
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        self.bot = commands.Bot(command_prefix=config.command_prefix, intents=intents)
        
        self._register_events()
        self._register_commands()
    
    def _register_events(self):
        """Register event handlers"""
        
        @self.bot.event
        async def on_ready():
            self.logger.info(f'{self.bot.user} connected!')
            await self.socket_server.start()
            self.message_processor.add_broadcaster(self.socket_server.broadcast_message)
        
        @self.bot.event
        async def on_message(message):
            if message.author != self.bot.user and self.channel_manager.is_monitored(message.channel.id):
                await self.message_processor.process_message(message, "NEW")
            await self.bot.process_commands(message)
        
        @self.bot.event
        async def on_message_edit(before, after):
            if self.channel_manager.is_monitored(after.channel.id):
                await self.message_processor.process_message(after, "EDITED")
        
        @self.bot.event
        async def on_message_delete(message):
            if self.channel_manager.is_monitored(message.channel.id):
                await self.message_processor.process_message(message, "DELETED")
    
    def _register_commands(self):
        """Register bot commands"""
        
        @self.bot.command()
        async def listen(ctx, channel_id: Optional[int] = None):
            """Monitor channel untuk pesan"""
            target_id = channel_id or ctx.channel.id
            success = self.channel_manager.add_channel(target_id)
            msg = f"{'Started' if success else 'Already'} monitoring <#{target_id}>"
            await ctx.send(msg)
        
        @self.bot.command()
        async def unlisten(ctx, channel_id: Optional[int] = None):
            """Stop monitoring channel"""
            target_id = channel_id or ctx.channel.id
            success = self.channel_manager.remove_channel(target_id)
            msg = f"{'Stopped' if success else 'Not'} monitoring <#{target_id}>"
            await ctx.send(msg)
        
        @self.bot.command(name='ping')
        async def ping(ctx):
            """Ping bot"""
            await ctx.send('Pong!')
        
        @self.bot.command()
        async def status(ctx):
            """Show monitoring status"""
            channels = self.channel_manager.get_monitored_channels()
            
            if not channels:
                await ctx.send("No channels monitored")
                return
            
            channel_list = []
            for ch_id in channels:
                channel = self.bot.get_channel(ch_id)
                name = channel.name if channel else "Unknown"
                channel_list.append(f"• {name} ({ch_id})")
            
            status = [
                "**Status:**",
                f"Socket: {'Running' if self.socket_server.is_running else 'Stopped'}",
                f"Clients: {self.socket_server.client_count}",
                f"Channels ({len(channels)}):",
                *channel_list
            ]
            
            await ctx.send("\n".join(status))
    
    async def start(self):
        """Start bot"""
        try:
            await self.bot.start(self.config.bot_token)
        except Exception as e:
            self.logger.error(f"Start error: {e}")
            raise
    
    async def stop(self):
        """Stop bot"""
        try:
            await self.bot.close()
        except Exception as e:
            self.logger.error(f"Stop error: {e}")