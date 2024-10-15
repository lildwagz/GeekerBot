
import discord

from discord.ext import commands
from utils import default, permissions
from utils.pagination import BotEmbedPaginator


class HelpCog(commands.Cog, name="help command"):
    def __init__(self, bot):
        self.bot = bot
        self.author = default.get("config.json")
        self.COLOUR = int("ee84ca", 16)

    @commands.command(name='help')
    async def help(self, ctx):
        if ctx.guild:
            prefix = self.bot.cache.prefixes.get(str(ctx.guild.id), self.bot.prefixdefault)
        else:
            prefix = self.bot.prefixdefault

        page1 = discord.Embed(title=f"__**Help page of {self.bot.user.name}**__",
                              description=f"{prefix}info :** To show the Information of the bot**\n"
                                          f"{prefix}joinme : **get Geekerbot manage your server.**\n\n"
                                          "[**DISCORD**](https://discord.gg/EZN4gnk)", color=0xdeaa0c)
        page1.set_thumbnail(url=f'{self.bot.user.avatar_url}')
        page1.add_field(name="__Admin :__",
                        value=f"{prefix}settings :** Display the list of settings.\n**"
                        # f"{prefix}dm  :** dm a specific user.\n**"
                        # f"{prefix}change  :** changes avatar, nickname, playing, username.\n**"
                              f"{prefix}prefix  :** customize your own prefix.\n**"
                              f"{prefix}emoji  :** Emoji management commands.\n**"
                        # f"{prefix}nickall  :** changes all members nickaname to default.\n**"
                              f"{prefix}scanname  :** scans all members nickaname if there's profanity nicknames and changes it.\n**"
                              f"{prefix}announce  :** make an announcement and send it in specific channel.\n**"
                        ,
                        inline=False)
        page1.add_field(name="__Mod :__",
                        value=f"{prefix}ban      :**  Bans a user from the current server.\n**"
                              f"{prefix}kick     :**  Kicks a user from the current server.\n**"
                              f"{prefix}lock     :**  Locks a channel.\n**"
                              f"{prefix}mute     :**  Mutes a user from the current server.\n**"
                              f"{prefix}prune    :**  Removes messages from the current server.\n**"
                              f"{prefix}unban    :** Unbans a user from the current server. \n**"
                              f"{prefix}unmute   :**Unmutes a user from the current server. \n**"
                              f"{prefix}warn     :**warns a user. \n**"
                              f"{prefix}warns    :**See all the warns a user has.\n**"
                              f"{prefix}removewarn :**Removes a specific warn from a specific user.\n**"
                        # f"{prefix}editwarn :**Edits a specific warn from a specific user.\n**"
                              f"{prefix}addrole :**<user> <role>: Adds a role to an user.\n**"
                              f"{prefix}deleterole :**<user> <role>: deletes a role to an user.\n**"
                        , inline=False)
        # page1.add_field(name="__Hacking Tools :__",
        #                value=f"{prefix}emailinfo :** Get email information.\n**"
        #                      f"{prefix}whoisweb  :** Lookup whois domain information.\n**"
        #                      f"{prefix}exploit  :** Searches exploit-db for exploits.\n**",
        #                inline=False)

        page1.add_field(name="__For Fun :__",
                        value=f"{prefix}poll :** Makes a simple poll so you can vote either yes or no.\n**"
                        # f"{prefix}quotes  :**  Posts a random quotes.\n**"
                              f"{prefix}roast  :**  Lets GeekerBot insult someone or yourself.\n**"
                              f"{prefix}gayscanner   :**  See how gAe another user is. Shows my level of maturity too.\n**"
                              f"{prefix}ship    :**  Test love between two users.\n**"
                        # f"{prefix}8ball    :**   Consult 8ball to receive an answer.\n**"
                              f"{prefix}coffee    :**  Posts a random coffee.\n**"
                              f"{prefix}f    :**  Press F to pay respect.\n**"
                              f"{prefix}comic    :**  Random comic with pictures.\n**"
                              f"{prefix}hug    :**  hug someone.\n**"
                              f"{prefix}kiss    :**  kiss someone.\n**"
                              f"{prefix}pat    :**  pat someone.\n**"
                              f"{prefix}slap    :**  slap someone.\n**"
                              f"{prefix}cuddle    :**  cuddle with someone.\n**"
                              f"{prefix}spank    :**  spank someone.\n**"
                              f"{prefix}poke    :**  poke someone.\n**"
                        # f"{prefix}urban    :** Find the 'best' definition to your words .\n**"
                        # f"{prefix}beer    :** Give someone a beer! 🍻 .\n**"

                        , inline=False)
        page1.set_footer(text=f"Bot Created by ".join([str(self.bot.get_user(x)) for x in self.author.owners]))

        # --------------------page1------------------------------------------------------------------#
        page2 = discord.Embed(title=f"__**Help page of {self.bot.user.name}**__",
                              description="[**DISCORD**](https://discord.gg/EZN4gnk)", color=0xdeaa0c)
        page2.set_thumbnail(url=f'{self.bot.user.avatar_url}')
        page2.add_field(name="__For Fun :__",
                        value=f"{prefix}guessav    :** a someone's avatar guessing  game, if you win you will get points\n**"
                              f"{prefix}guessgeo    :** a geography guessing  game, if you win you will get points\n**"
                              f"{prefix}leaderboard/lb    :**  posts the current exp/points leaderboard in the channel\n**"
                              f"{prefix}topgames    :**  returns top 5 played games for the author\n**"
                              f"{prefix}guildtopgames    :** returns the top 5 played games for the entire guild\n**"
                              f"{prefix}bored    :** gives you suggestion what should you do when you're feeling bored\n**"
                              f"{prefix}hotcalc    :** Returns a random percent for how hot is a discord user\n**"
                              f"{prefix}reverse    :**  !poow ,ffuts esreveR Everything you type after reverse will of course, be reversed\n**"
                              f"{prefix}statuscat    :** Sends an embed with an image of a cat, portraying the status code.If no status code is given it will return a random status cat.\n**"
                              f"{prefix}gif    :** Post a gif Displays a random gif for the specified search term\n**")

        page2.add_field(name="__Utility :__", value=f"{prefix}qrcode :** Makes a QR code for you\n**"
                                                    f"{prefix}readqr :** Reads qr code from a image.\n**"
                                                    f"{prefix}avatar :** Displays a user's avatar.\n**"
                                                    f"{prefix}rhymes :** Find the best rhymes based on keyword search.\n**"
                                                    f"{prefix}memberinfo :** Displays a member's account information.\n**"
                                                    # f"{prefix}serverinfo :**  Display information about a server.`guild`: The server of which to get information for. Can be it's ID or Name. Defaults to the current server.\n**"
                                                    # f"{prefix}wiki :** search the best definition on wikipedia\n**"
                                                    f"{prefix}weather :** gets the current weather\n**"
                                                    f"{prefix}news :** gets the trending news\n**"
                                                    f"{prefix}feedback :** Give feedback to improve the bot's functionality\n**"

                        , inline=False)
        page2.set_footer(text=f"Bot Created by ".join([str(self.bot.get_user(x)) for x in self.author.owners]))

        page3 = discord.Embed(title=f"__**Help page of {self.bot.user.name}**__",
                              description="[**DISCORD**](https://discord.gg/EZN4gnk)", color=0xdeaa0c)

        page3.add_field(name="__Utility :__",
                        value=
                        # f"{prefix}printroles :** Print all the current defined roles in the server.\n**"
                        # f"{prefix}dumpmsg :** Fetch message from channel into file.\n**"
                        f"{prefix}find  : ** Finds a user within your search term.\n**"
                        f"{prefix}recipe :** searches for recipe of cooking based on search term.\n**"
                        f"{prefix}movie :** searches up for your favorite tv show / movie.\n**"
                        f"{prefix}films :** gets the film with the most star ratings.\n**"
                        f"{prefix}yt :** searches any video from youtube and plays it based on search terms.\n**"
                        # f"{prefix}ytmp3 :** converts youtube video links in .mp3 files wich it then sent to users.\n**"
                        f"{prefix}country :** search the information of country based on search term.\n**"
                        f"{prefix}eventnow :** looks up the current events.\n**"
                        f"{prefix}isitdown :** checks the status of the website based on search term.\n**"
                        f"{prefix}enmorse :** Generates morse code from a text.\n**"
                        f"{prefix}demorse :** Reads morse code.\n**"
                        , inline=False)

        page2.set_footer(text=f"Bot Created by ".join([str(self.bot.get_user(x)) for x in self.author.owners]))

        page4 = discord.Embed(title=f"__**Help page of  {self.bot.user.name}**__",
                              description="[**DISCORD**](https://discord.gg/EZN4gnk)", color=0xdeaa0c)

        page4.add_field(name="__Engineer's Tools :__",
                        value=
                        f"{prefix}convert/cvrt :** Converts from one unit to another by an optional scalar amount.\n**"
                        f"{prefix}units :** Lists the units of a certain quantity (e.g. velocity).\n**"
                        f"{prefix}const :** Gives info about a constant and prints info about a given constant or shows all known constants if you type 'show' after the command.\n**"
                        f"{prefix}parallel :** Returns the equivalent resistance of parallel elements and MUST use SI units.\n**"

                        , inline=False)

        page4.set_footer(text=f"Bot Created by ".join([str(self.bot.get_user(x)) for x in self.author.owners]))

        embeds = [
            page1, page2, page3, page4
        ]
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()

    @commands.command(aliases=['joinme', 'join', 'botinvite'])
    async def inviteme(self, ctx):
        """ Invite me to your server """
        await ctx.send(
            f"**{ctx.author.name}**, use this URL to invite me\n<https://discord.com/api/oauth2/authorize?client_id=772748636554788895&permissions=1544027255&scope=bot>")

    @commands.check(permissions.is_owner)
    @commands.command(name="help2")
    async def _help(self, ctx):
        if ctx.guild:
            prefix = self.bot.cache.prefixes.get(str(ctx.guild.id), self.bot.prefixdefault)
        else:
            prefix = self.bot.prefixdefault
        admin = ["`prefix`", "`scanname`", "`announce`", "`settings`"]
        settings = ["`whitelist`", "`automod`", "`antispam`", "`toxic`", "`antilink`", "`allowspam`", "`minaccountage`",
                    "`setguildgames`", "`setlevelingsystem`", "`autorole`", "`trigger`"]
        moderation = ["`ban`", "`unban`", "`lock`", "`kick`", "`unban`", "`mute`", "`unmute`", "`warn`", "`warns`",
                      "`removewarn`", "`addrole`", "`deleterole`", "`prune`"]
        Fun_Commands = ["`guessav`", "`guessgeo`", "`bored`", "`gif`", "`poll`", "`roast`", "`gayscanner`", "`ship`",
                        "`f`", "`coffee`", "`comic`", "`statuscat`", "`hotcalc`", "`reverse`"]
        Utility_Commands = ["`qrcode`","`readqr`","`avatar`","`memberinfo`","`serverinfo`","`wiki`","`weather`","`news`","`recipe`"
                            ,"`eventnow`","`movie`","`films`","`country`","`isitdown`","`enmorse`","`demorse`"]
        youtube_commands = ["`yt`", "`channelinfo`"]
        engineer_commands = ["`convert`", "`units`", "`const`", "`parallel`"]

        others = ["`leaderboard/lb`", "`topgames`", "`guildtopgames`", "`find`"]
        embed = discord.Embed(title=f"__**Help page of {self.bot.user.name}**__",
                              description=f"{prefix}info :** To show the Information of the bot**\n"
                                          f"{prefix}joinme : **get Geekerbot manage your server.**\n\n"
                                          "[**DISCORD**](https://discord.gg/EZN4gnk)", color=0xdeaa0c)
        embed.set_thumbnail(url=f'{self.bot.user.avatar_url}')

        embed.add_field(
            name=f"Admin ({len(admin)})",
            value=", ".join(str(x) for x in admin),
            inline=False)
        embed.add_field(
            name=f"Settings ({len(settings)})",
            value=", ".join(str(x) for x in settings),
            inline=False
        )
        embed.add_field(name=f"Moderation ({len(moderation)})",
                        value=", ".join(str(x) for x in moderation),
                        inline=False)
        embed.add_field(name=f"Fun Commands ({len(Fun_Commands)})",
                        value=", ".join(str(x) for x in Fun_Commands),
                        inline=False)
        embed.add_field(name=f"Utility Commands ({len(Utility_Commands)})",
                        value=", ".join(str(x) for x in Utility_Commands),
                        inline=False)
        embed.add_field(name=f"Engineer's Commands ({len(engineer_commands)})",
                        value=", ".join(str(x) for x in engineer_commands),
                        inline=False)
        embed.add_field(name=f"Youtube commands ({len(youtube_commands)})",
                        value=", ".join(str(x) for x in youtube_commands),
                        inline=False)
        embed.add_field(name=f"Other commands ({len(others)})",
                        value=", ".join(str(x) for x in others),
                        inline=False)
        embed.set_footer(text=f"{prefix}feedback to give us feedbacks and compliments")

        await ctx.send(embed=embed)


def setup(bot):
    bot.remove_command("help")
    bot.add_cog(HelpCog(bot))
