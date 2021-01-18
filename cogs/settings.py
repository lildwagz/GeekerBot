import os
from datetime import datetime

import discord
import asyncio
import json

import psutil
from discord.ext import commands

from utils import default


class SettingsCog(commands.Cog, name="settings command"):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self.process = psutil.Process(os.getpid())

    # ------------------------------------------------------ #

    @commands.command(name='settings')
    async def settings(self, ctx):

        with open("config.json", "r") as config:
            data = json.load(config)
            captcha = data["captcha"]
            captchaChannel = data["captchaChannel"]
            antispam = data["antiSpam"]
            allowSpam = data["allowSpam"]

            allowSpam2 = ""
            if len(allowSpam) == 0:
                allowSpam2 = "None"
            else:
                for x in allowSpam:
                    allowSpam2 = f"{allowSpam2}<#{x}>, "
            #
            # channelCaptcha = ""
            # if not captchaChannel:
            #     channelCaptcha = "None"
            # else:
            #     for x in captchaChannel:
            #         channelCaptcha = f"{channelCaptcha}<#{x}>, "

        embed = discord.Embed(title=f"**SERVER SETTINGS**", description=f"[**DISCORD**](https://discord.gg/EZN4gnk)",
                              color=0xdeaa0c)
        embed.add_field(name=f"**ANTI SPAM** - ``({self.bot.command_prefix}antispam <true/false>)``",
                        value=f"Anti spam enabled : {self.config.antiSpam}", inline=False)
        embed.add_field(name=f"**ANTI TOXIC** - ``({self.bot.command_prefix}antitoxic <true/false>)``",
                        value=f"Anti toxic enabled : {self.config.antitoxic}", inline=False)
        embed.add_field(name=f"**ANTI URL/LINKS** - ``({self.bot.command_prefix}antilinks <true/false>)``",
                        value=f"Anti Url/Links enabled : {self.config.antiLinks}", inline=False)
        embed.add_field(name=f"**ALLOW SPAM** - ``({self.bot.command_prefix}allowspam <#channel> (remove))``",
                        value=f"Channel where spam is allowed : #{allowSpam2[:-2]}", inline=False)
        embed.add_field(name=f"**CAPTCHA VERIFICATION** - ``({self.bot.command_prefix}setCaptcha <#channel> ("
                             f"true))``",
                        value=f"Capctha enabled : {self.config.captcha}\n"
                              f"Captcha channel : <{captchaChannel}>",
                        inline=False)

        embed.add_field(name=f"**AUTO MOD** - ``({self.bot.command_prefix}automod  <true/false>)``",
                        value=f"Auto mod enabled : {self.config.automod}", inline=False)

        embed.set_footer(text="Bot Created by Zam")
        return await ctx.channel.send(embed=embed)

    @commands.command(aliases=['info', 'stats', 'status'])
    async def about(self, ctx):
        """ About the bot """
        ramUsage = self.process.memory_full_info().rss / 1024 ** 2
        avgmembers = round(len(self.bot.users) / len(self.bot.guilds))

        embedColour = discord.Embed.Empty
        if hasattr(ctx, 'guild') and ctx.guild is not None:
            embedColour = ctx.me.top_role.colour

        embed = discord.Embed(colour=embedColour)
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        embed.add_field(name="Last boot", value=default.timeago(datetime.now() - self.bot.uptime), inline=True)
        embed.add_field(
            name=f"Developer{'' if len(self.config.owners) == 1 else 's'}",
            value=', '.join([str(self.bot.get_user(x)) for x in self.config.owners]),
            inline=True)
        embed.add_field(name="Library", value="discord.py", inline=True)
        embed.add_field(name="Servers", value=f"{len(ctx.bot.guilds)} ( avg: {avgmembers} users/server )", inline=True)
        embed.add_field(name="Commands loaded", value=len([x.name for x in self.bot.commands]), inline=True)
        embed.add_field(name="RAM", value=f"{ramUsage:.2f} MB", inline=True)

        await ctx.send(content=f"About **{ctx.bot.user}** | **{self.config.version}**", embed=embed)


def setup(bot):
    bot.add_cog(SettingsCog(bot))
