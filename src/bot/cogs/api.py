from typing import Union, Any, Optional

import discord
from discord.ext import commands
from discord import app_commands

import aiohttp
import asyncio
import json as JSON
import time
import io

from racbot import RACBot
from utils.context import Context
from utils.enums import Endpoints, api_headers
from utils.exceptions import GeneralException, HTTPException


class API(commands.Cog):
    """Commands that interact with the API"""

    def __init__(self, bot: RACBot) -> None:
        self.bot: RACBot = bot
        self.get_body = bot.functions.get_body
        self.request = bot.functions.endpoint_request
        self.image_request = bot.functions.image_request
        self.variables = bot.variables

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{BLACK QUESTION MARK ORNAMENT}')

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
                
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def wordcloud(self, ctx: Context, max_messages: int = 500):
        """Generate a wordcloud in a channel

        Args:
            ctx (Context): _description_
            max_messages (int, optional): The max amount of messages to get. Defaults to 500.
        """

        if max_messages > 1000:
            raise HTTPException(422, 'Maximum messages parameter too large (1000)')
        if max_messages < 50:
            raise HTTPException(422, 'Maximum messages parameter too small (50)')
        
        channel_history: list[discord.Message] = []
        async with ctx.typing():
            async for message in ctx.channel.history(limit=max_messages):
                channel_history.append(message)
            
            text = ' '.join([message.content for message in channel_history])
            json: dict[str, Union[str, int]] = {
                'text': text,
                'max_words': max_messages
            }

            try:
                request = await asyncio.wait_for(
                    self.image_request(Endpoints.fun1_wordcloud, 'post', json=json, headers=api_headers),
                    timeout=30
                )
            except TimeoutError:
                raise HTTPException(504, 'Gateway Timeout')
            except Exception as e:
                raise commands.CommandInvokeError(e)
            else:
                status, reason, body = request
                if status not in self.variables['ok_status_codes']:
                    return await ctx.handle_error_body(status, body, reason)
                
                if type(body) == bytes:
                    image_file = io.BytesIO(body)
                    file = discord.File(image_file, filename='wordcloud.png')

                    embed = discord.Embed()
                    embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
                    embed.set_image(url='attachment://wordcloud.png')

                    await ctx.reply(file=file, embed=embed)
                else:
                    raise GeneralException('Response mimetype was not image/png')
                

async def setup(bot: RACBot):
    await bot.add_cog(API(bot))