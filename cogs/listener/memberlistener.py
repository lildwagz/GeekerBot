import time
from datetime import datetime

import discord
from discord.ext import commands
import random

from discord.utils import get

from cogs.listener.antilinklistener import antilinks
from cogs.listener.antitoxiclistener import antitoxic
from cogs.listener.triggeredwordlistener import triggeredword

FILE_EMBED_DESCRIPTION = (
    f"""
    **Oh No!** Your message got zapped by our spam filter.
    We currently don't allow `.txt` attachments or any source files, so here are some tips you can use: \n
    • Try shortening your message, if it exceeds 2000 character limit
    to fit within the character limit or use a pasting service (see below) \n
    • If you're showing code, you can use codeblocks or use a pasting service.
    """
)


class memberlistener(commands.Cog, name="member listener"):
    def __init__(self, bot):
        self.bot = bot

    def check(self, message):
        return message.author == message.author and (datetime.utcnow() - message.created_at).seconds < 15

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return
        if message.guild is None:
            return
        whitelist = ['.3gp', '.svg', '.txt']
        guildidid = message.guild.id
        # if message.attachments:
        #     file_extensions = {splitext(attachment.filename.lower())[1] for attachment in message.attachments}
        #     is_blocked = file_extensions - set(whitelist)
        #
        #     file_pastes = []
        channel = self.bot.get_channel(773837322612506634)
        #     # await channel.send(f"{is_blocked}")
        #
        #     if is_blocked:
        #         log_message = f"User <@{message.author.id}> posted a message on {message.guild.id} with protected attachments"
        #
        #
        #         embed = Embed(description=FILE_EMBED_DESCRIPTION, color=Color.dark_blue())
        #
        #         await channel.send(f"Hey {message.author.mention}!", embed=embed)
        #
        #
        if len(message.attachments) > 0:
            for i in message.attachments:
                embed = discord.Embed(title=f"**{message.author} has sent a image.**",
                                          description=f"In {message.channel.mention}.\n**__User informations :__**\n**Name :** {message.author}\n**Id :** {message.author.id}\n"
                                                      f"Guiold : {message.guild.name}\n**The image :",
                                          color=0xff0000)
                embed.set_image(url=i.url)

                await channel.send(embed=embed)

        statusantitoxic = self.bot.cache.antitoxic_toogle.get(str(guildidid))
        if statusantitoxic:
            await antitoxic.on_anti_toxic(self, message)
        statusantilink = self.bot.cache.antiLinks_toogle.get(str(guildidid))
        # print(self.bot.cache.antitoxic_toogle.get(str(guildidid)))
        if statusantilink:
            await antilinks.on_anti_links(self, message)
        # statusAntiSpam = self.bot.cache.antiSpam_toogle.get(str(guildidid))
        # if statusAntiSpam:
        #     await antispam.on_anti_spam(self, message)

        if self.bot.cache.trigerword_toogle.get(str(guildidid)):
            await triggeredword.on_triggered_word(self, message)

        getstatus = self.bot.cache.levelsystem_toogle.get(str(guildidid))
        if getstatus:
            codeuser = str(f"USR{int(message.author.id) + int(guildidid) - int(message.author.id * 2)}")
            resultq = self.bot.cache.users.get(codeuser)
            if resultq is None:
                code = int(message.author.id) + int(guildidid) - int(message.author.id * 2)
                self.bot.cache.users["USR" + str(code)] = message.author.id, guildidid, 1, 0, 0
                self.bot.app.send_task('celerys.worker.insert_new_member',
                                       kwargs={'guildidid': guildidid, 'member': message.author.id, 'code': str(code)})
                return

            # print(resultq)
            try:
                user_id, guild_id, user_level, user_exp, user_points = resultq
            except TypeError as e:
                self.bot.cache.users["USR" + str(codeuser)] = message.author.id, guildidid, 1, 0, 0
                resultq = self.bot.cache.users.get(codeuser)
                user_id, guild_id, user_level, user_exp, user_points = resultq

            # print(user_level)
            points = random.randint(1, 10 * user_level)
            # message_str = re.sub('<[^>]+>', '', message.content).strip()
            # if "http" in message_str:
            #     message_str = " ".join([word for word in message_str.split(" ") if not word.startswith("http")])
            exp = 5
            next_level_exp = 50 * ((user_level + 1) ** 2) - (50 * (user_level + 1))
            # print(f"{user_id} {user_level} {user_level} {user_points} {guildidid}")

            if user_exp > next_level_exp:
                user_level += 1
                await message.channel.send(
                    '{} reached level {}'.format(message.author.mention, user_level, user_level))
            # await self.set_user_data(user_id, user_level, user_exp + exp, user_points + points, guildidid)
            self.bot.cache.users[codeuser] = user_id, guild_id, user_level, user_exp + exp, user_points + points
            self.bot.app.send_task('celerys.worker.set_user_data',
                                   kwargs={'user_id': user_id, 'user_level': user_level, 'user_exp': user_exp + exp,
                                           'user_points': user_points + points, 'guildidid': guildidid})

            # print(self.bot.cache.users.get(codeuser))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Event handler when user leaves the server
        Add a new database entry
        """
        # Do nothing if author is bot
        guildidid = member.guild.id
        code = int(member.id) + int(guildidid) - int(member.id * 2)

        if member.bot:
            return
        minage = self.bot.cache.ageaccount.get(str(guildidid))
        toogleminage = self.bot.cache.ageaccount_toggle.get(str(guildidid))
        if toogleminage:
            userAccountDate = int(time.time() - member.created_at.timestamp())
            if int(userAccountDate) < minage:
                minAccountDate = minage / 3600
                embed = discord.Embed(title=f"**YOU HAVE BEEN KICKED FROM {member.guild.name}**",
                                      description=f"Reason : minimal account that allowed to join is more than ({minAccountDate} hours).",
                                      color=0xff0000)
                await member.send(embed=embed)
                await member.kick()
                return
        self.bot.cache.users["USR" + str(code)] = member.id, guildidid, 1, 0, 0
        self.bot.app.send_task('celerys.worker.insert_new_member',
                               kwargs={'guildidid': guildidid, 'member': member.id, 'code': str(code)}
                               )
        getautorole = self.bot.cache.autorole.get(str(guildidid))

        if getautorole != 0:
            role = member.guild.get_role(getautorole)
            try:
                await member.add_roles(role)
            except discord.errors.Forbidden:
                await member.guild.send(
                    f"`error: {role} is higher than me`"
                )
            except Exception as e:
                pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.id == self.bot.user.id:
            return
        guildidid = member.guild.id

        code = int(member.id) + int(guildidid) - int(member.id * 2)
        try:

            del self.bot.cache.users["USR" + str(code)]
            self.bot.app.send_task('celerys.worker.remove_member',
                                   kwargs={'usedid': member.id, 'guildid': member.guild.id}
                                   )
        except Exception as e:
            pass
        # print("Status of the Task "+ str(result.state))

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.guild.id == after.guild.id:
            if self.bot.cache.trigerrole_toogle.get(str(after.guild.id)):
                getrolenew = get(after.roles, id=self.bot.cache.triger_role.get(str(after.guild.id))[0])
                getroleold = get(after.roles, id=self.bot.cache.triger_role.get(str(after.guild.id))[1])

                if len(before.roles) < len(after.roles):
                    newRole = next(role for role in after.roles if role not in before.roles)
                    try:
                        if newRole.id == getrolenew.id:
                            try:
                                await after.remove_roles(getroleold)
                            except discord.errors.Forbidden as e:
                                await after.guild.owner.send(e)
                    except discord.errors.Forbidden as e:
                        await after.guild.owner.send(e)

                    except AttributeError as e:
                        pass

            if self.bot.cache.antitoxic_toogle.get(str(after.guild.id)):
                if not after.bot:
                    await antitoxic.on_anti_toxic_member_update(self, before, after)


def setup(bot):
    bot.add_cog(memberlistener(bot))
