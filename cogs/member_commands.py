import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# Chargement des données utilisateur depuis le fichier JSON
def load_user_data():
    if os.path.exists("user_data.json"):
        with open("user_data.json", "r") as file:
            return json.load(file)
    return {}

# Sauvegarde des données utilisateur dans le fichier JSON
def save_user_data(user_data):
    with open("user_data.json", "w") as file:
        json.dump(user_data, file, indent=4)

# Chargement initial des données
user_db = load_user_data()

class RegisterModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Inscription")

        self.first_name = discord.ui.TextInput(label="Prénom", required=True)
        self.last_name = discord.ui.TextInput(label="Nom de famille", required=True)
        self.class_name = discord.ui.TextInput(label="Classe", required=True)
        self.study_mode = discord.ui.TextInput(label="Mode d'études (Alternance/Initial)", required=False)

        # Ajout des champs dans le modal
        self.add_item(self.first_name)
        self.add_item(self.last_name)
        self.add_item(self.class_name)
        self.add_item(self.study_mode)

    async def on_submit(self, interaction: discord.Interaction):
        user_data = {
            "username": str(interaction.user),
            "first_name": self.first_name.value,
            "last_name": self.last_name.value,
            "class_name": self.class_name.value,
            "study_mode": self.study_mode.value or "Non spécifié",
            "points": 0  # Initialisation des points à 0 lors de l'inscription
        }

        role = discord.utils.get(interaction.guild.roles, name="Membre")
        
        # Attribuer le rôle à l'utilisateur s'il existe
        if role:
            try:
                await interaction.user.add_roles(role)
                # Enregistrer les données de l'utilisateur dans la base de données
                user_db[interaction.user.id] = user_data
                save_user_data(user_db)  # Sauvegarde les données après l'ajout
                await interaction.response.send_message(
                    f"Inscription réussie\n"
                    f"Vous avez maintenant accès aux canaux réservés aux membres !",
                    ephemeral=True
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "Je n'ai pas les permissions nécessaires pour attribuer le rôle. Veuillez contacter un administrateur.",
                    ephemeral=True
                )
        else:
            await interaction.response.send_message(
                "Rôle 'Membre' non trouvé. Veuillez contacter un administrateur.",
                ephemeral=True
            )


class MemberCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="register", description="Inscrivez-vous au serveur")
    async def register(self, interaction: discord.Interaction):
        # Ouvre le modal pour l'inscription
        await interaction.response.send_modal(RegisterModal())

    @commands.command(name="list_members")
    async def list_members(self, ctx):
        """Affiche la liste des membres du serveur avec leur nom, prénom, classe et points"""
        member_list = []
        
        for member in ctx.guild.members:
            # Récupérer les données de l'utilisateur depuis la base de données
            user_data = user_db.get(member.id)
            
            if user_data:
                # Construire la chaîne pour chaque membre avec son nom, prénom, classe et points
                member_info = f"{user_data['first_name']} {user_data['last_name']} ({user_data['class_name']}): {user_data['points']} points"
                member_list.append(member_info)

        # Joindre tous les membres dans une chaîne et afficher
        if member_list:
            member_list_str = "\n".join(member_list)
            await ctx.send(f"Voici la liste des membres du serveur avec leurs informations :\n{member_list_str}")
        else:
            await ctx.send("Aucun membre inscrit trouvé.")


async def setup(bot):
    await bot.add_cog(MemberCommands(bot))
