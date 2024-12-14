from typing import Union, Any

import aiohttp.client_exceptions
import discord
from discord.ext import commands
from discord import app_commands

import aiohttp
import aiohttp.client_exceptions as ClientExceptions

from racbot import RACBot
from utils.context import Context
from utils.enums import Endpoints, api_headers
from utils.flags import (
    IISRTempBanFlags,
    IISRPermBanFlags
)


class Roblox(commands.Cog):
    """Roblox commands for our games"""

    def __init__(self, bot: RACBot) -> None:
        self.bot: RACBot = bot

    async def get_body(self, response: aiohttp.ClientResponse) -> Union[Any, str]:
        try:
            body = await response.json()
            return body
        except:
            body = await response.text()
            return body

    @commands.group()
    async def iisr(self, ctx: Context):
        pass

    @iisr.command(name='tempban')
    async def iisr_temp_ban(self, ctx: Context, *, flags: IISRTempBanFlags):
        """Ban a player temporarily in IISR

        Args:
            ctx (Context): _description_
            flags (IISRTempBanFlags): The flags to use
        
        Usage:
            r.iisr tempban -target <str> -duration <str> -reason <str?>
            r.iisr tempban -target rulebreaker -duration 14 days -reason breaking rules
        """

        json: dict[str, str] = {
            'username': flags.target
        }
        params: dict[str, str] = {
            'mod': ctx.author.name,
            'duration': flags.duration,
            'reason': flags.reason or 'No reason provided'
        }
        
        async with ctx.typing():
            try:
                async with self.bot.session.post(
                    Endpoints.PERM_BAN_CREATE.value, 
                    headers=api_headers,
                    json=json,
                    params=params
                ) as resp:
                    if resp.status != 200:
                        body: Union[Any, str] = await self.get_body(resp)
                        return await ctx.handle_error_body(resp.status, body, resp.reason)
            except (TimeoutError, ClientExceptions.SocketTimeoutError):
                await ctx.handle_error(504, 'Gateway Timeout')
            else:
                await ctx.reply('ok')

    @iisr.command(name='permban')
    async def iisr_perm_ban(self, ctx: Context, *, flags: IISRPermBanFlags):
        """Ban a player permanently in IISR

        Args:
            ctx (Context): _description_
            flags (IISRPermBanFlags): The flags to use
        
        Usage:
            r.iisr permban -target <str> -reason <str?>
            r.iisr permban -target rulebreaker -reason breaking rules
        """

        json: dict[str, str] = {
            'username': flags.target
        }
        params: dict[str, str] = {
            'mod': ctx.author.name,
            'reason': flags.reason or 'No reason provided'
        }
        
        async with ctx.typing():
            try:
                async with self.bot.session.post(
                    Endpoints.PERM_BAN_CREATE.value, 
                    headers=api_headers,
                    json=json,
                    params=params
                ) as resp:
                    if resp.status != 200:
                        body: Union[Any, str] = await self.get_body(resp)
                        return await ctx.handle_error_body(resp.status, body, resp.reason)
            except (TimeoutError, ClientExceptions.SocketTimeoutError):
                await ctx.handle_error(504, 'Gateway Timeout')
            else:
                await ctx.reply('ok')


async def setup(bot: RACBot):
    await bot.add_cog(Roblox(bot))