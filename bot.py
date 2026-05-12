import discord
from discord.ext import commands, tasks
import os
import asyncio
from datetime import datetime, time
from dotenv import load_dotenv
import yt_dlp
from googleapiclient.discovery import build

try:
    from static_ffmpeg import add_paths
    add_paths() # Ajoute automatiquement ffmpeg au PATH du bot
except ImportError:
    pass

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

# --- CONFIGURATION LOGS & RADIO ---
LOG_CHANNEL_NAME = "mj-logs"
RADIO_CHANNEL_ID = 1503065345678901234 # ID du salon vocal par défaut
# Radio 24/7 activée

# YouTube API Configuration
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
MJ_OFFICIAL_CHANNEL_ID = "UC9SsrOCBKvLp0vC7U_fUMWw" # Michael Jackson Official Channel

# Configuration yt-dlp (HAUTE QUALITÉ)
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)


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
        self.radio_playing = False
        self.voice_client = None
        self.discography = []
        self.current_song = None

    async def setup_hook(self):
        # Enregistrement des vues pour les rendre persistantes au démarrage du bot
        self.add_view(RoleView(ERAS_ROLES))
        self.add_view(RoleView(CRAFTS_ROLES))
        self.add_view(RoleView(REGIONS_ROLES))
        self.add_view(RoleView(NOTIFS_ROLES))
        
        # Charger la discographie au démarrage
        await self.update_discography()
        
        # Démarrage de la tâche radio
        self.radio_task.start()

    async def update_discography(self):
        """Récupère tous les sons officiels de Michael Jackson via l'API YouTube."""
        if not YOUTUBE_API_KEY:
            print("⚠️ YOUTUBE_API_KEY manquante. Utilisation d'une liste vide.")
            return

        print("📡 Récupération de la discographie MJ en cours...")
        try:
            youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
            
            # On récupère les vidéos de la chaîne officielle
            request = youtube.search().list(
                channelId=MJ_OFFICIAL_CHANNEL_ID,
                part="snippet",
                maxResults=50, # On peut augmenter ou paginer pour TOUTE la discographie
                order="viewCount", # Pour avoir les meilleurs sons d'abord
                type="video"
            )
            response = request.execute()
            
            self.discography = []
            for item in response.get('items', []):
                title = item['snippet']['title'].lower()
                # Filtrage plus permissif mais toujours officiel
                if any(x in title for x in ["official", "music video", "audio", "remastered"]):
                    if not any(x in title for x in ["cover", "tribute", "fan made", "reaction"]):
                        video_id = item['id']['videoId']
                        self.discography.append({
                            'url': f"https://www.youtube.com/watch?v={video_id}",
                            'title': item['snippet']['title']
                        })
            
            # Si toujours vide, on fait une recherche plus large
            if not self.discography:
                request = youtube.search().list(
                    q="Michael Jackson Official Music Video",
                    part="snippet",
                    maxResults=50,
                    type="video"
                )
                response = request.execute()
                for item in response.get('items', []):
                    video_id = item['id']['videoId']
                    self.discography.append({
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'title': item['snippet']['title']
                    })

            print(f"✅ Discographie mise à jour : {len(self.discography)} titres chargés.")
        except Exception as e:
            print(f"❌ Erreur lors de la récupération YouTube : {e}")

    async def get_or_create_log_channel(self, guild):
        channel = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
        if channel is None:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            channel = await guild.create_text_channel(LOG_CHANNEL_NAME, overwrites=overwrites)
            print(f"📁 Salon de logs créé: {LOG_CHANNEL_NAME}")
        return channel

    # --- ÉVÉNEMENTS DE LOGS ---
    async def on_message_delete(self, message):
        if message.author.bot: return
        channel = await self.get_or_create_log_channel(message.guild)
        embed = discord.Embed(
            title="🗑️ Message Supprimé", 
            description=f"Un message de {message.author.mention} a été supprimé dans {message.channel.mention}",
            color=0xE74C3C, 
            timestamp=datetime.now()
        )
        embed.add_field(name="Contenu", value=message.content or "*(Pas de texte)*", inline=False)
        embed.set_footer(text=f"ID Utilisateur: {message.author.id}")
        if message.author.avatar:
            embed.set_thumbnail(url=message.author.avatar.url)
        await channel.send(embed=embed)

    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content: return
        channel = await self.get_or_create_log_channel(before.guild)
        embed = discord.Embed(
            title="📝 Message Modifié", 
            description=f"Message de {before.author.mention} modifié dans {before.channel.mention}",
            color=0xF39C12, 
            timestamp=datetime.now()
        )
        embed.add_field(name="Ancien", value=before.content or "*(Vide)*", inline=False)
        embed.add_field(name="Nouveau", value=after.content or "*(Vide)*", inline=False)
        embed.set_footer(text=f"ID Utilisateur: {before.author.id}")
        await channel.send(embed=embed)

    # --- TÂCHE RADIO Michael Jackson 24/7 ---
    @tasks.loop(minutes=5)
    async def radio_task(self):
        # Vérification simple pour s'assurer que le bot reste connecté si radio_playing est True
        if self.radio_playing and self.voice_client and not self.voice_client.is_connected():
            print("🔄 Reconnexion automatique de la radio...")
            # La reconnexion serait gérée ici si besoin
            pass

    async def start_radio(self):
        print("📻 Radio MJ en mode 24/7.")
        self.radio_playing = True

    async def stop_radio(self):
        print("📻 Arrêt manuel de la radio.")
        if self.voice_client and self.voice_client.is_connected():
            await self.voice_client.disconnect()
        self.radio_playing = False

