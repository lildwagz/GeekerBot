import asyncio
import base64

from datetime import datetime

import arrow
import discord
from discord.ext import commands, tasks

from utils import default


class serverlistener(commands.Cog, name="server listener"):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self.get_activity.start()
        self.loop = asyncio.get_event_loop()


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.bot.app.send_task('celerys.worker.remove_guild_id', kwargs={'guildid': guild.id})
        del self.bot.cache.prefixes[str(guild.id)]
        del self.bot.cache.guildgame_toogle[str(guild.id)]
        del self.bot.cache.levelsystem_toogle[str(guild.id)]
        del self.bot.cache.imgwelcome_toggle[str(guild.id)]
        del self.bot.cache.antiSpam_toogle[str(guild.id)]
        del self.bot.cache.automod_toogle[str(guild.id)]
        del self.bot.cache.captcha_toogle[str(guild.id)]
        del self.bot.cache.antitoxic_toogle[str(guild.id)]
        del self.bot.cache.antiLinks_toogle[str(guild.id)]
        del self.bot.cache.ageaccount_toggle[str(guild.id)]
        del self.bot.cache.allowspam[str(guild.id)]
        del self.bot.cache.ageaccount[str(guild.id)]
        del self.bot.cache.autorole[str(guild.id)]
        content = discord.Embed(color=discord.Color.red())
        content.title = "New guild just leff!"
        content.description = (
            f"Geekerbot just left **{guild}**\nWith **{guild.member_count - 1}** members"
        )
        content.set_thumbnail(url=guild.icon_url)
        content.set_footer(text=f"#{guild.id}")
        content.timestamp = arrow.utcnow().datetime
        logchannel = self.bot.get_channel(769841795219587083)
        await logchannel.send(embed=content)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        dt_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.config.join_message:
            return
        try:
            to_send = sorted([chan for chan in guild.channels if
                              chan.permissions_for(guild.me).send_messages and isinstance(chan, discord.TextChannel)],
                             key=lambda x: x.position)[0]
        except IndexError:
            pass
        else:
            self.bot.app.send_task('celerys.worker.initialize_guild', kwargs={'guild_id': guild.id,'datejoin':dt_string})
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

            # await to_send.send(self.config.join_message)

        content = discord.Embed(color=discord.Color.green())
        content.title = "New guild!"
        content.description = (
            f"Geekerbot just joined **{guild}**\nWith **{guild.member_count - 1}** members"
        )
        content.set_thumbnail(url=guild.icon_url)
        content.set_footer(text=f"#{guild.id}")
        content.timestamp = arrow.utcnow().datetime
        logchannel = self.bot.get_channel(769841795219587083)
        await logchannel.send(embed=content)
        # await asyncio.gather(self.insert_guild_member(guild))

    async def insert_guild_member(self, guild):
        guildidid = guild.id
        member, membercount = [], 0
        await asyncio.sleep(0.0001)

        for i in range(guild.member_count):
            member.append(guild.members[i].id)
            membercount = int(membercount) + 1

        onlyuser = 0
        for i in range(0, membercount):
            filter = member[i]
            if not self.bot.get_user(filter).bot:
                code = int(member[i]) + int(guildidid) - int(member[i] * 2)
                # print(f"{guildidid} {member[i]} {code}")
                self.bot.app.send_task('celerys.worker.insert_new_member',
                                             kwargs={'guildidid': guildidid, 'member': member[i], 'code': str(code)})
                onlyuser = int(onlyuser) + 1


    @tasks.loop(seconds=60)
    async def get_activity(self):
        """
        Get all online users' activity every minute and store in db
        """
        for key in self.bot.cache.guildgame_toogle.keys():

            if self.bot.cache.guildgame_toogle[str(key)]:
                guild = self.bot.get_guild(int(key))
                if guild is None:
                    return

                await asyncio.gather(self.fecth_activity(guild))

    async def fecth_activity(self, guild):
        # print("got called")
        await asyncio.sleep(0.0001)

        for member in guild.members:

            if member.bot or str(member.status) == "offline":
                continue
            if member.activities:
                game_name = None
                for activity in member.activities:
                    if str(activity.type) == "ActivityType.playing":
                        game_name = activity.name
                        break
                if not game_name:
                    continue
                encodeapp = base64.b64encode(bytes(game_name, 'utf-8'))
                filterencode = encodeapp.decode('utf-8')
                # print(guild.id)
                self.bot.app.send_task('celerys.worker.update_guildgames', kwargs={'userid': member.id,
                                                                                   'app_id': filterencode,
                                                                                   'guildidid': guild.id})





def setup(bot):
    bot.add_cog(serverlistener(bot))
