from discord.ext import commands

from utils import default


class Hacking(commands.Cog, name="hacking"):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self._last_result = None


def setup(bot):
    bot.add_cog(Hacking(bot))