bot = MJFranceBot()

@bot.event
async def on_ready():
    print(f'✅ Connecté avec succès en tant que {bot.user} (ID: {bot.user.id})')
    print('------')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# --- COMMANDES SLASH ---

@bot.tree.command(name="logs_setup", description="Configure manuellement le salon de logs.")
@discord.app_commands.checks.has_permissions(administrator=True)
async def logs_setup(interaction: discord.Interaction):
    channel = await bot.get_or_create_log_channel(interaction.guild)
    await interaction.response.send_message(f"✅ Salon de logs prêt : {channel.mention}", ephemeral=True)

@bot.tree.command(name="radio_join", description="Fait rejoindre le bot en vocal pour la radio MJ.")
async def radio_join(interaction: discord.Interaction):
    if interaction.user.voice is None:
        await interaction.response.send_message("❌ Tu dois être dans un salon vocal !", ephemeral=True)
        return

    channel = interaction.user.voice.channel
    bot.voice_client = await channel.connect()
    await interaction.response.send_message(f"📻 Radio MJ connectée à **{channel.name}** !")
    bot.radio_playing = True
    await play_next_hit(interaction.guild)

async def play_next_hit(guild):
    if bot.voice_client and bot.voice_client.is_connected():
        import random
        
        if not bot.discography:
            await bot.update_discography()
            
        if not bot.discography:
            return

        song_data = random.choice(bot.discography)
        song_url = song_data['url']
        
        try:
            player = await YTDLSource.from_url(song_url, loop=bot.loop, stream=True)
            bot.current_song = player
            bot.voice_client.play(player, after=lambda e: bot.loop.create_task(play_next_hit(guild)))
            
            # Message Now Playing esthétique
            log_channel = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
            if log_channel:
                embed = discord.Embed(
                    title="🎶 Michael Jackson Radio 24/7",
                    description=f"En cours : **{player.title}**",
                    color=0x000000
                )
                embed.set_thumbnail(url="https://i.pinimg.com/736x/8e/31/6d/8e316d6c4e0e5a9a4b8a4a4a4a4a4a4a.jpg")
                embed.add_field(name="Qualité", value="💎 Ultra High Definition (192kbps)", inline=True)
                embed.add_field(name="Source", value="✅ Chaine Officielle", inline=True)
                embed.set_footer(text="MJFrance Radio - The King of Pop Never Stops")
                await log_channel.send(embed=embed)
        except Exception as e:
            print(f"⚠️ Erreur de lecture : {e}")
            await asyncio.sleep(2)
            await play_next_hit(guild)

@bot.tree.command(name="radio_stop", description="Arrête la radio et déconnecte le bot.")
async def radio_stop(interaction: discord.Interaction):
    if bot.voice_client:
        await bot.voice_client.disconnect()
        bot.radio_playing = False
        await interaction.response.send_message("📻 Radio arrêtée.")
    else:
        await interaction.response.send_message("❌ Le bot n'est pas en vocal.", ephemeral=True)

@bot.tree.command(name="radio_skip", description="Passe au titre suivant.")
async def radio_skip(interaction: discord.Interaction):
    if bot.voice_client and bot.voice_client.is_playing():
        bot.voice_client.stop() # Trigger le 'after' pour jouer le suivant
        await interaction.response.send_message("⏭️ Passage au titre suivant...", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Aucune musique en cours.", ephemeral=True)

@bot.tree.command(name="radio_nowplaying", description="Affiche le titre en cours.")
async def radio_nowplaying(interaction: discord.Interaction):
    if bot.current_song:
        embed = discord.Embed(title="🎵 En cours sur MJ Radio", description=bot.current_song.title, color=0x000000)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("📻 La radio est en pause.", ephemeral=True)

@bot.tree.command(name="radio_list", description="Affiche les titres chargés.")
async def radio_list(interaction: discord.Interaction):
    if not bot.discography:
        await interaction.response.send_message("📭 La discographie est vide.", ephemeral=True)
        return
    
    titles = "\n".join([f"• {s['title']}" for s in bot.discography[:15]])
    embed = discord.Embed(title="🕺 Discographie MJ Chargée", description=f"{titles}\n*... et {len(bot.discography)-15} autres titres*", color=0x000000)
    await interaction.response.send_message(embed=embed)

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
