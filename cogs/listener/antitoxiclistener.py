from better_profanity import profanity
from discord.ext import commands
import random

import discord


class antitoxic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def on_anti_toxic(self, message):
        try:
            for role in message.author.roles:
                if role.id in self.bot.cache.whitelist[str(message.guild.id)]:
                    return
        except KeyError as e:
            pass
        embed = discord.Embed(title=f'**{message.author}** has been warned!',
                              description=f'**Reason**: Using blacklisted content\n**Content**: ||{message.content}||',
                              color=0x0fa7d0)
        embed.set_thumbnail(url=message.author.avatar_url)
        if profanity.contains_profanity(message.content):
            if self.bot.cache.infractionchannel.get(str(message.guild.id)) is not None:
                channellog = self.bot.get_channel(self.bot.cache.infractionchannel.get(str(message.guild.id)))
                try:
                    await message.delete()
                    await channellog.send(embed=embed)
                except discord.errors.Forbidden:
                    await channellog.send("`error: I'm missing required discord permission [ manage messages ]`")
                    await channellog.send(embed=embed)

            else:
                try:
                    await message.delete()
                    await message.channel.send(embed=embed, delete_after=10)
                except discord.errors.Forbidden:
                    await message.channel.send("`error: I'm missing required discord permission [ manage messages ]`")

    async def on_anti_toxic_member_update(self, before, member):
        try:
            for role in member.roles:
                if role.id in self.bot.cache.whitelist[str(member.guild.id)]:
                    return
        except KeyError as e:
            pass
        Titles = ['Lovely', 'Adorable', 'Cute', 'Friendly', 'Aesthetic', 'Gorgeous', 'Attractive', 'Beautiful']
        nameList = ['Cool Dude', 'Squirrel', 'Panda', 'Lion', 'Cat', 'Hamster', 'Frog', 'Puppy', 'Turtle']
        if self.bot.cache.infractionchannel.get(str(member.guild.id)) is not None:
            channellog = self.bot.get_channel(self.bot.cache.infractionchannel.get(str(member.guild.id)))
            if profanity.contains_profanity(member.display_name):
                try:
                    await member.edit(nick=f'{random.choice(Titles)} {random.choice(nameList)}')
                except discord.errors.Forbidden as e:
                    embed = discord.Embed(title=f"Hello **{member.name}**!",
                                          description="We've noticed that your nickname didn't comply with our **ToS** so "
                                                      "please change your name as soon as possible.",
                                          color=0x0fa7d0)
                    embed.set_thumbnail(url=member.avatar_url)
                    return await channellog.send(
                        f"`error: I'm missing required discord permission [manage nicknames or change nickname] or "
                        f"the member has higher role than me` ",embed=embed

                    )
                except Exception as e:
                    pass
                try:
                    embed = discord.Embed(title=f"Hello **{member.name}**!",
                                          description="We've noticed that your nickname didn't comply with our **ToS** so "
                                                      "we decided to rename you automatically.",
                                          color=0x0fa7d0)
                    embed.set_thumbnail(url=member.avatar_url)
                    embed.set_footer(text='if you think this was a mistake please let us know')
                    await channellog.send( embed=embed)
                except Exception as e:
                    channellog.send(f"An exception occurred while sending the member the notice message: {e}")

            if len(member.activities) >= 1:
                if str(before.status) == "offline":
                    return
                if member.activities[0].name is not None:
                    if len(before.activities) >= 1 and before.activities[0].name is not None :
                        if before.activities[0].name != member.activities[0].name:
                            if profanity.contains_profanity(member.activities[0].name):
                                embed = discord.Embed(title=f'**{member.name}** has been warned!',
                                                      description=f'**Reason**: Using blacklisted content in their '
                                                                  f'status\n**Content**: ||{member.activities[0].name}||',
                                                      color=0x0fa7d0)
                                embed.set_thumbnail(url=member.avatar_url)
                                await channellog.send(f"{member}", embed=embed)
                            else:
                                pass
                    else:
                        if profanity.contains_profanity(member.activities[0].name):
                            embed = discord.Embed(title=f'**{member.name}** has been warned!',
                                                  description=f'**Reason**: Using blacklisted content in their '
                                                              f'status\n**Content**: ||{member.activities[0].name}||',
                                                  color=0x0fa7d0)
                            embed.set_thumbnail(url=member.avatar_url)
                            await channellog.send(f"{member}", embed=embed)



def setup(bot):
    bot.add_cog(antitoxic(bot))
