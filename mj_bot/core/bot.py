import discord
from discord.ext import commands, tasks
from mj_bot.core.config import TOKEN, LOG_CHANNEL_NAME
from mj_bot.utils.youtube import YouTubeManager
import os

try:
    from static_ffmpeg import add_paths
    add_paths()
except ImportError:
    pass

class MJFranceBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(command_prefix="!", intents=intents)
        
        self.radio_playing = False
        self.voice_client = None
        self.discography = []
        self.current_song_title = None
        self.yt_manager = YouTubeManager()

    async def setup_hook(self):
        # Load extensions (Cogs)
        await self.load_extension("mj_bot.cogs.radio")
        await self.load_extension("mj_bot.cogs.roles")
        await self.load_extension("mj_bot.handlers.logs")
        
        # Initial discography load
        self.discography = await self.yt_manager.fetch_discography()
        print(f"✅ Bot prêt avec {len(self.discography)} titres.")

    async def on_ready(self):
        print(f'✅ Connecté en tant que {bot.user}')
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"❌ Error syncing commands: {e}")

    async def get_or_create_log_channel(self, guild):
        channel = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
        if channel is None:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            channel = await guild.create_text_channel(LOG_CHANNEL_NAME, overwrites=overwrites)
        return channel

bot = MJFranceBot()
