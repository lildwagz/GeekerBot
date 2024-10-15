import discord
from discord.ext import commands
from discord.utils import get


class triggeredword(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    async def on_triggered_word(self, message):
        guildidid = message.guild.id

        if self.bot.cache.triger_word[str(guildidid)][2] == 0:
            if message.content == self.bot.cache.triger_word[str(guildidid)][0]:
                role = get(message.guild.roles, id=self.bot.cache.triger_word.get(str(guildidid))[1])
                try:
                    await message.author.add_roles(role)
                except discord.errors.Forbidden as e:
                    await message.channel.send(e)

        else:
            if self.bot.cache.triger_word[str(guildidid)][2] == message.channel.id:
                if message.content == self.bot.cache.triger_word[str(guildidid)][0]:
                    role = get(message.guild.roles, id=self.bot.cache.triger_word.get(str(guildidid))[1])
                    try:
                        await message.delete()
                        await message.author.add_roles(role)

                    except discord.errors.Forbidden as e:
                        await message.channel.send(e)

def setup(bot):
    bot.add_cog(triggeredword(bot))
