from .secrets import PASSWORD, USERNAME, token, STEWARD_URL

cogs: list[str] = []

primary_cogs: list[str] = [
        'content',
        ]

cogs.extend(['cogs.' + cog for cog in primary_cogs])

