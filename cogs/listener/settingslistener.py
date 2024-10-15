
from discord.ext import commands



class settingslistener(commands.Cog, name="settings listener"):
    def __init__(self,bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return


def setup(bot):
    bot.add_cog(settingslistener(bot))
