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

    @commands.group(invoke_without_command=True)
    async def ping(self, ctx: Context):
        """Get the ping of the bot"""

        await ctx.reply(f'pong! {round(self.bot.latency, 3)} ms')

    @ping.command(name='api')
    async def ping_api(self, ctx: Context):
        """Ping the API"""

        start_time: float = time.time()
        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(
                        Endpoints.utility_ping, 
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
                    end_time: float = body['time']
                    total: float = end_time - start_time
                    await ctx.reply(f'took {total:.2f} seconds')
                else:
                    raise GeneralException('Response mimetype was not application/json')
                
    @commands.group(invoke_without_command=True)
    async def usage(self, ctx: Context):
        """Get the process usage of the bot"""

        await ctx.reply(f'not done yet')

    @usage.command(name='api')
    async def api_usage(self, ctx: Context):
        """Get the process usage of the API"""

        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(
                        Endpoints.utility_usage, 
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
                    main: dict = body['main']
                    storage: dict = body['storage']
                    cpu_usage: str = main['cpu']
                    rss_mem: str = main['rssMem']
                    vms_mem: str = main['vmsMem']

                    await ctx.reply(f'CPU: `{cpu_usage}`\nRSS MEMORY: `{rss_mem}`\nVMS MEMORY: `{vms_mem}`')
                else:
                    raise GeneralException('Response mimetype was not application/json')

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