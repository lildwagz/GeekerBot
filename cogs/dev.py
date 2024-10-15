import asyncio
import importlib
import io
import os
import sys
import textwrap
import time
import traceback
from contextlib import redirect_stdout
from datetime import datetime

import aiohttp
import discord
import humanize
import pkg_resources
from discord.ext import commands
from discord.ext.commands import CheckFailure
from discord.ext.buttons import Paginator

from utils import permissions, default, http, dataIO, utilss

class Pag(Paginator):
    async def teardown(self):
        try:
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass

class Dev(commands.Cog, name="Developers perm"):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self._last_result = None


    @commands.group()
    @commands.check(permissions.is_owner)
    async def change(self, ctx):
        if ctx.invoked_subcommand is None:
            embedColour = ctx.me.top_role.colour
            prefix = self.bot.cache.prefixes.get(str(ctx.guild.id))

            embed = discord.Embed(title=f"**{prefix}change**", colour=0xdeaa0c)

            embed.add_field(name="__Commands :__",
                            value=f"{prefix}change avatar :** Change avatar. \n**"
                                  f"{prefix}change nickname  :**  Change nickname.\n**"
                                  f"{prefix}change playing  :**   Change playing status. \n**"
                                  f"{prefix}change username   :** Change username.\n**",
                            inline=False)
            await ctx.send(content=f"", embed=embed)

    @change.command(name="playing")
    @commands.check(permissions.is_owner)
    async def change_playing(self, ctx, *, playing: str):
        """ Change playing status. """
        if self.config.status_type == "idle":
            status_type = discord.Status.idle
        elif self.config.status_type == "dnd":
            status_type = discord.Status.dnd
        else:
            status_type = discord.Status.online

        if self.config.activity_type == "listening":
            activity_type = 2
        elif self.config.activity_type == "watching":
            activity_type = 3
        else:
            activity_type = 0

        try:
            await self.bot.change_presence(
                activity=discord.Activity(type=activity_type, name=playing),
                status=status_type
            )
            dataIO.change_value("config.json", "playing", playing)
            await ctx.send(f"Successfully changed playing status to **{playing}**")
        except discord.InvalidArgument as err:
            await ctx.send(err)
        except Exception as e:
            await ctx.send(e)

    @change.command(name="username")
    @commands.check(permissions.is_owner)
    async def change_username(self, ctx, *, name: str):
        """ Change username. """
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"Successfully changed username to **{name}**")
        except discord.HTTPException as err:
            await ctx.send(err)

    @change.command(name="nickname")
    @commands.check(permissions.is_owner)
    async def change_nickname(self, ctx, *, name: str = None):
        """ Change nickname. """
        try:
            await ctx.guild.me.edit(nick=name)
            if name:
                await ctx.send(f"Successfully changed nickname to **{name}**")
            else:
                await ctx.send("Successfully removed nickname")
        except Exception as err:
            await ctx.send(err)

    @change.command(name="avatar")
    @commands.check(permissions.is_owner)
    async def change_avatar(self, ctx, url: str = None):
        """ Change avatar. """
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip('<>') if url else None

        try:
            bio = await http.get(url, res_method="read")
            await self.bot.user.edit(avatar=bio)
            await ctx.send(f"Successfully changed the avatar. Currently using:\n{url}")
        except aiohttp.InvalidURL:
            await ctx.send("The URL is invalid...")
        except discord.InvalidArgument:
            await ctx.send("This URL does not contain a useable image")
        except discord.HTTPException as err:
            await ctx.send(err)
        except TypeError:
            await ctx.send("You need to either provide an image URL or upload one with the command")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def reloadall(self, ctx):
        """ Reloads all extensions. """
        error_collection = []
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                try:
                    self.bot.reload_extension(f"cogs.{name}")
                except Exception as e:
                    error_collection.append(
                        [file, default.traceback_maker(e, advance=False)]
                    )

        if error_collection:
            output = "\n".join([f"**{g[0]}** ```diff\n- {g[1]}```" for g in error_collection])
            return await ctx.send(
                f"Attempted to reload all extensions, was able to reload, "
                f"however the following failed...\n\n{output}"
            )

        await ctx.send("Successfully reloaded all extensions")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def load(self, ctx, name: str):
        """ Loads an extension. """
        try:
            self.bot.load_extension(f"cogs.listener.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"Loaded extension **{name}.py**")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def reload(self, ctx, name: str):
        """ Reloads an extension. """
        try:
            self.bot.reload_extension(f"cogs.listener.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"Reloaded extension **{name}.py**")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def reloadutils(self, ctx, name: str):
        """ Reloads a utils module. """
        name_maker = f"utils/{name}.py"
        try:
            module_name = importlib.import_module(f"utils.{name}")
            importlib.reload(module_name)
        except ModuleNotFoundError:
            return await ctx.send(f"Couldn't find module named **{name_maker}**")
        except Exception as e:
            error = default.traceback_maker(e)
            return await ctx.send(f"Module **{name_maker}** returned error and was not reloaded...\n{error}")
        await ctx.send(f"Reloaded module **{name_maker}**")
    @commands.command()
    @commands.check(permissions.is_owner)
    async def reboot(self, ctx):
        """ Reboot the bot """
        try:
            await ctx.send('Rebooting now...')
            time.sleep(1)
            await self.bot.close()
        except:
            pass
        finally:
            os.system("python ../main.py &")

    @commands.check(permissions.is_owner)
    @commands.command(aliases=["poweroff"])
    async def shutdown(self, ctx):
        print("Goodbye")
        await self.bot.change_presence(status=discord.Status.offline)
        await asyncio.sleep(60)
        await ctx.send(f"""Going to sleep :sleeping:...""")
        await self.bot.close()

    @commands.check(permissions.is_owner)
    @commands.command(name="addusertodatabase")
    async def adduserdb(self, ctx, id : int):
        guild = self.bot.get_guild(id)
        guildidid = guild.id

        member, membercount = [], 0

        for i in range(guild.member_count):
            member.append(guild.members[i].id)
            membercount = int(membercount) + 1

        onlyuser = 0
        for i in range(0, membercount):
            filter = member[i]
            if not self.bot.get_user(filter).bot:
                code = int(member[i]) + int(guildidid) - int(member[i] * 2)
                self.bot.app.send_task('celerys.worker.insert_new_member',
                                       kwargs={'guildidid': guildidid, 'member': member[i],'code': str(code)})
                # print(f"{guildidid} {member[i]} {code}")

                onlyuser = int(onlyuser) + 1

        await ctx.send(f"succesfully {guild.name}'s member added  to table users total {onlyuser} members")

    @commands.check(permissions.is_owner)
    @commands.command(name="reg")
    async def regiserver(self, ctx , id):
        guild = self.bot.get_guild(int(id))
        dt_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.bot.app.send_task('celerys.worker.initialize_guild', kwargs={'guild_id': guild.id, 'datejoin': dt_string})
        self.bot.cache.prefixes[str(guild.id)] = self.bot.prefixdefault
        self.bot.cache.guildgame_toogle[str(guild.id)] = bool(0)
        self.bot.cache.levelsystem_toogle[str(guild.id)] = bool(0)
        self.bot.cache.imgwelcome_toggle[str(guild.id)] = bool(0)
        self.bot.cache.antiSpam_toogle[str(guild.id)] = bool(0)
        self.bot.cache.automod_toogle[str(guild.id)] = bool(0)
        self.bot.cache.captcha_toogle[str(guild.id)] = bool(0)
        self.bot.cache.antitoxic_toogle[str(guild.id)] = bool(0)
        self.bot.cache.antiLinks_toogle[str(guild.id)] = bool(0)
        self.bot.cache.ageaccount_toggle[str(guild.id)] = bool(0)
        self.bot.cache.allowspam[str(guild.id)] = 0
        self.bot.cache.ageaccount[str(guild.id)] = 0
        self.bot.cache.autorole[str(guild.id)] = 0

    @commands.check(permissions.is_owner)
    @commands.command(name="del")
    async def delserver(self, ctx , id):
        # guild = self.bot.get_guild(int(id))
        self.bot.app.send_task('celerys.worker.remove_guild_id', kwargs={'guildid':id})
        del self.bot.cache.prefixes[str(id)]
        del self.bot.cache.guildgame_toogle[str(id)]
        del self.bot.cache.levelsystem_toogle[str(id)]
        del self.bot.cache.imgwelcome_toggle[str(id)]
        del self.bot.cache.antiSpam_toogle[str(id)]
        del self.bot.cache.automod_toogle[str(id)]
        del self.bot.cache.captcha_toogle[str(id)]
        del self.bot.cache.antitoxic_toogle[str(id)]
        del self.bot.cache.antiLinks_toogle[str(id)]
        del self.bot.cache.ageaccount_toggle[str(id)]
        del self.bot.cache.allowspam[str(id)]
        del self.bot.cache.ageaccount[str(id)]
        del self.bot.cache.autorole[str(id)]

    @commands.check(permissions.is_owner)
    @commands.group(name='dev', hidden=True, invoke_without_command=True)
    async def dev(self, ctx):
        """
        Base command for bot developer commands.
        Displays a message with stats about the bot.
        """

        python_version = f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
        discordpy_version = pkg_resources.get_distribution('discord.py').version
        platform = sys.platform
        process_id = self.bot.process.pid
        thread_count = self.bot.process.num_threads()

        description = [
            f'I am running on the python version **{python_version}** on the OS **{platform}** using the discord.py version **{discordpy_version}**. '
            f'The process is running as **** on PID **{process_id}** and is using **{thread_count}** threads.']

        if isinstance(self.bot, commands.AutoShardedBot):
            description.append(
                f'The bot is automatically sharded with **{self.bot.shard_count}** shard(s) and can see **{len(self.bot.guilds)}** guilds and '
                f'**{len(self.bot.users)}** users.')
        else:
            description.append(
                f'The bot is not sharded and can see **{len(self.bot.guilds)}** guilds and **{len(self.bot.users)}** users.')

        with self.bot.process.oneshot():

            memory_info = self.bot.process.memory_full_info()
            physical_memory = humanize.naturalsize(memory_info.rss)
            virtual_memory = humanize.naturalsize(memory_info.vms)
            unique_memory = humanize.naturalsize(memory_info.uss)
            cpu_usage = self.bot.process.cpu_percent(interval=None)

            description.append(
                f'The process is using **{physical_memory}** of physical memory, **{virtual_memory}** of virtual memory and **{unique_memory}** of memory '
                f'that is unique to the process. It is also using **{cpu_usage}%** of CPU.')

        embed = discord.Embed(title=f'{self.bot.user.name} bot information page.', colour=0xF5F5F5)
        embed.description = '\n\n'.join(description)

        await ctx.send(embed=embed)
        
    @commands.check(permissions.is_owner)
    @commands.command()
    async def gamestatus(self, ctx):
        result = self.bot.cache.guildgame_toogle.get(str(ctx.guild.id))
        if result:
            await ctx.send(f"game status is {result}")
        else:
            await ctx.send(f"game status is {result}")

    @commands.check(permissions.is_owner)
    @commands.command()
    async def initialize_guild(self, ctx):
        dt_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        guildid = ctx.guild.id
        self.bot.app.send_task('celerys.worker.initialize_guild', kwargs={'guild_id': guildid, 'datejoin': dt_string})
        await ctx.send("success sending task to redis server")
        time.sleep(2)
        await ctx.send("the worker is getting the tasks and is doing task from redis server")
        await ctx.send("success inserting new guild into tbl_settings")

    @commands.check(permissions.is_owner)
    @commands.command()
    async def roles_to_db(self, ctx):
        guildid = ctx.guild.id
        server = ctx.message.guild
        roles_name, roles_id, role_count = [], [], 0
        for role in server.roles:
            roles_name.append(role.name)
            roles_id.append(role.id)
            role_count = int(role_count) + 1

        for i in range(0, role_count):
            self.bot.app.send_task('celerys.worker.roles_to_db',
                                   kwargs={'guild_id': guildid, 'role_name': roles_name[i], 'role_id': roles_id[i]})
        await ctx.send("success sending task to redis server")
        time.sleep(2)
        await ctx.send("the worker is getting the tasks and is doing task from redis server")
        await ctx.send("success inserting all guild roles into tbl_settings")

    @commands.check(permissions.is_owner)
    @commands.command()
    async def guilds(self, ctx):
        """Show all connected guilds."""
        membercount = len(set(self.bot.get_all_members()))
        content = discord.Embed(
            title=f"Total **{len(self.bot.guilds)}** guilds, **{membercount}** unique users"
        )

        rows = []
        for guild in sorted(self.bot.guilds, key=lambda x: x.member_count, reverse=True):
            rows.append(f"[`{guild.id}`] **{guild.member_count}** members : **{guild.name}**")

        await utilss.send_as_pages(ctx, content, rows)

    @commands.check(permissions.is_owner)
    @commands.command()
    async def userguilds(self, ctx, user: discord.User):
        """Get all guilds user is part of."""
        rows = []
        for guild in sorted(self.bot.guilds, key=lambda x: x.member_count, reverse=True):
            guildmember = guild.get_member(user.id)
            if guildmember is not None:
                rows.append(f"[`{guild.id}`] **{guild.member_count}** members : **{guild.name}** member id : **{user.id}**")

        content = discord.Embed(title=f"User **{user}** found in **{len(rows)}** guilds")
        await utilss.send_as_pages(ctx, content, rows)

    @commands.check(permissions.is_owner)
    @commands.command()
    async def getemoji(self,ctx):
        for emoji in ctx.guild.emojis:
            await ctx.send(f"{emoji} + id : {emoji.id}")

    @commands.check(permissions.is_owner)
    @commands.group()
    async def dm(self, ctx, user_id: discord.Member, *, message: str):
        # user = self.bot.get_user(user_id)
        if user_id is None:
            return await ctx.send(f"Could not find any UserID matching **{user_id}**")

        try:
            await user_id.send(message)
            await ctx.send(f"✉️ Sent a DM to **{user_id}**")
        except discord.Forbidden:
            await ctx.send("This user might be having DMs blocked or it's a bot account...")

    @dm.error
    async def dm_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("You need the Administrator permission to do that.")

    @commands.check(permissions.is_owner)
    @commands.command()
    async def get_infra(self,ctx):
        resultinfraction = self.bot.app2.send_task('celerys.worker2.get_infractionchannel')

        if resultinfraction.get():
            row = resultinfraction.get()
            for guildid, channel in row:
                self.bot.cache.infractionchannel[str(guildid)] = channel
            # await ctx.send(f"{resultinfraction.get()}")

    @commands.check(permissions.is_owner)
    @commands.command()
    async def show_infra(self, ctx):

        await ctx.send(f"{self.bot.cache.infractionchannel}")


    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')


    @commands.check(permissions.is_owner)
    @commands.command(pass_context=True, hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    pager = Pag(
                        timeout=100,
                        entries=[value[i: i + 2000] for i in range(0, len(value), 2000)],
                        length=1,
                        prefix="```py\n",
                        suffix="```"
                    )

                    await pager.start(ctx)
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

def setup(bot):
    bot.add_cog(Dev(bot))
