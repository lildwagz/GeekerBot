import os
import time

import discord
import typing

import qrcode
from discord.ext import commands

from utils import default, converters, utils


class UtilityCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")

    @commands.command(name='avatar', aliases=['avy'])
    async def avatar(self, ctx, *, user: typing.Union[discord.Member, converters.User] = None):
        """
        Display a user's avatar.
        `user`: The user of which to get the avatar for. Can be their ID, Username, Nickname or Mention. Defaults to you.
        """

        if not user:
            user = ctx.author

        embed = discord.Embed(color=0xdeaa0c, title=f"{user.name}'s avatar")
        embed.description = f'[PNG]({user.avatar_url_as(format="png")}) | [JPEG]({user.avatar_url_as(format="jpeg")}) | [WEBP]({user.avatar_url_as(format="webp")})'
        embed.set_image(url=str(user.avatar_url_as(format='png')))

        if user.is_avatar_animated():
            embed.description += f' | [GIF]({user.avatar_url_as(format="gif")})'
            embed.set_image(url=str(user.avatar_url_as(format='gif')))

        return await ctx.send(embed=embed)

    @commands.command(aliases=['qrcode'])
    async def qr(self, ctx, *, data):
        """ Makes a QR code for you"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(data)
        img = qr.make_image(fill_color="white", back_color="black")
        img.save("databases/qrcodes/QR.png")
        await ctx.send(f"{ctx.author.mention} here it is", file=discord.File("databases/qrcodes/QR.png"))
        os.remove("databases/qrcodes/QR.png")

    @commands.command(name='member', aliases=['memberinfo'])
    async def member(self, ctx, *, member: discord.Member = None):
        """
        Displays a member's account information.
        `member`: The member of which to get information for. Can be their ID, Username, Nickname or Mention. Defaults to you.
        """

        if member is None:
            member = ctx.author

        embed = discord.Embed(colour=self.bot.utils.colours[member.status], title=f'{member}\'s information.')
        embed.description = f'`Discord Name:` {member} {"<:owner:738961071729278987>" if member.id == member.guild.owner.id else ""}\n' \
                            f'`Created on:` {self.bot.utils.format_datetime(datetime=member.created_at)}\n' \
                            f'`Created:` {self.bot.utils.format_difference(datetime=member.created_at)} ago\n' \
                            f'`Badges:` {self.bot.utils.badges(person=member)}\n' \
                            f'`Status:` {member.status.name.replace("dnd", "Do Not Disturb").title()}' \
                            f'{"<:phone:738961150343118958>" if member.is_on_mobile() else ""}\n' \
                            f'`Bot:` {str(member.bot).replace("True", "Yes").replace("False", "No")}\n' \
                            f'`Activity:` {self.bot.utils.activities(person=member)}'

        embed.add_field(name='Server related information:',
                        value=f'`Server nickname:` {member.nick}\n'
                              f'`Joined on:` {self.bot.utils.format_datetime(datetime=member.joined_at)}\n'
                              f'`Joined:` {self.bot.utils.format_difference(datetime=member.joined_at)} ago\n'
                              f'`Join Position:` {sorted(ctx.guild.members, key=lambda m: m.joined_at).index(member) + 1}\n'
                              f'`Top role:` {member.top_role.mention}\n'
                              f'`Role count:` {len(member.roles) - 1}', inline=False)

        embed.set_thumbnail(
            url=str(member.avatar_url_as(format='gif' if member.is_avatar_animated() is True else 'png')))
        embed.set_footer(text=f'ID: {member.id}')
        return await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        """ Pong! """
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        message = await ctx.send("ðŸ“ Pong")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"ðŸ“ WS: {before_ws}ms  |  REST: {int(ping)}ms")




def setup(bot):
    bot.add_cog(UtilityCommand(bot))
