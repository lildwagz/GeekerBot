import asyncio
import copy
import datetime as dt
import json
import typing
from json import loads
from urllib.parse import quote_plus

import discord
import humanize
import pendulum
import pendulum.exceptions
from discord import Color
from discord.ext import commands


class GetRequestFailedException(Exception): pass


class Utilss:

    def __init__(self, bot) -> None:
        self.bot = bot

        self.channel_emojis = {
            'text': '<:text:739399497200697465>',
            'text_locked': '<:text_locked:739399496953364511>',
            'text_nsfw': '<:text_nsfw:739399497251160115>',
            'news': '<:news:739399496936718337>',
            'news_locked': '<:news_locked:739399497062416435>',
            'voice': '<:voice:739399497221931058>',
            'voice_locked': '<:voice_locked:739399496924135476>',
            'category': '<:category:738960756233601097>'
        }

        self.badge_emojis = {
            'staff': '<:staff:738961032109752441>',
            'partner': '<:partner:738961058613559398>',
            'hypesquad': '<:hypesquad:738960840375664691>',
            'bug_hunter': '<:bug_hunter:738961014275571723>',
            'bug_hunter_level_2': '<:bug_hunter_level_2:739390267949580290>',
            'hypesquad_bravery': '<:hypesquad_bravery:738960831596855448>',
            'hypesquad_brilliance': '<:hypesquad_brilliance:738960824327995483>',
            'hypesquad_balance': '<:hypesquad_balance:738960813460684871>',
            'early_supporter': '<:early_supporter:738961113219203102>',
            'system': '<:system_1:738960703284576378><:system_2:738960703288770650>',
            'verified_bot': '<:verified_bot_1:738960728022581258><:verified_bot_2:738960728102273084>',
            'verified_bot_developer': '<:verified_bot_developer:738961212250914897>',
        }

        self.features = {
            'VERIFIED': 'Is verified server',
            'PARTNERED': 'Is partnered server',
            'MORE_EMOJI': 'Can have 50+ emoji',
            'DISCOVERABLE': 'Is discoverable',
            'FEATURABLE': 'Is featurable',
            'PUBLIC': 'Is public',
            'VIP_REGIONS': 'Can have VIP voice regions',
            'VANITY_URL': 'Can have vanity invite',
            'INVITE_SPLASH': 'Can have invite splash',
            'COMMERCE': 'Can have store channels',
            'NEWS': 'Can have news channels',
            'BANNER': 'Can have banner',
            'ANIMATED_ICON': 'Can have animated icon',
            'PUBLIC_DISABLED': 'Can not be public',
            'WELCOME_SCREEN_ENABLED': 'Can have welcome screen',
            'MEMBER_VERIFICATION_GATE_ENABLED': 'Has member verify gate'
        }

        self.mfa_levels = {
            0: 'Not required',
            1: 'Required'
        }

        self.colours = {
            discord.Status.online: 0x008000,
            discord.Status.idle: 0xFF8000,
            discord.Status.dnd: 0xFF0000,
            discord.Status.offline: 0x808080,
            discord.Status.invisible: 0x808080,
        }

        self.verification_levels = {
            discord.VerificationLevel.none: 'None - No criteria set.',
            discord.VerificationLevel.low: 'Low - Must have a verified email.',
            discord.VerificationLevel.medium: 'Medium - Must have a verified email and be registered on discord for more than 5 minutes.',
            discord.VerificationLevel.high: 'High - Must have a verified email, be registered on discord for more than 5 minutes and be a member of the guild for more '
                                            'then 10 minutes.',
            discord.VerificationLevel.extreme: 'Extreme - Must have a verified email, be registered on discord for more than 5 minutes, be a member of the guild for '
                                               'more then 10 minutes and a have a verified phone number.'
        }

        self.content_filter_levels = {
            discord.ContentFilter.disabled: 'None',
            discord.ContentFilter.no_role: 'No roles',
            discord.ContentFilter.all_members: 'All members',
        }

    def encode_uri(self, text: str) -> str:
        """ Encodes a string to URI text. """
        return quote_plus(text).replace("+", "%20")

    def format_seconds(self, *, seconds: int, friendly: bool = False) -> str:

        minute, second = divmod(seconds, 60)
        hour, minute = divmod(minute, 60)
        day, hour = divmod(hour, 24)

        days, hours, minutes, seconds = round(day), round(hour), round(minute), round(second)

        if friendly is True:
            return f'{f"{days}d " if not days == 0 else ""}{f"{hours}h " if not hours == 0 or not days == 0 else ""}{minutes}m {seconds}s'

        return f'{f"{days:02d}:" if not days == 0 else ""}{f"{hours:02d}:" if not hours == 0 or not days == 0 else ""}{minutes:02d}:{seconds:02d}'

    def convert_datetime(self, *, datetime: typing.Union[pendulum.datetime, dt.datetime]) -> pendulum.datetime:

        if isinstance(datetime, dt.datetime):
            datetime = pendulum.instance(datetime)

        return datetime

    def format_datetime(self, *, datetime: typing.Union[pendulum.datetime, dt.datetime]) -> str:
        return self.convert_datetime(datetime=datetime).format('dddd Do [of] MMMM YYYY [at] HH:mm A (zzZZ)')

    def format_difference(self, *, datetime: typing.Union[pendulum.datetime, dt.datetime],
                          suppress: typing.List[str] = None) -> str:

        if suppress is None:
            suppress = ['seconds']

        return humanize.precisedelta(pendulum.now(tz='UTC').diff(self.convert_datetime(datetime=datetime)),
                                     format='%0.0f', suppress=suppress)

    def activities(self, *, person: discord.Member) -> str:

        if not person.activities:
            return 'N/A'

        message = '\n'
        for activity in person.activities:

            if activity.type == discord.ActivityType.custom:
                message += f'• '
                if activity.emoji:
                    message += f'{activity.emoji} '
                if activity.name:
                    message += f'{activity.name}'
                message += '\n'

            elif activity.type == discord.ActivityType.playing:

                message += f'• Playing **{activity.name}** '
                if not isinstance(activity, discord.Game):
                    if activity.details:
                        message += f'**| {activity.details}** '
                    if activity.state:
                        message += f'**| {activity.state}** '
                    message += '\n'

            elif activity.type == discord.ActivityType.streaming:
                message += f'• Streaming **[{activity.name}]({activity.url})** on **{activity.platform}**\n'

            elif activity.type == discord.ActivityType.watching:
                message += f'• Watching **{activity.name}**\n'

            elif activity.type == discord.ActivityType.listening:

                if isinstance(activity, discord.Spotify):
                    url = f'https://open.spotify.com/track/{activity.track_id}'
                    message += f'• Listening to **[{activity.title}]({url})** by **{", ".join(activity.artists)}** '
                    if activity.album and not activity.album == activity.title:
                        message += f'from the album **{activity.album}** '
                    message += '\n'
                else:
                    message += f'• Listening to **{activity.name}**\n'

        return message

    def badges(self, *, person: typing.Union[discord.User, discord.Member]) -> str:
        member = discord.utils.get(self.bot.get_all_members(), id=person.id)
        badges = [badge for name, badge in self.badge_emojis.items() if dict(person.public_flags)[name] is True]
        if dict(person.public_flags)['verified_bot'] is False and person.bot:
            badges.append('<:bot:738979752244674674>')

        if any([guild.get_member(person.id).premium_since for guild in self.bot.guilds if person in guild.members]):
            badges.append('<:booster_level_4:738961099310760036>')

        if person.is_avatar_animated() or any(
                [guild.get_member(person.id).premium_since for guild in self.bot.guilds if person in guild.members]):
            badges.append('<:nitros:772586567092142100>')

        elif member:
            activity = discord.utils.get(member.activities, type=discord.ActivityType.custom)
            if activity:
                if activity.emoji and activity.emoji.is_custom_emoji():
                    badges.append('<:nitros:772586567092142100>')

        return ' '.join(badges) if badges else 'N/A'

    async def get_request(self, url, **kwargs):
        """ Does a GET request to a specific URL with a query parameters."""

        return_json, raise_errors, using_alexflipnote_token, force_json, content_type = False, False, False, False, False

        if len(kwargs.keys()) > 0:
            if kwargs.get("json") is not None:
                return_json = True
                kwargs.pop("json")
            if kwargs.get("raise_errors") is not None:
                raise_errors = True
                kwargs.pop("raise_errors")
            if kwargs.get("alexflipnote") is not None:
                using_alexflipnote_token = True
                kwargs.pop("alexflipnote")
            if kwargs.get("force_json") is not None:
                force_json = True
                kwargs.pop("force_json")
            # if kwargs.get("content_type") is not None:
            #     content_type = True
            #     kwargs.pop("content_type")

            query_param = "?" + "&".join(
                [i + "=" + quote_plus(str(kwargs[i])).replace("+", "%20") for i in kwargs.keys()])
        else:
            query_param = ""

        try:
            session = self.alex_client if using_alexflipnote_token else self.default_client
            result = await session.get(url + query_param)
            assert result.status < 400
            if return_json:
                if force_json:
                    result = await result.read()
                    return json.loads(result)

                return await result.json()
            return await result.text()
        except Exception as e:
            if raise_errors:
                raise GetRequestFailedException("Request Failed. Exception: " + str(e))
            return None


