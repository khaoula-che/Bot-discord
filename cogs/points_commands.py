# cogs/points_commands.py

import discord
from discord.ext import commands
from utils import load_json, save_json 

USER_DATA_FILE = 'user_data.json'

class PointsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_data_list = load_json(USER_DATA_FILE)

    @commands.command(name="add_points")
    async def add_points(self, ctx, member: discord.Member, points: int):
        if 'Présidente' in [role.name for role in ctx.author.roles] or 'Vice-Présidente' in [role.name for role in ctx.author.roles]:
            for user_data in self.user_data_list:
                if user_data['username'] == str(member):
                    user_data['points'] += points
                    save_json(self.user_data_list, USER_DATA_FILE)
                    await ctx.send(f"{points} points ont été ajoutés à {member.display_name}.")
                    return
            await ctx.send(f"Membre {member.display_name} non trouvé.")
        else:
            await ctx.send("Vous n'avez pas la permission d'ajouter des points.", ephemeral=True)

    @commands.command(name="remove_points")
    async def remove_points(self, ctx, member: discord.Member, points: int):
        if 'Présidente' in [role.name for role in ctx.author.roles] or 'Vice-Présidente' in [role.name for role in ctx.author.roles]:
            for user_data in self.user_data_list:
                if user_data['username'] == str(member):
                    if user_data['points'] >= points:
                        user_data['points'] -= points
                        save_json(self.user_data_list, USER_DATA_FILE)
                        await ctx.send(f"{points} points ont été retirés à {member.display_name}.")
                    else:
                        await ctx.send(f"{member.display_name} n'a pas assez de points.")
                    return
            await ctx.send(f"Membre {member.display_name} non trouvé.")
        else:
            await ctx.send("Vous n'avez pas la permission de retirer des points.", ephemeral=True)

    @commands.command(name="reset_points")
    async def reset_points(self, ctx):
        if 'Présidente' in [role.name for role in ctx.author.roles] or 'Vice-Présidente' in [role.name for role in ctx.author.roles]:
            for user_data in self.user_data_list:
                user_data['points'] = 0
            save_json(self.user_data_list, USER_DATA_FILE)
            await ctx.send("Les points de tous les membres ont été remis à zéro.")
        else:
            await ctx.send("Vous n'avez pas la permission de réinitialiser les points.", ephemeral=True)

# Fonction pour ajouter le Cog aux commandes du bot
def setup(bot):
    bot.add_cog(PointsCommands(bot))
