import discord
from discord.ext import commands
import asyncio
from copy import deepcopy
from typing import List, Tuple

from utils.dialog import Dialog


class EmbedPaginator(Dialog):
    """ Represents an interactive menu containing multiple embeds. """

    def __init__(self, client: discord.Client, pages: [discord.Embed], message: discord.Message = None, *,
                control_emojis: Tuple[str, str, str, str, str] = None):
        """
        Initialize a new EmbedPaginator.
        """
        super().__init__()

        self._client = client
        self.pages = pages
        self.message = message

        self.control_emojis = control_emojis or ('⏮', '◀', '▶', '⏭')

    @property
    def formatted_pages(self):
        pages = deepcopy(self.pages)  # copy by value not reference
        for page in pages:
            if page.footer.text == discord.Embed.Empty:
                page.set_footer(text=f"({pages.index(page)+1}/{len(pages)})")
            else:
                if page.footer.icon_url == discord.Embed.Empty:
                    page.set_footer(text=f"{page.footer.text} - ({pages.index(page)+1}/{len(pages)})")
                else:
                    page.set_footer(icon_url=page.footer.icon_url, text=f"{page.footer.text} - ({pages.index(page)+1}/{len(pages)})")
        return pages

    async def run(self, users: List[discord.User], channel: discord.TextChannel = None):
        """
        Runs the paginator.
        """

        if channel is None and self.message is not None:
            channel = self.message.channel
        elif channel is None:
            raise TypeError("Missing argument. You need to specify a target channel.")

        self._embed = self.pages[0]

        if len(self.pages) == 1:  # no pagination needed in this case
            self.message = await channel.send(embed=self._embed)
            return

        self.message = await channel.send(embed=self.formatted_pages[0])
        current_page_index = 0

        for emoji in self.control_emojis:
            await self.message.add_reaction(emoji)

        def check(r: discord.Reaction, u: discord.User):
            res = (r.message.id == self.message.id) and (r.emoji in self.control_emojis)

            if len(users) > 0:
                res = res and u.id in [u1.id for u1 in users]

            return res

        while True:
            try:
                reaction, user = await self._client.wait_for('reaction_add', check=check, timeout=100)
            except asyncio.TimeoutError:
                try:
                    if not isinstance(channel, discord.channel.DMChannel) and not isinstance(channel, discord.channel.GroupChannel):
                        try:
                            await self.message.clear_reactions()
                        except discord.errors.Forbidden:
                            await self.message.edit(
                                comtent="`error: I'm missing required discord permission [ manage massages or emoji reactions ]`"
                                )
                        except Exception as e:
                            pass

                except discord.errors.Forbidden:
                    await self.message.edit(comtent="`error: I'm missing required discord permission [ manage messages ]`"
                    )
                return

            emoji = reaction.emoji
            max_index = len(self.pages) - 1

            if emoji == self.control_emojis[0]:
                load_page_index = 0

            elif emoji == self.control_emojis[1]:
                load_page_index = current_page_index - 1 if current_page_index > 0 else current_page_index

            elif emoji == self.control_emojis[2]:
                load_page_index = current_page_index + 1 if current_page_index < max_index else current_page_index

            elif emoji == self.control_emojis[3]:
                load_page_index = max_index

            else:
                await self.message.delete()
                return
                pass

            await self.message.edit(embed=self.formatted_pages[load_page_index])
            if not isinstance(channel, discord.channel.DMChannel) and not isinstance(channel, discord.channel.GroupChannel):
                try:
                    await self.message.remove_reaction(reaction, user)
                except discord.errors.Forbidden:
                    await self.message.edit(content="`error: I'm missing required discord permission [ manage messages ]`")


            current_page_index = load_page_index

    @staticmethod
    def generate_sub_lists(l: list) -> [list]:
        if len(l) > 25:
            sub_lists = []

            while len(l) > 20:
                sub_lists.append(l[:20])
                del l[:20]

            sub_lists.append(l)

        else:
            sub_lists = [l]

        return sub_lists


class BotEmbedPaginator(EmbedPaginator):
    def __init__(self, ctx: commands.Context, pages: [discord.Embed], message: discord.Message = None, *,
                 control_emojis: Tuple[str, str, str, str, str] = None):
        """
        Initialize a new EmbedPaginator.
        """
        self._ctx = ctx

        super(BotEmbedPaginator, self).__init__(ctx.bot, pages, message, control_emojis=control_emojis)

    async def run(self, channel: discord.TextChannel = None, users: List[discord.User] = None):
        """
        Runs the paginator.
        """

        if users is None:
            users = [self._ctx.author]

        if self.message is None and channel is None:
            channel = self._ctx.channel

        await super().run(users, channel)