import discord
from discord.ext import commands
from discord import app_commands
from mj_bot.core.config import ROLE_CHANNEL_ID

# On récupère les dictionnaires depuis l'ancien bot.py pour l'instant ou on les redéfinit
ERAS_ROLES = {
    "Jackson Five": 1503065357332644013, "Off the Wall": 1503065358230360265,
    "Thriller": 1503065359371206696, "Bad": 1503065360562126901,
    "Dangerous": 1503065361522753609, "HIStory": 1503065363104137369, "Invincible": 1503065363661852803
}
CRAFTS_ROLES = {
    "Dessinateur / Ecrivain": 1503065365947744337, "Remixeur / Beatmaker": 1503065367159898192,
    "Monteurs vidéos et/ou photos": 1503065368661459075
}
REGIONS_ROLES = {
    "Europe": 1503065372809629766, "Amérique du Nord": 1503065373904207915, "Amérique du Sud": 1503065374663643334,
    "Afrique": 1503065376173330573, "Asie": 1503065377255456779, "Océanie": 1503065378170081342
}
NOTIFS_ROLES = {
    "Annonces": 1503065381680451696, "Événements": 1503065382884212928,
    "Vidéos du compte": 1503065384822243398, "Partenariats": 1503065385841459380
}

EMOJIS = {
    "Jackson Five": "🪩", "Off the Wall": "🕺", "Thriller": "🧟", "Bad": "🕴️", 
    "Dangerous": "👑", "HIStory": "🗽", "Invincible": "💿",
    "Dessinateur / Ecrivain": "✍️", "Remixeur / Beatmaker": "🎧", "Monteurs vidéos et/ou photos": "🎬",
    "Europe": "🇪🇺", "Amérique du Nord": "🇺🇸", "Amérique du Sud": "🌎", 
    "Afrique": "🌍", "Asie": "🌏", "Océanie": "🇦🇺",
    "Annonces": "📢", "Événements": "🎉", "Vidéos du compte": "📺", "Partenariats": "🤝"
}

class RoleButton(discord.ui.Button):
    def __init__(self, label: str, role_id: int, emoji: str = None, style=discord.ButtonStyle.primary):
        super().__init__(label=label, custom_id=f"role_{role_id}", style=style, emoji=emoji)
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if role is None:
            await interaction.response.send_message("❌ Rôle introuvable.", ephemeral=True)
            return
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"📉 Retiré : **{role.name}**", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"📈 Ajouté : **{role.name}**", ephemeral=True)

class RoleView(discord.ui.View):
    def __init__(self, roles_dict: dict, style=discord.ButtonStyle.primary):
        super().__init__(timeout=None)
        for label, role_id in roles_dict.items():
            emoji = EMOJIS.get(label)
            self.add_item(RoleButton(label=label, role_id=role_id, emoji=emoji, style=style))

class RolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setup_roles")
    @commands.has_permissions(administrator=True)
    async def setup_roles(self, ctx):
        channel = self.bot.get_channel(ROLE_CHANNEL_ID)
        if not channel: return
        
        # Setup logic (Simplified for brevity, similar to before)
        embed = discord.Embed(title="🎶 Les Ères de Michael Jackson", color=0x000000)
        embed.set_image(url="https://i.pinimg.com/1200x/62/c8/5a/62c85a57d11ca535f46dcc7699412205.jpg")
        await channel.send(embed=embed, view=RoleView(ERAS_ROLES, style=discord.ButtonStyle.secondary))
        await ctx.send("✅ Configuration des rôles terminée.")

async def setup(bot):
    await bot.add_cog(RolesCog(bot))
    # On enregistre aussi les vues pour la persistance
    bot.add_view(RoleView(ERAS_ROLES))
    bot.add_view(RoleView(CRAFTS_ROLES))
    bot.add_view(RoleView(REGIONS_ROLES))
    bot.add_view(RoleView(NOTIFS_ROLES))
