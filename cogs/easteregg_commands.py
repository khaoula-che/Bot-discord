import random
import discord
from discord.ext import commands

class EasterEgg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="easteregg")
    async def easteregg(self, ctx):
        facts = [
            "💡 Saviez-vous que les premiers concepts d'intelligence artificielle remontent aux années 1950 ?",
            "📊 Les données sont souvent appelées le 'nouvel or noir' en raison de leur immense valeur dans le monde moderne.",
            "🤖 Le test de Turing, proposé par Alan Turing en 1950, est un test de l'intelligence d'une machine.",
            "🧠 Le machine learning est une sous-catégorie de l'IA qui permet aux systèmes d'apprendre et de s'améliorer automatiquement.",
            "🚀 L'intelligence artificielle est utilisée dans des domaines allant de la médecine à l'exploration spatiale.",
            "📈 Les algorithmes de recommandation utilisés par des entreprises comme Netflix et Amazon sont basés sur des techniques d'IA avancées.",
            "🌐 L'IA joue un rôle clé dans le développement des voitures autonomes."
        ]

        fact = random.choice(facts)
        await ctx.send(fact)

async def setup(bot):
    await bot.add_cog(EasterEgg(bot))
