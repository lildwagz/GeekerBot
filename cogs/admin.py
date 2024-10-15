import asyncio
import collections
import random
import re

import aiohttp
import discord
import yarl
from better_profanity import profanity

from discord.ext import commands
from discord.ext.commands import CheckFailure

from utils import permissions, default,  utilss
from utils.utilss import send_error_message

EMOJI_REGEX = re.compile(r'<a?:.+?:([0-9]{15,21})>')
EMOJI_NAME_REGEX = re.compile(r'[0-9a-zA-Z\_]{2,32}')


def emoji_name(argument, *, regex=EMOJI_NAME_REGEX):
    m = regex.match(argument)
    if m is None:
        raise commands.BadArgument('Invalid emoji name.')
    return argument


class EmojiURL:
    def __init__(self, *, animated, url):
        self.url = url
        self.animated = animated

    @classmethod
    async def convert(cls, ctx, argument):
        try:
            partial = await commands.PartialEmojiConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                url = yarl.URL(argument)
                if url.scheme not in ('http', 'https'):
                    raise RuntimeError
                path = url.path.lower()
                if not path.endswith(('.png', '.jpeg', '.jpg', '.gif')):
                    raise RuntimeError
                return cls(animated=url.path.endswith('.gif'), url=url)
            except Exception:
                raise commands.BadArgument('Not a valid or supported emoji URL.') from None
        else:
            return cls(animated=partial.animated, url=str(partial.url))


