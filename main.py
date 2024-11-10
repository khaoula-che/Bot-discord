import discord
from discord.ext import commands
from keep_alive import keep_alive
import os  # Pour récupérer les variables d'environnement
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Récupérer le TOKEN depuis les variables d'environnement
TOKEN = os.getenv('TOKEN')

# Vérifier si le TOKEN est chargé
if not TOKEN:
    raise ValueError("Erreur : le token Discord est manquant. Assurez-vous que le fichier .env contient DISCORD_TOKEN.")

# Configurez votre bot avec les intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Initialisez le bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Fonction pour charger les cogs
async def load_cogs():
    cogs = ['cogs.quiz_commands', 'cogs.points_commands', 'cogs.member_commands', 
            'cogs.easteregg_commands', 'cogs.feedback_commands', 'cogs.event_commands']

    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f'{cog} chargé avec succès.')
        except Exception as e:
            print(f'Erreur lors du chargement de {cog}: {e}')

# Événement lors de la connexion du bot
@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user}')

# Démarrer le bot
async def main():
    keep_alive()  # Garder le bot en vie si vous utilisez un service externe
    print("Démarrage du bot...")
    await load_cogs()  # Charger les cogs
    await bot.start(TOKEN)  # Utiliser le token sécurisé depuis les variables d'environnement

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