async def determine_prefix(bot, message):
    """Get the prefix used in the invocation context."""
    if message.guild:
        prefix = bot.cache.prefixes.get(str(message.guild.id), bot.prefixdefault)
        return commands.when_mentioned_or(prefix)(bot, message)
    else:
        return commands.when_mentioned_or(bot.prefixdefault)(bot, message)


async def send_success(ctx, message):
    await ctx.send(
        embed=discord.Embed(description=":white_check_mark: " + message, color=int("77b255", 16))
    )

async def send_error_message(ctx, message):
    await ctx.send(
        embed=discord.Embed(
            title="Error",
            description=message,
            color=Color.red()
        )
    )

async def toogle_enable(ctx, message):

    await ctx.send(
        embed=discord.Embed(description=f":white_check_mark: " + message,color=0x2fa737)
    )

async def toogle_disable(ctx, message):
    await ctx.send(
        embed=discord.Embed(description=f":white_check_mark: " + message,colour=0xe00000)
    )

async def success_actionmessage(ctx, case, mass=False):
    output = f"**{case}** the user"

    if mass:
        output = f"**{case}** the IDs/Users"

    await ctx.send(
        embed=discord.Embed(description=f"✅ Successfully " + output,colour=0xe00000)
    )

class TwoWayIterator:
    """Two way iterator class that is used as the backend for paging."""

    def __init__(self, list_of_stuff):
        self.items = list_of_stuff
        self.index = 0

    def next(self):
        if self.index == len(self.items) - 1:
            return None
        else:
            self.index += 1
            return self.items[self.index]

    def previous(self):
        if self.index == 0:
            return None
        else:
            self.index -= 1
            return self.items[self.index]

    def current(self):
        return self.items[self.index]

