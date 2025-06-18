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
    """Discord Bot service dengan command handling"""
    
    def __init__(self, config: BotConfig, channel_manager: ChannelManager, 
                 message_processor: MessageProcessor, socket_server: SocketServer):
        self.config = config
        self.channel_manager = channel_manager
        self.message_processor = message_processor
        self.socket_server = socket_server
        self.logger = Logger.get_logger(self.__class__.__name__, config.log_file, config.log_level)
        
        # Setup Discord Bot
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        self.bot = commands.Bot(command_prefix=config.command_prefix, intents=intents)
        
        self._setup_events()
        self._setup_commands()
    
    def _setup_events(self):
        """Setup Discord bot events"""
        
        @self.bot.event
        async def on_ready():
            self.logger.info(f'{self.bot.user} connected to Discord!')
            self.logger.info(f'Bot is in {len(self.bot.guilds)} servers')
            
            # Start socket server
            await self.socket_server.start()
            
            # Register socket server sebagai broadcaster
            self.message_processor.add_broadcaster(self.socket_server.broadcast_message)
        
        @self.bot.event
        async def on_message(self, message):
            """Handler untuk setiap pesan yang diterima"""
            
            
            if message.author == self.bot.user:
                return
            
            # Check apakah channel dimonitor
            if self.channel_manager.is_monitored(message.channel.id):
                await self.message_processor.process_message(message, "NEW")
            
            # Process commands
            await self.bot.process_commands(message)
        
        @self.bot.event
        async def on_message_edit(self, before, after):
            """Handler untuk pesan yang diedit"""
            if self.channel_manager.is_monitored(after.channel.id):
                await self.message_processor.process_message(after, "EDITED")
        
        @self.bot.event
        async def on_message_delete(self, message):
            """Handler untuk pesan yang dihapus"""
            if self.channel_manager.is_monitored(message.channel.id):
                await self.message_processor.process_message(message, "DELETED")
    
    def _setup_commands(self):
        """Setup Discord bot commands"""
        
        @self.bot.command(name='listen')
        async def add_channel(ctx, channel_id: Optional[int] = None):
            """Tambah channel untuk dimonitor"""
            target_channel_id = channel_id or ctx.channel.id
            
            if self.channel_manager.add_channel(target_channel_id):
                await ctx.send(f"Started monitoring channel <#{target_channel_id}>")
            else:
                await ctx.send(f"Channel <#{target_channel_id}> is already being monitored!")

        @self.bot.command(name='ping')
        async def ping(ctx):
            print(f"Received message: {message.content}")
            """Cek koneksi bot"""
            await ctx.send('Pong!')
        
        @self.bot.command(name='unlisten')
        async def remove_channel(ctx, channel_id: Optional[int] = None):
            """Hapus channel dari monitoring"""
            target_channel_id = channel_id or ctx.channel.id
            
            if self.channel_manager.remove_channel(target_channel_id):
                await ctx.send(f"Stopped monitoring channel <#{target_channel_id}>")
            else:
                await ctx.send(f"Channel <#{target_channel_id}> is not being monitored!")
        
        @self.bot.command(name='status')
        async def status(ctx):
            """Tampilkan status monitoring"""
            monitored_channels = self.channel_manager.get_monitored_channels()
            
            if not monitored_channels:
                await ctx.send("No channels are being monitored")
                return
            
            channels_list = []
            for channel_id in monitored_channels:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    channels_list.append(f"• {channel.name} (ID: {channel_id})")
                else:
                    channels_list.append(f"• Unknown Channel (ID: {channel_id})")
            
            status_msg = f"**Monitoring Status:**\n"
            status_msg += f"Socket Server: {'Running' if self.socket_server.is_running else 'Stopped'}\n"
            status_msg += f"Connected Clients: {self.socket_server.client_count}\n"
            status_msg += f"Monitored Channels ({len(monitored_channels)}):\n"
            status_msg += "\n".join(channels_list)
            
            await ctx.send(status_msg)
    
    async def start(self):
        """Start Discord bot"""
        try:
            await self.bot.start(self.config.bot_token)
        except Exception as e:
            self.logger.error(f"Error starting bot: {e}")
            raise
    
    def stop(self):
        """Stop Discord bot"""
        try:
            asyncio.create_task(self.bot.close())
        except Exception as e:
            self.logger.error(f"Error stopping bot: {e}")
