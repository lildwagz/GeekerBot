import asyncio
import datetime
import json
import random
from http import HTTPStatus

# import ksoftapi
import requests

import aiohttp
import discord

from PIL import Image
from discord import Embed
from discord.ext import commands
from discord.ext.commands import clean_content
from requests import get

from cogs.mod2 import color_list
from utils import lists, http, default, permissions, utilss, parsers, games
from utils.decorators import cooldown
from utils.utilss import send_error_message


class Fun_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.countries = get("https://restcountries.eu/rest/v2").json()
        self.config = default.get("config.json")
        self.config = default.get("config.json")
        self.triggered_text = Image.open(f"assets/pics/triggered.jpg")
        self.triggered_red = Image.new(mode="RGBA", size=(216, 216), color=(255, 0, 0, 100))
        self.triggered_bg = Image.new(mode="RGBA", size=(216, 216), color=(0, 0, 0, 0))

        # self.ksoft = ksoftapi.Client(self.config.ksoft_token)
    #
    # @commands.command(aliases=['8ball'])
    # async def eightball(self, ctx, *, question: commands.clean_content):
    #     """ Consult 8ball to receive an answer """
    #     answer = random.choice(ballresponse)
    #     await ctx.send(f"🎱 **Question:** {question}\n**Answer:** {answer}")

    async def randomimageapi(self, ctx, url, endpoint,title):
        try:
            r = await http.get(url, res_method="json", no_cache=True)
        except aiohttp.ClientConnectorError:
            return await ctx.send("The API seems to be down...")
        except aiohttp.ContentTypeError:
            return await ctx.send("The API returned an error or didn't return JSON...")
        embed = discord.Embed(title=title, color=random.choice(color_list))
        embed.set_image(
            url=r[endpoint])
        await ctx.send(
            embed=embed
        )


    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def coffee(self, ctx):
        """ Posts a random coffee """
        await self.randomimageapi(ctx, 'https://coffee.alexflipnote.dev/random.json', 'file',title="Coffee Time")

    @commands.command()
    async def f(self, ctx, *, text: commands.clean_content = None):
        """ Press F to pay respect """
        hearts = ['❤', '💛', '💚', '💙', '💜']
        reason = f"for **{text}** " if text else ""
        await ctx.send(f"**{ctx.author.name}** has paid their respect {reason}{random.choice(hearts)}")

    # @commands.command()
    # @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    # async def urban(self, ctx, *, search: commands.clean_content):
    #     """ Find the 'best' definition to your words """
    #     async with ctx.channel.typing():
    #         try:
    #             url = await http.get(f'https://api.urbandictionary.com/v0/define?term={search}', res_method="json")
    #         except Exception:
    #             return await ctx.send("Urban API returned invalid data... might be down atm.")
    #
    #         if not url:
    #             return await ctx.send("I think the API broke...")
    #
    #         if not len(url['list']):
    #             return await ctx.send("Couldn't find your search in the dictionary...")
    #
    #         result = sorted(url['list'], reverse=True, key=lambda g: int(g["thumbs_up"]))[0]
    #
    #         definition = result['definition']
    #         if len(definition) >= 1000:
    #             definition = definition[:1000]
    #             definition = definition.rsplit(' ', 1)[0]
    #             definition += '...'
    #
    #         await ctx.send(f"📚 Definitions for **{result['word']}**```fix\n{definition}```")

    @commands.command()
    async def reverse(self, ctx, *, text: str):
        """ !poow ,ffuts esreveR
        Everything you type after reverse will of course, be reversed
        """
        t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
        await ctx.send(f"🔁 {t_rev}")

    @commands.command()
    async def rate(self, ctx, *, thing: commands.clean_content):
        """ Rates what you desire """
        rate_amount = random.uniform(0.0, 100.0)
        await ctx.send(f"I'd rate `{thing}` a **{round(rate_amount, 4)} / 100**")

    # @commands.command()
    # async def beer(self, ctx, user: discord.Member = None, *, reason: commands.clean_content = ""):
    #     """ Give someone a beer! 🍻 """
    #     if not user or user.id == ctx.author.id:
    #         return await ctx.send(f"**{ctx.author.name}**: paaaarty!🎉🍺")
    #     if user.id == self.bot.user.id:
    #         return await ctx.send("*drinks beer with you* 🍻")
    #     if user.bot:
    #         return await ctx.send(
    #             f"I would love to give beer to the bot **{ctx.author.name}**, but I don't think it will respond to you :/")
    #
    #     beer_offer = f"**{user.name}**, you got a 🍺 offer from **{ctx.author.name}**"
    #     beer_offer = beer_offer + f"\n\n**Reason:** {reason}" if reason else beer_offer
    #     msg = await ctx.send(beer_offer)
    #
    #     def reaction_check(m):
    #         if m.message_id == msg.id and m.user_id == user.id and str(m.emoji) == "🍻":
    #             return True
    #         return False
    #
    #     try:
    #         await msg.add_reaction("🍻")
    #         await self.bot.wait_for('raw_reaction_add', timeout=30.0, check=reaction_check)
    #         await msg.edit(content=f"**{user.name}** and **{ctx.author.name}** are enjoying a lovely beer together 🍻")
    #     except asyncio.TimeoutError:
    #         await msg.delete()
    #         await ctx.send(f"well, doesn't seem like **{user.name}** wanted a beer with you **{ctx.author.name}** ;-;")
    #     except discord.Forbidden:
    #         # Yeah so, bot doesn't have reaction permission, drop the "offer" word
    #         beer_offer = f"**{user.name}**, you got a 🍺 from **{ctx.author.name}**"
    #         beer_offer = beer_offer + f"\n\n**Reason:** {reason}" if reason else beer_offer
    #         await msg.edit(content=beer_offer)

    @commands.command(aliases=['howhot', 'hot'])
    async def hotcalc(self, ctx, *, user: discord.Member = None):
        """ Returns a random percent for how hot is a discord user """
        user = user or ctx.author

        random.seed(user.id)
        r = random.randint(1, 100)
        hot = r / 1.17

        emoji = "💔"
        if hot > 25:
            emoji = "❤"
        if hot > 50:
            emoji = "💖"
        if hot > 75:
            emoji = "💞"

        await ctx.send(f"**{user.name}** is **{hot:.2f}%** hot {emoji}")

    # @commands.command(aliases=['slots', 'bet'])
    # @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    # async def slot(self, ctx):
    #     """ Roll the slot machine """
    #     emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
    #     a = random.choice(emojis)
    #     b = random.choice(emojis)
    #     c = random.choice(emojis)
    #
    #     slotmachine = f"**[ {a} {b} {c} ]\n{ctx.author.name}**,"
    #
    #     if (a == b == c):
    #         await ctx.send(f"{slotmachine} All matching, you won! 🎉")
    #     elif (a == b) or (a == c) or (b == c):
    #         await ctx.send(f"{slotmachine} 2 in a row, you won! 🎉")
    #     else:
    #         await ctx.send(f"{slotmachine} No match, you lost 😢")

    @commands.command(aliases=['slots', 'bet'])
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def slot(self, ctx):
        """ Roll the slot machine, find out lucky in you """
        win, jackpot, slots = False, False, []
        for i in range(1):
            newslot = games.slot()
            if newslot[0] == newslot[1] and newslot[0] == newslot[2] and newslot[1] == newslot[2]:
                win = True
                if newslot[1] == ':flushed:':
                    jackpot = True
            # await ctx.send(f"{newslot}")
            # await ctx.send(f"{newslot[0]}  {newslot[1]} {newslot[2]}  ")
            # win = True
            slots.append(games.slotify(newslot))
        if win:
            msgslot = 'You win!'
            col = ctx.guild.me.roles[::-1][0].color
            if jackpot:
                msgslot = 'JACKPOT!'
                col = ctx.guild.me.roles[::-1][0].color
            # if ctx.bot.db.Economy.get(ctx.author.id) is not None:
                reward = random.randint(500, 1000)
            #     ctx.bot.db.Economy.addbal(ctx.author.id, reward)
                await ctx.send('thanks for playing! you received a whopping ' + str(reward) + ' points!')
        else:
            msgslot = 'You lose... Try again!'
            col = ctx.guild.me.roles[::-1][0].color
        embed = discord.Embed(title=msgslot, description=slots[0] , colour=col)
        await ctx.send(embed=embed)
    #
    # @commands.command(aliases=['quotes', 'qt'])
    # @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    # async def quote(self, ctx):
    #     """ Posts a random quotes """
    #     url = await http.get(f'http://quotes.stormconsultancy.co.uk//random.json', res_method="json")
    #
    #     embedColour = discord.Embed.Empty
    #     if hasattr(ctx, 'guild') and ctx.guild is not None:
    #         embedColour = ctx.me.top_role.colour
    #
    #     await ctx.send(f"```fix\n{url['quote']}\nby :{url['author']}```")

    @commands.command()
    async def poll(self, ctx, *, pollInfo):
        emb = (discord.Embed(description=pollInfo, colour=0x36393e))
        emb.set_author(name=f"Poll by {ctx.message.author}",
                       icon_url="https://lh3.googleusercontent.com/7ITYJK1YP86NRQqnWEATFWdvcGZ6qmPauJqIEEN7Cw48DZk9ghmEz_bJR2ccRw8aWQA=w300")
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        try:
            pollMessage = await ctx.send(embed=emb)
            await pollMessage.add_reaction(f"{self.bot.get_emoji(771498392475926539)}")
            await pollMessage.add_reaction("\N{THUMBS DOWN SIGN}")
        except Exception as e:
            await ctx.send(
                f"Oops, I couldn't react to the poll. Check that I have permission to add reactions! ```py\n{e}```")

    @commands.command()
    async def roast(self, ctx):
        if not permissions.is_nsfw(ctx):
            return await ctx.send("Sorry bro I can't insult anyone in this sfw channel")
        response = requests.get(url="https://evilinsult.com/generate_insult.php?lang=en&type=json")
        roast = json.loads(response.text)
        await ctx.send(roast['insult'])

    @commands.command(aliases=['gay-scanner', 'gayscanner', 'gay'])
    async def gay_scanner(self, ctx, *, user: clean_content = None):
        """very mature command yes haha"""
        if not user:
            user = ctx.author.name
        gayness = random.randint(0, 100)
        if gayness <= 33:
            gayStatus = random.choice(["No homo",
                                       "Wearing socks",
                                       "Straight-ish",
                                       "Only sometimes",
                                       "No homo bro",
                                       "Girl-kisser",
                                       "Hella straight"])
            gayColor = 0xFFC0CB
        elif 33 < gayness < 66:
            gayStatus = random.choice(["Possible homo",
                                       "My gay-sensor is picking something up",
                                       "I can't tell if the socks are on or off",
                                       "Gay-ish",
                                       "Looking a bit homo",
                                       "lol half  g a y",
                                       "safely in between for now"])
            gayColor = 0xFF69B4
        else:
            gayStatus = random.choice(["LOL YOU GAY XDDD FUNNY",
                                       "HOMO ALERT",
                                       "MY GAY-SENSOR IS OFF THE CHARTS",
                                       "STINKY GAY",
                                       "BIG GEAY",
                                       "THE SOCKS ARE OFF",
                                       "HELLA GAY"])
            gayColor = 0xFF00FF
        emb = discord.Embed(description=f"gay level of **{user}**", color=gayColor)
        emb.add_field(name="Result:", value=f"{gayness}% gay \n"
                                            f"{gayStatus} :xD")

        emb.set_author(name="Gay-Scanner™")
        await ctx.send(embed=emb)


    @commands.command()
    async def ship(self, ctx, name1: clean_content, name2: clean_content):
        shipnumber = random.randint(0, 100)
        if 0 <= shipnumber <= 10:
            status = "Really low! {}".format(random.choice(["Friendzone ;(",
                                                            'Just "friends"',
                                                            '"Friends"',
                                                            "Little to no love ;(",
                                                            "There's barely any love ;("]))
        elif 10 < shipnumber <= 20:
            status = "Low! {}".format(random.choice(["Still in the friendzone",
                                                     "Still in that friendzone ;(",
                                                     "There's not a lot of love there... ;("]))
        elif 20 < shipnumber <= 30:
            status = "Poor! {}".format(random.choice(["But there's a small sense of romance from one person!",
                                                      "But there's a small bit of love somewhere",
                                                      "I sense a small bit of love!",
                                                      "But someone has a bit of love for someone..."]))
        elif 30 < shipnumber <= 40:
            status = "Fair! {}".format(random.choice(["There's a bit of love there!",
                                                      "There is a bit of love there...",
                                                      "A small bit of love is in the air..."]))
        elif 40 < shipnumber <= 60:
            status = "Moderate! {}".format(random.choice(["But it's very one-sided OwO",
                                                          "It appears one sided!",
                                                          "There's some potential!",
                                                          "I sense a bit of potential!",
                                                          "There's a bit of romance going on here!",
                                                          "I feel like there's some romance progressing!",
                                                          "The love is getting there..."]))
        elif 60 < shipnumber <= 70:
            status = "Good! {}".format(random.choice(["I feel the romance progressing!",
                                                      "There's some love in the air!",
                                                      "I'm starting to feel some love!"]))
        elif 70 < shipnumber <= 80:
            status = "Great! {}".format(random.choice(["There is definitely love somewhere!",
                                                       "I can see the love is there! Somewhere...",
                                                       "I definitely can see that love is in the air"]))
        elif 80 < shipnumber <= 90:
            status = "Over average! {}".format(random.choice(["Love is in the air!",
                                                              "I can definitely feel the love",
                                                              "I feel the love! There's a sign of a match!",
                                                              "There's a sign of a match!",
                                                              "I sense a match!",
                                                              "A few things can be imporved to make this a match made in heaven!"]))
        elif 90 < shipnumber <= 100:
            status = "True love! {}".format(random.choice(["It's a match!",
                                                           "There's a match made in heaven!",
                                                           "It's definitely a match!",
                                                           "Love is truely in the air!",
                                                           "Love is most definitely in the air!"]))

        if shipnumber <= 33:
            shipColor = 0xE80303
        elif 33 < shipnumber < 66:
            shipColor = 0xff6600
        else:
            shipColor = 0x3be801

        emb = (discord.Embed(color=shipColor, \
                             title="❤  COMPATIBILITY  ❤", \
                             description="**{0}** and **{1}** {2}".format(name1, name2, random.choice([
                                 ":sparkling_heart:",
                                 ":heart_decoration:",
                                 ":heart_exclamation:",
                                 ":heartbeat:",
                                 ":heartpulse:",
                                 ":hearts:",
                                 ":blue_heart:",
                                 ":green_heart:",
                                 ":purple_heart:",
                                 ":revolving_hearts:",
                                 ":yellow_heart:",
                                 ":two_hearts:"]))))
        emb.add_field(name="Results:", value=f"{shipnumber}%", inline=True)
        emb.add_field(name="Status:", value=(status), inline=False)

        await ctx.send(embed=emb)

    @commands.command(
        name='statuscat'
    )
    async def statuscat(self, ctx, code: int = None):
        """Sends an embed with an image of a cat, portraying the status code.
           If no status code is given it will return a random status cat."""
        valid = [s.value for s in list(HTTPStatus)]
        # Append values which are not present in python3.8
        new_valid = [
            425,  # UNORDERED COLLECTION
            418  # IM_A_TEAPOT
        ]
        valid.extend(new_valid)
        code = code or random.choice(valid)

        if code not in valid:
            raise commands.BadArgument(f'Invalid status code: **{code}**')

        embed = Embed()
        embed.set_image(url=f'https://http.cat/{code}.jpg')
        embed.set_footer(text=f"Provided by: https://http.cat")
        await ctx.send(embed=embed)

    async def gif_url(self, terms):
        url = (
                f'http://api.giphy.com/v1/gifs/search' +
                f'?api_key={self.config.API_KEY_GIPHY}' +
                f'&q={terms}' +
                f'&limit=20' +
                f'&rating=R' +
                f'&lang=en'
        )
        response = requests.get(url, timeout=10)
        gifs = response.json()
        if 'data' not in gifs:
            if 'message' in gifs:
                if 'Invalid authentication credentials' in gifs['message']:
                    print('ERROR: Giphy API key is not valid')
            return None
        if not gifs['data']:
            return None
        gif = random.choice(gifs['data'])['images']['original']['url']
        return gif

    @commands.command(
        name='gif'
    )
    async def gif_embed(self, ctx, *, gif_name):
        """Post a gif
        Displays a random gif for the specified search term"""
        await ctx.trigger_typing()
        gif_url = await self.gif_url(gif_name)
        if gif_url is None:
            await ctx.send(f'Sorry {ctx.author.mention}, no gif found 😔')
            await ctx.message.add_reaction('❌')
        else:
            e = Embed(color=0x000000)
            e.set_image(url=gif_url)
            e.set_footer(
                text=ctx.author.display_name,
                icon_url=ctx.author.avatar_url
            )

            await ctx.send(embed=e)

    @commands.command(name="programmerhumor", aliases=["programmermeme", "programming", "programmer"])
    async def programmingmeme(self, ctx):
        url = "https://useless-api.vierofernando.repl.co/programmermeme"
        await self.randomimageapi(ctx, url, 'url',title='Programmer meme')

    @commands.command(name='serverdeathnote',aliases=['dn'])
    @cooldown(10)
    async def deathnote(self, ctx):
        if ctx.guild.member_count > 500:
            return await send_error_message(ctx,'This server has soo many members')
        member, in_the_note, notecount, membercount = [], "", 0, 0
        for i in range(ctx.guild.member_count):
            if ctx.guild.members[i].display_name != ctx.author.display_name:
                member.append(ctx.guild.members[i].name)
                membercount = int(membercount) + 1
        chances = ['ab', 'abc', 'abcd']
        strRandomizer = random.choice(chances)
        for i in range(int(membercount)):
            if random.choice(list(strRandomizer)) == 'b':
                notecount = int(notecount) + 1
                in_the_note = in_the_note + str(notecount) + '. ' + str(member[i]) + '\n'
        death, count = random.choice(member), random.choice(list(range(int(membercount))))
        embed = discord.Embed(
            title=ctx.guild.name + '\'s death note',
            description=str(in_the_note),
            colour=ctx.guild.me.roles[::-1][0].color
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=['guessav','avatarguess','avguess','avatargame','avgame'])
    @cooldown(30)
    async def guessavatar(self, ctx):
        avatarAll, nameAll = [str(i.avatar_url) for i in ctx.guild.members if i.status.name!='offline' and not i.bot], [i.display_name for i in ctx.guild.members if i.status.name!='offline' and not i.bot]
        if len(avatarAll)<=4: return await ctx.send('Need more online members! :x:')
        numCorrect = random.randint(0, len(avatarAll)-1)
        corr_avatar, corr_name = avatarAll[numCorrect], nameAll[numCorrect]
        nameAll.remove(corr_name)
        wrongArr = []
        for i in range(3):
            wrongArr.append(random.choice(nameAll))
        abcs, emots = list('🇦🇧🇨🇩'), list('🇦🇧🇨🇩')
        randomInt = random.randint(0, 3)
        corr_order = random.choice(abcs[randomInt])
        abcs[randomInt] = '0'
        question, chooseCount = '', 0
        for assign in abcs:
            if assign!='0':
                question += '**'+ str(assign) + '.** '+str(wrongArr[chooseCount])+ '\n'
                chooseCount += 1
            else:
                question += '**'+ str(corr_order) + '.** '+str(corr_name)+ '\n'
        embed = discord.Embed(title='What does the avatar below belongs to?', description=':eyes: Click the reactions! **You have 20 seconds.**\n\n'+str(question), colour=ctx.guild.me.roles[::-1][0].color)
        embed.set_footer(text='For privacy reasons, the people displayed above are online users.')
        embed.set_image(url=corr_avatar)
        main = await ctx.send(embed=embed)
        for i in emots: await main.add_reaction(i)
        def is_correct(reaction, user):
            return user == ctx.author
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', check=is_correct, timeout=20.0)
        except asyncio.TimeoutError:
            return await ctx.send(':pensive: No one? Okay then, the answer is: '+str(corr_order)+'. '+str(corr_name))
        if str(reaction.emoji)==str(corr_order):
            await ctx.send(' | <@'+str(ctx.author.id)+'>, You are correct! :tada:')
            # if ctx.bot.db.Economy.get(ctx.author.id) is not None:
            reward = random.randint(5, 100)
                # ctx.bot.db.Economy.addbal(ctx.author.id, reward)
            await ctx.send('thanks for playing! You received '+str(reward)+' extra coins!')
        else:
            return await ctx.send(f'<@{ctx.author.id}>, Incorrect. The answer is {corr_order}. {corr_name}')

    @commands.guild_only()
    @commands.command(aliases=['guessgeo', 'geoguess', 'geogame'])
    @cooldown(10)
    async def geoquiz(self, ctx):
        global reaction
        data, topic = self.countries, random.choice(
            ['capital', 'region', 'subregion', 'population', 'demonym', 'nativeName'])
        chosen_nation_num = random.randint(0, len(data))
        chosen_nation, wrongs = data[chosen_nation_num], []
        del data[chosen_nation_num]
        correct = str(chosen_nation[topic])
        try:
            for i in range(4):
                integer = random.randint(0, len(data))
                wrongs.append(str(data[integer][str(topic)]))
                data.remove(data[integer])
        except IndexError as a :
            return utilss.send_error_message(ctx, "please try again!")
        emot, static_emot, corr_order_num = list('🇦🇧🇨🇩'), list('🇦🇧🇨🇩'), random.randint(0, 3)
        corr_order = emot[corr_order_num]
        emot[corr_order_num], question, guy = '0', '', ctx.author
        for each_emote in emot:
            if each_emote != '0':
                added = random.choice(wrongs)
                question += each_emote + ' ' + added + '\n'
                wrongs.remove(added)
            else:
                question += corr_order + ' ' + correct + '\n'
        embed = discord.Embed(title='Geography: ' + str(topic) + ' quiz!',
                              description=':nerd: Click on the reaction! **You have 20 seconds.**\n\nWhich ' + str(
                                  topic) + ' belongs to ' + str(chosen_nation['name']) + '?\n' + str(question),
                              colour=ctx.guild.me.roles[::-1][0].color)
        main = await ctx.send(content='', embed=embed)
        for i in range(len(static_emot)):
            await main.add_reaction(static_emot[i])

        def check(reaction, user):
            return user == guy

        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await main.add_reaction('😔')
        try:
            if str(reaction.emoji) == str(corr_order):
                reward = random.randint(5, 100)
                await ctx.send(' | <@' + str(guy.id) + '>, Congrats! You are correct. :partying_face:')
                await ctx.send('thanks for playing! You received ' + str(reward) + ' extra coins!')
            else:
                return await ctx.send(f'<@{guy.id}>, You are incorrect. The answer is {corr_order}.')
        except NameError as e:
            pass
    @commands.command(name="comic")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def comic(self, ctx):
        """Random comic with pictures."""
        link = f"http://xkcd.com/{random.randint(1, 2304)}/info.0.json"
        async with aiohttp.ClientSession() as s:
            async with s.get(link) as r:
                data = await r.json()

        desc = ""
        desc += data['transcript']
        desc += "\n" + data['alt']

        embed = discord.Embed(color=ctx.author.color, description=desc, title=data['safe_title'])
        embed.set_image(url=data['img'])

        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=2.0)
    async def shoot(self, ctx, user: discord.Member):

        embed = discord.Embed(name="You've been shot.", color=random.choice(color_list))
        embed.add_field(name="{} :gun:   you were shot, you will probably bleed out and die.".format(user.name), value='shot by {}'.format(ctx.message.author.name), inline=True)
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=2.0)
    async def stab(self, ctx, user: discord.Member):

        embed = discord.Embed(name="You've been shot.", color=random.choice(color_list))
        embed.add_field(name=":dagger:{}  You were stabbed. Go to a hospital.".format(user.name), value= 'stabbed by {}'.format(ctx.message.author.name), inline=True)
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    @commands.cooldown(rate=1, per=2.0)
    async def slap(self, ctx, user: discord.Member):
        async with aiohttp.ClientSession() as s:
            async with s.get("https://nekos.life/api/v2/img/slap") as r:
                data = await r.json()
        embed = discord.Embed(description="{} was slapped by {}".format(user.mention, ctx.message.author.mention), color=random.choice(color_list))
        datas = data["url"]
        embed.set_image(url=datas)
        x = datetime.datetime.now()
        time = x.strftime("%X")
        embed.set_footer(text=f'Requested by: {ctx.author.name} | at: {time}')
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    @commands.cooldown(rate=1, per=2.0)
    async def hug(self, ctx, user: discord.Member):
        async with aiohttp.ClientSession() as s:
            async with s.get("https://nekos.life/api/v2/img/hug") as r:
                data = await r.json()
        embed = discord.Embed(description="{} was hugged by {}".format(user.mention, ctx.message.author.mention), color=random.choice(color_list))
        embed.set_image(url=data["url"])
        x = datetime.datetime.now()
        time = x.strftime("%X")
        embed.set_footer(text=f'Requested by: {ctx.author.name} | at: {time}')
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    @commands.cooldown(rate=1, per=2.0)
    async def pat(self, ctx, user: discord.Member):
        async with aiohttp.ClientSession() as s:
            async with s.get("https://nekos.life/api/v2/img/pat") as r:
                data = await r.json()
        embed = discord.Embed(description="{} was patted by {}".format(user.mention, ctx.message.author.mention), color=random.choice(color_list))
        embed.set_image(url=data["url"])
        x = datetime.datetime.now()
        time = x.strftime("%X")
        embed.set_footer(text=f'Requested by: {ctx.author.name} | at: {time}')
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    @commands.cooldown(rate=1, per=2.0)
    async def kiss(self, ctx, user: discord.Member):
        async with aiohttp.ClientSession() as s:
            async with s.get("https://nekos.life/api/v2/img/kiss") as r:
                data = await r.json()
        embed = discord.Embed(description="{} was kissed by {}".format(user.mention, ctx.message.author.mention), color=random.choice(color_list))
        embed.set_image(url=data["url"])
        x = datetime.datetime.now()
        time = x.strftime("%X")
        embed.set_footer(text=f'Requested by: {ctx.author.name} | at: {time}')
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    @commands.cooldown(rate=1, per=2.0)
    async def spank(self, ctx, user: discord.Member):
        if not permissions.is_nsfw(ctx):
            return await ctx.send("I am so sad, I can't spank anyone in this sfw channel :(")
        fucktonOfLinks = ["https://i.imgur.com/V0LMJkt.gif", "https://i.imgur.com/SnZ8Szh.gif", "https://i.imgur.com/jzJyCJp.gif", "https://i.imgur.com/BZDfN8b.gif", "https://i.imgur.com/9DMPdIV.gif", "https://i.imgur.com/j90b50B.gif", "https://i.imgur.com/JyjwigU.gif"] #God forgive me for this atrocity.
        embed = discord.Embed(description="{} was spanked by {}".format(user.mention, ctx.message.author.mention), color=random.choice(color_list))
        embed.set_image(url=random.choice(fucktonOfLinks))
        x = datetime.datetime.now()
        time = x.strftime("%X")
        embed.set_footer(text=f'Requested by: {ctx.author.name} | at: {time}')
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    @commands.cooldown(rate=1, per=2.0)
    async def cuddle(self, ctx, user: discord.Member):
        async with aiohttp.ClientSession() as s:
            async with s.get("https://nekos.life/api/v2/img/cuddle") as r:
                data = await r.json()
        embed = discord.Embed(description="{} cuddles with {}".format(ctx.message.author.mention, user.mention), color=random.choice(color_list))
        embed.set_image(url=data["url"])
        x = datetime.datetime.now()
        time = x.strftime("%X")
        embed.set_footer(text=f'Requested by: {ctx.author.name} | at: {time}')
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    @commands.cooldown(rate=1, per=2.0)
    async def poke(self, ctx, user: discord.Member):
        async with aiohttp.ClientSession() as s:
            async with s.get("https://nekos.life/api/v2/img/poke") as r:
                data = await r.json()
        embed = discord.Embed(description="{} was poked by {}".format(user.mention, ctx.message.author.mention), color=random.choice(color_list))
        embed.set_image(url=data["url"])
        x = datetime.datetime.now()
        time = x.strftime("%X")
        embed.set_footer(text=f'Requested by: {ctx.author.name} | at: {time}')

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Fun_Commands(bot))