async def reaction_buttons(
    ctx, message, functions, timeout=300.0, only_author=False, single_use=False, only_owner=False
):
    """
    Handler for reaction buttons
    :param message     : message to add reactions to
    :param functions   : dictionary of {emoji : function} pairs. functions must be async.
                         return True to exit
    :param timeout     : time in seconds for how long the buttons work for.
    :param only_author : only allow the user who used the command use the buttons
    :param single_use  : delete buttons after one is used
    """

    try:
        for emojiname in functions:
            await message.add_reaction(emojiname)
    except discord.errors.Forbidden:
        return

    def check(payload):
        return (
            payload.message_id == message.id
            and str(payload.emoji) in functions
            and not payload.member == ctx.bot.user
            and (
                (payload.member.id == ctx.bot.owner_id)
                if only_owner
                else (payload.member == ctx.author or not only_author)
            )
        )

    while True:
        try:
            payload = await ctx.bot.wait_for("raw_reaction_add", timeout=timeout, check=check)

        except asyncio.TimeoutError:
            break
        else:
            exits = await functions[str(payload.emoji)]()
            try:
                await message.remove_reaction(payload.emoji, payload.member)
            except discord.errors.NotFound:
                pass
            except discord.errors.Forbidden:
                await ctx.send(
                    "`error: I'm missing required discord permission [ manage messages ]`"
                )
            if single_use or exits is True:
                break

    for emojiname in functions:
        try:
            await message.clear_reactions()
        except (discord.errors.NotFound, discord.errors.Forbidden):
            pass


