import discord
from discord.ext import commands

class Scripts(commands.Cog):
    types = ('tech', 'share')

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity = discord.Game('Testing Steward'))
        print('Steward is ready')

    
    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f'Version 0.0.1 online.')

    async def parse(self):
        pass

def setup(bot):
    bot.add_cog(Scripts(bot))

