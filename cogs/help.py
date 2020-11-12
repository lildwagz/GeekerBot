import asyncio

import discord

from discord.ext import commands
from utils import default
from utils.pagination import BotEmbedPaginator


class HelpCog(commands.Cog, name="help command"):
    def __init__(self, bot):
        self.bot = bot
        self.author = default.get("config.json")

    @commands.command(name='help')
    async def help(self, ctx):
        page1 = discord.Embed(title=f"__**Help page of {self.bot.user.name}**__",
                                  description="[**DISCORD**](https://discord.gg/EZN4gnk)", color=0xdeaa0c)
        page1.set_thumbnail(url=f'{self.bot.user.avatar_url}')
        page1.add_field(name="__Admin :__",
                        value=f"{self.bot.command_prefix}settings :** Display the list of settings.\n**"
                              f"{self.bot.command_prefix}antispam <true/false> :** Enable or disable the spam protection.\n**"
                              f"{self.bot.command_prefix}dm  :** dm a specific user.\n**"
                              f"{self.bot.command_prefix}change  :** changes avatar, nickname, playing, username.\n**",
                        inline=False)
        page1.add_field(name="__Mod :__",
                        value=f"{self.bot.command_prefix}ban      :**  Bans a user from the current server.\n**"
                              f"{self.bot.command_prefix}kick     :**  Kicks a user from the current server.\n**"
                              f"{self.bot.command_prefix}mute     :**  Mutes a user from the current server.\n**"
                              f"{self.bot.command_prefix}prune    :**  Removes messages from the current server.\n**"
                              f"{self.bot.command_prefix}unban    :** Unbans a user from the current server. \n**"
                              f"{self.bot.command_prefix}unmute   :**Unmutes a user from the current server. \n**"
                              f"{self.bot.command_prefix}warn     :**warns a user. \n**"
                              f"{self.bot.command_prefix}warns    :**See all the warns a user has.\n**"
                              f"{self.bot.command_prefix}removewarn :**Removes a specific warn from a specific user.\n**"
                              f"{self.bot.command_prefix}editwarn :**Edits a specific warn from a specific user.\n**",
                        inline=False)
        page1.add_field(name="__Hacking Tools :__",
                        value=f"{self.bot.command_prefix}emailinfo :** Get email information.\n**"
                              f"{self.bot.command_prefix}whoisweb  :** Lookup whois domain information.\n**",
                        inline=False)

        page1.add_field(name="__For Fun :__",
                        value=f"{self.bot.command_prefix}poll :** Makes a simple poll so you can vote either yes or no.\n**"
                              f"{self.bot.command_prefix}quotes  :**  Posts a random quotes.\n**"
                              f"{self.bot.command_prefix}roast  :**  Lets GeekerBot insult someone or yourself.\n**"
                              f"{self.bot.command_prefix}gayscanner   :**  See how gAe another user is. Shows my level of maturity too.\n**"
                              f"{self.bot.command_prefix}ship    :**  Test love between two users.\n**"
                              f"{self.bot.command_prefix}8ball    :**   Consult 8ball to receive an answer.\n**"
                              f"{self.bot.command_prefix}cat    :**    Posts a random cat.\n**"
                              f"{self.bot.command_prefix}dog    :**   Posts a random dog.\n**"
                              f"{self.bot.command_prefix}birb    :**    Posts a random birb.\n**"
                              f"{self.bot.command_prefix}coffee    :**  Posts a random coffee.\n**"
                              f"{self.bot.command_prefix}f    :**  Press F to pay respect.\n**"
                              f"{self.bot.command_prefix}urban    :** Find the 'best' definition to your words .\n**"
                              f"{self.bot.command_prefix}beer    :** Give someone a beer! 🍻 .\n**"
                              f"{self.bot.command_prefix}hotcalc    :** Returns a random percent for how hot is a discord user\n**"
                              f"{self.bot.command_prefix}reverse    :**  !poow ,ffuts esreveR Everything you type after reverse will of course, be reversed\n**"
                        , inline=False)
        page1.set_footer(text=f"Bot Created by {self.author.owners}")

        # --------------------page1------------------------------------------------------------------#
        page2 = discord.Embed(title=f"__**Help page of {self.bot.user.name}**__",
                              description="[**DISCORD**](https://discord.gg/EZN4gnk)", color=0xdeaa0c)
        page2.set_thumbnail(url=f'{self.bot.user.avatar_url}')
        page2.add_field(name="__Utility :__", value=f"{self.bot.command_prefix}qrcode :** Makes a QR code for you\n**"
                                                    f"{self.bot.command_prefix}avatar :** Displays a user's avatar.\n**"
                                                    f"{self.bot.command_prefix}memberinfo :** Displays a member's account information..\n**",
                        inline=False)
        page2.set_footer(text="Bot Created by Zam")

        embeds = [
                page1, page2
        ]
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()



def setup(bot):
    bot.remove_command("help")
    bot.add_cog(HelpCog(bot))
