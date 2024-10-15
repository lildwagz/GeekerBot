import asyncio
import json
import random

import arrow
import discord
import psutil
import os

from datetime import datetime

from discord.ext import commands, tasks
from discord.ext.commands import errors

# from cogs.func.cleverbot import chatbot_response_b
from utils import default, utilss

step = 0
chat_history_ids = []


class Events(commands.Cog):
    """A tons of Utility commands"""
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self.process = psutil.Process(os.getpid())
        self.guildid = []
        self.statuses = [
            ("watching", lambda: f"{len(self.bot.guilds)} servers"),
            ("listening", lambda: f"{len(set(self.bot.get_all_members()))} users"),
            ("playing", lambda: "gabutcodex.tk"),
        ]
        self.activities = {"playing": 0, "streaming": 1, "listening": 2, "watching": 3}
        self.current_status = None
        self.status_loop.start()
        self.logcommand = 800650161020993586
        self.message_levels = {
            "info": {
                "description_prefix": ":information_source:",
                "color": int("3b88c3", 16),
                "help_footer": False,
            },
            "warning": {
                "description_prefix": ":warning:",
                "color": int("ffcc4d", 16),
                "help_footer": False,
            },
            "error": {
                "description_prefix": ":no_entry:",
                "color": int("be1931", 16),
                "help_footer": False,
            },
            "cooldown": {
                "description_prefix": ":hourglass_flowing_sand:",
                "color": int("ffe8b6", 16),
                "help_footer": False,
            }
        }

    async def send(self, ctx, level, message, help_footer=None, codeblock=False, **kwargs):
        """Send error message to chat."""
        settings = self.message_levels.get(level)
        if codeblock:
            message = f"`{message}`"

        embed = discord.Embed(
            color=settings["color"], description=f"{settings['description_prefix']} {message}"
        )

        help_footer = help_footer or settings["help_footer"]
        if help_footer:
            embed.set_footer(text=f"Learn more: {ctx.prefix}help {ctx.command.qualified_name}")

        try:
            await ctx.send(embed=embed, **kwargs)
        except discord.errors.Forbidden:
            self.bot.logger.warning("Forbidden when trying to send error message embed")


    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
            await ctx.send_help(helper)

        elif isinstance(err, commands.MissingPermissions):
            perms = ", ".join(f"**{x}**" for x in err.missing_perms)
            await utilss.send_error_message(ctx, f"You require {perms} permission to use this command!")

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

        elif isinstance(err, commands.errors.MaxConcurrencyReached):
            await ctx.send("Stop spamming! You are really bad(")





    @commands.Cog.listener()
    async def on_command(self, ctx):
        logchannel = self.bot.get_channel(self.logcommand)
        content = discord.Embed(color=discord.Color.green())
        content.title = "LOGG COMMAND"
        content.timestamp = arrow.utcnow().datetime

        try:
            content.description = (
                f"{ctx.guild.name} > {ctx.author} > {ctx.message.clean_content}"
            )
            content.set_thumbnail(url=ctx.guild.icon_url)
            content.set_footer(text=f"{ctx.guild.name}")

            await logchannel.send(embed=content)

            print(f"{ctx.guild.name} > {ctx.author} > {ctx.message.clean_content}")

        except AttributeError:
            content.description = (
                f"Private message > {ctx.author} > {ctx.message.clean_content}"
            )
            content.set_footer(text=f"{ctx.author}")
            content.set_thumbnail(url=str(ctx.author.avatar_url_as(format='gif' if ctx.author.is_avatar_animated() is True else 'png')))
            await logchannel.send(embed=content)

            print(f"Private message > {ctx.author} > {ctx.message.clean_content}")

    @commands.Cog.listener()
    async def on_ready(self):
        """ The function that activates when boot was completed """
        if not hasattr(self.bot, 'uptime'):
            self.bot.uptime = datetime.utcnow()

        status = self.config.status_type.lower()
        status_activity = f" {len(self.bot.users)} users | {len(self.bot.guilds)} servers"
        status_type = {"idle": discord.Status.idle, "dnd": discord.Status.dnd}

        activity = self.config.activity_type.lower()
        activity_type = {"listening": 2, "watching": 3, "competing": 5}

        await self.bot.change_presence(
            activity=discord.Game(
                type=activity_type.get(activity, 2), name=status_activity
            ),
            status=status_type.get(status, discord.Status.dnd)
        )

        # Indicate that the bot has successfully booted up

        print(f'Ready: {self.bot.user} | Servers: {len(self.bot.guilds)}')

    def load_captchas(self):
        with open('Databases/captcha/captchas.json') as json_file:
            return json.load(json_file)

    def save_catchas(self, captchas):
        with open('Databases/captcha/captchas.json', 'w') as outfile:
            json.dump(captchas, outfile)


    @tasks.loop(minutes=3.0)
    async def status_loop(self):
        try:
            await self.next_status()
        except Exception as e:
            # logger.error(e)
            print(e)

    @status_loop.before_loop
    async def before_status_loop(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(30)  # avoid rate limit from discord in case of rapid reconnect
        # print("Starting status loop")

    async def next_status(self):
        """switch to the next status message."""
        new_status_id = self.current_status
        while new_status_id == self.current_status:
            new_status_id = random.randrange(0, len(self.statuses))

        status = self.statuses[new_status_id]
        self.current_status = new_status_id

        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType(self.activities[status[0]]), name=status[1]()
            )
        )

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































