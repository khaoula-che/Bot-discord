import discord
from discord.ext import commands
from utils import load_json, save_json
from config import FEEDBACK_FILE

feedback_data = load_json(FEEDBACK_FILE)

class FeedbackModal(discord.ui.Modal):
    def __init__(self, admin_channel):
        super().__init__(title="📝 Feedback sur l'événement")
        self.admin_channel = admin_channel

        self.enjoyed = discord.ui.TextInput(label="Qu'avez-vous aimé ?", style=discord.TextStyle.long)
        self.not_enjoyed = discord.ui.TextInput(label="Qu'avez-vous moins aimé ?", style=discord.TextStyle.long)

        self.add_item(self.enjoyed)
        self.add_item(self.not_enjoyed)

    async def on_submit(self, interaction: discord.Interaction):
        self.feedback = {
            "user": str(interaction.user),
            "enjoyed": self.enjoyed.value,
            "not_enjoyed": self.not_enjoyed.value,
            "rating": None  # Will be set later
        }

        view = RatingButtons(self.feedback, self.admin_channel)
        await interaction.response.send_message("Merci pour votre feedback ! Veuillez évaluer l'événement avec des étoiles ci-dessous.", view=view, ephemeral=True)

class RatingButtons(discord.ui.View):
    def __init__(self, feedback, admin_channel):
        super().__init__(timeout=60)
        self.feedback = feedback
        self.admin_channel = admin_channel

    async def handle_rating(self, interaction: discord.Interaction, rating: int):
        self.feedback['rating'] = rating
        feedback_data.append(self.feedback)
        save_json(FEEDBACK_FILE, feedback_data)

        summary = (
            f"**Feedback de {self.feedback['user']}**\n"
            f"**👍 Aimé**: {self.feedback['enjoyed']}\n"
            f"**👎 Moins aimé**: {self.feedback['not_enjoyed']}\n"
            f"**⭐ Note**: {'⭐' * self.feedback['rating']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        await self.admin_channel.send(summary)
        await interaction.response.send_message("Merci pour votre évaluation ! ⭐️", ephemeral=True)
        self.stop()

    @discord.ui.button(label="⭐", style=discord.ButtonStyle.secondary)
    async def one_star(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_rating(interaction, 1)

    @discord.ui.button(label="⭐⭐", style=discord.ButtonStyle.secondary)
    async def two_stars(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_rating(interaction, 2)

    @discord.ui.button(label="⭐⭐⭐", style=discord.ButtonStyle.secondary)
    async def three_stars(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_rating(interaction, 3)

    @discord.ui.button(label="⭐⭐⭐⭐", style=discord.ButtonStyle.secondary)
    async def four_stars(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_rating(interaction, 4)

    @discord.ui.button(label="⭐⭐⭐⭐⭐", style=discord.ButtonStyle.secondary)
    async def five_stars(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_rating(interaction, 5)

class FeedbackCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="demande_feedback")
    @commands.has_permissions(administrator=True)
    async def demande_feedback(self, ctx):
        feedback_channel = discord.utils.get(ctx.guild.channels, name="feedback-événements")
        admin_channel = discord.utils.get(ctx.guild.channels, name="admin-feedback")

        if feedback_channel is None:
            await ctx.send("Le canal `feedback-événements` est introuvable.")
            return

        if admin_channel is None:
            await ctx.send("Le canal `admin-feedback` est introuvable.")
            return

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Donner un feedback", emoji="📝", style=discord.ButtonStyle.primary, custom_id="feedback_button"))

        await feedback_channel.send(
            "Nous aimerions connaître votre avis sur l'événement qui vient de se dérouler. Merci de cliquer sur le bouton ci-dessous pour donner votre feedback.",
            view=view
        )

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.data.get("custom_id") == "feedback_button":
            admin_channel = discord.utils.get(interaction.guild.channels, name="admin-feedback")
            if admin_channel:
                await interaction.response.send_modal(FeedbackModal(admin_channel))

async def setup(bot):
    await bot.add_cog(FeedbackCommands(bot))
