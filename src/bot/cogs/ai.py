from typing import Union

import discord
from discord.ext import commands
from discord import app_commands

import asyncio

from racbot import RACBot
from utils.context import Context
from utils.enums import Endpoints, api_headers


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
class AI(commands.GroupCog, group_name='ai'):
    """Robot chat commands"""

    def __init__(self, bot: RACBot) -> None:
        self.bot: RACBot = bot
        self.get_body = bot.functions.get_body
        self.request = bot.functions.endpoint_request
        self.variables = bot.variables

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{ROBOT FACE}')

    @commands.hybrid_command()
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
                    self.request(Endpoints.AI_GEMINI_CREATE, 'post', json=json, headers=api_headers),
                    timeout=30
                )
            except TimeoutError:
                await ctx.handle_error(504, 'Gateway Timeout')
            except Exception as e:
                self.bot.logger.exception(e)
                await ctx.handle_error_no_http('Something happened')
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
                    await ctx.handle_error_no_http('API returned a non-JSON response')


async def setup(bot: RACBot):
    await bot.add_cog(AI(bot))