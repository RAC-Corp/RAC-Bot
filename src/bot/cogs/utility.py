from typing import Any

import discord
from discord.ext import commands

import unicodedata

from racbot import RACBot
from utils.context import Context
from utils.enums import Endpoints, api_headers


class Utility(commands.Cog):
    """Utility commands"""

    def __init__(self, bot: RACBot) -> None:
        self.bot: RACBot = bot

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{TOOLBOX}')

    @commands.group(invoke_without_command=True)
    async def ping(self, ctx: Context):
        """Get the ping of the bot"""

        await ctx.reply(f'pong! {round(self.bot.latency, 3)} ms')

    @ping.command(name='api')
    async def ping_api(self, ctx: Context):
        """Ping the API"""

        async with ctx.typing():
            async with self.bot.session.get(Endpoints.UTILITY_PING.value, headers=api_headers) as resp:
                if resp.status != 200:
                    return await ctx.handle_error(resp.status, resp.reason)
                
                data: Any = await resp.json()
                await ctx.reply(data['response'])

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