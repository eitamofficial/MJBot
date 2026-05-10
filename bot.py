import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# --- CONFIGURATION DES ROLES ---

# Salon où envoyer les messages de rôles
ROLE_CHANNEL_ID = 1503065454946549761

# Dictionnaires contenant les "Nom du Rôle": "ID du Rôle"
ERAS_ROLES = {
    "Jackson Five": 1503065357332644013,
    "Off the Wall": 1503065358230360265,
    "Thriller": 1503065359371206696,
    "Bad": 1503065360562126901,
    "Dangerous": 1503065361522753609,
    "HIStory": 1503065363104137369,
    "Invincible": 1503065363661852803
}

CRAFTS_ROLES = {
    "Dessinateur / Ecrivain": 1503065365947744337,
    "Remixeur / Beatmaker": 1503065367159898192,
    "Monteurs vidéos et/ou photos": 1503065368661459075
}

REGIONS_ROLES = {
    "Europe": 1503065372809629766,
    "Amérique du Nord": 1503065373904207915,
    "Amérique du Sud": 1503065374663643334,
    "Afrique": 1503065376173330573,
    "Asie": 1503065377255456779,
    "Océanie": 1503065378170081342
}

NOTIFS_ROLES = {
    "Annonces": 1503065381680451696,
    "Événements": 1503065382884212928,
    "Vidéos du compte": 1503065384822243398,
    "Partenariats": 1503065385841459380
}

# Dictionnaires pour les Emojis associés (Optionnel pour rendre les boutons plus jolis)
EMOJIS = {
    "Jackson Five": "🪩", "Off the Wall": "🕺", "Thriller": "🧟", "Bad": "🕴️", 
    "Dangerous": "👑", "HIStory": "🗽", "Invincible": "💿",
    
    "Dessinateur / Ecrivain": "✍️", "Remixeur / Beatmaker": "🎧", "Monteurs vidéos et/ou photos": "🎬",
    
    "Europe": "🇪🇺", "Amérique du Nord": "🇺🇸", "Amérique du Sud": "🌎", 
    "Afrique": "🌍", "Asie": "🌏", "Océanie": "🇦🇺",
    
    "Annonces": "📢", "Événements": "🎉", "Vidéos du compte": "📺", "Partenariats": "🤝"
}


# --- CLASSES DES BOUTONS ET VUES ---

class RoleButton(discord.ui.Button):
    def __init__(self, label: str, role_id: int, emoji: str = None, style=discord.ButtonStyle.primary):
        # Utiliser l'ID du rôle pour le custom_id garantit que la vue persistera après redémarrage du bot
        super().__init__(label=label, custom_id=f"role_{role_id}", style=style, emoji=emoji)
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if role is None:
            await interaction.response.send_message("❌ Ce rôle n'existe plus ou est introuvable.", ephemeral=True)
            return
        
        # Ajouter ou retirer le rôle selon s'il l'a déjà ou non
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"📉 Le rôle **{role.name}** vous a été retiré.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"📈 Le rôle **{role.name}** vous a été ajouté.", ephemeral=True)

class RoleView(discord.ui.View):
    def __init__(self, roles_dict: dict, style=discord.ButtonStyle.primary):
        super().__init__(timeout=None) # timeout=None est requis pour les vues persistantes
        for label, role_id in roles_dict.items():
            emoji = EMOJIS.get(label)
            self.add_item(RoleButton(label=label, role_id=role_id, emoji=emoji, style=style))

# --- CLASSE PRINCIPALE DU BOT ---

class MJFranceBot(commands.Bot):
    def __init__(self):
        # Configuration des intents (Permissions nécessaires)
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True # Indispensable pour modifier les rôles
        
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Enregistrement des vues pour les rendre persistantes au démarrage du bot
        self.add_view(RoleView(ERAS_ROLES))
        self.add_view(RoleView(CRAFTS_ROLES))
        self.add_view(RoleView(REGIONS_ROLES))
        self.add_view(RoleView(NOTIFS_ROLES))

bot = MJFranceBot()

@bot.event
async def on_ready():
    print(f'✅ Connecté avec succès en tant que {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command(name="setup_roles")
@commands.has_permissions(administrator=True)
async def setup_roles(ctx):
    """Commande pour initialiser les messages de rôles dans le salon dédié."""
    channel = bot.get_channel(ROLE_CHANNEL_ID)
    if channel is None:
        await ctx.send(f"❌ Le salon configuré (ID: {ROLE_CHANNEL_ID}) est introuvable. Vérifiez que le bot a accès au salon.")
        return

    await ctx.send("⏳ Création des messages de rôles en cours...")

    # --- 1. Les Ères ---
    embed_eras = discord.Embed(
        title="🎶 Les Ères de Michael Jackson", 
        description="Cliquez sur les boutons ci-dessous pour choisir vos ères préférées !", 
        color=0x000000
    )
    # Remplacez cette URL par le lien direct vers votre image (qui se termine par .png ou .jpg)
    embed_eras.set_image(url="https://i.pinimg.com/1200x/62/c8/5a/62c85a57d11ca535f46dcc7699412205.jpg") 
    await channel.send(embed=embed_eras, view=RoleView(ERAS_ROLES, style=discord.ButtonStyle.secondary))

    # --- 2. Artisanats ---
    embed_crafts = discord.Embed(
        title="🎨 Vos Artisanats / Passions", 
        description="Sélectionnez vos spécialités et talents créatifs.", 
        color=0x3498db
    )
    embed_crafts.set_image(url="https://i.pinimg.com/1200x/b7/cd/de/b7cdde3c84315155009229a6d9760769.jpg")
    await channel.send(embed=embed_crafts, view=RoleView(CRAFTS_ROLES, style=discord.ButtonStyle.primary))

    # --- 3. Régions ---
    embed_regions = discord.Embed(
        title="🌍 Votre Région", 
        description="D'où venez-vous ? Choisissez votre continent.", 
        color=0x2ecc71
    )
    embed_regions.set_image(url="https://i.pinimg.com/1200x/c7/dc/2e/c7dc2e661313a86e2cb0bc058fdf9297.jpg")
    await channel.send(embed=embed_regions, view=RoleView(REGIONS_ROLES, style=discord.ButtonStyle.success))

    # --- 4. Notifications ---
    embed_notifs = discord.Embed(
        title="🔔 Pings & Notifications", 
        description="Choisissez quelles notifications vous souhaitez recevoir du serveur.", 
        color=0xf1c40f
    )
    embed_notifs.set_image(url="https://i.pinimg.com/1200x/c2/e1/1d/c2e11deec26ce39026f7a7d6eb8327d0.jpg")
    await channel.send(embed=embed_notifs, view=RoleView(NOTIFS_ROLES, style=discord.ButtonStyle.danger))
    
    await ctx.send(f"✅ Les messages de rôles ont été envoyés avec succès dans le salon {channel.mention}.")

# Lancement du bot
if __name__ == '__main__':
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Erreur: Le token Discord est introuvable. Veuillez le définir dans le fichier .env")
    else:
        bot.run(token)
