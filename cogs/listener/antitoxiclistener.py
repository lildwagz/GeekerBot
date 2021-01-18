import random
import re

from better_profanity import profanity
from discord.ext import commands
import json
import os
import re
from datetime import datetime
import random

import discord
from cogs.mod2 import color_list


class antitoxic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def on_anti_toxic(self, message):


        embed = discord.Embed(title=f'**{message.author}** has been warned!',
                              description=f'**Reason**: Using blacklisted content\n**Content**: ||{message.content}||',
                              color=0x0fa7d0)
        embed.set_thumbnail(url=message.author.avatar_url)
        if profanity.contains_profanity(message.content):
            await message.delete()
            await message.channel.send(embed=embed, delete_after=10)


def setup(bot):
    bot.add_cog(antitoxic(bot))
