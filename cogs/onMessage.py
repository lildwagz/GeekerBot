import discord
import json

from discord.ext import commands
from discord.utils import get

from datetime import datetime, timedelta



class OnMessageCog(commands.Cog, name="on message"):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        with open("config.json", "r") as config:
            data = json.load(config) 
            antiSpam = data["antiSpam"] 
            allowSpam = data["allowSpam"]
            logChannel = self.bot.get_channel(data["logChannel"])

        if antiSpam:
            def check (message):
                return message.author == message.author and (datetime.utcnow() - message.created_at).seconds < 15

            try :
                if message.author.guild_permissions.administrator:
                    return

                if message.channel.id in allowSpam:
                    return

                if len(list(filter(lambda m: check(m), self.bot.cached_messages))) >= 8 and len(list(filter(lambda m: check(m), self.bot.cached_messages))) < 14:
                    await message.channel.send(f"{message.author.mention} don't do that bruh!")
                elif len(list(filter(lambda m: check(m), self.bot.cached_messages))) >= 14:
                    embed = discord.Embed(title = f"**YOU HAVE BEEN KICKED FROM {message.author.guild.name}**", description = f"Reason : You spammed.", color = 0xff0000)
                    await message.author.send(embed = embed)
                    await message.author.kick() # Kick the user
                    await message.channel.send(f"{message.author.mention} hell yeah this dude has no chill !")
                # Logs
                try:
                    embed = discord.Embed(title = f"**{message.author} has been kicked.**", description = f"**Reason :** He spammed in {message.channel}.\n\n**__User informations :__**\n\n**Name :** {message.author}\n**Id :** {message.author.id}", color = 0xff0000)
                    await logChannel.send(embed = embed)
                except:
                    pass
            except:
                pass

def setup(bot):
    bot.add_cog(OnMessageCog(bot))

