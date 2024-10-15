import asyncio

from discord.ext import commands
import random
import discord
from cogs.mod2 import color_list


class antispam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def on_anti_spam(self, message):
        logs = {}
        timeout = 3
        guildidid = message.guild.id
        allowSpam = self.bot.cache.allowspam[str(message.guild.id)]

        if message.author.guild_permissions.administrator:
            return

        if message.channel.id == allowSpam:
            return

        try:
            for role in message.author.roles:
                if role.id in self.bot.cache.whitelist[str(message.guild.id)]:
                    return
        except KeyError as e:
            pass
        counter = 0
        i = message.author.id
        if logs:
            for index, val in enumerate(logs):
                if i in val.keys():
                    print("ada")
                    return



        else:
            data = {
                i: []
            }

        # print(list(logs))

        # codeuser = str(f"USR{int(message.author.id) + int(guildidid) - int(message.author.id * 2)}")
        # self.bot.app.send_task('celerys.worker.insert_new_member',
        #                        kwargs={'guildidid': message.guild.id, 'member': message.author.id,
        #                                'code': str(codeuser)})
        # print(list(filter(lambda m: self.check(m), self.bot.cached_messages())))
        # if len(list(filter(lambda m: self.check(m), self.bot.cached_messages))) >= 6 and len(
        #         list(filter(lambda m: self.check(m), self.bot.cached_messages))) < 10:
        #     await message.channel.send(f"{message.author.mention} don't do that bruh!")
        # elif len(list(filter(lambda m: self.check(m), self.bot.cached_messages))) >= 10:
        #     dt_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #     # await message.channel.send(f"{message.author.mention} bastard")
        #     kode_user = int(message.author.id) + int(message.guild.id) - int(message.author.id * 2)
        #     await antispam.do_warn(self, message, kode_user, dt_string)

    async def do_warn(self, message, kode_user, dt_string):
        await asyncio.sleep(0.0001)
        """
        do warn
        :param kode_user:
        :return:
        """
        i = str(f"USR{kode_user}")
        # print(i)
        if self.bot.cache.warns:
            for index, val in enumerate(self.bot.cache.warns):
                # for koy in val.keys():
                #     print(koy)
                # print(self.bot.cache.warns[index])
                # print(val.keys)
                # print(i)
                if i in val.keys():
                    # print(self.bot.cache.warns[index][i])
                    listwarns = self.bot.cache.warns[index][i]
                    for subindex, key in enumerate(listwarns):
                        # print(f"keys {listwarns[0][list(key.keys())[0]]}")
                        try:
                            checkpoint = listwarns[-1][list(key.keys())[0]]
                            lastwarnkey = list(key.keys())[0]
                            if len(listwarns) >= 3:
                                embed = discord.Embed(
                                    title=f"**YOU HAVE BEEN KICKED FROM {message.author.guild.name}**",
                                    description=f"Reason : You spammed.", color=0xff0000)
                                try:
                                    await message.author.kick()  # Kick the user
                                    await message.channel.send(
                                        f"{message.author.mention} hell yeah this dude has no chill !")
                                    await message.author.send(embed=embed)
                                except Exception as e:
                                    return await message.channel.send(e)

                            await antispam.send_warnd(self, message,
                                                      index=index,
                                                      kodeuser=i,
                                                      lastwarnkey=lastwarnkey,
                                                      dt_string=dt_string,
                                                      newuser=False
                                                      )
                            # print("sent!")
                            return

                        except Exception as e:
                            pass
                    return
            await antispam.send_warnd(self, message,
                                      kodeuser=i,
                                      dt_string=dt_string,
                                      newuser=True
                                      )

            return
        else:
            await antispam.send_warnd(self, message,
                                      kodeuser=i,
                                      dt_string=dt_string,
                                      newuser=True
                                      )
            return

    async def send_warnd(self, message, **kwargs):
        global lastwarnkey, newuser, index
        if kwargs.get("newuser"):
            newuser = True
            lastwarnkey = 0
        else:
            lastwarnkey = kwargs.get("lastwarnkey")
            index = kwargs.get("index")
            newuser = False
        dt_string = kwargs.get("dt_string")
        kodeuser = kwargs.get("kodeuser")

        # print(message)
        warnerName = "GeekerBot"
        warnerId = 772748636554788895
        color = random.choice(color_list)
        reason = "spamming"

        new_amount = lastwarnkey + 1
        offender_name = message.author.name
        position = new_amount
        user_id = message.author.id
        warner_id = warnerId
        warner_name = warnerName
        reasons = reason
        channel = message.channel.id
        datetimes = dt_string
        if newuser:
            data = {
                kodeuser: [{new_amount: [offender_name, position, user_id, warner_id, warner_name, reasons,
                                         channel, datetimes]}]
            }
            datas = {'kode_user': kodeuser,
                     'code': new_amount,
                     'offender_name': offender_name,
                     'position': position,
                     'user_id': user_id,
                     'warner': warner_id,
                     'warner_name': warner_name,
                     'reason': reasons,
                     'channel': channel,
                     'datetime': datetimes}
            self.bot.cache.warns.append(data)
            self.bot.app.send_task('celerys.worker.insert_warn', kwargs=datas)
        else:
            data = {
                new_amount: [offender_name, position, user_id, warner_id, warner_name, reasons, channel,
                             datetimes]
            }
            datas = {'kode_user': kodeuser,
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
            self.bot.cache.warns[index][kodeuser].append(data)
        # print(self.bot.cache.warns[index])

        embed = discord.Embed(
            title=f"{offender_name}'s new warn",
            color=random.choice(color_list)
        )
        embed.set_author(
            name=message.author.name,
            icon_url=message.author.avatar_url,
            url=f"https://discord.com/users/{message.author.id}/"
        )
        embed.add_field(
            name=f"Warn {new_amount}",
            value=f"Warner: {warner_name} (<@{warner_id}>)\nReason: {reasons}\nChannel: <#{str(channel)}>\nDate and Time: {dt_string}",
            inline=True
        )
        await message.channel.send(
            content="Successfully added new warn.",
            embed=embed
        )


def setup(bot):
    bot.add_cog(antispam(bot))
