from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

import unicodedata
import time
import asyncio

from racbot import RACBot
from utils.context import Context
from utils.enums import Endpoints, api_headers
from utils.exceptions import HTTPException, GeneralException


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
class Utility(commands.GroupCog, name='utility'):
    """Utility commands"""

    def __init__(self, bot: RACBot) -> None:
        self.bot: RACBot = bot
        self.request = bot.functions.endpoint_request
        self.variables = bot.variables

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{TOOLBOX}')

    @commands.hybrid_command(aliases=['char'])
    async def charinfo(self, ctx: Context, *, characters: str):
        """Gets the information of up to 25 characters

        Args:
            ctx (Context): The context for this command
            characters (str): The characters to get information on
        """

        def to_string(c: str):
            digit: str = f'{ord(c):x}'
            name: str = unicodedata.name(c, 'Unknown Character')
            return f'`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>'

        msg: str = '\n'.join(map(to_string, characters))
        if len(msg) > 2000:
            return await ctx.handle_error(414, 'Message was too big to send')
        await ctx.reply(msg)


async def setup(bot: RACBot):
    await bot.add_cog(Utility(bot))