import os
from datetime import time
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Channels
ROLE_CHANNEL_ID = 1503065454946549761
LOG_CHANNEL_NAME = "mj-logs"
RADIO_CHANNEL_ID = 1503065345678901234 # Default VC

# Michael Jackson Channel
MJ_OFFICIAL_CHANNEL_ID = "UC9SsrOCBKvLp0vC7U_fUMWw"

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "data", "cache")

# Audio Settings
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(CACHE_DIR, '%(id)s.%(ext)s'),
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
