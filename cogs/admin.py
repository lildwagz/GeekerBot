import aiohttp
import discord

from discord.ext import commands
from utils import permissions, default, http, dataIO


class Admin(commands.Cog, name="admin"):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self._last_result = None


    @commands.group()
    @commands.check(permissions.is_owner)
    async def dm(self, ctx, user_id: discord.Member, *, message: str):
        # user = self.bot.get_user(user_id)
        if user_id is None:
            return await ctx.send(f"Could not find any UserID matching **{user_id}**")

        try:
            await user_id.send(message)
            await ctx.send(f"✉️ Sent a DM to **{user_id}**")
        except discord.Forbidden:
            await ctx.send("This user might be having DMs blocked or it's a bot account...")

    @commands.group()
    @commands.check(permissions.is_owner)
    async def change(self, ctx):
        if ctx.invoked_subcommand is None:
            embedColour = ctx.me.top_role.colour
            embed = discord.Embed(title=f"**{self.bot.command_prefix}change**", colour=0xdeaa0c)

            embed.add_field(name="__Commands :__",
                            value=f"{self.bot.command_prefix}avatar :** Change avatar. \n**"
                                  f"{self.bot.command_prefix}nickname  :**  Change nickname.\n**"
                                  f"{self.bot.command_prefix}playing  :**   Change playing status. \n**"
                                  f"{self.bot.command_prefix}username   :** Change username.\n**",
                            inline=False)
            await ctx.send(content=f"", embed=embed)

    @change.command(name="playing")
    @commands.check(permissions.is_owner)
    async def change_playing(self, ctx, *, playing: str):
        """ Change playing status. """
        if self.config.status_type == "idle":
            status_type = discord.Status.idle
        elif self.config.status_type == "dnd":
            status_type = discord.Status.dnd
        else:
            status_type = discord.Status.online

        if self.config.activity_type == "listening":
            activity_type = 2
        elif self.config.activity_type == "watching":
            activity_type = 3
        else:
            activity_type = 0

        try:
            await self.bot.change_presence(
                activity=discord.Activity(type=activity_type, name=playing),
                status=status_type
            )
            dataIO.change_value("config.json", "playing", playing)
            await ctx.send(f"Successfully changed playing status to **{playing}**")
        except discord.InvalidArgument as err:
            await ctx.send(err)
        except Exception as e:
            await ctx.send(e)

    @change.command(name="username")
    @commands.check(permissions.is_owner)
    async def change_username(self, ctx, *, name: str):
        """ Change username. """
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"Successfully changed username to **{name}**")
        except discord.HTTPException as err:
            await ctx.send(err)

    @change.command(name="nickname")
    @commands.check(permissions.is_owner)
    async def change_nickname(self, ctx, *, name: str = None):
        """ Change nickname. """
        try:
            await ctx.guild.me.edit(nick=name)
            if name:
                await ctx.send(f"Successfully changed nickname to **{name}**")
            else:
                await ctx.send("Successfully removed nickname")
        except Exception as err:
            await ctx.send(err)

    @change.command(name="avatar")
    @commands.check(permissions.is_owner)
    async def change_avatar(self, ctx, url: str = None):
        """ Change avatar. """
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip('<>') if url else None

        try:
            bio = await http.get(url, res_method="read")
            await self.bot.user.edit(avatar=bio)
            await ctx.send(f"Successfully changed the avatar. Currently using:\n{url}")
        except aiohttp.InvalidURL:
            await ctx.send("The URL is invalid...")
        except discord.InvalidArgument:
            await ctx.send("This URL does not contain a useable image")
        except discord.HTTPException as err:
            await ctx.send(err)
        except TypeError:
            await ctx.send("You need to either provide an image URL or upload one with the command")


def setup(bot):
    bot.add_cog(Admin(bot))
