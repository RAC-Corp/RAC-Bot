from typing import Any

import discord
from discord.ext import commands
from discord import app_commands

import unicodedata

from racbot import RACBot
from utils.context import Context
from utils.enums import Endpoints, api_headers


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
class AI(commands.GroupCog, group_name='ai'):
    """Robot chat commands"""

    def __init__(self, bot: RACBot) -> None:
        self.bot: RACBot = bot

    @commands.hybrid_command()
    async def gemini(self, ctx: Context, *, prompt: str):
        pass


async def setup(bot: RACBot):
    await bot.add_cog(AI(bot))