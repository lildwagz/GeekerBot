from discord.ext import commands

from utils import utilss, permissions


class Security(commands.Cog, name="Security"):
    def __init__(self, bot):
        self.bot = bot
        self.filenotallowed = {"guildid": {"file":
                               ['filetipe'],
                                           "channel":[]}
                               }



    @commands.check(permissions.is_owner)
    @commands.guild_only()
    @commands.command(name="filetypenot")
    async def filetype(self, ctx , action, extension , channel):
        if action.lower() == "add":
            channel = channel.replace("<", "")
            channel = channel.replace("#", "")
            channel = channel.replace(">", "")
            channel = self.bot.get_channel(channel)





def setup(bot):
    bot.add_cog(Security(bot))
