import discord
import json

from discord.ext import commands
from discord.ext.commands import has_permissions


class AllowSpamCog(commands.Cog, name="allow spam command"):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='allowspam', aliases=["aspam"])
    @has_permissions(administrator=True)
    async def allowspam(self, ctx, channel, remove="False"):

        channel = channel.replace("<", "");
        channel = channel.replace("#", "");
        channel = channel.replace(">", "")

        if remove == "False":
            try:
                channel = int(channel)
                spamChannel = self.bot.get_channel(channel)

                # Edit configuration.json
                with open("config.json", "r") as config:
                    data = json.load(config)

                if spamChannel.id in data["allowSpam"]:
                    embed = discord.Embed(title=f"**ERROR**",
                                          description=f"The channel where you want to allow to spam is already ignored by anti spam.",
                                          color=0xe00000)  # Red
                    embed.set_footer(text="Bot Created by Darkempire#8245")
                    return await ctx.channel.send(embed=embed)

                data["allowSpam"].append(spamChannel.id)
                newdata = json.dumps(data, indent=4, ensure_ascii=False)

                with open("config.json", "w") as config:
                    config.write(newdata)
                embed = discord.Embed(title=f"**SUCCESS**",
                                      description=f"The <#{spamChannel.id}> channel is ignored by the anti spam.",
                                      color=0x2fa737)  # Green
                embed.set_footer(text="Bot Created by Darkempire#8245")
                await ctx.channel.send(embed=embed)

            except:
                embed = discord.Embed(title=f"**ERROR**",
                                      description=f"The channel where you want to allow to spam must be a number\nFollow the example : ``{self.bot.command_prefix}allowspam <#channel>``",
                                      color=0xe00000)  # Red
                embed.set_footer(text="Bot Created by Darkempire#8245")
                return await ctx.channel.send(embed=embed)
        else:
            try:
                channel = int(channel)
                spamChannel = self.bot.get_channel(channel)

                # Edit configuration.json
                with open("config.json", "r") as config:
                    data = json.load(config)

                if not spamChannel.id in data["allowSpam"]:
                    embed = discord.Embed(title=f"**ERROR**",
                                          description=f"The channel where you want to disable the spam is already disabled.",
                                          color=0xe00000)  # Red
                    embed.set_footer(text="Bot Created by Darkempire#8245")
                    return await ctx.channel.send(embed=embed)

                data["allowSpam"].remove(spamChannel.id)
                newdata = json.dumps(data, indent=4, ensure_ascii=False)

                with open("config.json", "w") as config:
                    config.write(newdata)
                embed = discord.Embed(title=f"**SUCCESS**",
                                      description=f"The <#{spamChannel.id}> channel is not ignored by the anti spam.",
                                      color=0x2fa737)  # Green
                embed.set_footer(text="Bot Created by Darkempire#8245")
                await ctx.channel.send(embed=embed)

            except:
                embed = discord.Embed(title=f"**ERROR**",
                                      description=f"The channel where you want to disable the spam must be a number\nFollow the example : ``{self.bot.command_prefix}allowspam <#channel> remove``",
                                      color=0xe00000)  # Red
                embed.set_footer(text="Bot Created by Zam")
                return await ctx.channel.send(embed=embed)



def setup(bot):
    bot.add_cog(AllowSpamCog(bot))
