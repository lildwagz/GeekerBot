from discord.ext import commands
import re
# from datetime import datetime
# import random

import discord
# from cogs.mod2 import color_list
from utils import permissions


class antilinks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def on_anti_links(self, message):
        if permissions.is_owner(message):
            return
        try:
            for role in message.author.roles:
                if role.id in self.bot.cache.whitelist[str(message.guild.id)]:
                    return
        except KeyError as e:
            pass
        embed = discord.Embed(title=f'**{message.author}** has been warned!',
                              description=f'**Reason**: the message containts link\n**Content**: ||{message.content}||',
                              color=0x0fa7d0)
        regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

        url = re.findall(regex, message.content)


        # detect = ([x[0] for x in url])
        # print(detect)
        if url:
            if self.bot.cache.infractionchannel.get(str(message.guild.id)) is not None:
                channellog = self.bot.get_channel(self.bot.cache.infractionchannel.get(str(message.guild.id)))
                try:
                    await message.delete()
                    await channellog.send(embed=embed)
                except discord.errors.Forbidden:
                    await channellog.send("`error: I'm missing required discord permission [ manage messages ]`")
                    await channellog.send(embed=embed)

            else:
                try:
                    await message.delete()
                    await message.channel.send(embed=embed, delete_after=10)
                except discord.errors.Forbidden:
                    await message.channel.send("`error: I'm missing required discord permission [ manage messages ]`")


def setup(bot):
    bot.add_cog(antilinks(bot))
