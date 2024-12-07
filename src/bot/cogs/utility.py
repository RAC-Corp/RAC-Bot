from typing import Any

import discord
from discord.ext import commands

from racbot import RACBot
from utils.context import Context
from utils.enums import Endpoints, api_headers


class Utility(commands.Cog):
    """Utility commands"""

    def __init__(self, bot: RACBot):
        self.bot: RACBot = bot

    @commands.group(invoke_without_command=True)
    async def ping(self, ctx: Context):
        """Get the ping of the bot"""

        await ctx.reply(f'pong! {round(self.bot.latency), 3} ms')

    @ping.command()
    async def ping_api(self, ctx: Context):
        """Ping the API"""

        async with self.bot.session.get(Endpoints.UTILITY_PING.value, headers=api_headers) as resp:
            if resp.status != 200:
                return await ctx.handle_error(resp.status, resp.reason)
            
            data: Any = await resp.json()
            await ctx.reply(data['response'])


async def setup(bot: RACBot):
    await bot.add_cog(Utility(bot))