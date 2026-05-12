from mj_bot.core.bot import bot
from mj_bot.core.config import TOKEN

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ Erreur : DISCORD_TOKEN manquant dans le fichier .env")
