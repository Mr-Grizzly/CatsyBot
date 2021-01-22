from discord.ext import commands


class Calculator(commands.Cog):
    """Calculator commands"""
    def __init__(self, client):
        self.guild = None
        self.author = None
        self.client = client

    @commands.command()
    async def add(self, ctx, a: int, b: int):
        """+ calculator"""
        await ctx.send(a + b)

    @commands.command()
    async def sub(self, ctx, a: int, b: int):
        """- calculator"""
        await ctx.send(a - b)

    @commands.command()
    async def multiply(self, ctx, a: int, b: int):
        """x calculator"""
        await ctx.send(a * b)

    @commands.command()
    async def divide(self, ctx, a: int, b: int):
        """: calculator"""
        await ctx.send(a / b)


def setup(bot):
    bot.add_cog(Calculator(bot))
