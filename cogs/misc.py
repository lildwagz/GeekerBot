from collections import OrderedDict

import discord
from discord.ext import commands
from discord.ext.commands import  errors

from utils import utilss


class Misc(commands.Cog, name="misc"):
    def __init__(self, bot):
        self.bot = bot

    # @commands.check(permissions.is_owner)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.command(name="prefix")
    async def change_prefix(self, ctx, new: str):
        # if not permissions.can_manageserver(ctx):
        #     return
        if len(new) > 5:
            await ctx.send("The prefix can not be more than 5 characters in length.")

        else:
            self.bot.cache.prefixes[str(ctx.guild.id)] = new
            self.bot.app.send_task('celerys.worker.change_prefix', kwargs={'guildid': ctx.guild.id, 'prefix': new})
            await utilss.send_success(ctx,
                                      f"Command prefix for this server is now `{new}`. "
                                      f"Example command usage: {new}ping",
                                      )

    # @change_prefix.error
    # async def change_prefix_error(self, ctx, exc):
    #     if isinstance(exc, CheckFailure):
    #         await ctx.send("You need the Manage Server permission to do that.")
    #         return

    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.command(name="whitelist", aliases=['wlr'])
    async def set_whitelistrole(self, ctx, cmd, role=None):
        """
        set up a role that can bypass anti link,anti toxic, anti spam and so on

        """
        # if not permissions.can_manageserver(ctx):
        #     return
        # print(self.bot.cache.whitelist[str(ctx.guild.id)])
        if cmd.lower() == "add":
            if role is None:
                return await self.send_error_wlr(ctx)
            role = role.replace("<", "")
            role = role.replace("@&", "")
            role = role.replace(">", "")
            rolenew = discord.utils.get(ctx.guild.roles, id=int(role))
            try:

                if self.bot.cache.whitelist[str(ctx.guild.id)] is None:
                    self.bot.cache.whitelist[str(ctx.guild.id)] = rolenew.id
                    self.bot.app.send_task('celerys.worker.insert_whitelist',
                                           kwargs={'guildid': ctx.guild.id, 'role': rolenew.id})
                    await utilss.send_success(ctx, f"{rolenew.name} was successfully added into the whitelist!")

                else:
                    self.bot.cache.whitelist[str(ctx.guild.id)].append(rolenew.id)

                    if not len(self.bot.cache.whitelist[str(ctx.guild.id)]) != len(
                            set(self.bot.cache.whitelist[str(ctx.guild.id)])):
                        self.bot.app.send_task('celerys.worker.insert_whitelist',
                                               kwargs={'guildid': ctx.guild.id, 'role': rolenew.id})
                        await utilss.send_success(ctx, f"{rolenew.name} was successfully added into the whitelist!")
                    else:
                        self.bot.cache.whitelist[str(ctx.guild.id)] = list(
                            dict.fromkeys(self.bot.cache.whitelist[str(ctx.guild.id)]))

                        await utilss.send_error_message(ctx, "role is already added, please choose another role")



            except KeyError:
                self.bot.cache.whitelist[str(ctx.guild.id)] = [rolenew.id]
                self.bot.app.send_task('celerys.worker.insert_whitelist',
                                       kwargs={'guildid': ctx.guild.id, 'role': rolenew.id})
                await utilss.send_success(ctx, f"{rolenew.name} was successfully added into the whitelist!")


        elif cmd.lower() == "del":
            if role is None:
                return await self.send_error_wlr(ctx)
            role = role.replace("<", "")
            role = role.replace("@&", "")
            role = role.replace(">", "")
            rolenew = discord.utils.get(ctx.guild.roles, id=int(role))
            # print(len(self.bot.cache.whitelist[str(ctx.guild.id)]))
            i = str(ctx.guild.id)
            try:

                if len(self.bot.cache.whitelist[str(ctx.guild.id)]) == 1:
                    if self.bot.cache.whitelist[i][0] == rolenew.id:
                        del self.bot.cache.whitelist[str(ctx.guild.id)]
                        self.bot.app.send_task('celerys.worker.delete_whitelist',
                                               kwargs={'guildid': ctx.guild.id, 'role': rolenew.id})
                        await utilss.toogle_disable(ctx, f"{rolenew.name} was successfully deleted from the whitelist!")
                    else:
                        await utilss.send_error_message(ctx, "role not found, please choose the right role")

                else:
                    # try :
                    for index, val in enumerate(self.bot.cache.whitelist[i]):
                        if val == rolenew.id:
                            del self.bot.cache.whitelist[i][index]
                            self.bot.app.send_task('celerys.worker.delete_whitelist',
                                                   kwargs={'guildid': ctx.guild.id, 'role': rolenew.id})
                            return await utilss.toogle_disable(ctx,
                                                               f"{rolenew.name} was successfully deleted from the whitelist!")

                    await utilss.send_error_message(ctx, "role not found, please choose the right role")

            except KeyError as e:
                await utilss.send_error_message(ctx, "you havent added roles to a whitelist")


        else:
            return await self.send_error_wlr(ctx)

    @set_whitelistrole.error
    async def set_whitelistrole_error(self, ctx, exc):
        if isinstance(exc, errors.MissingRequiredArgument) or isinstance(exc, errors.BadArgument):
            return await self.send_error_wlr(ctx)

    async def send_error_wlr(self, ctx):
        prefix = self.bot.cache.prefixes.get(str(ctx.guild.id))
        embed = discord.Embed(title=f"**{prefix}whitelist**",
                              description="set up a role that can bypass anti link,anti toxic, anti spam and so on",
                              colour=0xdeaa0c)

        embed.add_field(name="__Commands :__",
                        value=f"{prefix}whitelist/wlr add <role>:** To add a role to the whitelist. \n**"
                              f"{prefix}whitelist/wlr del <role>:**  To remove a role from the whitelist.\n**",
                        inline=False)
        await ctx.send(content=f"", embed=embed)

    @commands.guild_only()
    @commands.command(name='smartmodlog', aliases=["sml"],
                      usage="<channel/disable>")
    @commands.has_permissions(manage_guild=True)
    async def infractionchannel(self, ctx, channel):
        guildid = ctx.guild.id

        if channel.lower() == "disable" or channel.lower() == "false":
            try:
                del self.bot.cache.infractionchannel[str(guildid)]
                self.bot.app.send_task("celerys.worker.set_infractionchannel",
                                       kwargs={'guildid': guildid, 'channel': 'NULL'})
                await utilss.toogle_disable(ctx, "disabled infraction channel logs")
            except KeyError :
                await utilss.send_error_message(ctx, "already disabled infraction channel logs")


        else:
            channel = channel.replace("<", "")
            channel = channel.replace("#", "")
            channel = channel.replace(">", "")
            # chache = self.bot.cache.infractionchannel[str(guildid)]
            try:
                channel = int(channel)
                getchannel = self.bot.get_channel(channel)
                self.bot.cache.infractionchannel[str(guildid)] = getchannel.id
                self.bot.app.send_task("celerys.worker.set_infractionchannel",
                                       kwargs={'guildid': guildid, 'channel': getchannel.id})
                await utilss.send_success(ctx, f" set <#{getchannel.id}> as infraction log")
            except Exception as e:
                await ctx.send(f"please input a valid channel")

        # print(self.bot.cache.infractionchannel)


def setup(bot):
    bot.add_cog(Misc(bot))
