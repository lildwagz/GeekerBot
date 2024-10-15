import json

import discord
from discord.ext import commands

from utils.permissions import has_permissions


class SetCaptcha(commands.Cog, name="change setting from captcha command"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setCaptcha', aliases=["captcha"])
    @has_permissions(administrator=True)
    async def setCaptcha(self, ctx, setCaptcha):

        setCaptcha = setCaptcha.lower()

        if setCaptcha == "true":
            # Edit configuration.json
            with open("config.json", "r") as config:
                data = json.load(config)
                data["captcha"] = True
                newdata = json.dumps(data, indent=4, ensure_ascii=False)

            embed = discord.Embed(title=f"**CAPTCHA WAS ENABLED**", description=f"The captcha verification was enabled.",
                                  color=0x2fa737)  # Green
            await ctx.channel.send(embed=embed)
        else:
            # Edit configuration.json
            with open("config.json", "r") as config:
                data = json.load(config)
                # Add modifications
                data["captcha"] = False
                newdata = json.dumps(data, indent=4, ensure_ascii=False)

            embed = discord.Embed(title=f"**CAPTCHA WAS DISABLED**", description=f"The CAPTCHA was disabled.",
                                  color=0xe00000)  # Red
            await ctx.channel.send(embed=embed)

        with open("config.json", "w") as config:
            config.write(newdata)


def setup(bot):
    bot.add_cog(SetCaptcha(bot))
