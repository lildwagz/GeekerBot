import discord, typing
from discord.ext import commands

from utils import utilss
from utils.engenees import initdata, convert, units_of


class engineer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['cvrt'])
    async def convert(self, ctx, units_from: str, units_to: str, quantity: typing.Optional[float] = 1):
        """Gives the conversion factor between units
            Converts from one unit to another by an optional scalar amount
        """
        sheet = initdata("assets/sheets/")
        try:
            conversion_factor = convert(sheet[0], units_from, units_to, quantity)
            await ctx.send(str(conversion_factor) + " " + units_to + " per " + str(quantity) + " " + units_from)
        except:
            await utilss.send_error_message(ctx,"Could not find conversion factor for those units.")

    @commands.command(pass_context=True, aliases=['units'])
    async def unitsof(self, ctx, unit: str):
        """Lists the units of a certain quantity (e.g. velocity)"""
        sheet = initdata("assets/sheets/")

        try:
            content = discord.Embed(title=f"Units of {unit}",description=f"```{units_of(sheet[0], unit)}```")
            await ctx.send(embed=content)
        except:
            await utilss.send_error_message(ctx,"Could not find units of type: " + unit)

    @commands.command(pass_context=True, aliases=['const'])
    async def constant(self, ctx, variable: str):
        """Gives info about a constant
            Prints info about a given constant or shows all known constants if you type 'show' after the command
        """
        sheet = initdata("assets/sheets/")
        if variable in ['show', 'list']:
            constants = list(sheet[1].keys())
            # await ctx.send("Constants: " + ", ".join(constants[1:]))
            content = discord.Embed(title="Constants: ")
            await utilss.send_as_pages(ctx, content ,constants)
        else:
            try:
                header = " ".join(sheet[1][variable][:1])
                rest = " ".join(sheet[1][variable][1:])
                content = discord.Embed(title=f"{header}\'s constant ", description=f"```{rest}```")
                await ctx.send(embed=content)
            except:
                await utilss.send_error_message(ctx,"Could not find constant: " + variable)

    @commands.command(pass_context=True, aliases=['par'])
    async def parallel(self, ctx, *resistors: float):
        """Returns the equivalent resistance of parallel elements
            MUST use SI units
        """
        total = 0
        for R in resistors:
            total += 1 / R
        try:
            await ctx.send(f"```Equivalent resistance is: {1 / total} Ohms ```")
        except ZeroDivisionError as e:
            await ctx.send(f"```{e}```")


def setup(bot):
    bot.add_cog(engineer(bot))
