import collections
import time

import aiohttp
import psutil
from celery import Celery

from discord.ext.commands import AutoShardedBot, DefaultHelpCommand, when_mentioned_or

from utils import permissions, lists, utilss, helper


class Bot(AutoShardedBot):
    def __init__(self, *args, prefix=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefixdefault = "g!"
        self.prefix = prefix
        self.utils = utilss.Utilss(bot=self)
        self.socket_stats = collections.Counter()
        self.process = psutil.Process()
        self.start_time = time.time()
        self.session = aiohttp.ClientSession(loop=self.loop)

        # self.app = Celery('worker', broker='redis://127.0.0.1:6379/0', backend='redis://127.0.0.1:6379/0')
        self.app = Celery('worker',
                          broker='redis:// lildwagz:lildwagz@redis-10450.c81.us-east-1-2.ec2.cloud.redislabs.com:10450',
                          backend='redis:// lildwagz:lildwagz@redis-10450.c81.us-east-1-2.ec2.cloud.redislabs.com:10450',
                          )
        self.app2 = Celery('worker',
                                  broker='redis:// lildwagz:lildwagz@redis-17460.c232.us-east-1-2.ec2.cloud.redislabs.com:17460',
                                  backend='redis:// lildwagz:lildwagz@redis-17460.c232.us-east-1-2.ec2.cloud.redislabs.com:17460'
                                  )

        # self.app = Celery('worker',
        #                   broker='redis://localhost:6380',
        #                   backend='redis://localhost:6380'
        #                   )
        # self.app2 = Celery('worker',
        #                    broker='redis://localhost:6379',
        #                    backend='redis://localhost:6379'
        #                           )



        self.userdata = []


        self.cache = helper.Cache(self)



    # async def get_prefix(self, message):
    #     guildid = message.guild.id
    #     # # prefix = app.send_task('celerys.worker.get_prefix',kwargs={'guildid':guildid,'prefix':message})
    #     # # prefix = self.app.send_task('celerys.worker.get_prefix', kwargs={'guildid': guildid, 'prefix': message})
    #     # print(message)
    #
    #     return "-g"



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

