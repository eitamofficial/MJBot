import discord
from discord.ext import commands
from datetime import datetime

class LogsHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot: return
        channel = await self.bot.get_or_create_log_channel(message.guild)
        embed = discord.Embed(
            title="🗑️ Message Supprimé", 
            description=f"Message de {message.author.mention} dans {message.channel.mention}",
            color=0xE74C3C, timestamp=datetime.now()
        )
        embed.add_field(name="Contenu", value=message.content or "*(Pas de texte)*", inline=False)
        if message.author.avatar: embed.set_thumbnail(url=message.author.avatar.url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content: return
        channel = await self.bot.get_or_create_log_channel(before.guild)
        embed = discord.Embed(
            title="📝 Message Modifié", 
            description=f"Message de {before.author.mention} dans {before.channel.mention}",
            color=0xF39C12, timestamp=datetime.now()
        )
        embed.add_field(name="Ancien", value=before.content, inline=False)
        embed.add_field(name="Nouveau", value=after.content, inline=False)
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LogsHandler(bot))
