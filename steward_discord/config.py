from .secrets import PASSWORD, USERNAME, token

cogs: list[str] = []

primary_cogs: list[str] = [
        'content',
        ]

cogs.extend(['cogs.' + cog for cog in primary_cogs])

STEWARD_URL = 'https://steward.aulonsal.com'
