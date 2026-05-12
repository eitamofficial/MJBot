import os
import asyncio
import discord
import yt_dlp
from mj_bot.core.config import YTDL_OPTIONS, FFMPEG_OPTIONS, CACHE_DIR

# Ensure cache dir exists
os.makedirs(CACHE_DIR, exist_ok=True)

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class AudioCacheManager:
    @staticmethod
    async def get_audio_source(song_data, loop=None):
        video_id = song_data['id']
        url = song_data['url']
        
        # Check if file exists in cache
        file_path = os.path.join(CACHE_DIR, f"{video_id}.webm") # yt-dlp defaults to webm for audio usually
        # We check for common extensions
        possible_extensions = ['.webm', '.m4a', '.mp3']
        actual_path = None
        for ext in possible_extensions:
            p = os.path.join(CACHE_DIR, f"{video_id}{ext}")
            if os.path.exists(p):
                actual_path = p
                break

        if actual_path:
            print(f"📦 Utilisation du cache pour : {song_data['title']}")
            return discord.FFmpegPCMAudio(actual_path, **FFMPEG_OPTIONS)
        
        # Download if not in cache
        print(f"📥 Téléchargement en cours : {song_data['title']}...")
        loop = loop or asyncio.get_event_loop()
        try:
            # On utilise extract_info avec download=True pour le mettre en cache
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=True))
            filename = ytdl.prepare_filename(data)
            return discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS)
        except Exception as e:
            print(f"❌ Erreur de téléchargement : {e}")
            return None

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
