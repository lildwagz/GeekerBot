import discord
from discord.ext.commands import AutoShardedBot, DefaultHelpCommand

from utils import permissions, lists, utils


class Bot(AutoShardedBot):
    def __init__(self, *args, prefix=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = prefix
        self.utils = utils.Utils(bot=self)

    # async def on_message(self, msg):
    #     if not self.is_ready() or msg.author.bot or not permissions.can_send(msg):
    #         return
    #     await self.process_commands(msg)



# class HelpFormat(DefaultHelpCommand):
#     def get_destination(self, no_pm: bool = True):
#         if no_pm:
#             return self.context.channel
#         else:
#             return self.context.author

