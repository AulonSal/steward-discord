from __future__ import annotations

from itertools import chain

import discord
import httpx

from discord.ext import commands
from steward_discord.config import PASSWORD, STEWARD_URL, USERNAME
from httpx_auth import OAuth2ResourceOwnerPasswordCredentials


class ParseContentHistory(commands.Cog):
    types = ('tech', 'share')

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    @commands.check
    async def globally_block_dms(ctx):
        return ctx.guild is not None

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity = discord.Game('Testing Steward'))
        print('Steward is ready')

    
    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f'Version 0.0.1 online.')

    @commands.command()
    @commands.is_owner()
    async def parse(self, ctx, channel_name: str):
        if channel_name not in ParseContentHistory.types:
            raise ValueError(f'Channel not one of {str(ParseContentHistory.types)}')

        channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
        if channel is None:
            raise ValueError(f'Channel #{channel_name} not Found')

        async with httpx.AsyncClient() as client:
            request_auth = OAuth2ResourceOwnerPasswordCredentials(token_url=STEWARD_URL + '/token', username=USERNAME, password=PASSWORD)

            async for message in channel.history(limit=2):
                message: discord.Message

                url, *description = message.content.splitlines()
                embedded_description = [embed.description for embed in message.embeds]
                meta = '\n::\n'.join(chain(description, embedded_description))
            
                # TODO: Generate pydantic models and then use them from a library
                content = dict(
                    meta=meta,
                    url=url,
                    source_id=ctx.guild.name,
                    type_id=channel_name,
                    )

                result = await client.post(STEWARD_URL, json=content, auth=request_auth)
                print(result)


def setup(bot):
    bot.add_cog(ParseContentHistory(bot))

