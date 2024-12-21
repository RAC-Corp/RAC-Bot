from typing import Union, Any, Optional

import discord
from discord.ext import commands
from discord import app_commands

import aiohttp
import asyncio
import json as JSON

from racbot import RACBot
from utils.context import Context
from utils.enums import Endpoints, api_headers
from utils.exceptions import HTTPException, GeneralException
from utils import checks


class RoGuessr(commands.Cog):
    """RoGuessr game commands"""

    def __init__(self, bot: RACBot):
        self.bot: RACBot = bot
        self.get_body = bot.functions.get_body
        self.request = bot.functions.endpoint_request
        self.variables = bot.variables

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{BLACK QUESTION MARK ORNAMENT}')

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.guild_only()
    async def roguessr(self, ctx: Context):
        """Parent command"""

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @roguessr.group(name='server')
    async def roguessr_server(self, ctx: Context):
        """Parent for RoGuessr server commands"""

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @roguessr_server.command(name='shutdown')
    @checks.is_a_mod()
    async def roguessr_server_shutdown(self, ctx: Context, server_id: str):
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
                        Endpoints.roguessr_server_shutdown, 
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

    @roguessr_server.command(name='info')
    @checks.is_a_mod()
    async def roguessr_server_info(self, ctx: Context, server_id: str):
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
                        Endpoints.roguessr_server_info, 
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

    @roguessr_server.command(name='announce')
    @checks.is_a_mod()
    async def roguessr_server_announce(self, ctx: Context, server_id: str, *, text: str):
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
                        Endpoints.roguessr_server_announce, 
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

    @roguessr_server.command(name='announce-all')
    @checks.is_a_mod()
    async def roguessr_server_announce_all(self, ctx: Context, *, text: str):
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
                        Endpoints.roguessr_server_announce_all, 
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

    @roguessr.group(name='game')
    async def roguessr_game(self, ctx: Context):
        """Parent for RoGuessr game commands"""

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @roguessr_game.command(name='maps')
    async def roguessr_game_maps(self, ctx: Context):
        """Get a list of all implemented maps in RoGuessr

        Args:
            ctx (Context): _description_
        """

        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(
                        Endpoints.roguessr_game_maps, 
                        'get',
                        headers=api_headers,
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
                    maps: list[str] = body['maps']
                    total: int = body['total']
                    joined = '\n'.join(maps)

                    await ctx.reply(f'```{joined}\n\n{total} maps total```')
                else:
                    raise GeneralException('Response mimetype was not application/json')
                
    @roguessr_game.command(name='change-map')
    @checks.is_a_mod()
    async def roguessr_game_change_map(self, ctx: Context, server_id: str, *, map_name: str):
        """Send an announcement to a server

        Args:
            ctx (Context): _description_
            server_id (str): The server to change the map
            map_name (str): The map to change to
        """

        json: dict[str, str] = {
            'id': server_id
        }
        params: dict[str, str] = {
            'mod': ctx.author.name,
            'map_name': map_name
        }
        
        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(
                        Endpoints.roguessr_game_change_map, 
                        'put',
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
                
                await ctx.reply(f'ok, changed the map to `{map_name}`')

    
async def setup(bot: RACBot):
    await bot.add_cog(RoGuessr(bot))