from discord.ext import commands


class SetCaptcha(commands.Cog, name="change setting from captcha command"):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(SetCaptcha(bot))