class Admin(commands.Cog, name="admin"):
    def __init__(self, bot):
        self.conf = {}
        self.bot = bot
        self.config = default.get("config.json")
        self._last_result = None
        self.conf["LEVEL_IMAGES"] = {}

    @commands.command(name="announce", pass_context=True, aliases=["announcement"])
    @commands.has_permissions(administrator=True)
    async def announce(self, ctx, channel: discord.TextChannel, *, message):
        try:

            await channel.send(message)
            await ctx.send(f'{ctx.message.author.mention} Announcement Have Been Sent! :white_check_mark: ')
        except Exception as e:
            await ctx.send(f'{ctx.message.author.mention} Failed Sending Announcement! :x: ')
            # await ctx.send

    @announce.error
    async def announce_error(self, ctx, exc):
        pass

    # @commands.guild_only()
    # @commands.command(aliases=['na', 'nicknameall'])
    # @commands.has_permissions(manage_guild=True)
    # async def nickall(self, ctx, *, args=None):
    #     # print(f"{ctx.guild.name} - #{ctx.channel.name} - {ctx.author.name} - {ctx.message.content}")
    #     if not ctx.author.guild_permissions.administrator:
    #         await ctx.send("You do not have the permissions to use this command.")
    #         return
    #     if len(ctx.guild.members) > 50:
    #         await ctx.send("Nickall cannot be used on guilds with over 50 members.")
    #         return
    #     if not args:
    #         msg = await ctx.send(f"Resetting all nicks... (This may take a while)")
    #     else:
    #         if len(args) < 2:
    #             await ctx.send("That nickname is too short. It must be 2 characters or more.")
    #             return
    #         if len(args) > 32:
    #             await ctx.send("That nickname is too long. It must be 32 characters or less.")
    #             return
    #         msg = await ctx.send(f"Nicknaming everyone to {args}... (This may take a while)")
    #     for p in ctx.guild.members:
    #         try:
    #             await p.edit(nick=args)
    #         except Exception as e:
    #             ctx.send(f"An exception occurred : {e}")
    #             pass
    #     if args:
    #         await msg.edit(content=f"All members were nicknamed {args}.")
    #     else:
    #         await msg.edit(content=f"All nicks were reset.")

    # @nickall.error
    # async def nickall_error(self, ctx, error):
    #     if isinstance(error, CheckFailure):
    #         await ctx.send("You need the Administrator permission to do that.")
    #     else:
    #         await ctx.send("Please follow format: `nickall {name}`")

    @commands.guild_only()
    # @commands.has_permissions(manage_guild=True)
    @commands.check(permissions.is_owner)
    @commands.cooldown(rate=1, per=820.0, type=commands.BucketType.user)
    @commands.command(name="scanname")
    async def scanname(self, ctx):
        Titles = ['Lovely', 'Adorable', 'Cute', 'Friendly', 'Aesthetic', 'Gorgeous', 'Attractive', 'Beautiful']
        nameList = ['Cool Dude', 'Squirrel', 'Panda', 'Lion', 'Cat', 'Hamster', 'Frog', 'Puppy', 'Turtle']

        message = await ctx.send(
            "scan all member username in database, we limit only 5 members to change their username automatically in one scan time to avoid abuse of Discord API...")
        counter = 0
        for member in ctx.guild.members:
            if profanity.contains_profanity(member.display_name) or profanity.contains_profanity(member.name):
                try:

                    await member.edit(nick=f'{random.choice(Titles)} {random.choice(nameList)}')
                    counter = counter + 1
                    if counter == 5:
                        return await ctx.send(
                            "oops already changed 5 member's nickname, try again later when its off coldown!")
                except discord.errors.Forbidden as e:
                    return await ctx.send(
                        f"`error: I'm missing required discord permission [manage nicknames or change nickname] \n` or the member has higher role than me"

                    )
                except Exception as e:
                    pass
                try:
                    embed = discord.Embed(title=f"Hello **{member}**!",
                                          description="We've noticed that your nickname didn't comply with our **ToS** so we decided to rename you automatically.",
                                          color=0x0fa7d0)
                    embed.set_thumbnail(url=member.avatar_url)
                    embed.set_footer(text='if you think this was a mistake please let us know')
                    await ctx.send(embed=embed)
                except Exception as e:
                    ctx.send(f"An exception occurred while sending the member the notice message: {e}")
                    continue
        await message.edit(content="Not found")

    @scanname.error
    async def scanname_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            return await utilss.send_error_message(ctx, "At this time, this command is disabled. Since there are a "
                                                        "lot of changes that need to "
                                                        "be done, we expect the scanname command to be back by this week. ")

    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.command(aliases=["sgg"])
    async def setguildgames(self, ctx, status: bool):
        """Enable or disable guild games"""
        if ctx.guild.member_count > 1000:
            return await send_error_message(ctx,
                                            'currently I cannot run guildgames in server with more 1000 members :(')
        self.bot.cache.guildgame_toogle[str(ctx.guild.id)] = status
        self.bot.app.send_task('celerys.worker.set_guildtoogle',
                               kwargs={'guildid': ctx.guild.id, 'toogle': bool(status)})
        if status:
            await utilss.toogle_enable(ctx, "guildgames was enabled.")

        else:
            await utilss.toogle_disable(ctx, "guildgames was disabled")

    @setguildgames.error
    async def setguildgames_error(self, ctx, exc):
        pass
        # if isinstance(exc, CheckFailure):
        #     await ctx.send("You need the manage server permission to do that.")

    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.command(aliases=["sls"])
    async def setlevelingsystem(self, ctx, status: bool):
        """Enable or disable level up messages system"""
        self.bot.cache.levelsystem_toogle[str(ctx.guild.id)] = status
        self.bot.app.send_task('celerys.worker.set_leveltoogle',
                               kwargs={'guildid': ctx.guild.id, 'toogle': bool(status)})
        if status:
            await utilss.toogle_enable(ctx, "level up messages system was enabled.")

        else:
            await utilss.toogle_disable(ctx, "level up messages system was disabled")

    @commands.guild_only()
    @commands.command(name='antispam', aliases=["spam"])
    @commands.check(permissions.is_owner)
    # @commands.has_permissions(manage_guild=True)
    async def antispam(self, ctx, status: bool):

        self.bot.cache.antiSpam_toogle[str(ctx.guild.id)] = status
        self.bot.app.send_task('celerys.worker.set_antispamtoogle',
                               kwargs={'guildid': ctx.guild.id, 'toogle': bool(status)})
        if status:
            await utilss.toogle_enable(ctx, "anti spam was enabled.")

        else:
            await utilss.toogle_disable(ctx, "anti spam was disabled")

    @commands.guild_only()
    @commands.command(name='allowspam', aliases=["aspam"])
    @commands.has_permissions(manage_guild=True)
    async def allowspam(self, ctx, channel, remove="False"):

        channel = channel.replace("<", "")
        channel = channel.replace("#", "")
        channel = channel.replace(">", "")
        guildid = ctx.guild.id
        chache = self.bot.cache.allowspam[str(guildid)]
        if remove == "False":
            try:
                channel = int(channel)
                spamChannel = self.bot.get_channel(channel)

                if spamChannel.id == chache:
                    embed = discord.Embed(title=f"**ERROR**",
                                          description=f"The channel where you want to allow to spam is already "
                                                      f"ignored by anti spam.",
                                          color=0xe00000)
                    return await ctx.channel.send(embed=embed)

                await utilss.toogle_enable(ctx, f"The <#{spamChannel.id}> channel is ignored by the anti spam..")

                self.bot.cache.allowspam[str(guildid)] = spamChannel.id
                self.bot.app.send_task('celerys.worker.set_spamchannel',
                                       kwargs={'guildid': guildid, 'channel': spamChannel.id})
            except:
                embed = discord.Embed(title=f"**ERROR**",
                                      description=f"The channel where you want to allow to spam must be a "
                                                  f"number\nFollow the example : ``{self.bot.cache.prefixes.get(str(guildid))}allowspam "
                                                  f"<#channel>``",
                                      color=0xe00000)  # Red
                return await ctx.channel.send(embed=embed)
        else:
            try:
                channel = int(channel)
                spamChannel = self.bot.get_channel(channel)
                if not spamChannel.id == chache:
                    embed = discord.Embed(title=f"**ERROR**",
                                          description=f"The channel where you want to disable the spam is already "
                                                      f"disabled.",
                                          color=0xe00000)  # Red
                    return await ctx.channel.send(embed=embed)

                await utilss.toogle_enable(ctx, f"The <#{spamChannel.id}> channel is deleted by the anti spam list..")
                self.bot.cache.allowspam[str(guildid)] = 0
                self.bot.app.send_task('celerys.worker.set_spamchannel', kwargs={'guildid': guildid, 'channel': 0})



            except:
                embed = discord.Embed(title=f"**ERROR**",
                                      description=f"The channel where you want to disable the spam must be a number\nFollow the example : ``{self.bot.command_prefix}allowspam <#channel> remove``",
                                      color=0xe00000)  # Red
                return await ctx.channel.send(embed=embed)

    @commands.guild_only()
    @commands.command(name='anttoxic', aliases=["toxic"])
    @commands.has_permissions(manage_guild=True)
    async def antitoxic(self, ctx, status: bool):

        self.bot.cache.antitoxic_toogle[str(ctx.guild.id)] = status
        self.bot.app.send_task('celerys.worker.set_antitoxictoogle',
                               kwargs={'guildid': ctx.guild.id, 'toogle': bool(status)})
        if status:
            await utilss.toogle_enable(ctx, "anti toxic was enabled.")

        else:
            await utilss.toogle_disable(ctx, "anti toxic was disabled")

    @commands.guild_only()
    @commands.command(name='antilink', aliases=["link"])
    @commands.has_permissions(manage_guild=True)
    async def antilink(self, ctx, status: bool):

        self.bot.cache.antiLinks_toogle[str(ctx.guild.id)] = status
        self.bot.app.send_task('celerys.worker.set_antilinkstoogle',
                               kwargs={'guildid': ctx.guild.id, 'toogle': bool(status)})
        if status:
            await utilss.toogle_enable(ctx, "anti links was enabled.")

        else:
            await utilss.toogle_disable(ctx, "anti links was disabled")

    @commands.guild_only()
    @commands.command(name='minaccountage',
                      aliases=["minage", "agarequired", "age"],
                      usage="<numberInHour/false>")
    @commands.has_permissions(manage_guild=True)
    async def minaccountage(self, ctx, accountAge):
        """
        Update or disable the minimal account age to join the server.
        :param ctx:
        :param accountAge:
        :return:
        """
        guildid = ctx.guild.id
        accountAge = accountAge.lower()
        if accountAge == "false":
            self.bot.cache.ageaccount_toggle[str(guildid)] = False
            self.bot.app.send_task('celerys.worker.ageaccount_toggle',
                                   kwargs={'guildid': guildid, 'toogle': bool(False)})
            await utilss.toogle_disable(ctx, "minimal account age to join the server was disabled")
        else:
            try:
                accountAge = int(accountAge)
                # hour to second
                accountAge = accountAge * 3600
                self.bot.cache.ageaccount[str(guildid)] = accountAge
                self.bot.cache.ageaccount_toggle[str(guildid)] = True
                self.bot.app.send_task('celerys.worker.ageaccount_toggle',
                                       kwargs={'guildid': guildid, 'toogle': bool(True)})
                self.bot.app.send_task('celerys.worker.set_housminage',
                                       kwargs={'guildid': ctx.guild.id, 'hours': accountAge})

                await utilss.toogle_enable(ctx, "the minimal account age to join the server was updated.")

            except:

                return await utilss.send_error_message(ctx,
                                                       f"The minimum account age must be a number (default = 24 hours)\nFollow the example : ``{self.bot.cache.prefixes.get(str(guildid))}minaccountage <number (hours)>``")

    @commands.guild_only()
    @commands.command(name="setwelcome")
    @commands.has_permissions(manage_guild=True)
    async def imgwelcome_toggle(self, ctx, status: bool):
        """Toggle on/off the imgwelcome"""
        self.bot.cache.imgwelcome_toggle[(str(ctx.guild.id))] = status
        if status:
            await utilss.toogle_enable(ctx, "Welcome image is now enabled")
            # edit_settings_img.delay(ctx.guild.id, 1)
        else:
            await utilss.toogle_enable(ctx, "Welcome image is now disabled")
            # edit_settings_img.delay(ctx.guild.id, 0)

    @commands.guild_only()
    @commands.command(name="automod")
    @commands.has_permissions(manage_guild=True)
    async def automod_toggle(self, ctx, status: bool):
        """Toggle on/off the auto moderation"""

        self.bot.cache.antitoxic_toogle[(str(ctx.guild.id))] = status
        self.bot.cache.automod_toogle[(str(ctx.guild.id))] = status
        self.bot.cache.antiLinks_toogle[(str(ctx.guild.id))] = status
        self.bot.cache.antiSpam_toogle[(str(ctx.guild.id))] = status
        if status:
            await utilss.toogle_enable(ctx, "Auto Moderation  is now enabled")
            # edit_settings_img.delay(ctx.guild.id, 1)
        else:
            await utilss.toogle_disable(ctx, "Auto Moderation is now disabled")
            # edit_settings_img.delay(ctx.guild.id, 0)

    # @commands.check(permissions.is_owner)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.group(name="autorole", aliases=["atr"])
    async def autorole(self, ctx):
        """
        enable auto role to auto add role when new member joins
        :param ctx:
        :param role:
        :return:
        """
        prefix = self.bot.cache.prefixes.get(str(ctx.guild.id))
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title=f"**{prefix}autorole**", colour=0xdeaa0c)

            embed.add_field(name="__Commands :__",
                            value=f"{prefix}autorole add :** To add auto role. \n**"
                                  f"{prefix}autorole del :**  To remove auto role.\n**",
                            inline=False)
            await ctx.send(content=f"", embed=embed)

    @autorole.command(name="add")
    async def autoroleadd(self, ctx, role: discord.Role):
        guildid = ctx.guild.id
        try:

            self.bot.cache.autorole[str(guildid)] = role.id
            self.bot.app.send_task('celerys.worker.set_autorole', kwargs={'guildid': guildid, 'roleid': role.id})
            await utilss.toogle_enable(ctx, f"new role {role.name}  is added to auto role system"
                                       )
        except:
            await utilss.toogle_disable(ctx, f"failed adding new role {role.name} into auto role system"
                                        )

    @autorole.command(name="del")
    async def autoroledel(self, ctx, role: discord.role):
        guildid = ctx.guild.id
        try:
            self.bot.cache.autorole[str(guildid)] = 0
            self.bot.app.send_task('celerys.worker.set_autorole', kwargs={'guildid': guildid, 'roleid': role.id})
            await utilss.toogle_enable(ctx, f"successfully deleted role {role.name}  from auto role system"
                                       )
        except:
            await utilss.toogle_disable(ctx, f"failed deleting role {role.name} from auto role system"
                                        )

    @autorole.error
    async def autoroleerror(self, ctx, exc):
        pass

    async def triggered_error(self, ctx):
        prefix = self.bot.cache.prefixes.get(str(ctx.guild.id))
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title=f"**{prefix}trigger/trig**", colour=0xdeaa0c)

            embed.add_field(name="__Commands :__",
                            value=f"{prefix}trigger word <false/word>  <role> [channel] :** gives a role to a user when "
                                  f"the triggered word is called\n** "
                                  f"{prefix}trigger role <false/new role>  <old role> **replaces the old role with the new "
                                  f"role whenever it's added*\n** "
                            ,
                            inline=False)
            await ctx.send(content=f"", embed=embed)

    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.group(name="trigger", aliases=["trig"])
    async def triggered_word_role(self, ctx):
        """
        Add/customize your triggered word role
        :param ctx:
        :return:
        """
        await self.triggered_error(ctx)

    @triggered_word_role.command(name="word")
    async def t_word_command(self, ctx, word: str = None, role: discord.Role = None,
                             channel: discord.TextChannel = None):
        guildid = ctx.guild.id
        if channel is None:
            channel = 0
        else:
            channel = channel.id
        if word is None:
            return await self.triggered_error(ctx)

        tostring = word.lower()
        if tostring == "false" or tostring == "disable":
            try:
                self.bot.cache.trigerword_toogle[str(guildid)] = 0
                self.bot.app.send_task('celerys.worker.set_triggerwordtoogle',
                                       kwargs={'guildid': guildid, 'toogle': bool(False)})
                await utilss.toogle_disable(ctx, f"triggered word was disabled")
            except Exception as e:
                await utilss.send_error_message(ctx, f"failed adding word `{word}`"
                                                )
        else:
            try:
                self.bot.cache.trigerword_toogle[str(guildid)] = 1
                self.bot.cache.triger_word[str(guildid)] = [word, role.id, channel]
                self.bot.app.send_task('celerys.worker.set_triggerwordtoogle',
                                       kwargs={'guildid': guildid, 'toogle': bool(True)})
                self.bot.app.send_task('celerys.worker.set_triggerword',
                                       kwargs={'guildid': guildid, 'roleid': role.id, 'channel': channel, 'word': word})
                await utilss.toogle_enable(ctx, f"successfully adding word `{word}` with response {role.mention}")
            except Exception as e:
                await utilss.send_error_message(ctx, f"failed adding word `{word}`"
                                                )
                # await ctx.send(f"'{e}'")

    @triggered_word_role.command(name="role")
    async def t_role_command(self, ctx, Newrole, Oldrole: discord.Role = None):
        """"""
        if Newrole is None:
            return await self.triggered_error(ctx)

        if Newrole.lower() == "false" or Newrole.lower() == "disable":
            try:
                self.bot.cache.trigerrole_toogle[str(ctx.guild.id)] = 0
                self.bot.app.send_task('celerys.worker.set_triggerroletoogle',
                                       kwargs={'guildid': ctx.guild.id, 'toogle': bool(False)})
                await utilss.toogle_disable(ctx, f"triggered word was disabled")
            except Exception as e:
                await utilss.send_error_message(ctx, f"failed adding role `{Newrole}`"
                                                )
        else:
            Newrole = Newrole.replace("<", "")
            Newrole = Newrole.replace("@&", "")
            Newrole = Newrole.replace(">", "")
            getrole = discord.utils.get(ctx.guild.roles, id=int(Newrole))
            return await self.send_role(ctx, getrole, Oldrole)

    @triggered_word_role.error
    async def triggerederror(self, ctx, exc):
        pass
        # if isinstance(exc, CheckFailure):
        #     await ctx.send("You need the Manage Server permission to do that.")

    async def send_role(self, ctx, Newrole, Oldrole: discord.Role):
        guildid = ctx.guild.id

        try:
            self.bot.cache.trigerrole_toogle[str(guildid)] = 1
            self.bot.cache.triger_role[str(guildid)] = [Newrole.id, Oldrole.id]
            self.bot.app.send_task('celerys.worker.set_triggerroletoogle',
                                   kwargs={'guildid': guildid, 'toogle': bool(True)})
            self.bot.app.send_task('celerys.worker.set_triggerrole',
                                   kwargs={'guildid': guildid, 'newrole': Newrole.id, 'oldrole': Oldrole.id})
            await utilss.toogle_enable(ctx,
                                       f"successfully adding role {Newrole.mention} with response {Oldrole.mention}")
        except Exception as e:
            await utilss.send_error_message(ctx, f"failed adding role `{Newrole.mention}`")

    @commands.group(name='emoji')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def _emoji(self, ctx):
        """Emoji management commands."""
        if ctx.subcommand_passed is None:
            prefix = self.bot.cache.prefixes.get(str(ctx.guild.id))
            embed = discord.Embed(title=f"**{prefix}emoji**", colour=0xdeaa0c)
            embed.add_field(name="__Commands :__",
                            value=f"{prefix}emoji add :** Create a custom emoji for the server under the given name. \n**",
                            inline=False)
            await ctx.send(content=f"", embed=embed)

    @_emoji.command(name='add', usage="<name> <url gif,png,jpeg,jpg>")
    async def _emoji_add(self, ctx, name: emoji_name, *, emoji: EmojiURL):
        """Create a custom emoji for the server under the given name.
        """
        if not ctx.me.guild_permissions.manage_emojis:
            return await ctx.send(f"`error: I'm missing required discord permission [ manage emojis ]`")

        reason = f'added by {ctx.author} (ID: {ctx.author.id})'

        emoji_count = sum(e.animated == emoji.animated for e in ctx.guild.emojis)
        if emoji_count >= ctx.guild.emoji_limit:
            return await utilss.send_error_message(ctx,'Oops... no more emoji slots in this server.')

        async with aiohttp.ClientSession().get(emoji.url) as resp:
            if resp.status >= 400:
                return await utilss.send_error_message(ctx,'Opps... could not fetch the image.')
            if int(resp.headers['Content-Length']) >= (256 * 1024):
                return await utilss.send_error_message(ctx,'Opps... image is too big.')
            data = await resp.read()
            coro = ctx.guild.create_custom_emoji(name=name, image=data, reason=reason)
            async with ctx.typing():
                try:
                    created = await asyncio.wait_for(coro, timeout=10.0)
                except asyncio.TimeoutError:
                    return await utilss.send_error_message(ctx,'Sorry, the bot took too long to proceed.')
                except discord.HTTPException as e:
                    return await utilss.send_error_message(ctx,f'Failed to create emoji: {e}')
                else:
                    return await utilss.send_success(ctx,f'successfully added emoji {name} {created}')

    async def say_permissions(self, ctx, member, channel):
        permissions = channel.permissions_for(member)
        e = discord.Embed(colour=member.colour)
        avatar = member.avatar_url_as(static_format='png')
        e.set_author(name=str(member), url=avatar)
        allowed, denied = [], []
        for name, value in permissions:
            name = name.replace('_', ' ').replace('guild', 'server').title()
            if value:
                allowed.append(name)
            else:
                denied.append(name)

        e.add_field(name='Allowed', value='\n'.join(allowed))
        e.add_field(name='Denied', value='\n'.join(denied))
        await ctx.send(embed=e)


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def botpermissions(self, ctx, *, channel: discord.TextChannel = None):
        """Shows the bot's permissions in a specific channel.

        If no channel is given then it uses the current one.

        This is a good way of checking if the bot has the permissions needed
        to execute the commands it wants to execute.

        To execute this command you must have Manage Roles permission.
        You cannot use this in private messages.
        """
        channel = channel or ctx.channel
        member = ctx.guild.me
        await self.say_permissions(ctx, member, channel)

    @commands.guild_only()
    # @commands.has_permissions(Administrator=True)
    @commands.check(permissions.is_owner)
    @commands.command(name='server', aliases=['serverinfo'])
    async def server(self, ctx, *, guild: int = None) -> None:
        """
        Display information about a server.
        `guild`: The server of which to get information for. Can be it's ID or Name. Defaults to the current server.
        """

        if not guild:
            guild = ctx.guild
        else:
            guild = self.bot.get_guild(guild)
        region = guild.region.name.title().replace('Vip', 'VIP').replace('_', '-').replace('Us-', 'US-')
        if guild.region == discord.VoiceRegion.hongkong:
            region = 'Hong Kong'
        if guild.region == discord.VoiceRegion.southafrica:
            region = 'South Africa'

        statuses = collections.Counter([member.status for member in guild.members])

        features = []
        for feature, description in self.bot.utils.features.items():
            if feature in guild.features:
                features.append(f':white_check_mark: {description}')
            else:
                features.append(f':x: {description}')

        embed = discord.Embed(colour=ctx.guild.me.roles[::-1][0].color, title=f'`{guild.name}`\'s information.')
        embed.description = f'`Owner:` {guild.owner}\n' \
                            f'`Created on:` {self.bot.utils.format_datetime(datetime=guild.created_at)}\n' \
                            f'`Created:` {self.bot.utils.format_difference(datetime=guild.created_at)} ago\n' \
                            f'`Members:` {guild.member_count} | ' \
                            f'<:online:804933653464875008>{statuses[discord.Status.online]} | <:away:808445189781061634>{statuses[discord.Status.idle]} | ' \
                            f'<:dnd:808447780900962325>{statuses[discord.Status.dnd]} | <:offline:808448417835647006>{statuses[discord.Status.offline]}\n' \
                            f'`Content filter level:` {self.bot.utils.content_filter_levels[ctx.guild.explicit_content_filter]} | ' \
                            f'`2FA:` {self.bot.utils.mfa_levels[ctx.guild.mfa_level]}\n' \
                            f'`Verification level:` {self.bot.utils.verification_levels[ctx.guild.verification_level]}\n'

        embed.add_field(name='Boost information:',
                        value=f'`Nitro Tier:` {ctx.guild.premium_tier} | `Boosters:` {ctx.guild.premium_subscription_count} | '
                              f'`File Size:` {round(ctx.guild.filesize_limit / 1048576)} MB | `Bitrate:` {round(ctx.guild.bitrate_limit / 1000)} kbps\n'
                              f'`Emoji limit:` {ctx.guild.emoji_limit} | `Normal emoji:` {sum([1 for emoji in guild.emojis if not emoji.animated])} | '
                              f'`Animated emoji:` {sum([1 for emoji in guild.emojis if emoji.animated])}')

        embed.add_field(name='Channels:',
                        value=f'`AFK timeout:` {int(ctx.guild.afk_timeout / 60)}m | `AFK channel:` {ctx.guild.afk_channel}\n `Voice region:` {region} | '
                              f'`Text channels:` {len(ctx.guild.text_channels)} | `Voice channels:` {len(ctx.guild.voice_channels)}\n',

                        inline=False)

        embed.add_field(name='Features:', value='\n'.join(features[0:8]))
        embed.add_field(name='\u200b', value='\n'.join(features[8:16]))
        embed.set_footer(text=f'ID: {guild.id} | Owner ID: {guild.owner.id}')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Admin(bot))
