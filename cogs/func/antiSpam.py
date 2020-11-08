import discord
import json

from discord.ext import commands
from discord.ext.commands import has_permissions


class AntiSpamCog(commands.Cog, name="change setting from anti spam command"):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name = 'antispam', aliases= ["spam"])
    @has_permissions(administrator = True)
    async def antispam (self, ctx, antiSpam):

        antiSpam = antiSpam.lower()

        if antiSpam == "true":
            # Edit configuration.json
            with open("config.json", "r") as config:
                data = json.load(config)
                # Add modifications
                data["antiSpam"] = True
                newdata = json.dumps(data, indent=4, ensure_ascii=False)
                
            embed = discord.Embed(title = f"**ANTI SPAM WAS ENABLED**", description = f"The anti spam was enabled.", color = 0x2fa737) # Green
            await ctx.channel.send(embed = embed)
        else:
            # Edit configuration.json
            with open("config.json", "r") as config:
                data = json.load(config)
                # Add modifications
                data["antiSpam"] = False
                newdata = json.dumps(data, indent=4, ensure_ascii=False)
                
            embed = discord.Embed(title = f"**ANTI SPAM WAS DISABLED**", description = f"The anti spam was disabled.", color = 0xe00000) # Red
            await ctx.channel.send(embed = embed)
            
        with open("config.json", "w") as config:
            config.write(newdata)


def setup(bot):
    bot.add_cog(AntiSpamCog(bot))