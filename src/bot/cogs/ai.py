from typing import Union

import discord
from discord.ext import commands
from discord import app_commands

import asyncio
import io

from racbot import RACBot
from utils.context import Context
from utils.enums import Endpoints, api_headers
from utils.exceptions import HTTPException, GeneralException


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
class AI(commands.GroupCog, group_name='ai'):
    """Robot chat commands"""

    def __init__(self, bot: RACBot) -> None:
        self.bot: RACBot = bot
        self.get_body = bot.functions.get_body
        self.request = bot.functions.endpoint_request
        self.image_request = bot.functions.image_request
        self.variables = bot.variables

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{ROBOT FACE}')

    @commands.hybrid_command()
    @commands.cooldown(1, 2.5, commands.BucketType.user)
    async def gemini(self, ctx: Context, *, prompt: str):
        """Chat with Google Gemini

        Args:
            ctx (Context): _description_
            prompt (str): The prompt to send to the AI

        Usage:
            !!gemini hello
            !!gemini 2+2
        """

        json: dict[str, Union[str, bool]] = {
            'prompt': prompt,
            'debug': False
        }
        
        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(Endpoints.ai_gemini_create, 'post', json=json, headers=api_headers),
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
                
                if type(body) == dict:
                    response: Union[str, None] = body.get('response')
                    if not response:
                        return await ctx.handle_error_no_http('API did not return a response')
                    
                    if len(response) > 2000:
                        message = await ctx.reply(response[:2000])
                        await message.reply(response[2000:])
                    else:
                        await ctx.reply(response)
                else:
                    raise GeneralException('Response mimetype was not application/json')

    @commands.hybrid_command()
    @commands.cooldown(1, 2.5, commands.BucketType.user)
    async def hermes(self, ctx: Context, *, prompt: str):
        """Chat with Hermes 2 AI model

        Args:
            ctx (Context): _description_
            prompt (str): The prompt to send to the AI

        Usage:
            !!hermes hello
            !!hermes 2+2
        """

        json: dict[str, str] = {
            'prompt': prompt
        }

        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.request(Endpoints.ai_cloudflare_text_create, 'post', json=json, headers=api_headers),
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
                
                if type(body) == dict:
                    response: str = body['result']['response']
                    await ctx.reply(response)
                else:
                    raise GeneralException('Response mimetype was not application/json')

    @commands.hybrid_command()
    @commands.cooldown(1, 2.5, commands.BucketType.user)
    async def imagine(self, ctx: Context, *, prompt: str):
        """Generate an image using Stable Diffusion

        Args:
            ctx (Context): _description_
            prompt (str): The prompt to turn into an image

        Usage:
            !!imagine ok sign
            !!imagine a beach
        """

        json: dict[str, Union[str, int]] = {
            'prompt': prompt,
            'steps': 16,
            'strength': 1,
            'height': 512,
            'width': 512
        }

        async with ctx.typing():
            try:
                request = await asyncio.wait_for(
                    self.image_request(Endpoints.ai_cloudflare_image_create, 'post', json=json, headers=api_headers),
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
                    file = discord.File(image_file, filename='imagine.png')
                    
                    embed = discord.Embed()
                    embed.description = f'Prompt: {prompt}'
                    embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
                    embed.set_image(url='attachment://imagine.png')

                    await ctx.reply(file=file, embed=embed)
                else:
                    raise GeneralException('Response mimetype was not image/png')


async def setup(bot: RACBot):
    await bot.add_cog(AI(bot))