async def paginate_list(ctx, items, use_locking=False, only_author=False):
    pages = TwoWayIterator(items)
    msg = await ctx.send(pages.current())

    async def next_result():
        new_content = pages.next()
        if new_content is None:
            return
        await msg.edit(content=new_content, embed=None)

    async def previous_result():
        new_content = pages.previous()
        if new_content is None:
            return
        await msg.edit(content=new_content, embed=None)

    async def done():
        return True

    functions = {"⬅": previous_result, "➡": next_result}
    if use_locking:
        functions["🔒"] = done

    asyncio.ensure_future(reaction_buttons(ctx, msg, functions, only_author=only_author))


async def page_switcher(ctx, pages):
    """
    :param ctx   : Context
    :param pages : List of embeds to use as pages
    """

    if len(pages) == 1:
        return await ctx.send(embed=pages[0])

    pages = TwoWayIterator(pages)

    # add all page numbers
    for i, page in enumerate(pages.items, start=1):
        old_footer = page.footer.text
        if old_footer == discord.Embed.Empty:
            old_footer = None
        page.set_footer(
            text=f"{i}/{len(pages.items)}" + (f" | {old_footer}" if old_footer is not None else "")
        )

    msg = await ctx.send(embed=pages.current())

    async def switch_page(content):
        await msg.edit(embed=content)

    async def previous_page():
        content = pages.previous()
        if content is not None:
            await switch_page(content)

    async def next_page():
        content = pages.next()
        if content is not None:
            await switch_page(content)

    functions = {"⬅": previous_page, "➡": next_page}
    asyncio.ensure_future(reaction_buttons(ctx, msg, functions))


def create_pages(content, rows, maxrows=15, maxpages=10):
    """
    :param content : Embed object to use as the base
    :param rows    : List of rows to use for the embed description
    :param maxrows : Maximum amount of rows per page
    :param maxpages: Maximu amount of pages until cut off
    :returns       : List of Embed objects
    """
    pages = []
    content.description = ""
    thisrow = 0
    rowcount = len(rows)
    for row in rows:
        thisrow += 1
        if len(content.description) + len(row) < 2000 and thisrow < maxrows + 1:
            content.description += f"\n{row}"
            rowcount -= 1
        else:
            thisrow = 1
            if len(pages) == maxpages - 1:
                content.description += f"\n*+ {rowcount} more entries...*"
                pages.append(content)
                content = None
                break

            pages.append(content)
            content = copy.deepcopy(content)
            content.description = f"{row}"
            rowcount -= 1

    if content is not None and not content.description == "":
        pages.append(content)

    return pages


async def send_as_pages(ctx, content, rows, maxrows=15, maxpages=10):
    """
    :param ctx     : Context
    :param content : Base embed
    :param rows    : Embed description rows
    :param maxrows : Maximum amount of rows per page
    :param maxpages: Maximum amount of pages untill cut off
    """
    pages = create_pages(content, rows, maxrows, maxpages)
    if len(pages) > 1:
        await page_switcher(ctx, pages)
    else:
        await ctx.send(embed=pages[0])

