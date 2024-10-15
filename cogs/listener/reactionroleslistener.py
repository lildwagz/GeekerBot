import asyncio


import discord
from discord.ext import commands


class reactionroleslistener(commands.Cog, name="reaction roles listener"):
    def __init__(self,bot):
        self.bot = bot

    @commands.command(brief="Adds reactions to a message")
    async def add_reaction(self, ctx, messageid: int, channel: discord.TextChannel):
        """
        add reaction role

        """
        async with ctx.channel.typing():
            message = await channel.fetch_message(messageid)

        try:
            def check(reaction, user):
                return user == message.author

            await ctx.send("Please react to the message above with the emoji of your choice. You have 20 secs to do so")
            reaction_tupel = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
            reaction = reaction_tupel[0]
            emoji = reaction.emoji
            # print(type(emoji))
            # print(emoji)
        except asyncio.TimeoutError:
            await ctx.send("Timed out please resend the command" + '👎')
            return
        else:
            await ctx.send("Done " + '👍')
        try:
            await ctx.send("Now please mention a role you want to give a user when then user"
                           " reacts with a the given emote. You have 30 seconds todo sp")

            def check(m):
                return m.author == ctx.message.author and m.channel == ctx.message.channel

            m = await self.bot.wait_for('message', timeout=20.0, check=check)
            role = m.role_mentions
        except asyncio.TimeoutError:
            await ctx.send("Timed out please resend the command" + '👎')
            return
        else:
            await ctx.send("Done " + '👍')
        await message.add_reaction(emoji)
        # insert_reaction.delay(ctx.guild.id, messageid, role[0].id, emoji)

    # @commands.command(brief="deletes reactions from a message, cant be undone")
    # async def del_reaction(self, messageid: int, emoji: discord.emoji):
    #     pass

    # @commands.Cog.listener()
    # async def on_raw_reaction_add(self, payload):
    #     if not payload.member.bot:
    #         if payload.emoji.name:
    #             roleid = await self.bot.sql.get_reaction_role(payload.guild_id, payload.message_id,
    #                                                              payload.emoji.name)
    #             if roleid:
    #                 role = discord.utils.get(payload.member.guild.roles, id=roleid)
    #                 await payload.member.add_roles(role, reason="reaction added", atomic=True)
    #
    # @commands.Cog.listener()
    # async def on_raw_reaction_remove(self, payload):
    #     if not payload.guild_id:
    #         return
    #     guild = self.bot.get_guild(payload.guild_id)
    #     member = guild.get_member(payload.user_id)
    #     if not member.bot:
    #         roleid = await self.bot.sql.get_reaction_role(payload.guild_id, payload.message_id, payload.emoji.name)
    #         if roleid:
    #             role = discord.utils.get(guild.roles, id=roleid)
    #             await member.remove_roles(role, reason="reaction removed", atomic=True)


def setup(bot):
    bot.add_cog(reactionroleslistener(bot))
