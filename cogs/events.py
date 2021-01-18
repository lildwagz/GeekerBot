import json
import random
import re
import sys
from os import path

import discord
import psutil
import os
import asyncio

from datetime import datetime

from discord.ext import commands
from discord.ext.commands import errors

from cogs.mod2 import color_list
from utils import default, lists
from better_profanity import profanity


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self.process = psutil.Process(os.getpid())

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
            await ctx.send_help(helper)

        elif isinstance(err, errors.CommandInvokeError):
            error = default.traceback_maker(err.original)

            if "2000 or fewer" in str(err) and len(ctx.message.clean_content) > 1900:
                return await ctx.send(
                    "You attempted to make the command display more than 2,000 characters...\n"
                    "Both error and command will be ignored."
                )

            await ctx.send(f"There was an error processing the command ;-;\n{error}")

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.MaxConcurrencyReached):
            await ctx.send("You've reached max capacity of command usage at once, please finish the previous one...")

        elif isinstance(err, errors.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown... try again in {err.retry_after:.2f} seconds.")

        elif isinstance(err, errors.CommandNotFound):
            pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if not self.config.join_message:
            return

        try:
            to_send = sorted([chan for chan in guild.channels if
                              chan.permissions_for(guild.me).send_messages and isinstance(chan, discord.TextChannel)],
                             key=lambda x: x.position)[0]
        except IndexError:
            pass
        else:
            await to_send.send(self.config.join_message)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        try:
            print(f"{ctx.guild.name} > {ctx.author} > {ctx.message.clean_content}")
        except AttributeError:
            print(f"Private message > {ctx.author} > {ctx.message.clean_content}")

    @commands.Cog.listener()
    async def on_ready(self):
        """ The function that activates when boot was completed """
        if not hasattr(self.bot, 'uptimes'):
            self.bot.uptime = datetime.utcnow()

        status = self.config.status_type.lower()
        status_type = {"idle": discord.Status.idle, "dnd": discord.Status.dnd}

        activity = self.config.activity_type.lower()
        activity_type = {"listening": 2, "watching": 3, "competing": 5}

        await self.bot.change_presence(
            activity=discord.Game(
                type=activity_type.get(activity, 0), name=self.config.activity
            ),
            status=status_type.get(status, discord.Status.online)
        )
        # Indicate that the bot has successfully booted up
        print(f'Ready: {self.bot.user} | Servers: {len(self.bot.guilds)}')

    def load_captchas(self):
        with open('Databases/captcha/captchas.json') as json_file:
            return json.load(json_file)

    def save_catchas(self, captchas):
        with open('Databases/captcha/captchas.json', 'w') as outfile:
            json.dump(captchas, outfile)

    @commands.Cog.listener()
    async def on_message(self, message):
        whitelisted_roles = [771035451128938506]
        with open("config.json", "r") as con:
            config = json.load(con)
            antiSpam = config["antiSpam"]
            allowSpam = config["allowSpam"]
            antitoxic = config["antitoxic"]
            captcha = config["captcha"]
            antiLinks = config["antiLinks"]
        if message.author.bot:
            return

        if antitoxic or antiLinks:
            if self.config.SkipBots and message.author.bot:
                return None
            for role in message.author.roles:
                if role.id in whitelisted_roles:
                    return None
            regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([" \
                    r"^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])) "

            url = re.findall(regex, message.content)
            detect = ([x[0] for x in url])
            censored = profanity.censor(message.content)

            embed = discord.Embed(title=f'**{message.author}** has been warned!',
                                  description=f'**Reason**: Using blacklisted content\n**Content**: ||{message.content}||',
                                  color=0x0fa7d0)
            embed.set_thumbnail(url=message.author.avatar_url)

            if profanity.contains_profanity(message.content) and antitoxic:
                await message.delete()
                await message.channel.send(embed=embed, delete_after=10)
            elif detect and antiLinks:
                await message.delete()
                await message.channel.send(embed=embed, delete_after=10)


        if antiSpam:
            warnerName = "GeekerBot"
            warnerId = 772748636554788895
            color = random.choice(color_list)

            def check(message):
                return message.author == message.author and (datetime.utcnow() - message.created_at).seconds < 15

            try:
                if message.author.guild_permissions.administrator:
                    return

                if message.channel.id in allowSpam:
                    return

                if len(list(filter(lambda m: check(m), self.bot.cached_messages))) >= 9 and len(
                        list(filter(lambda m: check(m), self.bot.cached_messages))) < 12:
                    await message.channel.send(f"{message.author.mention} don't do that bruh!")
                elif len(list(filter(lambda m: check(m), self.bot.cached_messages))) >= 14 \
                        :
                    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    if not os.path.exists("Databases/warns/" + str(message.guild.id) + "/"):
                        os.makedirs("Databases/warns/" + str(message.guild.id) + "/")
                    try:
                        with open(f"Databases/warns/{str(message.guild.id)}/{str(message.author.id)}.json") as f:
                            data = json.load(f)
                            warn_amount = data.get("warns")
                            new_warn_amount = warn_amount + 1
                            data["warns"] = new_warn_amount
                            data["offender_name"] = message.author.name
                            new_warn = ({
                                'warner': self.bot.user.id,
                                'warner_name': self.bot.user.name,
                                'reason': "spamming",
                                'channel': str(message.channel.id),
                                'datetime': dt_string
                            })
                            data[new_warn_amount] = new_warn
                            if warn_amount == 3:
                                reason = "spamming multiple times"
                                muted_role = next((g for g in message.guild.roles if g.name == "Muted"), None)
                                try:
                                    await message.author.add_roles(muted_role, reason=reason)
                                    await message.channel.send(
                                        f"<@{message.author.id}> has been muted by <@{warnerId}> for *{reason}*")
                                except Exception as e:
                                    await message.channel.send(e)
                            else:
                                json.dump(data, open(
                                    f"Databases/warns/{str(message.guild.id)}/{str(message.author.id)}.json", "w"))
                                embed = discord.Embed(title=f"{message.author.name}'s new warn", color=color)
                                embed.add_field(
                                    name=f"Warn  {new_warn_amount}",
                                    value=f"Warner: {warnerName} (<@{warnerId}>)\nReason: spamming\nChannel: <#{str(message.channel.id)}>\nDate and Time: {dt_string}",
                                    inline=True
                                )
                                await message.channel.send(
                                    content="Successfully added new warn.",
                                    embed=embed
                                )

                    except FileNotFoundError:

                        with open(f"Databases/warns/{str(message.guild.id)}/{str(message.author.id)}.json", "w") as f:
                            data = ({
                                'offender_name': message.author.name,
                                'warns': 1,
                                1: ({
                                    'warner': warnerId,
                                    'warner_name': warnerName,
                                    'reason': "spamming",
                                    'channel': str(message.channel.id),
                                    'datetime': dt_string
                                })
                            })  #
                            json.dump(data, f)
                        embed = discord.Embed(title=f"{message.author.name}'s new warn",
                                              color=random.choice(color_list))
                        embed.add_field(
                            name="Warn 1",
                            value=f"Warner: {warnerName} (<@{warnerId}>)\nReason: Spamming\nChannel: <#{str(message.channel.id)}>\nDate and Time: {dt_string}",
                            inline=True
                        )
                        await message.channel.send(
                            content="Successfully added new warn.",
                            embed=embed
                        )
                        return
                    # embed = discord.Embed(
                    #     title=f"**YOU HAVE BEEN KICKED FROM {message.author.guild.name}**",
                    #     description=f"Reason : You spammed.", color=0xff0000)
                    # await message.author.send(embed=embed)
                    # # await message.author.kick()  # Kick the user
                    # await message.channel.send(
                    #     f"{message.author.mention} hell yeah this dude has no chill !")

            except:
                pass

        if captcha:
            pass


    # @commands.Cog.listener()
    # async def on_member_join(self, member):
    #     chanel = self.bot.get_channel(773461453851983882)
    #     captcha_list = self.load_captchas()
    #     captchaValue = CaptchaMaker.create()
    #     captcha_list[member.id] = captchaValue
    #     self.save_catchas(captcha_list)
    #     file = "captcha_" + captchaValue + ".png"
    #     await chanel.send(file=discord.File("Databases/captcha/" + file))


def setup(bot):
    bot.add_cog(Events(bot))
