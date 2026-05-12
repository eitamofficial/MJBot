import discord
from discord.ext import commands, tasks
from discord import app_commands
import random
import asyncio
from datetime import datetime
from mj_bot.utils.audio import AudioCacheManager
from mj_bot.core.config import LOG_CHANNEL_NAME

class RadioCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="radio_join", description="Lance la radio MJ 24/7.")
    async def radio_join(self, interaction: discord.Interaction):
        if interaction.user.voice is None:
            await interaction.response.send_message("❌ Tu dois être dans un salon vocal !", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        self.bot.voice_client = await channel.connect()
        await interaction.response.send_message(f"📻 Radio MJ connectée à **{channel.name}** !")
        self.bot.radio_playing = True
        await self.play_next_hit(interaction.guild)

    @app_commands.command(name="radio_stop", description="Arrête la radio.")
    async def radio_stop(self, interaction: discord.Interaction):
        if self.bot.voice_client:
            await self.bot.voice_client.disconnect()
            self.bot.radio_playing = False
            await interaction.response.send_message("📻 Radio arrêtée.")
        else:
            await interaction.response.send_message("❌ Pas connecté.", ephemeral=True)

    @app_commands.command(name="radio_skip", description="Passe au titre suivant.")
    async def radio_skip(self, interaction: discord.Interaction):
        if self.bot.voice_client and self.bot.voice_client.is_playing():
            self.bot.voice_client.stop()
            await interaction.response.send_message("⏭️ Passage au titre suivant...", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Rien ne joue.", ephemeral=True)

    async def play_next_hit(self, guild):
        if self.bot.voice_client and self.bot.voice_client.is_connected():
            if not self.bot.discography:
                self.bot.discography = await self.bot.yt_manager.fetch_discography()
            
            if not self.bot.discography:
                return

            song_data = random.choice(self.bot.discography)
            
            source = await AudioCacheManager.get_audio_source(song_data, loop=self.bot.loop)
            if source:
                self.bot.current_song_title = song_data['title']
                self.bot.voice_client.play(source, after=lambda e: self.bot.loop.create_task(self.play_next_hit(guild)))
                
                # Log Now Playing
                log_channel = await self.bot.get_or_create_log_channel(guild)
                embed = discord.Embed(
                    title="🎶 Michael Jackson Radio - NOW PLAYING",
                    description=f"Titre : **{song_data['title']}**",
                    color=0x000000
                )
                embed.set_thumbnail(url="https://i.pinimg.com/736x/8e/31/6d/8e316d6c4e0e5a9a4b8a4a4a4a4a4a4a.jpg")
                embed.set_footer(text="Système de cache actif 🚀")
                await log_channel.send(embed=embed)
            else:
                await asyncio.sleep(2)
                await self.play_next_hit(guild)

async def setup(bot):
    await bot.add_cog(RadioCog(bot))
