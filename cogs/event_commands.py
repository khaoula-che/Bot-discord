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
    @commands.has_any_role('Présidente', 'Vice-Présidente')
    async def annonce_event(self, ctx):
        try:
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

            # Envoyer l'annonce dans le canal "événements-à-venir"
            channel = discord.utils.get(ctx.guild.channels, name="événements-à-venir")
            if channel:
                announcement = await channel.send(embed=embed)
                await announcement.add_reaction("✅")
                await announcement.add_reaction("❌")

                # Initialiser le fichier de présence
                with open(PRESENCE_FILE, 'w') as presence_file:
                    json.dump({"date": event_data['date'], "participants": []}, presence_file, indent=4)

                # Envoyer un message de confirmation visible uniquement par l'auteur de la commande
                await ctx.send("L'annonce de l'événement a été publiée avec succès dans le canal 'événements-à-venir'.", ephemeral=True)
            else:
                await ctx.send("Le canal 'événements-à-venir' n'a pas été trouvé.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"Une erreur s'est produite : {str(e)}", ephemeral=True)

    # Le reste du code reste inchangé...

async def setup(bot):
    await bot.add_cog(Event(bot))
