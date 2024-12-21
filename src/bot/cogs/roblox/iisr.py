from typing import Union, Any, Optional

import discord
from discord.ext import commands
from discord import app_commands

import aiohttp
import asyncio
import json as JSON

from racbot import RACBot
from utils.context import Context
from utils.enums import  CommandSignatures, Endpoints, api_headers
from utils.exceptions import HTTPException, GeneralException
from utils import checks
from utils.flags import (
    IISRTempBanFlags,
    IISRPermBanFlags,
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
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.guild_only()
    async def iisr(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @iisr.command(name='bans')
    @checks.is_a_mod()
    async def iisr_bans(self, ctx: Context):
        """Get the list of banned players

        Args:
            ctx (Context): _description_
        """

        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(
                        Endpoints.iisr_bans, 
                        'get',
                        headers=api_headers
                    ),
                    timeout=30
                )
            except TimeoutError:
                raise HTTPException(504, 'Gateway Timeout')
            except Exception as e:
                raise commands.CommandInvokeError(e)
            else:
                status, reason, body = request
                if status not in self.variables['ok_status_codes']:
                    raise HTTPException(status, reason or 'Unknown Error Detail', body)
                
                if type(body) == dict:
                    await ctx.reply(f'```js\n{body}```')
                else:
                    await ctx.handle_error_no_http('API returned a non-JSON response')

    @iisr.command(name='tempban', usage=CommandSignatures.iisr_temp_ban.value)
    @checks.is_a_mod()
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
                        Endpoints.iisr_temp_ban_create, 
                        'post',
                        headers=api_headers,
                        json=json,
                        params=params
                    ),
                    timeout=30
                )
            except TimeoutError:
                raise HTTPException(504, 'Gateway Timeout')
            except Exception as e:
                raise commands.CommandInvokeError(e)
            else:
                status, reason, body = request
                if status not in self.variables['ok_status_codes']:
                    raise HTTPException(status, reason or 'Unknown Error Detail', body)
                
                await ctx.reply('done')

    @iisr.command(name='permban', usage=CommandSignatures.iisr_perm_ban.value)
    @checks.is_a_mod()
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
                        Endpoints.iisr_perm_ban_create, 
                        'post',
                        headers=api_headers,
                        json=json,
                        params=params
                    ),
                    timeout=30
                )
            except TimeoutError:
                raise HTTPException(504, 'Gateway Timeout')
            except Exception as e:
                raise commands.CommandInvokeError(e)
            else:
                status, reason, body = request
                if status not in self.variables['ok_status_codes']:
                    raise HTTPException(status, reason or 'Unknown Error Detail', body)
                
                await ctx.reply('done')

    @iisr.command(name='tempban-allservers', usage=CommandSignatures.iisr_temp_ban.value)
    @checks.is_a_mod()
    async def iisr_temp_ban_all(self, ctx: Context, *, flags: IISRTempBanFlags):
        """Ban a player temporarily in IISR from all servers

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
                        Endpoints.iisr_temp_ban_all_servers, 
                        'post',
                        headers=api_headers,
                        json=json,
                        params=params
                    ),
                    timeout=30
                )
            except TimeoutError:
                raise HTTPException(504, 'Gateway Timeout')
            except Exception as e:
                raise commands.CommandInvokeError(e)
            else:
                status, reason, body = request
                if status not in self.variables['ok_status_codes']:
                    raise HTTPException(status, reason or 'Unknown Error Detail', body)
                
                await ctx.reply('done')

    @iisr.command(name='permban-allservers', usage=CommandSignatures.iisr_perm_ban.value)
    @checks.is_a_mod()
    async def iisr_perm_ban_all(self, ctx: Context, *, flags: IISRPermBanFlags):
        """Ban a player permanently in IISR from all servers

        Args:
            ctx (Context): _description_
            flags (IISRPermBanFlags): The flags to use
        
        Usage:
            !!iisr permban-allservers -target <str> -serverid <str> -reason [str]
            !!iisr permban-allservers -target rulebreaker -serverid asd -reason breaking rules
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
                        Endpoints.iisr_perm_ban_all_servers, 
                        'post',
                        headers=api_headers,
                        json=json,
                        params=params
                    ),
                    timeout=30
                )
            except TimeoutError:
                raise HTTPException(504, 'Gateway Timeout')
            except Exception as e:
                raise commands.CommandInvokeError(e)
            else:
                status, reason, body = request
                if status not in self.variables['ok_status_codes']:
                    raise HTTPException(status, reason or 'Unknown Error Detail', body)
                
                await ctx.reply('done')

    @iisr.command(name='unban')
    @checks.is_a_mod()
    async def iisr_unban(self, ctx: Context, target: str, server_id: str):
        """Unban a player

        Args:
            ctx (Context): _description_
            target (str): The player to unban
            server_id (str): The server to unban the player from
        """

        json: dict[str, str] = {
            'username': target
        }
        params: dict[str, str] = {
            'mod': ctx.author.name,
            'server_id': server_id
        }
        
        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(
                        Endpoints.iisr_ban_remove, 
                        'delete',
                        headers=api_headers,
                        json=json,
                        params=params
                    ),
                    timeout=30
                )
            except TimeoutError:
                raise HTTPException(504, 'Gateway Timeout')
            except Exception as e:
                raise commands.CommandInvokeError(e)
            else:
                status, reason, body = request
                if status not in self.variables['ok_status_codes']:
                    raise HTTPException(status, reason or 'Unknown Error Detail', body)
                
                await ctx.reply('done')

    @iisr.command(name='unban-allservers')
    @checks.is_a_mod()
    async def iisr_unban_all_servers(self, ctx: Context, *, target: str):
        """Unban a player from all servers

        Args:
            ctx (Context): _description_
            target (str): The player to unban
        """

        json: dict[str, str] = {
            'username': target
        }
        params: dict[str, str] = {
            'mod': ctx.author.name,
        }
        
        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(
                        Endpoints.iisr_ban_remove_all_servers, 
                        'delete',
                        headers=api_headers,
                        json=json,
                        params=params
                    ),
                    timeout=30
                )
            except TimeoutError:
                raise HTTPException(504, 'Gateway Timeout')
            except Exception as e:
                raise commands.CommandInvokeError(e)
            else:
                status, reason, body = request
                if status not in self.variables['ok_status_codes']:
                    raise HTTPException(status, reason or 'Unknown Error Detail', body)
                
                await ctx.reply('done')
            
    # TODO: kick commands and server commands


async def setup(bot: RACBot):
    await bot.add_cog(IISR(bot))