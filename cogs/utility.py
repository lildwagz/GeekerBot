import io
import json
import os
import time

import discord
import typing
import qrcode
import requests
from discord.ext import commands
from cogs.func import CaptchaMaker
from utils import default, converters
import wikipedia


class UtilityCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")

    @commands.command(name='avatar', aliases=['avy'])
    async def avatar(self, ctx, *, user: typing.Union[discord.Member, converters.User] = None):
        """
        Display a user's avatar.
        `user`: The user of which to get the avatar for. Can be their ID, Username, Nickname or Mention. Defaults to you.
        """

        if not user:
            user = ctx.author

        embed = discord.Embed(color=0xdeaa0c, title=f"{user.name}'s avatar")
        embed.description = f'[PNG]({user.avatar_url_as(format="png")}) | [JPEG]({user.avatar_url_as(format="jpeg")}) | [WEBP]({user.avatar_url_as(format="webp")})'
        embed.set_image(url=str(user.avatar_url_as(format='png')))

        if user.is_avatar_animated():
            embed.description += f' | [GIF]({user.avatar_url_as(format="gif")})'
            embed.set_image(url=str(user.avatar_url_as(format='gif')))

        return await ctx.send(embed=embed)

    @commands.command(aliases=['qrcode'])
    async def qr(self, ctx, *, data):
        """ Makes a QR code for you"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(data)
        img = qr.make_image(fill_color="white", back_color="black")
        img.save("databases/qrcodes/QR.png")
        await ctx.send(f"{ctx.author.mention} here it is", file=discord.File("databases/qrcodes/QR.png"))
        os.remove("databases/qrcodes/QR.png")

    @commands.command(name='member', aliases=['memberinfo'])
    async def member(self, ctx, *, member: discord.Member = None):
        """
        Displays a member's account information.
        `member`: The member of which to get information for. Can be their ID, Username, Nickname or Mention. Defaults to you.
        """

        if member is None:
            member = ctx.author

        embed = discord.Embed(colour=self.bot.utils.colours[member.status], title=f'{member}\'s information.')
        embed.description = f'`Discord Name:` {member} {"<:owner:738961071729278987>" if member.id == member.guild.owner.id else ""}\n' \
                            f'`Created on:` {self.bot.utils.format_datetime(datetime=member.created_at)}\n' \
                            f'`Created:` {self.bot.utils.format_difference(datetime=member.created_at)} ago\n' \
                            f'`Badges:` {self.bot.utils.badges(person=member)}\n' \
                            f'`Status:` {member.status.name.replace("dnd", "Do Not Disturb").title()}' \
                            f'{"<:phone:738961150343118958>" if member.is_on_mobile() else ""}\n' \
                            f'`Bot:` {str(member.bot).replace("True", "Yes").replace("False", "No")}\n' \
                            f'`Activity:` {self.bot.utils.activities(person=member)}'

        embed.add_field(name='Server related information:',
                        value=f'`Server nickname:` {member.nick}\n'
                              f'`Joined on:` {self.bot.utils.format_datetime(datetime=member.joined_at)}\n'
                              f'`Joined:` {self.bot.utils.format_difference(datetime=member.joined_at)} ago\n'
                              f'`Join Position:` {sorted(ctx.guild.members, key=lambda m: m.joined_at).index(member) + 1}\n'
                              f'`Top role:` {member.top_role.mention}\n'
                              f'`Role count:` {len(member.roles) - 1}', inline=False)

        embed.set_thumbnail(
            url=str(member.avatar_url_as(format='gif' if member.is_avatar_animated() is True else 'png')))
        embed.set_footer(text=f'ID: {member.id}')
        return await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        """ Pong! """
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        message = await ctx.send(":ping_pong:  Pong")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f":ping_pong: Pong  WS: {before_ws}ms  |  REST: {int(ping)}ms")

    def load_captchas(self):
        with open('Databases/captcha/captchas.json') as json_file:
            return json.load(json_file)

    def save_catchas(self, captchas):
        with open('Databases/captcha/captchas.json', 'w') as outfile:
            json.dump(captchas, outfile)

    @commands.command()
    async def verify(self, ctx):
        captcha_list = self.load_captchas()
        captchaValue = CaptchaMaker.create()
        captcha_list[ctx.author.id] = captchaValue
        self.save_catchas(captcha_list)
        file = "captcha_" + captchaValue + ".png"
        loading = await ctx.send(
            "Please verify that you are a human by completing this challenge.\n**Reply with ?verify "
            "captchahere** to verify your account.\n**Reply with ?new** to get a new challenge.",
            file=discord.File("Databases/captcha/" + file))
        os.system("rm -f " + file)

    @commands.Cog.listener()
    async def on_message(self, message):
        captcha_list = self.load_captchas()
        if message.content.startswith("?verify"):
            if captcha_list[str(message.author.id)] == message.content.split(" ")[1]:
                await message.channel.send("You have been verified.")
                captcha_list.pop(str(message.author.id))
                self.save_catchas(captcha_list)
            else:
                await message.channel.send("Incorrect captcha.")
        elif message.content == "?new":
            captcha_list = self.load_captchas()
            captchaValue = CaptchaMaker.create()
            captcha_list[str(message.author.id)] = captchaValue
            self.save_catchas(captcha_list)
            file = "captcha_" + captchaValue + ".png"
            await message.channel.send(file=discord.File("Databases/captcha/" + file))
            os.system("rm -f " + file)

    @commands.command()
    async def wiki(self, ctx, *, question):
        """search the best definition on wikipedia"""
        try:
            result = wikipedia.summary(question, sentences=2)
            await ctx.send(f"The result of {question} :\n```{result}```")
        except:
            await ctx.send("Invalid command")

    @commands.command(name="weather")
    async def weather(self, ctx, city):
        """gets the current weather """

        baseurl = "https://api.openweathermap.org/data/2.5/weather?"
        url = baseurl + "q=" + city + "&appid=" + self.config.API_KEY_WEATHER
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            main = data['main']
            temperature = main['temp']
            humidity = main['humidity']
            pressure = main['pressure']
            report = data['weather']
            msg1 = discord.Embed(title=f":cityscape:' Today's Weather", color=0x7CFC00)
            msg1.add_field(
                name=f"Temperature : {temperature}\nHumidity : {humidity}\nPressure : {pressure}\nWeather Report : {report[0]['description']}",
                value=f"{city:-^30}", inline=False)
            await ctx.send(embed=msg1)
        else:
            await ctx.channel.send("Unpredictable!")


def setup(bot):
    bot.add_cog(UtilityCommand(bot))
