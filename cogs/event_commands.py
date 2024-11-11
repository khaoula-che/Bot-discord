import discord
from discord.ext import commands
import json

EVENT_FILE = 'event.json'
PRESENCE_FILE = 'presence.json'
USER_DATA_FILE = 'user_data.json'

class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Création de la commande Slash
    @discord.app_commands.command(name="annonce_event", description="Annonce un événement pour tout le monde")
    async def annonce_event(self, interaction: discord.Interaction):
        # Charger les données de l'événement
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
                f"🔗 N’oubliez pas d’apporter votre énergie et vos idées !\n"
                f"Nous avons hâte de vous rencontrer et de commencer cette aventure ensemble.\n\n"
                f"À très bientôt ! 🚀"
            ),
            color=discord.Color.blue()
        )

        # Envoi de l'annonce de l'événement dans le canal pour tout le monde
        await interaction.response.send_message("L'annonce de l'événement est maintenant visible pour tout le monde!", ephemeral=True)
        await interaction.followup.send(embed=embed)

        # Ajout des réactions
        message = await interaction.followup.send("L'annonce de l'événement a été envoyée dans le canal !")
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        # Initialise le fichier de présence
        with open(PRESENCE_FILE, 'w') as presence_file:
            json.dump({"date": event_data['date'], "participants": []}, presence_file, indent=4)

        # Réponse uniquement visible pour l'utilisateur ayant invoqué la commande
        await interaction.user.send("L'annonce de l'événement a été envoyée et est visible pour tout le monde.")

    # Listener pour gérer les réactions
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        channel = reaction.message.channel
        if channel.name != "événements-à-venir":
            return

        with open(PRESENCE_FILE, 'r') as presence_file:
            presence_data = json.load(presence_file)

        if reaction.emoji == "✅":
            if not any(participant['name'] == user.name for participant in presence_data["participants"]):
                presence_data["participants"].append({"name": user.name, "came": False})
        elif reaction.emoji == "❌":
            presence_data["participants"] = [p for p in presence_data["participants"] if p["name"] != user.name]

        with open(PRESENCE_FILE, 'w') as presence_file:
            json.dump(presence_data, presence_file, indent=4)

    # Commande de confirmation de présence, accessible seulement aux rôles spécifiés
    @discord.app_commands.command(name="confirm_presence", description="Confirmer la présence des participants")
    @commands.has_any_role('Présidente', 'Vice-Présidente')
    async def confirm_presence(self, interaction: discord.Interaction):
        with open(PRESENCE_FILE, 'r') as presence_file:
            presence_data = json.load(presence_file)

        with open(USER_DATA_FILE, 'r') as user_data_file:
            user_data = json.load(user_data_file)

        embed = discord.Embed(
            title="Confirmation de Présence",
            description="Veuillez confirmer la présence des participants ci-dessous :",
            color=discord.Color.green()
        )

        for participant in presence_data["participants"]:
            embed.add_field(name=participant["name"], value="Présent ?", inline=False)

        message = await interaction.response.send_message(embed=embed)

        for i in range(len(presence_data["participants"])):
            await message.add_reaction(f"{i+1}️⃣")

        def check(reaction, user):
            return user in [ctx.guild.get_role(role.id) for role in ctx.guild.roles if role.name in ['Présidente', 'Vice-Présidente']]

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                index = int(reaction.emoji[0]) - 1
                if 0 <= index < len(presence_data["participants"]):
                    presence_data["participants"][index]["came"] = True

                    for user in user_data:
                        if user["username"] == presence_data["participants"][index]["name"]:
                            user["points"] += 1
                            break

                    with open(USER_DATA_FILE, 'w') as user_data_file:
                        json.dump(user_data, user_data_file, indent=4)

                    await interaction.followup.send(f"Présence confirmée pour {presence_data['participants'][index]['name']}")

            except TimeoutError:
                break

        with open(PRESENCE_FILE, 'w') as presence_file:
            json.dump(presence_data, presence_file, indent=4)

# Synchronisation des commandes Slash avec Discord
async def setup(bot):
    await bot.add_cog(Event(bot))
    await bot.tree.sync()  # Synchronisation des commandes Slash avec Discord

