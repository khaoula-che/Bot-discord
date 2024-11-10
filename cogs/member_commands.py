import discord
from discord.ext import commands
from config import USER_DATA_FILE
from utils import load_json, save_json

user_data_list = load_json(USER_DATA_FILE)

class RegisterModal(discord.ui.Modal):
    def __init__(self, level):
        super().__init__(title="Inscription")
        self.level = level

        self.first_name = discord.ui.TextInput(label="Prénom", required=True)
        self.last_name = discord.ui.TextInput(label="Nom de famille", required=True)
        self.class_name = discord.ui.TextInput(label="Classe", required=True)

        self.add_item(self.first_name)
        self.add_item(self.last_name)
        self.add_item(self.class_name)

        if level in ['1', '2']:
            self.study_mode = discord.ui.TextInput(label="Mode d'études (Alternance/Initial)", required=True)
            self.add_item(self.study_mode)

    async def on_submit(self, interaction: discord.Interaction):
        user_data = {
            "username": str(interaction.user),
            "first_name": self.first_name.value,
            "last_name": self.last_name.value,
            "class_name": self.class_name.value,
            "level": self.level,
            "filiere": None,
            "study_mode": self.study_mode.value if self.level in ['1', '2'] else "Alternance",
            "points": 0
        }

        if self.level in ['3', '4', '5']:
            view = FiliereSelectView(user_data)
            await interaction.response.send_message('Veuillez sélectionner votre filière.', view=view, ephemeral=True)
        else:
            user_data_list.append(user_data)
            save_json(USER_DATA_FILE, user_data_list)

            role = discord.utils.get(interaction.guild.roles, name="Membre")
            if role:
                try:
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message(f'Merci pour votre inscription, {user_data["first_name"]} {user_data["last_name"]}.', ephemeral=True)
                except discord.Forbidden:
                    await interaction.response.send_message("Je n'ai pas les autorisations nécessaires.", ephemeral=True)
                except discord.HTTPException:
                    await interaction.response.send_message("Une erreur s'est produite.", ephemeral=True)
            else:
                await interaction.response.send_message("Rôle 'Membre' non trouvé, mais vous êtes inscrit !", ephemeral=True)

class FiliereSelect(discord.ui.Select):
    def __init__(self, user_data):
        self.user_data = user_data
        options = [
            discord.SelectOption(label="AL", value="AL"),
            discord.SelectOption(label="MOC", value="MOC"),
            discord.SelectOption(label="IABD", value="IABD"),
            discord.SelectOption(label="SRC", value="SRC"),
            discord.SelectOption(label="SI", value="SI"),
            discord.SelectOption(label="IBC", value="IBC"),
            discord.SelectOption(label="IW", value="IW"),
            discord.SelectOption(label="MCSI", value="MCSI"),
        ]
        super().__init__(placeholder="Choisissez votre filière", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.user_data['filiere'] = self.values[0]
        user_data_list.append(self.user_data)
        save_json(USER_DATA_FILE, user_data_list)

        role = discord.utils.get(interaction.guild.roles, name="Membre")
        if role:
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f'Merci pour votre inscription, {self.user_data["first_name"]} {self.user_data["last_name"]}.', ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("Je n'ai pas les autorisations nécessaires.", ephemeral=True)
            except discord.HTTPException:
                await interaction.response.send_message("Une erreur s'est produite.", ephemeral=True)
        else:
            await interaction.response.send_message("Rôle 'Membre' non trouvé, mais vous êtes inscrit !", ephemeral=True)

class FiliereSelectView(discord.ui.View):
    def __init__(self, user_data):
        super().__init__()
        self.add_item(FiliereSelect(user_data))

class YearSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="1ère année", value="1"),
            discord.SelectOption(label="2ème année", value="2"),
            discord.SelectOption(label="3ème année", value="3"),
            discord.SelectOption(label="4ème année", value="4"),
            discord.SelectOption(label="5ème année", value="5")
        ]
        super().__init__(placeholder="Choisissez votre année", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        modal = RegisterModal(level=self.values[0])
        await interaction.response.send_modal(modal)

class YearSelectView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(YearSelect())

class MemberCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="register")
    async def register(self, ctx):
        view = YearSelectView()
        await ctx.send("Veuillez sélectionner votre année d'étude :", view=view)

    @commands.command(name="me")
    async def me(self, ctx):
        member = ctx.author
        user_data = next((user for user in user_data_list if user['username'] == str(member)), None)

        if user_data:
            # Calculate ranking
            sorted_users = sorted(user_data_list, key=lambda x: x['points'], reverse=True)
            ranking = next((i + 1 for i, user in enumerate(sorted_users) if user['username'] == str(member)), None)

            # Create an embed message
            embed = discord.Embed(title="Votre Profil", color=discord.Color.blue())

            # Use member.display_avatar to get the avatar URL
            avatar_url = member.display_avatar.url
            embed.set_thumbnail(url=avatar_url)

            embed.add_field(name="👤 Nom d'utilisateur", value=user_data['username'], inline=True)
            embed.add_field(name="📛 Prénom", value=user_data['first_name'], inline=True)
            embed.add_field(name="📝 Nom de famille", value=user_data['last_name'], inline=True)
            embed.add_field(name="🌟 Points", value=user_data['points'], inline=True)
            embed.add_field(name="🏅 Classement", value=ranking, inline=True)
            embed.set_footer(text="Merci de votre participation !")

            await ctx.send(embed=embed)
        else:
            await ctx.send("❗ Vous n'êtes pas encore enregistré. Utilisez la commande `!register` pour vous inscrire.")



async def setup(bot):
    await bot.add_cog(MemberCommands(bot))
