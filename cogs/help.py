import asyncio

import discord

from discord.ext import commands

from main import bot
from utils import default


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
                        , inline=False)
        page1.set_footer(text="Bot Created by Zam")

        # --------------------page1------------------------------------------------------------------#

        # await ctx.channel.send(embed=page1)
        page2 = discord.Embed(title=f"__**Help page of {self.bot.user.name}**__",
                              description="[**DISCORD**](https://discord.gg/EZN4gnk)", color=0xdeaa0c)
        page2.set_thumbnail(url=f'{self.bot.user.avatar_url}')
        page2.add_field(name="__Utility :__", value=f"{self.bot.command_prefix}qrcode :** Makes a QR code for you\n**"
                                                    f"{self.bot.command_prefix}avatar :** Displays a user's avatar.\n**"
                                                    f"{self.bot.command_prefix}memberinfo :** Displays a member's account information..\n**",
                        inline=False)
        page2.set_footer(text="Bot Created by Zam")

        pages = 2
        cur_page = 1
        message = await ctx.send(f"{cur_page}/{pages}:\n", embed=page1)
        # getting the message object for editing and reacting

        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
            # This makes sure nobody except the command sender can interact with the "menu"

        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check)
                # waiting for a reaction to be added - times out after x seconds, 60 in this
                # example

                if str(reaction.emoji) == "▶️" and cur_page != pages:
                    cur_page += 1
                    await message.edit(content=f"Page {cur_page}/{pages}:\n", embed=page2)
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️" and cur_page > 1:
                    cur_page -= 1
                    await message.edit(content=f"Page {cur_page}/{pages}:\n", embed=page1)
                    await message.remove_reaction(reaction, user)

                else:
                    await message.remove_reaction(reaction, user)
                    # removes reactions if the user tries to go forward on the last page or
                    # backwards on the first page
            except asyncio.TimeoutError:
                await message.delete()
                break
                # ending the loop if user doesn't react after x seconds


# ------------------------ BOT ------------------------ #

def setup(bot):
    bot.remove_command("help")
    bot.add_cog(HelpCog(bot))
