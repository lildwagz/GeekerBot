import typing
from abc import ABC

import discord
import fuzzywuzzy.process
import pendulum
import yarl
from discord.ext import commands


class ChannelEmojiConverter(commands.Converter, ABC):

    async def convert(self, ctx, channel: discord.abc.GuildChannel) -> str:

        if isinstance(channel, discord.VoiceChannel):
            emoji = 'voice'
            if channel.overwrites_for(channel.guild.default_role).connect is False:
                emoji = 'voice_locked'

        else:
            if channel.is_news():
                emoji = 'news'
                if channel.overwrites_for(channel.guild.default_role).read_messages is False:
                    emoji = 'news_locked'
            else:
                emoji = 'text'
                if channel.is_nsfw():
                    emoji = 'text_nsfw'
                elif channel.overwrites_for(channel.guild.default_role).read_messages is False:
                    emoji = 'text_locked'

        return ctx.bot.utils.channel_emojis[emoji]


class TimezoneConverter(commands.Converter, ABC):

    async def convert(self, ctx, argument: str) -> typing.Any:
        timezones = [timezone for timezone in pendulum.timezones]

        if argument not in timezones:
            matches = fuzzywuzzy.process.extract(query=argument, choices=pendulum.timezones, limit=5)
            extra_message = '\n'.join([f'`{index + 1}.` {match[0]}' for index, match in enumerate(matches)])
            raise ctx.ArgumentError(
                f'That was not a recognised timezone. Maybe you meant one of these?\n{extra_message}')

        return pendulum.timezone(argument)


class User(commands.UserConverter):

    async def convert(self, ctx, argument: str) -> discord.User:
        user = None
        try:
            user = await super().convert(ctx, argument)
        except commands.BadArgument:
            pass

        if not user:
            try:
                user = await ctx.bot.fetch_user(argument)
            except discord.NotFound:
                raise commands.BadArgument
            except discord.HTTPException:
                raise commands.BadArgument

        return user


