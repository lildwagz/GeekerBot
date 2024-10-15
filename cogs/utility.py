"""MIT License

Copyright (c) 2020 lildwagz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import base64
import collections
import glob
import json
import os
import random
import re
import time
import libmorse as morse
from datetime import datetime
from os.path import getsize

import aiohttp
import discord
import typing

import pytube
import qrcode
import regex
import requests
from aiohttp import ClientSession
from discord import Embed
from discord.ext import commands, flags
import arrow
from requests import get
from pytube import YouTube


from cogs.func import CaptchaMaker, mp3
from utils import default, converters, utilss, http, parsers, permissions
# import wikipedia

# start_time = time.time()
from utils.ChooseEmbed import ChooseEmbed
# from utils.pagination import EmbedPaginator


class UtilityCommand(commands.Cog):
    def __init__(self, bot):

        self.bot = bot
        self.config = default.get("config.json")
        self.default_client = ClientSession()
        self.ig_colors = [
            int("405de6", 16),
            int("5851db", 16),
            int("833ab4", 16),
            int("c13584", 16),
            int("e1306c", 16),
            int("fd1d1d", 16),
            int("f56040", 16),
            int("f77737", 16),
            int("fcaf45", 16),
        ]

    @commands.command(name='avatar', aliases=['avy'])
    async def avatar(self, ctx, *, user: typing.Union[discord.User, converters.User] = None):
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
            border=1,
        )
        qr.make(fit=True)
        qr.add_data(data)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save("Databases/qrcodes/QR.png")
        await ctx.send(f"{ctx.author.mention} here it is",
                       file=discord.File("Databases/qrcodes/QR.png"))
        os.remove("Databases/qrcodes/QR.png")

    @commands.command(name="readqr")
    async def readqr(self, ctx):
        """Reads qr code from a image."""
        at = ctx.message.attachments

        if len(at) < 1:
            return await utilss.send_error_message(ctx,"Please atach an qrcode image to decode.")
        lnk = at[0].url

        async with aiohttp.ClientSession() as s:
            async with s.get(f"http://api.qrserver.com/v1/read-qr-code/?fileurl={lnk}") as r:
                data = await r.json()

        if data[0]["symbol"][0]["data"] is not None:
            await ctx.send("Data : ```" + data[0]["symbol"][0]["data"]+"```")
        else:

            await utilss.send_error_message(ctx,"This is not a valid qr code!")


    @commands.guild_only()
    @commands.command(name='member', aliases=['memberinfo'])
    async def member(self, ctx, *, member: typing.Union[discord.Member, converters.User] = None):
        """
        Displays a member's account information.
        `member`: The member of which to get information for.Username, Nickname or Mention. Defaults to you.
        """

        if member is None:
            member = ctx.author

        embed = discord.Embed(colour=self.bot.utils.colours[member.status], title=f'{member}\'s information.')
        embed.description = f'`Discord Name:` {member} {"<:owner:808441992563785789>" if member.id == member.guild.owner.id else ""}\n' \
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
        # before = time.monotonic()
        before_ws = int(round(self.bot.latency * 100, 1))
        # message = await ctx.send(":ping_pong:  Pong")
        # ping = (time.monotonic() - before) * 100
        # await message.edit(content=f":ping_pong: Pong  WS: {before_ws}ms  |  REST: {int(ping)}ms")
        before = time.monotonic()
        message = await ctx.send(":ping_pong:  Pong")

        pingbot = (time.monotonic() - before) * 100

        if pingbot <= 50:
            embed = discord.Embed(title="COMMAND LATENCY",
                                  description=f":ping_pong:  The ping is **{int(pingbot)}** ms!",

                                  color=0x44ff44)
            embed.add_field(name="DISCORD LATENCY", value=f"The ping is **{int(before_ws)}** ms!")
        elif pingbot <= 100:
            embed = discord.Embed(title="COMMAND LATENCY",
                                  description=f":ping_pong:  The ping is **{int(pingbot)}** ms!",
                                  color=0xffd000)
            embed.add_field(name="DISCORD LATENCY", value=f"The ping is **{int(before_ws)}** ms!")

        elif pingbot <= 200:
            embed = discord.Embed(title="COMMAND LATENCY",
                                  description=f":ping_pong:  The ping is **{int(pingbot)}** ms!",
                                  color=0xff6600)
            embed.add_field(name="Disocord LATENCY", value=f"The ping is **{int(before_ws)}** ms!")

        else:
            embed = discord.Embed(title="COMMAND LATENCY",
                                  description=f":ping_pong:  The ping is **{int(pingbot)}** ms!",
                                  color=0x990000)
            embed.add_field(name="DISCORD LATENCY", value=f"The ping is **{before_ws}** ms!")

        await message.edit(content="", embed=embed)

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

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     captcha_list = self.load_captchas()
    #     if message.content.startswith("?verify"):
    #         if captcha_list[str(message.author.id)] == message.content.split(" ")[1]:
    #             await message.channel.send("You have been verified.")
    #             captcha_list.pop(str(message.author.id))
    #             self.save_catchas(captcha_list)
    #         else:
    #             await message.channel.send("Incorrect captcha.")
    #     elif message.content == "?new":
    #         captcha_list = self.load_captchas()
    #         captchaValue = CaptchaMaker.create()
    #         captcha_list[str(message.author.id)] = captchaValue
    #         self.save_catchas(captcha_list)
    #         file = "captcha_" + + ".png"
    #         await message.channel.send(file=discord.File("Databases/captcha/" + file))
    #         os.system("rm -f " + file)
    #
    # @commands.command()
    # async def wiki(self, ctx,*, question ):
    #     """search the best definition on wikipedia"""
    #     try:
    #         result = wikipedia.summary(f'{question}', sentences=2)
    #         await ctx.send(f"The result of {question} :\n```{result}```")
    #     except Exception as e:
    #         await ctx.send(f"Invalid command\n`{e}`")

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

    @commands.group(
        name="howto",
        invoke_without_command=True,
        aliases=['how-to']
    )
    async def howto(self, ctx):
        """Show useful information for newcomers"""
        await ctx.send_help('how-to')

    @howto.command(
        name='codeblocks',
        aliases=['codeblock', 'code-blocks', 'code-block', 'code']
    )
    async def codeblocks(self, ctx):
        """Instructions on how to properly paste code"""
        code_instructions = (
            "Discord has an awesome feature called **Text Markdown** which "
            "supports code with full syntax highlighting using codeblocks."
            "To use codeblocks all you need to do is properly place the "
            "backtick characters *(not single quotes)* and specify your "
            "language *(optional, but preferred)*.\n\n"
            "**This is what your message should look like:**\n"
            "*\\`\\`\\`[programming language]\nYour code here\n\\`\\`\\`*\n\n"
            "**Here's an example:**\n"
            "*\\`\\`\\`python\nprint('Hello world!')\n\\`\\`\\`*\n\n"
            "**This will result in the following:**\n"
            "```python\nprint('Hello world!')\n```\n"
            "**NOTE:** Codeblocks are also used to run code via `/run`."
        )
        link = (
            'https://support.discordapp.com/hc/en-us/articles/'
            '210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-'
        )

        e = Embed(title='Text markdown',
                  url=link,
                  description=code_instructions,
                  color=0x2ECC71)
        await ctx.send(embed=e)

    @howto.command(
        name='ask',
        aliases=['questions', 'question']
    )
    async def ask(self, ctx):
        """How to properly ask a question"""
        ask_instructions = (
            "From time to time you'll stumble upon a question like this:\n"
            "*Is anyone good at [this]?* / *Does anyone know [topic]?*\n"
            "Please **just ask** your question.\n\n"
            "• Make sure your question is easy to understand.\n"
            "• Use the appropriate channel to ask your question.\n"
            "• Always search before you ask (the internet is a big place).\n"
            "• Be patient (someone will eventually try to help you)."
        )

        e = Embed(title='Just ask',
                  description=ask_instructions,
                  color=0x2ECC71)
        await ctx.send(embed=e)

    # @commands.command(description="Returns the uptime of the bot.")
    # async def uptime(self,ctx):
    #     # Gets the time and substracts it to the current time.
    #     current_time = time.time()
    #     difference = int(round(current_time - start_time))
    #     text = str(datetime.timedelta(seconds=difference))
    #
    #     # Embed.
    #     embed = discord.Embed(
    #         color=random.choice(color_list)
    #     )
    #     embed.add_field(name="Uptime", value=text)
    #
    #     # Sends.
    #     await ctx.channel.send(embed=embed)

    @commands.command(name='feedback',
                      aliases=['question'], usage="(Feedback-Goes-Here)")
    @commands.cooldown(5, 600, commands.BucketType.guild)
    async def feedback(self, ctx, *, feedback):
        """Give feedback to improve the bot's functionality"""
        if feedback is None:
            if random.randint(0, 2) == 0:
                await ctx.send("😡, It's blank you NONCE!")
            else:
                await ctx.send("😕, Is it in invisible ink?")
        else:
            await ctx.send("Thanks, if this is any good I'll give you some garlicoin ")
            embed = discord.Embed(description=feedback, color=random.randint(0, 0xFFFFFF))
            embed.set_footer(text=f'From {ctx.author.name} | {ctx.guild.name}')
            await self.bot.get_channel(797027502387232788).send(embed=embed)

    @commands.guild_only()
    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        """
            -leaderboard -> posts the current exp/points leaderboard in the channel
            """
        if self.bot.cache.levelsystem_toogle.get(
                str(ctx.guild.id)) is None or not self.bot.cache.levelsystem_toogle.get(str(ctx.guild.id)):
            return await utilss.send_error_message(ctx, "please turn on leveling system first !")
        guildidid = ctx.guild.id

        result = self.bot.app2.send_task('celerys.worker2.get_leaderboard', kwargs={'guildid': guildidid})

        content = ''
        counter = 1
        conauth = 1
        within = False
        author = ''
        for user_info in result.get():
            kode_user, user_id, guild_id, level, exp, points = user_info

            if counter == 1:
                content += f'**{counter}** - :crown: __{self.bot.get_user(user_id)}__ - level {level} - {exp} xp\n'
                conauth = counter
            elif counter == 2:
                content += f'**{counter}** - :second_place: __{self.bot.get_user(user_id)}__ - level {level} - {exp} xp\n'
                conauth = counter
            elif counter == 3:
                content += f'**{counter}** - :third_place: __{self.bot.get_user(user_id)}__ - level {level} - {exp} xp\n'
                conauth = counter
            else:
                content += f'**{counter}** - __{self.bot.get_user(user_id)}__ - level {level} - {exp} xp\n'
                conauth = counter
            counter += 1
            if user_id == ctx.author.id:
                author = f'**{conauth}** - __**{self.bot.get_user(user_id)}**__ - level {level} - {exp} xp\n'

        if not within:
            content += "**------------------------------------------------------------**\n" + author
        embed = discord.Embed(
            title=f"{ctx.guild.name}'s leaderboard",
            color=ctx.author.color,
            description=content
        )
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command(name="dumpmsg", pass_context=True)
    async def dumpMessageHistory(self, ctx, limit, filters=[]):
        '''Fetch message from channel into file'''
        # await sleep(0.5)
        # await ctx.delete()

        limit_num = 0
        try:
            limit_num = int(limit)
        except:
            limit_num = 1

        if limit == 0:
            limit = None

        if filters is not []:
            pass

        messages = {}
        iter = 1
        async with ctx.channel.typing():
            async for message in ctx.channel.history(limit=limit_num):
                message_content = {}
                message_content["author"] = {"id": message.author.id, "name": message.author.name}
                message_content["created_at"] = message.created_at.strftime("%m/%d/%Y, %H:%M:%S")
                message_content["content"] = message.content
                message_content["embeds"] = [str(embed.url) for embed in message.embeds]
                message_content["attachments"] = [attachment.url for attachment in message.attachments]
                message_content["jump_url"] = message.jump_url
                messages[f"Message-{str(iter)}"] = message_content
                # print(iter, end="\r")
                iter += 1

        with open("out.json", "w") as f:
            json.dump(messages, f, indent=4)
        with open("out.json", "rb") as f:
            discord_file = discord.File(f, "history.json")
            response_message = await ctx.send(files=[discord_file])
        os.remove("out.json")

    @commands.command(pass_context=True)
    async def printroles(self, ctx):
        """Print all the current defined roles in the server."""
        server = ctx.message.guild
        roles_list = []
        for role in server.roles:
            roles_list.append("`" + role.name + "`" + " :hammer_pick:")

        await ctx.send("\n".join(roles_list))

    @commands.command(name='sof')
    @commands.cooldown(rate=1, per=20.0, type=commands.BucketType.user)
    async def stackoverflow(self, ctx, *args):
        if len(args) == 0:
            return await ctx.bot.util.send_error_message(ctx, 'Hey fellow developer, Try add a question!')
        else:
            try:
                data = await utilss.Utilss.get_request(self, url="https://api.stackexchange.com/2.2/search/advanced",
                                                       json=True,
                                                       raise_errors=True,
                                                       q=' '.join(args),
                                                       site='stackoverflow',
                                                       page=2,
                                                       answers=2,
                                                       order='asc',
                                                       sort='relevance'
                                                       )
                leng = len(data['items'])
                ques = data['items'][0]
                tags = ''
                for i in range(len(ques['tags'])):
                    if i == len(ques['tags']) - 1:
                        tags += '[' + str(ques['tags'][i]) + '](https://stackoverflow.com/questions/tagged/' + str(
                            ques['tags'][i]) + ')'
                        break
                    tags += '[' + str(ques['tags'][i]) + '](https://stackoverflow.com/questions/tagged/' + str(
                        ques['tags'][i]) + ') | '
                embed = discord.Embed(title=ques['title'], description='**' + str(
                    ques['view_count']) + ' *desperate* developers looked into this post.**\n**TAGS:** ' + str(tags),
                                      url=ques['link'], colour=ctx.guild.me.roles[::-1][0].color)
                embed.set_author(name=ques['owner']['display_name'], url=ques['owner']['link'],
                                 icon_url=ques['owner']['profile_image'])
                embed.set_footer(text='Shown 1 result out of ' + str(leng) + ' results!')
                await ctx.send(embed=embed)
            except Exception as e:
                return await ctx.send( 'There was an error on searching! Please check your spelling :eyes:')
                # print(e)

    @commands.command(name='films')
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def films(self, ctx, *, args=None):
        """gets the film with the most star ratings"""
        wait = await ctx.send(' | Please wait... Getting data...')
        data = await http.get(
            'https://ghibliapi.herokuapp.com/films',
            res_method="json"
        )
        if args is None:
            films = ""
            for i in range(len(data)):
                films = films + '(' + str(int(i) + 1) + ') ' + str(
                    data[i]['title'] + ' (' + str(data[i]['release_date']) + ')\n')
                # print(str(data[i]['title']))

            embed = discord.Embed(
                title='List of Films',
                description=str(films),
                color=ctx.guild.me.roles[::-1][0].color
            )
            embed.set_footer(text='Type `' + str(self.config.prefix) + 'films <number>` to get each movie info.')
            await wait.edit(content='', embed=embed)

        else:
            try:
                num = int([i for i in list(args) if i.isnumeric()][0]) - 1
                embed = discord.Embed(
                    title=data[num]['title'] + ' (' + str(data[num]['release_date']) + ')',
                    description='**Rotten Tomatoes Rating: ' + str(data[num]['rt_score']) + '%**\n' + data[num][
                        'description'],
                    color=ctx.guild.me.roles[::-1][0].color
                )
                embed.add_field(name='Directed by', value=data[num]['director'], inline='True')
                embed.add_field(name='Produced by', value=data[num]['producer'], inline='True')
                await wait.edit(content='', embed=embed)
            except Exception as e:
                return await ctx.send('the movie you requested does not exist!?')

    @commands.command(name='movie')
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def tv(self, ctx, *, movie):
        """searches up for your favorite tv show / movie"""
        if len(movie) == 0:
            return await ctx.send("Please give TV shows as arguments.")
        url = f'http://api.tvmaze.com/singlesearch/shows?q={movie}'
        data = await utilss.Utilss.get_request(self,
                                               url=url,
                                               json=True,
                                               q=' '.join(movie)
                                               )
        if data is None: return await ctx.send("Did not found anything.")
        try:
            star = str(':star:' * round(data['rating']['average'])) if data['rating'][
                                                                           'average'] is not None else 'No star rating provided.'
            em = discord.Embed(title=data['name'], url=data['url'],
                               description=parsers.Parsers.html_to_markdown(data['summary']),
                               color=ctx.guild.me.roles[::-1][0].color)
            em.add_field(name='General Information',
                         value='**Status: **' + data['status'] + '\n**Premiered at: **' + data[
                             'premiered'] + '\n**Type: **' + data['type'] + '\n**Language: **' + data[
                                   'language'] + '\n**Rating: **' + str(
                             data['rating']['average'] if data['rating'][
                                                              'average'] is not None else 'None') + '\n' + star)
            em.add_field(name='TV Network',
                         value=data['network']['name'] + ' at ' + data['network']['country']['name'] + ' (' +
                               data['network']['country']['timezone'] + ')')
            em.add_field(name='Genre',
                         value=str(', '.join(data['genres']) if len(data['genres']) > 0 else 'no genre avaliable'))
            em.add_field(name='Schedule', value=', '.join(data['schedule']['days']) + ' at ' + data['schedule']['time'])
            # em.set_image(url=data['image']['original'])
            await ctx.send(embed=em)
        except:
            return await ctx.send("There was an error on fetching the info.")

    @commands.command(aliases=['recipes,cook'])
    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    async def recipe(self, ctx, *args):
        """searches for recipe of cooking based on search term"""
        if len(args) == 0:
            await ctx.send(
                embed=discord.Embed(title='Here is a recipe to cook nothing:', description='1. Do nothing\n2. Profit'))
        else:
            data = await utilss.Utilss.get_request(self, url=
            "http://www.recipepuppy.com/api/",
                                                   force_json=True,
                                                   json=True,
                                                   raise_errors=True,
                                                   q=' '.join(args)
                                                   )
            if len(data['results']) == 0:
                return await ctx.send(ctx, "I did not find anything.")
            elif len([i for i in data['results'] if i['thumbnail'] != '']) == 0:
                return await ctx.send("Did not found anything with a delicious picture.")
            else:
                total = random.choice([i for i in data['results'] if i['thumbnail'] != ''])
                embed = discord.Embed(title=total['title'], url=total['href'],
                                      description='Ingredients:\n{}'.format(total['ingredients']),
                                      color=ctx.guild.me.roles[::-1][0].color)
                # embed.set_image(url=total['thumbnail'])
                await ctx.send(embed=embed)


    @commands.command(aliasess='nation')
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def country(self, ctx, *, args):
        """search the information of country based on search term"""
        url = f'https://restcountries.eu/rest/v2/name/{args}'
        data = await utilss.Utilss.get_request(self, url=url,
                                               json=True,
                                               raise_errors=True)
        assert isinstance(data, list), "No such country with the name `" + args + "` found."
        embed = ChooseEmbed(ctx, self.bot, data, key=(lambda x: x["name"]))
        res = await embed.run()
        if not res:
            return
        _country = " ".join(res["name"])
        embeds = discord.Embed(title=_country, description="Native name: \"" + str(res.get("nativeName")) + "\"")
        embeds.add_field(name="Location: ",
                         value="** Latitude Longitude:**" + ", ".join([str(i) for i in res["latlng"]]) +
                               "`\n**Region:** " + res["region"] +
                               "\n**Subregion: **" + res["subregion"] +
                               "\n**Capital:** " + res["capital"]
                         , inline=True)
        embeds.add_field(name="Detailed Info :",
                         value="**Population Count: **" + str(res["population"]) +
                               "\n**Country Area: **" + str(res.get("area")) +
                               " km²\n**Time Zones: **" + (", ".join(res["timezones"]))
                         , inline=True)
        embeds.add_field(name="Currency", value=(("\n".join(
            ["**" + currency["name"] + "** (" + currency["code"] + " `" + currency["symbol"] + "`)" for
             currency in res["currencies"]])) if len(
            res["currencies"]) > 0 else "`doesn't have currency :(`"), inline=False)
        # embeds.set_thumbnail(url=res.get("flag"))
        await ctx.send(embed=embeds)
        # for i in range(len(data)):
        #     print(data[i])
        # kontol = (lambda x : x["name"])
        # for i in range(3):
        #     print(kontol(x="babi"))
        #
        # # await ctx.send(data)

    @commands.guild_only()
    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def guildtopgames(self, ctx):
        """
        -guildtopgames -> returns the top 5 played games for the entire guild
        """
        guildid = ctx.guild.id
        if self.bot.cache.guildgame_toogle.get(
                str(ctx.guild.id)) is None or not self.bot.cache.levelsystem_toogle.get(str(ctx.guild.id)):
            return await utilss.send_error_message(ctx, "please turn on GUILD GAME ACTIVITY system first !")

        result = self.bot.app2.send_task('celerys.worker2.get_guildtopgames', kwargs={'guildid': guildid})
        response = ""


        for i, game in enumerate(result.get()):
            app_id, played = game

            played_hours = int(played) // 60
            played_mins = int(played) % 60

            if played_hours == 1:
                splayed_hours = "1 hour and "
            elif played_hours == 0:
                splayed_hours = ""
            else:
                splayed_hours = str(played_hours) + " hours and "

            if played_mins == 1:
                splayed_mins = "1 minute"
            else:
                splayed_mins = str(played_mins) + " minutes"
            apptobyte = bytes(app_id, 'utf8')
            decodeapp = apptobyte.decode('utf')
            appid = base64.b64decode(decodeapp)
            decode = appid.decode('utf-8')
            # print(type(apptobyte))
            # print(decode)
            # print(appid)

            response += "{}. {} - {}{} \n".format(i + 1, decode, splayed_hours, splayed_mins)
        embed = discord.Embed(title="The guild's top 10 games:", description=response,
                              color=0x0092ff)
        await ctx.channel.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def topgames(self, ctx, user: discord.Member = None):
        """
        -topgames -> returns top 5 played games for the author
        -topgames @user -> returns top 5 played games for the mentioned user
        """
        guildid = ctx.guild.id
        if not user:
            # No user provided, return stats for self
            user_id = ctx.author.id
            who = "Your"  # Used for formatting the response
        else:
            user_id = user.id
            who = "{}'s".format(user.display_name)
        if self.bot.cache.guildgame_toogle.get(
                str(ctx.guild.id)) is None or not self.bot.cache.levelsystem_toogle.get(str(ctx.guild.id)):
            return await utilss.send_error_message(ctx, "please turn on GUILD GAME ACTIVITY system first !")
        result = self.bot.app2.send_task('celerys.worker2.get_topgames',
                                         kwargs={'user_id': user_id, 'guildid': guildid})
        if not result.get():
            message = "{}, I don't have any data on {}.".format(self.bot.get_user(ctx.author.id).mention, self.bot.get_user(ctx.author.id).display_name)
            await ctx.send(message)
            return

        response = ""
        for i, game in enumerate(result.get()):
            id, user_id, guid_did, app_id, played = game

            # String formatting for response
            played_hours = played // 60
            played_mins = played % 60
            if played_hours == 1:
                splayed_hours = "1 hour and "
            elif played_hours == 0:
                splayed_hours = ""
            else:
                splayed_hours = str(played_hours) + " hours and "

            if played_mins == 1:
                splayed_mins = "1 minute"
            else:
                splayed_mins = str(played_mins) + " minutes"

            response += "{}. {} - {}{} \n".format(i + 1, base64.b64decode(app_id).decode(), splayed_hours, splayed_mins)
        embed = discord.Embed(title="{} top {} games:".format(who, len(result.get())), description=response,
                              color=0x0092ff)
        await ctx.channel.send(embed=embed)
        # print(result)

    @commands.group()
    @commands.cooldown(rate=1, per=15.0, type=commands.BucketType.user)
    @commands.guild_only()
    async def find(self, ctx):
        """ Finds a user within your search term """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @find.command(name="playing")
    async def find_playing(self, ctx, *, search: str):
        loop = []
        for i in ctx.guild.members:
            if i.activities and (not i.bot):
                for g in i.activities:
                    if g.name and (search.lower() in g.name.lower()):
                        loop.append(f"{i} | {type(g).__name__}: {g.name} ({i.id})")

        await default.prettyResults(
            ctx, "playing", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    @find.command(name="username", aliases=["name"])
    async def find_name(self, ctx, *, search: str):
        loop = [f"{i} ({i.id})" for i in ctx.guild.members if search.lower() in i.name.lower() and not i.bot]
        await default.prettyResults(
            ctx, "name", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    @find.command(name="nickname", aliases=["nick"])
    async def find_nickname(self, ctx, *, search: str):
        loop = [f"{i.nick} | {i} ({i.id})" for i in ctx.guild.members if i.nick if
                (search.lower() in i.nick.lower()) and not i.bot]
        await default.prettyResults(
            ctx, "name", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    @find.command(name="id")
    async def find_id(self, ctx, *, search: int):
        loop = [f"{i} | {i} ({i.id})" for i in ctx.guild.members if (str(search) in str(i.id)) and not i.bot]
        await default.prettyResults(
            ctx, "name", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    @find.command(name="discriminator", aliases=["discrim"])
    async def find_discriminator(self, ctx, *, search: str):
        if not len(search) == 4 or not re.compile("^[0-9]*$").search(search):
            return await ctx.send("You must provide exactly 4 digits")

        loop = [f"{i} ({i.id})" for i in ctx.guild.members if search == i.discriminator]
        await default.prettyResults(
            ctx, "discriminator", f"Found **{len(loop)}** on your search for **{search}**", loop
        )

    # -----------------------need to be fixed-----------------------

    @commands.command(name="bug", aliases=["Bug"], pass_context=True)
    async def bug(self, ctx, bugMessage: str):
        content = bugMessage
        # host = "server.smtp.com"
        # server = smtplib.SMTP(host)
        # FROM = "geekerbot@ohyeah.com"
        # TO = "lildwagz@gabutcodex.tk"
        # server.sendmail(FROM, TO, content)
        #
        # server.quit()

        await ctx.send("Bug has been reported :thumbsup:")

    # -----------------------need to be fixed-----------------------

    @commands.command(name="vtuberLives")
    async def vtuberLives(self, ctx):
        await ctx.send("Scraping through the channels in the vtuber list I have, give me a few moments...")
        # print("Request for: live VTubers")
        vtuberChannelIDs = {'UCom7qBRZf8hFlno7UXO2ZMw'}
        # check for {"text":" watching"}
        # make it look like the bot is typing while it searches up all the live list
        liveDict = {}
        async with ctx.channel.typing():
            base = "https://www.youtube.com/channel/"
            checkString = "{\"text\":\" watching\"}"
            embedSend = discord.Embed(
                title="Currently Live",
            )
            embedSend.set_thumbnail(
                url="https://w7.pngwing.com/pngs/963/811/png-transparent-youtube-logo-youtube-red-logo-computer-icons"
                    "-youtube-television-angle-rectangle.png")
            # go through all the sections of vtubers, check if anyone in any section is streaming.  if they are,
            # add that field + the streamer into the embed
            at_least_one = False
            for group, vtubers in vtuberChannelIDs.items():
                sectionLiveList = []
                for key in vtubers:
                    request = requests.get(base + vtubers[key])
                    if checkString in request.text:
                        sectionLiveList.append(key)
                        liveDict[key] = vtubers[key]
                if sectionLiveList:
                    embedSend.add_field(name=group, value=", ".join(sectionLiveList), inline=False)
                    at_least_one = True
            # if nobody at all is streaming, say so and return
            if at_least_one:
                await ctx.send(embed=embedSend)
            else:
                await ctx.send("Looks like no one on my list is live.")
                return

        # if they want the links, get it from the liveDict dictioanry
        await ctx.send("Do you want the links to the streams? (yes/no)")

        def check(message):
            return message.channel == ctx.message.channel and message.author == ctx.message.author and (
                    message.content.lower() == "yes" or message.content.lower() == "no")

        msg = await self.bot.wait_for("message", check=check)
        if msg.content.lower() == "no":
            return
        elif msg.content.lower() == "yes":
            liveLinks = ""
            for vtuber, channelId in liveDict.items():
                liveLinkURL = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channelId}&eventType=live&type=video&key={YOUR_API_KEY}".format(
                    channelId=channelId, YOUR_API_KEY="AIzaSyAKy7S9Ta8YoyiqdTcDk8ZDUCvqfK-c50s")
                videoRequest = requests.get(liveLinkURL)
                videoRequest = videoRequest.json()
                videoURL = "https://www.youtube.com/watch?v={videoID}".format(
                    videoID=videoRequest["items"][0]["id"]["videoId"])
                liveLinks += videoURL + "\n"
            await ctx.send(liveLinks)

    # -----------------------need to be fixed-----------------------

    @commands.command(name="channelinfo")
    async def channelinfo(self, ctx, arg1):
        # sub/viewer/video count
        # arg1 = "UCom7qBRZf8hFlno7UXO2ZMw"
        url = "https://youtube.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id=" + arg1 + "&key=AIzaSyAKy7S9Ta8YoyiqdTcDk8ZDUCvqfK-c50s"

        request = requests.get(url)
        request = request.json()

        # print("Request for channel: " + arg1)
        try:
            thumbnail = request["items"][0]["snippet"]["thumbnails"]["high"]["url"]
            channelTitle = request["items"][0]["snippet"]["title"]
            channelDescription = request["items"][0]["snippet"]["description"]
            publishDate = request["items"][0]["snippet"]["publishedAt"]
            subCount = request["items"][0]["statistics"]["subscriberCount"]
            viewCount = request["items"][0]["statistics"]["viewCount"]
            videoCount = request["items"][0]["statistics"]["videoCount"]
        except KeyError as e:
            return await utilss.send_error_message(ctx, "so sad this channel doesnt allow me to get  Statistics for the channel")
        embedSend = discord.Embed(
            title="Statistics for channel: " + channelTitle
        )
        embedSend.set_thumbnail(url=thumbnail)
        embedSend.add_field(name="Channel Description", value= 'None' if channelDescription == '' else channelDescription, inline=False)
        embedSend.add_field(name="Subscriber Count", value="{:,}".format(int(subCount)), inline=False)
        embedSend.add_field(name="Total Views", value="{:,}".format(int(viewCount)), inline=False)
        embedSend.add_field(name="Total Videos", value=videoCount, inline=False)
        embedSend.add_field(name="Publish Date", value=publishDate, inline=False)
        try:

            await ctx.send(embed=embedSend)
            # await ctx.send(channelDescription)

        except Exception as e:
            await ctx.send(f"`{e}`")
    # -----------------------need to be fixed-----------------------

    @commands.command(aliases=['isitup,webstatus'])
    async def isitdown(self, ctx, *args):
        if len(args) == 0: return await ctx.send("Please send a website link.")
        wait = await ctx.send(':arrows_counterclockwise:  | Pinging...')
        web = args[0].replace('<', '').replace('>', '')
        if not web.startswith('http'): web = 'http://' + web
        try:
            a = datetime.now()
            ping = get(web, timeout=5)
            pingtime = round((datetime.now() - a).total_seconds() * 1000)
            await wait.edit(
                content=':white_check_mark:  | That website is up.\nPing: {} ms\nStatus code: {}'.format(pingtime,
                                                                                                         ping.status_code))
        except:
            await wait.edit(content=':exclamation:  | Yes. that website is down.')

    @commands.command(name="eventnow")
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def googledoodle(self, ctx):
        """
        looks up the current events
        :param ctx:
        :return:
        """
        wait = await ctx.send('| Please wait... This may take a few moments...')
        url = "https://www.google.com/doodles/json/{}/{}".format(str(datetime.now().year), str(datetime.now().month))

        # print(datetime.now().year)
        # print(datetime.now().month)

        data = await utilss.Utilss.get_request(self, url=url,
                                               json=True,
                                               raise_errors=True
                                               )
        embed = discord.Embed(title=data[0]['title'], colour=ctx.guild.me.roles[::-1][0].color,
                              url='https://www.google.com/doodles/' + data[0]['name'])
        embed.set_image(url='https:' + data[0]['high_res_url'])
        embed.set_footer(text='Event date: ' + str('/'.join(
            [str(i) for i in data[0]['run_date_array'][::-1]]
        )))
        await wait.edit(content='', embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def bored(self, ctx):
        data = await utilss.Utilss.get_request(self,
                                               url="https://www.boredapi.com/api/activity",
                                               json=True,
                                               raise_errors=True,
                                               participants=1
                                               )
        await ctx.send('**Feeling bored?**\nWhy don\'t you ' + str(data['activity']).lower() + '? :wink::ok_hand:')

    @commands.command(aliases=["yt"])
    async def youtube(self, ctx, *, query):
        """Search videos from youtube."""
        if ctx.guild is None:
            await ctx.author.send('Hi. This command is not allowed in DM!')
            return

        if  not permissions.is_nsfw(ctx):
            return await ctx.send("only on nsfw channel")

        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": self.config.google_Key,
            "part": "snippet",
            "type": "video",
            "maxResults": 25,
            "q": query,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 403:
                    pass
                    # print("Daily youtube api quota reached.")
                else:
                    data = await response.json()

        if not data.get("items"):
            return await ctx.send("No results found!")

        items = []
        for i, item in enumerate(data.get("items"), start=1):
            items.append(f"`{i}.` https://youtube.com/watch?v={item['id']['videoId']}")

        await utilss.paginate_list(ctx, items, use_locking=True, only_author=True)

    @flags.add_flag("urls", nargs="+")
    @flags.add_flag("-d", "--download", action="store_true")
    @flags.command(aliases=["ig", "insta"])
    async def instagram(self, ctx, **flags):
        """Get all the images from one or more instagram posts."""
        async with aiohttp.ClientSession() as session:
            for url in flags["urls"]:
                result = regex.findall("/p/(.*?)(/|\\Z)", url)
                if result:
                    url = f"https://www.instagram.com/p/{result[0][0]}"
                else:
                    url = f"https://www.instagram.com/p/{url.strip('/').split('/')[0]}"

                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0",
                }
                post_id = url.split("/")[-1]
                newurl = "https://www.instagram.com/graphql/query/"
                params = {
                    "query_hash": "505f2f2dfcfce5b99cb7ac4155cbf299",
                    "variables": '{"shortcode":"'
                                 + post_id
                                 + '","include_reel":false,"include_logged_out":true}',
                }

                async with session.get(
                        newurl, params=params, headers=headers, proxy="192.109.165.55"
                ) as response:
                    try:
                        data = await response.json()
                    except aiohttp.ContentTypeError:
                        raise default.Error(
                            "This proxy IP address has been banned by Instagram. Try again later."
                        )
                    data = data["data"]["shortcode_media"]

                if data is None:
                    await ctx.send(f":warning: Invalid instagram URL `{url}`")
                    continue

                medias = []
                try:
                    for x in data["edge_sidecar_to_children"]["edges"]:
                        medias.append(x["node"])
                except KeyError:
                    medias.append(data)

                avatar_url = data["owner"]["profile_pic_url"]
                username = data["owner"]["username"]
                content = discord.Embed(color=random.choice(self.ig_colors))
                content.set_author(name=f"@{username}", icon_url=avatar_url, url=url)

                if not medias:
                    await ctx.send(f":warning: Could not find any media from `{url}`")
                    continue

                if flags["download"]:
                    # send as files
                    async with aiohttp.ClientSession() as session:
                        await ctx.send(f"<{url}>")
                        timestamp = arrow.get(data["taken_at_timestamp"]).format("YYMMDD")
                        for n, file in enumerate(medias, start=1):
                            if file.get("is_video"):
                                media_url = file.get("video_url")
                                extension = "mp4"
                            else:
                                media_url = file.get("display_url")
                                extension = "jpg"

                            filename = f"{timestamp}-@{username}-{post_id}-{n}.{extension}"
                            async with session.get(media_url) as response:
                                with open(filename, "wb") as f:
                                    while True:
                                        block = await response.content.read(1024)
                                        if not block:
                                            break
                                        f.write(block)

                            with open(filename, "rb") as f:
                                await ctx.send(file=discord.File(f))

                            os.remove(filename)
                else:
                    # send as embeds
                    for medianode in medias:
                        if medianode.get("is_video"):
                            await ctx.send(embed=content)
                            await ctx.send(medianode.get("video_url"))
                        else:
                            content.set_image(url=medianode.get("display_url"))
                            await ctx.send(embed=content)
                        content.description = None
                        content._author = None

        try:
            # delete discord automatic embed
            await ctx.message.edit(suppress=True)
        except discord.Forbidden:
            pass

    @commands.command(name='news', aliases=["trending"])
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def msn(self, ctx, *args):
        try:
            data = await utilss.Utilss.get_request(self,
                                                   url="http://cdn.content.prod.cms.msn.com/singletile/summary/alias/experiencebyname/today",
                                                   raise_errors=True,
                                                   market="en-GB",
                                                   source="appxmanifest",
                                                   tenant="amp",
                                                   vertical="news"
                                                   )
            imageURL = data.split('baseUri="')[1].split('"')[0] + data.split('src="')[1].split('?')[0].replace(".img",
                                                                                                               ".png")
            content = data.split('hint-wrap="true">')[1].split('<')[0]
            embed = discord.Embed(title=content, color=ctx.guild.me.roles[::-1][0].color)
            embed.set_image(url=imageURL)
            embed.set_footer(text="Content provided by msn.com")
            return await ctx.send(embed=embed)
        except Exception as e:
            # await ctx.send(f"yo, theres an error: `{str(e)}`")
            return await utilss.send_error_message(ctx, "Oopsies, there was an error on searching the news.")

    @commands.command(name='rhymes')
    @commands.cooldown(rate=1, per=7.0, type=commands.BucketType.user)
    async def rhyme(self, ctx, *args):
        await ctx.send(f'{self.bot.get_emoji(771500167064584212)} Please wait...')
        data = await utilss.Utilss.get_request(self,
                                               url='https://rhymebrain.com/talk?function=getRhymes&word=',
                                               json=True,
                                               raise_errors=True,
                                               function='getRhymes',
                                               word=' '.join(args)
                                               )

        words = [word['word'] for word in data if word['flags'] == 'bc']
        content = discord.Embed(title='Words that rhymes with ' + ' '.join(args) + ' :')
        if not words:
            raise utilss.send_error_message(ctx, 'We did not find any rhyming words corresponding to that letter.')

        await utilss.send_as_pages(ctx, content, words)

    @commands.check(permissions.is_owner)
    @commands.command(name="ytmp3")
    async def ytdownloads(self, ctx, *, url):
        """"""
        # msg = url
        # print(f'Mesagge content: {msg} \n')

        # regex to find url in the sent message
        urls = re.findall(r'(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+', url)
        # print(urls)
        #
        if urls:
            # check if there are more than one links being sent
            if len(urls) == 1:

                validated_yt_url_1 = 'https://www.youtube.com/watch?v='
                validated_yt_url_2 = 'https://youtu.be/'
                # print(urls[0])
                youtube_regex = (
                    r'(https?://)?(www\.)?'
                    '(youtube|youtu|youtube-nocookie)\.(com|be)/'
                    '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
                youtube_regex_match = re.match(youtube_regex, url)
                if youtube_regex_match:
                    channelparse = r"((http|https):\/\/|)(www\.|)youtube\.com\/(channel\/|user\/)[a-zA-Z0-9\-]{1,}"
                    check = re.findall(channelparse, urls[0])
                    if not check:
                        # print('Youtube link is valid...')
                        mp3.song(url)

                        os.listdir()
                        # get all of the .mp3 file in this directory
                        for files in glob.glob('*.mp3'):
                            # for each .mp3 file get the file size
                            file_size = getsize(files)
                            # convert the file size into an integer
                            file_size = int(file_size)

                            # check if the file size is over 8000000 bytes (discord limit for non bosted server's)
                            if file_size > 8000000:
                                # print('The file size is over 8MB...\n')
                                await utilss.send_error_message(ctx,
                                                                "Try sending a song that is under 7 minutes long, "
                                                                "\nbecause of Discord's file size limit.")

                                os.remove(files)
                                # print('File was removed')
                            else:
                                await ctx.send(file=discord.File(files))
                                # print('File was sent...\n')
                                os.remove(files)
                                # print('File was deleted...\n')
                    else:
                        await utilss.send_error_message(ctx,
                                                        "Not allowed to download all videos from a specific channel")
                else:
                    await utilss.send_error_message(ctx,
                                                    "The Link was not valid..")
                    # print('The link was not valid')
            #
            else:
                await utilss.send_error_message(ctx, "It looks like you sent more than one url's, please send one url "
                                                     "at time.")
        elif not urls:
            # split the message after the fisrt 'empty space'
            # msg = url.split(' ', 1)
            # # print(msg[1])
            # msg = msg[1].replace(' ', '+')
            # print(msg)
            await utilss.send_error_message(ctx, "please insert a valid url")
            # create a youtube serach link with our string
            # print(f'https://www.youtube.com/results?search_query={url}')
            # html = urllib.request.urlopen(f'https://www.youtube.com/results?search_query={url}')
            # video_ids = re.findall(r'watch\?v=(\S{11})', html.read().decode())
            #
            # # construct a new url from the videos id's we got back
            # new_url = 'https://www.youtube.com/watch?v=' + video_ids[0]
            # # print(new_url)
            #
            # mp3.song([new_url])
            # os.listdir()
            #
            # # get all of the .mp3 file in this directory
            # for files in glob.glob('*.mp3'):
            #
            #     # for each .mp3 file get the file size
            #     file_size = getsize(files)
            #     # convert the file size into an integer
            #     file_size = int(file_size)
            #
            #     # check if the file size is over 8000000 bytes (discord limit for non bosted server's)
            #     if file_size > 8000000:
            #         print('The file size is over 8MB...\n')
            #
            #         embedVar = discord.Embed(
            #             title="Something went wrong :confused:\nTry sending a song that is under 7 minutes long, \nbecause of Discord's file size limit.",
            #             color=0x0066ff)
            #         await ctx.send(embed=embedVar)
            #
            #         os.remove(files)
            #         # print('File was deleted...')
            #     else:
            #         await ctx.send(new_url)
            #         await ctx.send(file=discord.File(files))
            #         # print('File was sent...\n')
            #
            #         os.remove(files)
            #         # print('File was deleted...\n')
        else:
            embedVar = discord.Embed(title="Something wen't wrong.", color=0x0066ff)
            await ctx.send(embed=embedVar)

    @commands.command(name="enmorse")
    async def morsify(self, ctx, *, word: str):
        """Generate morse code from a text"""

        msg = morse.morsify(word)

        if len(list(word)) > 500:
            await ctx.send("This string is too big for me to decode!")
        else:
            try:
                await ctx.send(f"Code Morse : `{msg}`")
            except:
                await ctx.send("Something went wrong!")

    @commands.command(name="demorse")
    async def demorse(self, ctx, *, word: str):
        """Read morse code"""

        msg = morse.demorse(word)

        if len(list(word)) > 2000:
            await ctx.send("This string is too big for me to decode!")
        else:
            try:
                await ctx.send(f"Text Plain : `{msg}`")
            except:
                await ctx.send("Something went wrong!")

    @commands.check(permissions.is_owner)
    @commands.command(name="ytdownload")
    async def ytdownloader(self, ctx, *, url):
        SAVE_PATH = "Databases/downloads"

        try:
            yt = pytube.YouTube(url)
            mp4files = yt.filter('mp4')

            d_video = yt.get(mp4files[-1].extension, mp4files[-1].resolution)

            try:
                d_video.download(SAVE_PATH)
            except:
                print("Some Error!")
            await utilss.send_success(ctx, "successfully downloaded the video")
        except Exception as e:
            await utilss.send_error_message(ctx,f"```{e}```")



def setup(bot):
    bot.add_cog(UtilityCommand(bot))
