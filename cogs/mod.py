import discord
import re
import asyncio

from discord.ext import commands


from utils import permissions, default, utilss
from utils.utilss import send_error_message


class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
            except AttributeError :
                raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
        else:
            return m.id


class ActionReason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = argument

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
        return ret


class Mod(commands.Cog):
    """Moderation commands"""
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        """ Kicks a user from the current server. """
        if await permissions.check_priv(ctx, member):
            return
        if member.top_role.position >= ctx.author.top_role.position :
            return await ctx.send(
                "`user has a higher  role than you or same role inside the guild/server.`"
            )
        if ctx.guild.me.top_role.position <= member.top_role.position:
            return await ctx.send(
                "` user has a higher role than me inside the guild/server.`"
            )

        try:
            await member.kick(reason=default.responsible(ctx.author, reason))
            await utilss.success_actionmessage(ctx,"kicked")

        except discord.errors.Forbidden as e:
            return await ctx.send(
                "`error: I'm missing required discord permission [ kick members ]`"
            )

    # @kick.error
    # async def error_kick(self,ctx, error):
    #     if isinstance(error, commands.MissingPermissions):
    #         await ctx.send("You need the **kick members** permission")
    #         return


    @commands.command(aliases=["nick"])
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: discord.Member, *, name: str = None):
        """ Nicknames a user from the current server. """
        if await permissions.check_priv(ctx, member):
            return

        try:
            await member.edit(nick=name, reason=default.responsible(ctx.author, "Changed by command"))
            message = f"Changed **{member.name}'s** nickname to **{name}**"
            if name is None:
                message = f"Reset **{member.name}'s** nickname"
            await ctx.send(message)
        except discord.errors.Forbidden as e:
            return await ctx.send(
                "`error: I'm missing required discord permission [ change nickname ]`"
            )

    # @nickname.error
    # async def error_nickname(self, ctx, err):
    #     if isinstance(err, commands.MissingPermissions):
    #         await ctx.send("You need the **change nickname** permission")
    #         return

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: MemberID, *, reason: str = None):
        """ Bans a user from the current server. """


        m = ctx.guild.get_member(member)
        if m is None:
            return await ctx.send("is not a valid member or member ID.")
        if m.top_role.position >= ctx.author.top_role.position :
            return await ctx.send(
                "`user has a higher  role than you or same role inside the guild/server.`"
            )
        if ctx.guild.me.top_role.position <= m.top_role.position:
            return await ctx.send(
                "` user has a higher role than me or same role inside the guild/server.`"
            )
        if m is not None and await permissions.check_priv(ctx, m):
            return

        try:
            await ctx.guild.ban(discord.Object(id=member), reason=default.responsible(ctx.author, reason))
            await utilss.success_actionmessage(ctx,"banned")

        except discord.errors.Forbidden as e:
            return await ctx.send(
                "`error: I'm missing required discord permission [ ban members ]`"
            )

    # @ban.error
    # async def error_ban(self, ctx, err):
    #     if isinstance(err, commands.MissingPermissions):
    #         await ctx.send("You need the **ban members** permission")
    #         return
    # @commands.command()
    # @commands.guild_only()
    # @commands.max_concurrency(1, per=commands.BucketType.user)
    # @commands.has_permissions(ban_members=True)
    # async def massban(self, ctx, reason: ActionReason, *members: MemberID):
    #     """ Mass bans multiple members from the server. """
    #     try:
    #         for member_id in members:
    #             await ctx.guild.ban(discord.Object(id=member_id), reason=default.responsible(ctx.author, reason))
    #         await utilss.success_actionmessage(ctx,"massbanned",mass=True)
    #
    #     except discord.errors.Forbidden as e:
    #         return await ctx.send(
    #             "`error: I'm missing required discord permission [ ban members ]`"
    #         )

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: MemberID, *, reason: str = None):
        """ Unbans a user from the current server. """

        # m = ctx.guild.get_member(member)
        try:
            await ctx.guild.unban(discord.Object(id=member), reason=default.responsible(ctx.author, reason))
            await utilss.success_actionmessage(ctx,"unbanned")
        except discord.errors.Forbidden as e:
            return await ctx.send(
                "`error: I'm missing required discord permission [ ban members ]`"
            )
        except discord.NotFound:
            return await ctx.send(
                "`error: NOT FOUND!`"
            )

    # @unban.error
    # async def error_unban(self, ctx, err):
    #     if isinstance(err, commands.MissingPermissions):
    #         await ctx.send("You need the **ban members** permission")
    #         return

    @commands.command(name="mute",
                      usage="<member> <minutes> [reasons]")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member,
                   mute_minutes: int,
                   *, reason: str =None):
        """ Mutes a user from the current server.
         Usage :
         mute @user 1 nothing"""
        if member.top_role.position >= ctx.author.top_role.position :
            return await ctx.send(
                "`user has a higher role than you or same role inside the guild/server.`"
            )
        if ctx.guild.me.top_role.position <= member.top_role.position:
            return await ctx.send(
                "` user has a higher role than me or same role inside the guild/server.`"
            )
        if await permissions.check_priv(ctx, member):
            return


        muted_role = next((g for g in ctx.guild.roles if g.name == "Muted"), None)

        if not muted_role:
            # return await ctx.send(
            #     "Are you sure you've made a role called **Muted**? Remember that it's case sensetive too...")
            try:
                muted_role = await ctx.guild.create_role(name="Muted", reason="To use for muting")
                for channel in ctx.guild.channels:  # removes permission to view and send in the channels
                    await channel.set_permissions(muted_role, send_messages=False,
                                                  read_message_history=False,
                                                  read_messages=True)
            except discord.errors.Forbidden as e:
                return await ctx.send(
                    "`error: I'm missing required discord permission [ manage roles ]` "
                )

        try:
            await member.add_roles(muted_role, reason=reason)
            await utilss.send_success(ctx,
                                      "{0.mention} has been muted by {1.mention} for *{2}*".format(member, ctx.author,
                                                                                                   reason)
                                )

            embed = discord.Embed(title="time's up", description=f"{member} has been relieved from  jail",
                                  color=0x00ff00)
            if mute_minutes > 0:
                await asyncio.sleep(mute_minutes * 60)
                await member.remove_roles(muted_role, reason="time's up ")

            loading = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await loading.delete()
        except Exception as e:
            await ctx.send(e)

    # @mute.error
    # async def error_mute(self, ctx, err):
    #     if isinstance(err, commands.MissingPermissions):
    #         await ctx.send("You need the ** manage roles** permission")
    #         return
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = None):
        """ Unmutes a user from the current server. """
        if member.top_role.position >= ctx.author.top_role.position :
            return await ctx.send(
                "`user has a higher  role than you or same role inside the guild/server.`"
            )
        if ctx.guild.me.top_role.position <= member.top_role.position:
            return await ctx.send(
                "` user has a higher role than me or same role inside the guild/server.`"
            )
        if await permissions.check_priv(ctx, member):
            return

        muted_role = next((g for g in ctx.guild.roles if g.name == "Muted"), None)

        if not muted_role:
            return await ctx.send("Are you sure you've made a role called **Muted**? Remember that it's case "
                                  "sensetive too...")

        try:
            await member.remove_roles(muted_role, reason=default.responsible(ctx.author, reason))
            await utilss.send_success(ctx, "{0.mention} has been unmuted by {1.mention}*".format(member, ctx.author))
        except discord.errors.Forbidden as e:
            return await ctx.send(
                "`error: I'm missing required discord permission [ manage roles ]` "
            )

    # @unmute.error
    # async def error_unmute(self, ctx, err):
    #     if isinstance(err, commands.MissingPermissions):
    #         await ctx.send("You need the ** manage roles** permission")
    #         return

    @commands.command(name="addrole", pass_context=True)
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member,
                      roleName: discord.Role):
        """<user> <role>: Add a role to an user."""
        # added_role = next((g for g in ctx.guild.roles if g.name == roleName), None)
        # added_role = get(ctx.guild.roles, name=roleName)
        # print(roleName)
        if ctx.guild.me.top_role.position <= roleName.position:
            return await ctx.send(
                "`the role is higher than me or same role inside the guild/server.`"
            )
        if ctx.author.top_role.position <= roleName.position:
            return await ctx.send(
                "`the role is higher than you or same role inside the guild/server.`"
            )


        if ctx.guild.me.top_role.position <= member.top_role.position:
            return await ctx.send(
                "` the member has a higher role than me or same role inside the guild/server.`"
            )

        try:
            await member.add_roles(roleName, reason="None")
            await utilss.send_success(ctx, "{0.mention} has been added role {1.mention} by {2.mention}".format(member,roleName, ctx.author))

        except discord.errors.Forbidden as e:
            return await ctx.send(
                    "`error: I'm missing required discord permission [ manage roles ]`"
                )
    #
    # @addrole.error
    # async def error_addrole(self, ctx, err):
    #     if isinstance(err, commands.MissingPermissions):
    #         await ctx.send("You need the ** manage roles** permission")
    #         return
    @commands.command(name="deleterole", pass_context=True)
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def deleterole(self, ctx, member: discord.Member,
                      roleName: discord.Role):
        """<user> <role>: deletes a role to an user."""
        # added_role = next((g for g in ctx.guild.roles if g.name == roleName), None)
        # added_role = get(ctx.guild.roles, name=roleName)
        if ctx.guild.me.top_role.position <= roleName.position:
            return await ctx.send(
                "`the role is higher than me or same role inside the guild/server.`"
            )

        if member.top_role.position >= ctx.author.top_role.position:
            return await ctx.send(
                "`user has a higher  role than you or same role inside the guild/server.`"
            )
        if ctx.guild.me.top_role.position <= member.top_role.position:
            return await ctx.send(
                "` user has a higher role than me or same role inside the guild/server.`"
            )
        try:
            await member.remove_roles(roleName, reason="None")
            await utilss.send_success(ctx, "{0.mention} has been deleleted role {1.mention} by {2.mention}".format(member,roleName, ctx.author))

        except discord.errors.Forbidden as e:
            return await ctx.send(
                "`error: I'm missing required discord permission [ manage roles ]` "
            )

    # @deleterole.error
    # async def error_deleterole(self, ctx, err):
    #     if isinstance(err, commands.MissingPermissions):
    #         await ctx.send("You need the ** manage roles** permission")
    #         return


    @commands.command(aliases=["ar"])
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def announcerole(self, ctx, *, role: discord.Role):
        """ Makes a role mentionable and auto remove when gets mentioned"""
        if role == ctx.guild.default_role:
            return await ctx.send("To prevent abuse, I won't allow mentionable role for everyone/here role.")

        if ctx.author.top_role.position <= role.position:
            return await ctx.send(
                "It seems like the role you attempt to mention is over your permissions, therefor I won't allow you.")

        if ctx.me.top_role.position <= role.position:
            return await ctx.send("This role is above my permissions, I can't make it mentionable ;-;")

        await role.edit(mentionable=True, reason=f"[ {ctx.author} ] announcerole command")
        msg = await ctx.send(
            f"**{role.name}** is now mentionable, if you don't mention it within 30 seconds, I will revert the changes.")

        while True:
            def role_checker(m):
                if (role.mention in m.content):
                    return True
                return False

            try:
                checker = await self.bot.wait_for('message', timeout=30.0, check=role_checker)
                if checker.author.id == ctx.author.id:
                    await role.edit(mentionable=False, reason=f"[ {ctx.author} ] announcerole command")
                    return await msg.edit(
                        content=f"**{role.name}** mentioned by **{ctx.author}** in {checker.channel.mention}")
                    break
                else:
                    await checker.delete()
            except asyncio.TimeoutError:
                await role.edit(mentionable=False, reason=f"[ {ctx.author} ] announcerole command")
                return await msg.edit(content=f"**{role.name}** was never mentioned by **{ctx.author}**...")
                break


    @commands.group()
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.guild)
    @commands.has_permissions(manage_messages=True)
    async def prune(self, ctx):
        """ Removes messages from the current server. """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None, message=True):
        if limit > 2000:
            return await ctx.send(f'Too many messages to search given ({limit}/2000)')

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden:
            return await ctx.send('I do not have permissions to delete messages.')
        except discord.HTTPException as e:
            return await ctx.send(f'Error: {e} (try a smaller search?)')

        deleted = len(deleted)
        if message is True:
            await ctx.send(f'🚮 Successfully removed {deleted} message{"" if deleted == 1 else "s"}.')

    @prune.command()
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @prune.command(name='all')
    async def _remove_all(self, ctx, *, search=100):
        """Removes all messages."""
        # await self.do_removal(ctx, search, lambda e: True)

        await self.do_removal(ctx, search, lambda e: True)

    @prune.command(name='custom')
    async def _customdeletet(self, ctx, *, search: int):
        """Value of messages"""
        # await self.do_removal(ctx, search, lambda e: True)

        await self.do_removal(ctx, search, lambda e: True)

    @prune.command()
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @prune.command()
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring.
        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.send('The substring length must be at least 3 characters.')
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @prune.command(name='bots')
    async def _bots(self, ctx, search=100, prefix=None):
        """Removes a bot user's messages and messages with their optional prefix."""

        getprefix = prefix if prefix else self.config.prefix

        def predicate(m):
            return (m.webhook_id is None and m.author.bot) or m.content.startswith(tuple(getprefix))

        await self.do_removal(ctx, search, predicate)

    @prune.command(name='users')
    async def _users(self, ctx, prefix=None, search=100):
        """Removes only user messages. """

        def predicate(m):
            return m.author.bot is False

        await self.do_removal(ctx, search, predicate)

    @prune.command(name='emojis')
    async def _emojis(self, ctx, search=100):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r'<a?:(.*?):(\d{17,21})>|[\u263a-\U0001f645]')

        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @prune.command(name='reactions')
    async def _reactions(self, ctx, search=100):
        """Removes all reactions from messages that have them."""

        if search > 2000:
            return await ctx.send(f'Too many messages to search for ({search}/2000)')

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(f'Successfully removed {total_reactions} reactions.')

    # @prune.error
    # async def error_prune(self,ctx, err):
    #     if isinstance(err, commands.MissingPermissions):
    #         await ctx.send("You need the ** manage messages** permission")
    #         return



    # @permissions.has_permissions(manage_channels=True)
    @commands.command(name='serverinvite',aliases=['create-invite','createinvite','makeinvite','make-invite','server-invite'])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.user)
    async def getinvite(self, ctx):
        if not ctx.author.guild_permissions.create_instant_invite:
            return await ctx.send(ctx, 'No create invite permission?')
        else:
            try:
                serverinvite = await ctx.channel.create_invite(reason='Requested by ' + ctx.author.display_name)
                await ctx.send(' :white_check_mark: | New invite created! Link: **' + str(serverinvite) + '**')
            except discord.errors.Forbidden as e:
                return await ctx.send(
                    "`error: I'm missing required discord permission [ create invite ]`"
                )

    @commands.has_permissions(manage_channels=True)
    @commands.command(name='lock',
                      usage="<enable/disbale/true/false>")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def lock(self, ctx, status: bool):
        if status:
            status = False
        else:
            status= True
        try:
            await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=status)
            await utilss.send_success(ctx,f"Successfully {'Re-opened' if status else 'Locked'} the channel.\nto unlock the channel, I need admin perms.")
        except discord.errors.Forbidden:
            return await ctx.send(
                f"`error: I'm missing required discord permission [ manage roles ]`"
            )
        except Exception as e:
            return await ctx.send(f"```{e}```")


    # @lock.error
    # async def lock_error(self, ctx, exc):
    #     if isinstance(exc, commands.MissingPermissions):
    #         await ctx.send("You need the Manage channel permission to do that.")
    #         return
    # @commands.command(brief="Adds reactions to a message")

    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.command(name='slowmode')
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def slowmode(self, ctx, *args):
        if len(args) == 0:
            return await ctx.send("Please add on how long in seconds.")
        else:
            try:
                assert args[0].isnumeric(), "Please add the time in seconds. (number)"
                count = int(args[0])
                assert count in range(21599), "Invalid range."
                await ctx.channel.edit(slowmode_delay=count)
                return await ctx.send(":white_check_mark: | " + ("Disabled channel slowmode." if (
                        count == 0) else f"Successfully set slowmode for <#{ctx.channel.id}> to {count} seconds."))
            except discord.errors.Forbidden:
                return await ctx.send(
                    f"`error: I'm missing required discord permission [ manage channels ]`"
                )
            except Exception as e:
                return await send_error_message(ctx, str(e))
    # @slowmode.error
    # async def error_slowmode(self, ctx, err):
    #     if isinstance(err, commands.MissingPermissions):
    #         await ctx.send("You need the ** manage channels** permission")
    #         return
    # async def add_reaction(self, ctx, messageid: int, channel: discord.TextChannel):
    #     """
    #     :param ctx: is the current context, guild etc
    #     :param messageid: the message id to react on
    #     :param channel: the channel with the message to react to
    #     :return: nothing
    #     """
    #     async with ctx.channel.typing():
    #         message = await channel.fetch_message(messageid)
    #
    #     try:
    #         def check(reaction, user):
    #             return user == message.author
    #
    #         await ctx.send("Please react to the message above with the emoji of your choice. You have 20 secs to do so")
    #         reaction_tupel = await self.client.wait_for('reaction_add', timeout=20.0, check=check)
    #         reaction = reaction_tupel[0]
    #         emoji = reaction.emoji
    #         print(type(emoji))
    #         print(emoji)
    #     except asyncio.TimeoutError:
    #         await ctx.send("Timed out please resend the command" + '👎')
    #         return
    #     else:
    #         await ctx.send("Done " + '👍')
    #     try:
    #         await ctx.send("Now please mention a role you want to give a user when then user"
    #                        " reacts with a the given emote. You have 30 seconds todo sp")
    #
    #         def check(m):
    #             return m.author == ctx.message.author and m.channel == ctx.message.channel
    #
    #         m = await self.client.wait_for('message', timeout=20.0, check=check)
    #         role = m.role_mentions
    #     except asyncio.TimeoutError:
    #         await ctx.send("Timed out please resend the command" + '👎')
    #         return
    #     else:
    #         await ctx.send("Done " + '👍')
    #     await message.add_reaction(emoji)
    #     insert_reaction.delay(ctx.guild.id, messageid, role[0].id, emoji)
    #
    # @commands.command(brief="deletes reactions from a message, cant be undone")
    # async def del_reaction(self, messageid: int, emoji: discord.emoji):
    #     """
    #     :param messageid: the message id to react on
    #     :param emoji: the emoji that the bot reacted with
    #     :return:nothing
    #     """
    #     pass

    # @commands.Cog.listener()
    # async def on_raw_reaction_add(self, payload):
    #     if not payload.member.bot:
    #         if payload.emoji.name:
    #             roleid = await self.client.sql.get_reaction_role(payload.guild_id, payload.message_id,
    #                                                              payload.emoji.name)
    #             if roleid:
    #                 role = discord.utils.get(payload.member.guild.roles, id=roleid)
    #                 await payload.member.add_roles(role, reason="reaction added", atomic=True)
    #
    # @commands.Cog.listener()
    # async def on_raw_reaction_remove(self, payload):
    #     if not payload.guild_id:
    #         return
    #     guild = self.client.get_guild(payload.guild_id)
    #     member = guild.get_member(payload.user_id)
    #     if not member.bot:
    #         roleid = await self.client.sql.get_reaction_role(payload.guild_id, payload.message_id, payload.emoji.name)
    #         if roleid:
    #             role = discord.utils.get(guild.roles, id=roleid)
    #             await member.remove_roles(role, reason="reaction removed", atomic=True)
    #
    #

def setup(bot):
    bot.add_cog(Mod(bot))
