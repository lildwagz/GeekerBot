import socket
import random
import time

from discord.ext import commands


from utils import default


class Hacking(commands.Cog, name="hacking"):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self._last_result = None

    @commands.command()
    async def findip(self,ctx, times: int = 5, port: int = 80):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if ctx.author.id == 622741208313102336:
            for i in range(int(times)):
                ip = f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"

                try:
                    s.connect((ip, int(port)))
                    s.settimeout(1)

                    date = time.strftime("%I:%M:%S %p", time.localtime())
                    print(f'Discovered {ip}:{port} at {date}')

                    await ctx.send(f'Discovered {ip}:{port} at {date}')

                except:
                    await ctx.send(f'Oop! {ip}:{port} doesn\'t seem to be working!')

                finally:
                    s.close()
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        else:
            await ctx.send('You cant do this silly')
            
def setup(bot):
    bot.add_cog(Hacking(bot))
