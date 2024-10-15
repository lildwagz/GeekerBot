import os
import platform
from datetime import datetime, date

import discord


import pytz
from discord.utils import get
import psutil
from discord.ext import commands

from utils import default
from utils.pagination import BotEmbedPaginator

import subprocess
import cpuinfo


class SettingsCog(commands.Cog, name="settings command"):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self.process = psutil.Process(os.getpid())

    # ------------------------------------------------------ #

    @commands.command(name='settings')
    async def settings(self, ctx):
        if ctx.guild is None:
            await ctx.author.send('Hi. This command is not allowed in DM!')
            return
        prefix = self.bot.cache.prefixes.get(str(ctx.guild.id), self.bot.prefixdefault)
        guildid = ctx.guild.id
        triggeredword = f"{'[word]' if self.bot.cache.triger_word.get(str(guildid)) is None or not self.bot.cache.trigerword_toogle.get(str(guildid)) else f'{self.bot.cache.triger_word.get(str(guildid))[0]}'}"
        roleword = f"{'<role>' if triggeredword == '[word]' else get(ctx.guild.roles, id=self.bot.cache.triger_word.get(str(guildid))[1]).mention}"
        channelword = f"{'[channel]' if triggeredword == '[word]' else f'<#{self.bot.cache.triger_word.get(str(guildid))[2]}>'}"

        triggeredrole = f"{'<false/newrole>' if self.bot.cache.triger_role.get(str(guildid)) is None or not self.bot.cache.trigerrole_toogle.get(str(guildid)) else get(ctx.guild.roles, id=self.bot.cache.triger_role.get(str(guildid))[0]).mention}"
        oldrole = f"{'<oldrole>' if triggeredrole == '<false/newrole>' else get(ctx.guild.roles, id=self.bot.cache.triger_role.get(str(guildid))[1]).mention}"

        whitelist = f"{'None' if not self.bot.cache.whitelist.get(str(guildid)) else ', '.join([str(get(ctx.guild.roles, id=x).mention) for x in self.bot.cache.whitelist.get(str(guildid))])}"

        allowSpam = self.bot.cache.allowspam.get(str(guildid))
        allowSpam2 = ""
        if allowSpam == 0:
            allowSpam2 = "None"
        else:
            # for x in allowSpam:
            allowSpam2 = f"{allowSpam2}<#{allowSpam}>, "

        autorole = f"{'None' if self.bot.cache.autorole.get(str(guildid)) == 0 else get(ctx.guild.roles, id=self.bot.cache.autorole.get(str(guildid))).mention}"

        minageacc = self.bot.cache.ageaccount.get(str(guildid))
        minageacc2 = f"{'None' if minageacc == 0 else f'{int(minageacc / 3600)}'}"

        embed = discord.Embed(title=f"**SERVER SETTINGS**", description=f"[**DISCORD**](https://discord.gg/EZN4gnk)",
                              color=0xdeaa0c)
        embed.add_field(name=f"**WHITELIST ROLES** - ``({prefix}whitelist/wlr)``",
                        value=f"roles: {whitelist}",
                        inline=False)

        embed.add_field(name=f"**AUTO MOD** - ``({prefix}automod  <true/false>)``",
                        value=f"Auto mod enabled : {self.bot.cache.automod_toogle.get(str(guildid))}", inline=False)

        embed.add_field(name=f"**ANTI SPAM** - ``({prefix}antispam <true/false>)``",
                        value=f"the anti spam still on maintenance", inline=False)
        # value=f"Anti spam enabled : {self.bot.cache.antiSpam_toogle.get(str(guildid))}", inline=False)

        embed.add_field(name=f"**ANTI TOXIC** - ``({prefix}toxic <true/false>)``",
                        value=f"Anti toxic enabled : {self.bot.cache.antitoxic_toogle.get(str(guildid))}", inline=False)

        embed.add_field(name=f"**ANTI URL/LINKS** - ``({prefix}antilink <true/false>)``",
                        value=f"Anti Url/Links enabled : {self.bot.cache.antiLinks_toogle.get(str(guildid))}",
                        inline=False)

        embed.add_field(name=f"**ALLOW SPAM** - ``({prefix}allowspam <#channel> (remove))``",
                        value=f"Channel where spam is allowed : {allowSpam2}", inline=False)
        #
        # embed.add_field(name=f"**CAPTCHA VERIFICATION** - ``({prefix}setCaptcha <#channel> <true/false>)``",
        #                 value=f"Capctha enabled : {self.bot.cache.captcha_toogle.get(str(guildid))}\n"
        #                      f"Captcha channel : <{captchaChannel}>",
        #                 inline=False)

        embed.add_field(name=f"**MINIMUM ACCOUNT AGE** - ``({prefix}minaccountage  <numberInHour/false>)``",
                        value=f"is enabled : {self.bot.cache.ageaccount_toggle.get(str(guildid))}\n"
                              f"Minimum account age : {minageacc2} hours",
                        inline=False)

        embed.add_field(name=f"**GUILD GAME ACTIVITY** - ``({prefix}setguildgames <true/false>)``",
                        value=f"guild game activity enabled : {self.bot.cache.guildgame_toogle.get(str(guildid))}\n",
                        inline=False)

        embed.add_field(name=f"**LEVELING SYSTEM** - ``({prefix}setlevelingsystem  <true/false>)``",
                        value=f"leveling system enabled : {self.bot.cache.levelsystem_toogle.get(str(guildid))}",
                        inline=False)

        # embed.add_field(name=f"**WELCOMING SYSTEM** - ``({prefix}setwelcome  <true/false>)``",
        #                 value=f"welcoming system enabled : {self.bot.cache.imgwelcome_toggle.get(str(guildid))}\n"
        #                       f"image welcome enabled : NONE\n"
        #                       f"text welcome : NONE\n"
        #                       f"channel welcome : NONE",
        #                 inline=False)
        embed.set_footer(text="Bot Created by Zam")

        embed1 = discord.Embed(title=f"**SERVER SETTINGS**", description=f"[**DISCORD**](https://discord.gg/EZN4gnk)",
                               color=0xdeaa0c)

        embed1.add_field(name=f"**AUTO ROLE** - ``({prefix}autorole  add/delete <role>)``",
                         value=f"auto role when new member joins : {autorole}",
                         inline=False)
        #
        embed1.add_field(name=f"**TRIGGERS** - ``({prefix}trigger/trig)``",
                         value=f"**triggered word** : {triggeredword} , {roleword} , {'[channel]' if channelword == 0 or channelword == 'None' else channelword}\n"
                               f"**triggered role** : {triggeredrole} , {oldrole}\n",
                         inline=False)

        embeds = [
            embed, embed1
        ]
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()

    @commands.command(aliases=["shards"])
    async def shardinfo(self, ctx):
        """Get information about the current shards."""
        content = discord.Embed(title=f"Running {len(self.bot.shards)} shards")
        for shard in self.bot.shards.values():
            content.add_field(
                name=f"Shard [`{shard.id}`]"
                     + (f" {self.bot.get_emoji(747979755688558655)}" if ctx.guild.shard_id == shard.id else ""),
                value=f"```Connected: {not shard.is_closed()}\nHeartbeat: {shard.latency * 100:.2f} ms```",
            )

        await ctx.send(embed=content)

    @commands.command(name="speedtest")
    async def speedcli(self, ctx):
        """
        server speed internet testing
        :param ctx:
        :return:
        """
        command = os.popen('speedtest-cli').read()[:-1]
        embed = discord.Embed(colour=int("77b255", 16))
        embed.add_field(name="TESTING CONNECTION", value=command)
        await ctx.send(embed=embed)

    @commands.command(aliases=['info', 'stats', 'status'])
    async def about(self, ctx):
        """ About the bot """
        ramUsage = self.process.memory_full_info().rss / 1024 ** 2
        avgmembers = round(len(self.bot.users) / len(self.bot.guilds))
        uptime = os.popen('uptime -p').read()[:-1]
        net_io = psutil.net_io_counters()
        swap = psutil.swap_memory()
        cpufreq = psutil.cpu_freq()

        embedColour = discord.Embed.Empty
        if hasattr(ctx, 'guild') and ctx.guild is not None:
            embedColour = ctx.me.top_role.colour

        embed = discord.Embed(colour=embedColour)
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        embed.add_field(name="SYSTEM INFORMATION",
                        value="--------------------------------\n"
                              f"**OS Server**    : {platform.system()}\n"
                              f"**Release**    : {platform.release()}\n"
                              f"**Processor**    : {get_processor_info()}\n"
                              f"**Uptime Server**    : {uptime}\n"
                              f"**Current Frequency**    : {cpufreq.current:.2f}\n"
                              f"**Total Bytes Sent**    : {get_size(net_io.bytes_sent)}\n"
                              f"**Total Bytes Received**    : {get_size(net_io.bytes_recv)}\n",
                        inline=False)
        # embed.add_field(name="OS Server",value=f"",inline=False)
        # embed.add_field(name="Release",value=f"{platform.release()}",inline=False)
        # embed.add_field(name="Processor",value=f"{platform.processor()}",inline=False)
        # # embed.add_field(name="Uptime Server",value=f"{uptime}",inline=False)
        # embed.add_field(name="Current Frequency",value=f"{cpufreq.current:.2f}",inline=False)
        # embed.add_field(name="Total Bytes Sent",value=f"{get_size(net_io.bytes_sent)}",inline=False)
        # embed.add_field(name="Total Bytes Received",value=f"{get_size(net_io.bytes_recv)}",inline=False)

        embed.add_field(name="BOT INFORMATION",
                        value="---------------------------------", inline=False)

        embed.add_field(name="Last boot", value=default.timeago(datetime.now() - self.bot.uptime), inline=True)
        embed.add_field(
            name=f"Developer{'' if len(self.config.owners) == 1 else 's'}",
            value=', '.join([str(self.bot.get_user(x)) for x in self.config.owners]),
            inline=True)
        embed.add_field(name="Library", value="discord.py", inline=True)
        embed.add_field(name="Guilds", value=f"{len(ctx.bot.guilds)} ( avg: {avgmembers} users/server )", inline=True)
        embed.add_field(name="Commands loaded", value=len([x.name for x in self.bot.commands]), inline=True)
        embed.add_field(name="RAM", value=f"{ramUsage:.2f} MB", inline=True)

        await ctx.send(content=f"About **{ctx.bot.user}** | **{self.config.version}**", embed=embed)

    @commands.command(aliases=['clog', 'changel', 'cgl'])
    async def changelog(self, ctx):
        local_tz = pytz.timezone('Asia/Jakarta')
        today = date.today()

        embed = discord.Embed(title=f"**{ctx.bot.user}** | **{self.config.version}**'s Updates")
        embed.add_field(name='Date', value=str(today))
        embed.add_field(name='Revision', value=str(local_tz))

        await ctx.send(embed=embed)



def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def get_processor_info():
    if platform.system() == "Windows":
        return platform.processor()
    elif platform.system() == "Darwin":
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        command = "sysctl -n machdep.cpu.brand_string"
        return subprocess.check_output(command).strip()
    elif platform.system() == "Linux":
        brand_raw = cpuinfo.get_cpu_info()['brand_raw']
        return brand_raw
    return ""


def setup(bot):
    bot.add_cog(SettingsCog(bot))
