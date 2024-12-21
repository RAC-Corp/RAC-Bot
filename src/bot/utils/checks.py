from discord.ext.commands import check
from .context import Context


mod_list: list[str] = [
    'sledge_hammer',
    'regulated',
    'harrisson19',
    'kunzine',
    'striving',
    'reinhardcooldude',
    'kaog',
    'chocolate0of',
    # TODO: add more
]


def is_a_mod():
    async def predicate(ctx: Context) -> bool:
        return ctx.author.name in mod_list
    return check(predicate)