import asyncio
import json
import random
import ast
from datetime import datetime
import os
import time

import discord
from discord import Member
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

# These color constants are taken from discord.js library
from utils import default

with open("Databases/embed_colors.txt") as f:
    data = f.read()
    colors = ast.literal_eval(data)
    color_list = [c for c in colors.values()]


class Mod2(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")

    @commands.command(name='warn')
    @has_permissions(manage_messages=True)
    async def warn_command(self, ctx, user: discord.Member, *, reason: str):
        """warns a user"""
        global pst
        if user.top_role.position >= ctx.author.top_role.position:
            return await ctx.send(
                "`user has a higher  role than you or same role inside the guild/server.`"
            )
        if ctx.guild.me.top_role.position <= user.top_role.position:
            return await ctx.send(
                "` user has a higher role than me inside the guild/server.`"
            )
        if user.id == self.bot.user.id:
            await ctx.send(
                "Oh, REALLY now, huh? I do my best at maintaining this server and THIS is how you treat me? Screw "
                "this..")
            return
        if user.bot == 1:
            await ctx.send("It's useless to warn a bot. Why would you even try.")
            return
        if user == ctx.author:
            await ctx.send("Why the heck would you warn yourself? You hate yourself THAT much?")
            return

        if user.guild_permissions.manage_messages:
            await ctx.send(
                "The specified user has the \"Manage Messages\" permission ")
            return
        guildidid =ctx.guild.id
        codeuser = str(f"USR{int(user.id) + int(guildidid) - int(user.id * 2)}")
        resultq = self.bot.cache.users.get(codeuser)
        if resultq is None:
            code = int(user.id) + int(guildidid) - int(user.id * 2)
            self.bot.cache.users["USR" + str(code)] = user.id, guildidid, 1, 0, 0
            self.bot.app.send_task('celerys.worker.insert_new_member',
                                   kwargs={'guildidid': guildidid, 'member': user.id, 'code': str(code)})
            await ctx.send(
                "Try again to use commands In 3 seconds")
            return
        dt_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        kode_user = int(user.id) + int(ctx.guild.id) - int(user.id * 2)
        i = str(f"USR{kode_user}")
        # print(self.bot.cache.warns)
        if self.bot.cache.warns:
            for index, val in enumerate(self.bot.cache.warns):
                if i in val.keys():

                    listwarns = self.bot.cache.warns[index][i]
                    for subindex, key in enumerate(listwarns):
                        try:
                            checkpoint = listwarns[-1][list(key.keys())[0]]
                            lastwarnkey = list(key.keys())[0]
                            new_amount = lastwarnkey + 1
                            offender_name = user.name
                            position = new_amount
                            user_id = user.id
                            warner_id = ctx.author.id
                            warner_name = ctx.author.name
                            reasons = reason
                            channel = ctx.channel.id
                            datetimes = dt_string

                            data = {
                                new_amount: [offender_name, position, user_id, warner_id, warner_name, reasons, channel,
                                             datetimes]
                            }
                            datas = {'kode_user': i,
                                     'code': new_amount,
                                     'offender_name': offender_name,
                                     'position': position,
                                     'user_id': user_id,
                                     'warner': warner_id,
                                     'warner_name': warner_name,
                                     'reason': reasons,
                                     'channel': channel,
                                     'datetime': datetimes}

                            self.bot.app.send_task('celerys.worker.insert_warn', kwargs=datas)
                            self.bot.cache.warns[index][i].append(data)
                            # print(self.bot.cache.warns[index])

                            embed = discord.Embed(
                                title=f"{offender_name}'s new warn",
                                color=random.choice(color_list)
                            )
                            embed.set_author(
                                name=ctx.message.author.name,
                                icon_url=ctx.message.author.avatar_url,
                                url=f"https://discord.com/users/{ctx.message.author.id}/"
                            )
                            embed.add_field(
                                name=f"Warn {new_amount}",
                                value=f"Warner: {warner_name} (<@{warner_id}>)\nReason: {reason}\nChannel: <#{str(channel)}>\nDate and Time: {dt_string}",
                                inline=True
                            )
                            await ctx.send(
                                content="Successfully added new warn.",
                                embed=embed
                            )
                            return

                        except:
                            pass
                    return

            new_amount = 1
            offender_name = user.name
            position = new_amount
            user_id = user.id
            warner_id = ctx.author.id
            warner_name = ctx.author.name
            reasons = reason
            channel = ctx.channel.id
            datetimes = dt_string

            data = {
                i: [{new_amount: [offender_name, position, user_id, warner_id, warner_name, reasons,
                                  channel, datetimes]}]
            }
            self.bot.cache.warns.append(data)
            # print(self.bot.cache.warns[index][i][0][new_amount])
            embed = discord.Embed(
                title=f"{offender_name}'s new warn",
                color=random.choice(color_list)
            )
            embed.set_author(
                name=ctx.message.author.name,
                icon_url=ctx.message.author.avatar_url,
                url=f"https://discord.com/users/{ctx.message.author.id}/"
            )
            embed.add_field(
                name=f"Warn {position}",
                value=f"Warner: {ctx.author.name} (<@{ctx.author.id}>)\nReason: {reason}\nChannel: <#{str(ctx.channel.id)}>\nDate and Time: {dt_string}",
                inline=True
            )
            await ctx.send(
                content="Successfully added new warn.",
                embed=embed
            )
            datas = {'kode_user': i,
                     'code': new_amount,
                     'offender_name': offender_name,
                     'position': position,
                     'user_id': user_id,
                     'warner': warner_id,
                     'warner_name': warner_name,
                     'reason': reasons,
                     'channel': channel,
                     'datetime': datetimes}
            self.bot.app.send_task('celerys.worker.insert_warn', kwargs=datas)
            return
        else:
            new_amount = 1
            offender_name = user.name
            position = new_amount
            user_id = user.id
            warner_id = ctx.author.id
            warner_name = ctx.author.name
            reasons = reason
            channel = ctx.channel.id
            datetimes = dt_string
            data = {
                i: [{new_amount: [offender_name, position, user_id, warner_id, warner_name, reasons, channel,
                                  datetimes]}]
            }

            self.bot.cache.warns.append(data)
            # print(self.bot.cache.warns[0][i])
            embed = discord.Embed(
                title=f"{offender_name}'s new warn",
                color=random.choice(color_list)
            )
            embed.set_author(
                name=ctx.message.author.name,
                icon_url=ctx.message.author.avatar_url,
                url=f"https://discord.com/users/{ctx.message.author.id}/"
            )
            embed.add_field(
                name=f"Warn {position}",
                value=f"Warner: {ctx.author.name} (<@{ctx.author.id}>)\nReason: {reason}\nChannel: <#{str(ctx.channel.id)}>\nDate and Time: {dt_string}",
                inline=True
            )
            await ctx.send(
                content="Successfully added new warn.",
                embed=embed
            )
            datas = {'kode_user': i,
                     'code': new_amount,
                     'offender_name': offender_name,
                     'position': position,
                     'user_id': user_id,
                     'warner': warner_id,
                     'warner_name': warner_name,
                     'reason': reasons,
                     'channel': channel,
                     'datetime': datetimes}
            self.bot.app.send_task('celerys.worker.insert_warn', kwargs=datas)
            return

    # @warn_command.error
    # async def warn_handler(self, ctx, error):
    #     if isinstance(error, commands.MissingPermissions):
    #         await ctx.send("You need the ** manage messages** permission")
    #         return

    @commands.command(
        name='warns', aliases=['warnings']
    )
    async def warns_command(self, ctx, user: discord.Member):
        """See all the warns a user has"""
        kode_user = int(user.id) + int(ctx.guild.id) - int(user.id * 2)
        i = str(f"USR{kode_user}")
        if self.bot.cache.warns:
            for index, val in enumerate(self.bot.cache.warns):
                if i in val.keys():
                    # print(self.bot.cache.warns[index][i])
                    listwarns = self.bot.cache.warns[index][i]
                    amountwarns = len(listwarns)
                    if amountwarns == 1:
                        warns_word = "warn"
                    else:
                        warns_word = "warns"
                    getky = []
                    counter = 0
                    embed = discord.Embed(
                        title=f"{user.name}'s warns",
                        description=f"They have {amountwarns} {warns_word}.",
                        color=random.choice(color_list)
                    )
                    embed.set_author(
                        name=ctx.message.author.name,
                        icon_url=ctx.message.author.avatar_url,
                        url=f"https://discord.com/users/{ctx.message.author.id}/"
                    )
                    for index, key in enumerate(listwarns):
                        # getky.append(list(key.keys())[0])
                        # print(listwarns[index][list(key.keys())[0]])
                        if counter == 0:
                            offender_name, position, user_id, warner_id, warner_name, reasons, channel, datetimes = \
                                listwarns[index][list(key.keys())[0]]
                        else:
                            offender_name, position, user_id, warner_id, warner_name, reasons, channel, datetimes = \
                                listwarns[index][list(key.keys())[0]]
                        counter = int(counter) + 1
                        try:
                            warner_name = self.bot.get_user(id=warner_id)
                        except:
                            warner_name = warner_name

                        warn_reason = reasons
                        warn_channel = channel
                        warn_datetime = datetimes

                        embed.add_field(
                            name=f"Warn {list(key.keys())[0]}",
                            value=f"Warner: {warner_name} (<@{warner_id}>)\nReason: {warn_reason}\nChannel: <#{warn_channel}>\nDate and Time: {warn_datetime}",
                            inline=True
                        )

                    await ctx.send(
                        content=None,
                        embed=embed
                    )
                    return

            else:
                await ctx.send(f"{user.mention} doesn't have any warns")
                return
        else:
            await ctx.send(f"{user.mention} doesn't have any warns")
            return

        # Send embed.

    @warns_command.error
    async def warns_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'user':
                # Author did not specify user
                await ctx.send("Please mention someone to verify their warns.")
                return

        await ctx.send(error)


    @commands.command(name='removewarn', aliases=['clearwarn'])
    @has_permissions(manage_messages=True)
    async def remove_warn_command(self, ctx, user: discord.Member, *, warn: int):
        """Removes a specific warn from a specific user"""
        if user.top_role.position >= ctx.author.top_role.position:
            return await ctx.send(
                "`user has a higher  role than you or same role inside the guild/server.`"
            )
        if ctx.guild.me.top_role.position <= user.top_role.position:
            return await ctx.send(
                "` user has a higher role than me inside the guild/server.`"
            )
        kode_user = int(user.id) + int(ctx.guild.id) - int(user.id * 2)
        i = str(f"USR{kode_user}")

        if self.bot.cache.warns:
            for index, val in enumerate(self.bot.cache.warns):
                if i in val.keys():
                    # print(self.bot.cache.warns[index][i])
                    listwarns = self.bot.cache.warns[index][i]
                    counter = 0
                    for subdex, key in enumerate(listwarns):
                        # print(i)
                        try:
                            offender_name, position, user_id, warner_id, warner_name, reasons, channel, datetimes = \
                                listwarns[counter][warn]

                            confirmation_embed = discord.Embed(
                                title=f'{user.name}\'s warn number {warn}',
                                description=f'Warner: {warner_name}\nReason: {reasons}\nChannel: <#{channel}>\nDate '
                                            f'and Time: {datetimes}',
                                color=random.choice(color_list),
                            )
                            confirmation_embed.set_author(
                                name=ctx.message.author.name,
                                icon_url=ctx.message.author.avatar_url,
                                url=f"https://discord.com/users/{ctx.message.author.id}/"
                            )

                            def check(ms):
                                return ms.channel == ctx.message.channel and ms.author == ctx.message.author

                            loading = await ctx.send(
                                content='Are you sure you want to remove this warn? (Reply with y or n)',
                                embed=confirmation_embed)
                            msg = await self.bot.wait_for('message', check=check)
                            reply = msg.content.lower()
                            if reply in ('y', 'yes', 'confirm'):
                                await msg.delete()
                                await asyncio.sleep(1)
                                await loading.delete()
                                loading = await ctx.send(
                                    f"[{ctx.author.name}], user [{user.name} ({user.id})] has gotten their warn removed.")
                                await asyncio.sleep(2)
                                await loading.delete()

                                if len(listwarns) == 1:
                                    # print( f"{self.bot.cache.warns[index]}")
                                    del self.bot.cache.warns[index]

                                else:
                                    del listwarns[counter][warn]
                                    del listwarns[counter]
                                    pass
                                # print(f"deleted {listwarns[counter][warn]}")
                                self.bot.app.send_task('celerys.worker.delete_warn',
                                                       kwargs={'kode_user': i, 'code': warn})
                                return
                            elif reply in ('n', 'no', 'cancel'):
                                await ctx.send("Alright, action cancelled.")
                                return
                            else:
                                await ctx.send("I have no idea what you want me to do. Action cancelled.")
                                return
                        except:
                            pass
                        counter = counter + 1
                    await ctx.send("You specified an invalid ID.")
                    return
            await ctx.send(f"[{ctx.author.name}], user [{user.name} ({user.id})] does not have any warns.")
            return
        else:
            await ctx.send(f"[{ctx.author.name}], user [{user.name} ({user.id})] does not have any warns.")
            return

    @remove_warn_command.error
    async def remove_warn_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'user':
                # Author did not specify a user
                await ctx.send("Please mention someone to remove their warns.")
                return
            if error.param.name == 'warn':
                # Author did not specify a warn ID
                await ctx.send("You did not specify a warn ID to remove.")
                return
        if isinstance(error, commands.CommandInvokeError):
            # Author probably specified an invalid ID.
            await ctx.send("You specified an invalid ID.")
            return
        # if isinstance(error, commands.MissingPermissions):
        #     await ctx.send("You need the ** manage messages** permission")
        #     return
        await ctx.send(error)

    @commands.command(name='editwarn', aliases=['changewarn'])
    @has_permissions(manage_messages=True)
    async def edit_warn_command(self, ctx, user: discord.Member, *, warn: str):
        """Edits a specific warn from a specific user."""
        try:
            with open("Databases/warns/" + str(ctx.guild.id) + "/" + str(user.id) + ".json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            await ctx.send(f"[{ctx.author.name}], user [{user.name} ({user.id})] does not have any warns.")
            return

        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        await ctx.send(content='What would you like to change the warn\'s reason to?')
        msg = await self.bot.wait_for('message',
                                      check=check)
        warn_new_reason = msg.content.lower()

        specified_warn = data.get(warn)
        warn_warner = specified_warn.get('warner')
        warn_channel = specified_warn.get('channel')
        warn_datetime = specified_warn.get('datetime')
        try:
            warn_warner_name = self.bot.get_user(id=warn_warner)
        except:
            warn_warner_name = specified_warn.get('warner_name')

        confirmation_embed = discord.Embed(
            title=f'{user.name}\'s warn number {warn}',
            description=f'Warner: {warn_warner_name}\nReason: {warn_new_reason}\nChannel: <#{warn_channel}>\nDate and Time: {warn_datetime}',
            color=random.choice(color_list),
        )
        confirmation_embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )
        await ctx.send(content='Are you sure you want to edit this warn like this? (Reply with y/yes or n/no)',
                       embed=confirmation_embed)

        msg = await self.bot.wait_for('message', check=check)
        reply = msg.content.lower()  # Set the title
        if reply in ('y', 'yes', 'confirm'):
            specified_warn['reason'] = warn_new_reason
            json.dump(data, open("Databases/warns/" + str(ctx.guild.id) + "/" + str(user.id) + ".json", "w"))
            await ctx.send(f"[{ctx.author.name}], user [{user.name} ({user.id})] has gotten their warn edited.")
            return
        elif reply in ('n', 'no', 'cancel', 'flanksteak'):
            # dont ask me why i decided to put flanksteak
            await ctx.send("Alright, action cancelled.")
            return
        else:
            await ctx.send("I have no idea what you want me to do. Action cancelled.")

    @edit_warn_command.error
    async def edit_warn_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'user':
                # Author did not specify a user
                await ctx.send("Please mention someone to remove their warns.")
                return
            if error.param.name == 'warn':
                await ctx.send("You did not specify a warn ID to remove.")
                return
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("You specified an invalid ID.")
            return
        await ctx.send(error)


def setup(bot):
    bot.add_cog(Mod2(bot))
