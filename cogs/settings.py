import discord
import asyncio
import json

from discord.ext import commands
from discord.utils import get
from discord.ext.commands import has_permissions


# ------------------------ COGS ------------------------ #

class SettingsCog(commands.Cog, name="settings command"):
    def __init__(self, bot):
        self.bot = bot

    # ------------------------------------------------------ #

    @commands.command(name='settings')
    async def settings(self, ctx):

        with open("config.json", "r") as config:
            data = json.load(config)
            antispam = data["antiSpam"]
            automod = data["automod"]
            allowSpam = data["allowSpam"]


            allowSpam2 = ""
            if len(allowSpam) == 0:
                allowSpam2 = "None"
            else:
                for x in allowSpam:
                    allowSpam2 = f"{allowSpam2}<#{x}>, "



        embed = discord.Embed(title=f"**SERVER SETTINGS**", description=f"[**DISCORD**](https://discord.gg/EZN4gnk)",
                              color=0xdeaa0c)
        embed.add_field(name=f"**ANTI SPAM** - ``({self.bot.command_prefix}antispam <true/false>)``",
                        value=f"Anti spam enabled : {antispam}", inline=False)
        embed.add_field(name=f"**ALLOW SPAM** - ``({self.bot.command_prefix}allowspam <#channel> (remove))``",
                        value=f"Channel where spam is allowed : {allowSpam2[:-2]}", inline=False)

        embed.add_field(name=f"**AUTO MOD** - ``({self.bot.command_prefix}automod  <true/false>)``",
                        value=f"Auto mod enabled : {automod}", inline=False)

        embed.set_footer(text="Bot Created by Zam")
        return await ctx.channel.send(embed=embed)



def setup(bot):
    bot.add_cog(SettingsCog(bot))
