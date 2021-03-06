from __future__ import annotations

from itertools import chain
from pprint import pprint
from typing import Optional, Union

import discord
import httpx
import validators
from discord.ext import commands
from httpx_auth import OAuth2ResourceOwnerPasswordCredentials

from steward_discord.config import PASSWORD, STEWARD_URL, USERNAME

THUMBSUP_EMOJI = '👍'


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
        await ctx.send('Version 0.0.1 online.')

    @commands.command()
    @commands.is_owner()
    async def parse(self, ctx, channel_name: str):
        if channel_name not in ParseContentHistory.types:
            raise ValueError(f'Channel not one of {str(ParseContentHistory.types)}')

        channel: Optional[discord.TextChannel] = discord.utils.get(ctx.guild.text_channels, name=channel_name)
        if channel is None:
            raise ValueError(f'Channel #{channel_name} not Found')

        # Find last message parsed
        history_after = await self.last_parsed_message(channel) 
        if history_after == await channel.fetch_message(channel.last_message_id):
            await ctx.send('No new messages to be parsed')
            return

        async with httpx.AsyncClient() as client:
            request_auth = OAuth2ResourceOwnerPasswordCredentials(token_url=STEWARD_URL + '/token', username=USERNAME, password=PASSWORD)

            async for message in channel.history(after=history_after, oldest_first=True):
                message: discord.Message
                contents = self.parse_message(message)

                for content in contents:
                    result = await client.post(STEWARD_URL, json=content, auth=request_auth)
                    print(result)

                # Mark message as parsed
                await message.add_reaction(THUMBSUP_EMOJI)

    @commands.command(name='clean-reactions')
    @commands.is_owner()
    async def clean_reactions(self, ctx, channel_name: str):
        if channel_name not in ParseContentHistory.types:
            raise ValueError(f'Channel not one of {str(ParseContentHistory.types)}')

        channel: Optional[discord.TextChannel] = discord.utils.get(ctx.guild.text_channels, name=channel_name)
        if channel is None:
            raise ValueError(f'Channel #{channel_name} not Found')

        async for message in channel.history():
            message: discord.Message
            await message.clear_reactions()


    # TODO: Generate pydantic models and then use them from a library
    @staticmethod
    def parse_message(message: discord.Message) -> list[dict]:
        lines = message.content.splitlines()
        urls, description = [], []

        for line in lines:
            urls.append(line) if validators.url(line) else description.append(line) 

        embeds = message.embeds.copy()
    
        contents = []
        for url in urls:
            embedded_descriptions = []
            for index, embed in enumerate(embeds.copy()):
                if embed.url == url:
                    embeds.pop(index)
                    # TODO: Figure out if I want to always include titles
                    embedded_description: Optional[str] = embed.description if embed.description else embed.title if embed.title else None
                    if embedded_description:
                        embedded_descriptions.append(embedded_description)
                    break

            meta = ' \n::\n '.join(chain(description, embedded_descriptions))
            print(meta)

            contents.append(dict(
                meta=meta,
                url=url,
                source_id=message.guild.name,
                type_id=message.channel.name,
                ))

        return contents

    @staticmethod
    async def last_parsed_message(channel: discord.TextChannel) -> Optional[discord.Message]:
        # Based on https://www.python.org/dev/peps/pep-0492/#example-1
        message_iterator = channel.history().__aiter__()
        while True:
            try:
                current_message: discord.Message = await message_iterator.__anext__()
                if discord.utils.find(lambda reaction: reaction.emoji == THUMBSUP_EMOJI and reaction.me is True, current_message.reactions):
                    return current_message
            except StopAsyncIteration:
                break

def setup(bot):
    bot.add_cog(ParseContentHistory(bot))

