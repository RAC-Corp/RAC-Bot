from typing import Union, Any, Optional

import discord
from discord.ext import commands
from discord import app_commands

import aiohttp
import asyncio
import json as JSON

from racbot import RACBot
from utils.context import Context
from utils.enums import CommandSignatures, Endpoints, api_headers
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
        """Parent command"""

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @iisr.group(name='ban')
    async def iisr_ban(self, ctx: Context):
        """Parent for iisr ban commands"""

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @iisr_ban.command(name='list')
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

    @iisr_ban.command(name='temp', usage=CommandSignatures.iisr_temp_ban.value)
    @checks.is_a_mod()
    async def iisr_temp_ban(self, ctx: Context, *, flags: IISRTempBanFlags):
        """Ban a player temporarily in IISR

        Args:
            ctx (Context): _description_
            flags (IISRTempBanFlags): The flags to use
        """

        if flags.reason and len(flags.reason) > 100:
            raise HTTPException(414, 'Reason content too large (max 100)')

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

    @iisr_ban.command(name='perm', aliases=['permanent'], usage=CommandSignatures.iisr_perm_ban.value)
    @checks.is_a_mod()
    async def iisr_perm_ban(self, ctx: Context, *, flags: IISRPermBanFlags):
        """Ban a player permanently in IISR

        Args:
            ctx (Context): _description_
            flags (IISRPermBanFlags): The flags to use
        """

        if flags.reason and len(flags.reason) > 100:
            raise HTTPException(414, 'Reason content too large (max 100)')

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

    @iisr_ban.command(name='temp-all', usage=CommandSignatures.iisr_temp_ban.value)
    @checks.is_a_mod()
    async def iisr_temp_ban_all(self, ctx: Context, *, flags: IISRTempBanFlags):
        """Ban a player temporarily in IISR from all servers

        Args:
            ctx (Context): _description_
            flags (IISRTempBanFlags): The flags to use
        """

        if flags.reason and len(flags.reason) > 100:
            raise HTTPException(414, 'Reason content too large (max 100)')

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

    @iisr_ban.command(name='perm-all', usage=CommandSignatures.iisr_perm_ban.value)
    @checks.is_a_mod()
    async def iisr_perm_ban_all(self, ctx: Context, *, flags: IISRPermBanFlags):
        """Ban a player permanently in IISR from all servers

        Args:
            ctx (Context): _description_
            flags (IISRPermBanFlags): The flags to use
        """

        if flags.reason and len(flags.reason) > 100:
            raise HTTPException(414, 'Reason content too large (max 100)')

        json: dict[str, str] = {
            'username': flags.target
        }
        params: dict[str, str] = {
            'mod': ctx.author.name,
            'server_id': flags.serverid,
            'reason': flags.reason or 'No reason was provided'
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

    @iisr_ban.command(name='remove', aliases=['delete'])
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

    @iisr_ban.command(name='remove-all', aliases=['delete-all'])
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

    @iisr.command(name='kick')
    @checks.is_a_mod()
    async def iisr_kick(self, ctx: Context, target: str, *, reason: Optional[str] = None):
        """Kick a player from a server

        Args:
            ctx (Context): _description_
            target (str): The player to kick
            reason (Optional[str], optional): The reason for kicking the player. Defaults to None.
        """

        if not reason:
            reason = 'No reason provided'
        if len(reason) > 100:
            raise HTTPException(414, 'Reason content too large (max 100)')

        json: dict[str, str] = {
            'username': target
        }
        params: dict[str, str] = {
            'mod': ctx.author.name,
            'reason': reason
        }
        
        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(
                        Endpoints.iisr_kick, 
                        'get',
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

    @iisr.command(name='kick-all')
    @checks.is_a_mod()
    async def iisr_kick_all(self, ctx: Context, server_id: str, *, reason: Optional[str] = None):
        """Kick all players from a server

        Args:
            ctx (Context): _description_
            server_id (str): The server to kick all players from
            reason (Optional[str], optional): The reason for kicking all players. Defaults to None.
        """

        if not reason:
            reason = 'No reason provided'

        params: dict[str, str] = {
            'mod': ctx.author.name,
            'server_id': server_id,
            'reason': reason
        }
        
        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(
                        Endpoints.iisr_kick_all, 
                        'get',
                        headers=api_headers,
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

    @iisr.group(name='server', invoke_without_command=True)
    async def iisr_server(self, ctx: Context):
        """Parent for iisr server commands"""
        
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @iisr_server.command(name='shutdown')
    @checks.is_a_mod()
    async def iisr_server_shutdown(self, ctx: Context, server_id: str):
        """Shutdown a server

        Args:
            ctx (Context): _description_
            server_id (str): The server to shut down
        """

        json: dict[str, str] = {
            'id': server_id
        }
        params: dict[str, str] = {
            'mod': ctx.author.name,
        }
        
        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(
                        Endpoints.iisr_server_shutdown, 
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

    @iisr_server.command(name='info')
    @checks.is_a_mod()
    async def iisr_server_info(self, ctx: Context, server_id: str):
        """Get the info of a server

        Args:
            ctx (Context): _description_
            server_id (str): The server to fetch info from
        """

        params: dict[str, str] = {
            'mod': ctx.author.name,
            'server_id': server_id
        }
        
        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(
                        Endpoints.iisr_server_info, 
                        'get',
                        headers=api_headers,
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

    @iisr_server.command(name='lock')
    @checks.is_a_mod()
    async def iisr_server_lock(self, ctx: Context, server_id: str, *, duration: Optional[str] = None):
        """Lock a server for an optional amount of time

        Args:
            ctx (Context): _description_
            server_id (str): The server to lock
            duration (Optional[str], optional): The amount of time to keep the server locked for. Defaults to None.
        """

        if not duration:
            duration = '1 hour'

        json: dict[str, str] = {
            'id': server_id
        }
        params: dict[str, str] = {
            'mod': ctx.author.name,
            'duration': duration
        }
        
        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(
                        Endpoints.iisr_server_lock, 
                        'patch',
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

    @iisr_server.command(name='unlock')
    @checks.is_a_mod()
    async def iisr_server_unlock(self, ctx: Context, server_id: str):
        """Unlock a server

        Args:
            ctx (Context): _description_
            server_id (str): The server to unlock
        """

        json: dict[str, str] = {
            'id': server_id
        }
        params: dict[str, str] = {
            'mod': ctx.author.name,
        }
        
        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(
                        Endpoints.iisr_server_unlock, 
                        'patch',
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

    @iisr_server.command(name='announce')
    @checks.is_a_mod()
    async def iisr_server_announce(self, ctx: Context, server_id: str, *, text: str):
        """Send an announcement to a server

        Args:
            ctx (Context): _description_
            server_id (str): The server to announce to
            text (str): The text to send to the server
        """

        params: dict[str, str] = {
            'mod': ctx.author.name,
            'server_id': server_id,
            'text': text
        }
        
        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(
                        Endpoints.iisr_server_announce, 
                        'get',
                        headers=api_headers,
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
                
                await ctx.reply(f'ok, sent message of "{text}"')

    @iisr_server.command(name='announce-all')
    @checks.is_a_mod()
    async def iisr_server_announce_all(self, ctx: Context, *, text: str):
        """Send an announcement to all servers

        Args:
            ctx (Context): _description_
            text (str): The text to send to the servers
        """

        params: dict[str, str] = {
            'mod': ctx.author.name,
            'text': text
        }
        
        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(
                        Endpoints.iisr_server_announce_all, 
                        'get',
                        headers=api_headers,
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
                
                await ctx.reply(f'ok, sent message of "{text}"')


async def setup(bot: RACBot):
    await bot.add_cog(IISR(bot))