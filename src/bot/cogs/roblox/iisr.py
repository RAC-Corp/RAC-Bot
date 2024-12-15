from typing import Union, Any, Optional

import aiohttp.client_exceptions
import discord
from discord.ext import commands
from discord import app_commands

import aiohttp
import asyncio
import json as JSON

from racbot import RACBot
from utils.context import Context
from utils.enums import  CommandSignatures, Endpoints, api_headers
from utils.flags import (
    IISRTempBanFlags,
    IISRPermBanFlags
)


class IISR(commands.Cog):
    """IISR game commands"""

    def __init__(self, bot: RACBot) -> None:
        self.bot: RACBot = bot
        self.get_body = bot.functions.get_body
        self.request = bot.functions.endpoint_request
        self.variables = bot.variables

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{VIDEO GAME}')

    @commands.group(invoke_without_command=True)
    async def iisr(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @iisr.command(name='tempban', usage=CommandSignatures.iisr_temp_ban.value)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.guild_only()
    async def iisr_temp_ban(self, ctx: Context, *, flags: IISRTempBanFlags):
        """Ban a player temporarily in IISR

        Args:
            ctx (Context): _description_
            flags (IISRTempBanFlags): The flags to use
        
        Usage:
            !!iisr tempban -target <str> -duration <str> -serverid <str> -reason [str]
            !!iisr tempban -target rulebreaker -duration 14 days -serverid asd -reason breaking rules
        """

        json: dict[str, str] = {
            'username': flags.target,
        }
        params: dict[str, str] = {
            'mod': ctx.author.name,
            'duration': flags.duration,
            'server_id': flags.serverid,
            'reason': flags.reason or 'No reason provided'
        }
        
        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(
                        Endpoints.TEMP_BAN_CREATE, 
                        'post',
                        headers=api_headers,
                        json=json,
                        params=params
                    ),
                    timeout=30
                )
            except TimeoutError:
                await ctx.handle_error(504, 'Gateway Timeout')
            except Exception as e:
                self.bot.logger.exception(e)
                await ctx.handle_error_no_http('woops')
            else:
                status, reason, body = request
                if status not in self.variables['ok_status_codes']:
                    return await ctx.handle_error_body(status, body, reason)
                
                await ctx.reply('done')

    @iisr.command(name='permban', usage=CommandSignatures.iisr_perm_ban.value)
    async def iisr_perm_ban(self, ctx: Context, *, flags: IISRPermBanFlags):
        """Ban a player permanently in IISR

        Args:
            ctx (Context): _description_
            flags (IISRPermBanFlags): The flags to use
        
        Usage:
            !!iisr permban -target <str> -serverid <str> -reason [str]
            !!iisr permban -target rulebreaker -serverid asd -reason breaking rules
        """

        json: dict[str, str] = {
            'username': flags.target
        }
        params: dict[str, str] = {
            'mod': ctx.author.name,
            'server_id': flags.serverid,
            'reason': flags.reason or 'No reason provided'
        }
        
        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(
                        Endpoints.PERM_BAN_CREATE, 
                        'post',
                        headers=api_headers,
                        json=json,
                        params=params
                    ),
                    timeout=30
                )
            except TimeoutError:
                await ctx.handle_error(504, 'Gateway Timeout')
            except Exception as e:
                self.bot.logger.exception(e)
                await ctx.handle_error_no_http('woops')
            else:
                status, reason, body = request
                if status not in self.variables['ok_status_codes']:
                    return await ctx.handle_error_body(status, body, reason)
                
                await ctx.reply('done')


async def setup(bot: RACBot):
    await bot.add_cog(IISR(bot))