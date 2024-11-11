import discord
from discord.ext import commands
import json

EVENT_FILE = 'event.json'
PRESENCE_FILE = 'presence.json'
USER_DATA_FILE = 'user_data.json'

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="annonce_event")
    async def annonce_event(self, ctx):
        # Vérifiez si l'utilisateur a les permissions nécessaires
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        with open(EVENT_FILE, 'r') as file:
            event_data = json.load(file)

        embed = discord.Embed(
            title="🎉 Annonce de la Première Séance en Présentiel ! 🎉",
            description=(
                f"Chers membres et futurs membres de AI & Data Enthusiasts,\n\n"
                f"Nous sommes ravis de vous inviter à notre première séance en présentiel qui se déroulera :\n\n"
                f"🗓 **Date** : {event_data['date']}\n"
                f"🕒 **Heure** : {event_data['heure']}\n"
                f"📍 **Lieu** : {event_data['lieu']}\n\n"
                f"**Au programme :**\n"
                f"{event_data['description']}\n\n"
                f"🔗 N'oubliez pas d'apporter votre énergie et vos idées !\n"
                f"Nous avons hâte de vous rencontrer et de commencer cette aventure ensemble.\n\n"
                f"À très bientôt ! 🚀"
            ),
            color=discord.Color.blue()
        )

        # Envoyer le message dans le canal approprié
        channel = discord.utils.get(ctx.guild.channels, name="événements-à-venir")
        if channel:
            message = await channel.send(embed=embed)
            await message.add_reaction("✅")
            await message.add_reaction("❌")

            with open(PRESENCE_FILE, 'w') as presence_file:
                json.dump({"date": event_data['date'], "participants": []}, presence_file, indent=4)

            # Envoyer une confirmation à l'auteur de la commande
            await ctx.send("L'annonce de l'événement a été publiée avec succès.", ephemeral=True)
        else:
            await ctx.send("Le canal 'événements-à-venir' n'a pas été trouvé.", ephemeral=True)

    # ... (le reste du code reste inchangé)

async def setup(bot):
    await bot.add_cog(Event(bot))
