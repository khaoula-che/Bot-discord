import discord
import json
import os
from discord.ext import commands
from discord import app_commands

USER_DATA_FILE = 'user_data.json'

def load_user_data():
    """Charge les données utilisateur depuis le fichier JSON."""
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

def save_user_data(data):
    """Enregistre les données utilisateur dans le fichier JSON."""
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

class RegisterModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Inscription")

        self.first_name = discord.ui.TextInput(label="Prénom", required=True)
        self.last_name = discord.ui.TextInput(label="Nom de famille", required=True)
        self.class_name = discord.ui.TextInput(label="Classe", required=True)
        self.study_mode = discord.ui.TextInput(label="Mode d'études (Alternance/Initial)", required=False)

        self.add_item(self.first_name)
        self.add_item(self.last_name)
        self.add_item(self.class_name)
        self.add_item(self.study_mode)

    async def on_submit(self, interaction: discord.Interaction):
        user_data = load_user_data()
        
        user_data[str(interaction.user.id)] = {
            "username": str(interaction.user),
            "first_name": self.first_name.value,
            "last_name": self.last_name.value,
            "class_name": self.class_name.value,
            "study_mode": self.study_mode.value or "Non spécifié"
        }
        
        save_user_data(user_data)
        
        role = discord.utils.get(interaction.guild.roles, name="Membre")
        
        if role:
            try:
                await interaction.user.add_roles(role)
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
        await interaction.response.send_modal(RegisterModal())

async def setup(bot):
    await bot.add_cog(MemberCommands(bot))
