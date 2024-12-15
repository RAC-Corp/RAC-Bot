from typing import Union, Pattern

import discord
from discord.ext import commands
from discord import app_commands

import re

from racbot import RACBot
from utils.context import Context


regional_pattern: Pattern = re.compile(
    "["u"\U0001F600-\U0001F64F"
    u"\U0001F300-\U0001F5FF"
    u"\U0001F680-\U0001F6FF" 
    u"\U0001F1E0-\U0001F1FF"
    u"\U00002500-\U00002BEF"
    u"\U00002702-\U000027B0"
    u"\U00002702-\U000027B0"
    u"\U000024C2-\U0001F251"
    u"\U0001f926-\U0001f937"
    u"\U00010000-\U0010ffff"
    u"\u2640-\u2642"
    u"\u2600-\u2B55"
    u"\u200d"
    u"\u23cf"
    u"\u23e9"
    u"\u231a"
    u"\ufe0f"
    u"\u3030"
    "]+", 
    flags=re.UNICODE
)


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
class Fun(commands.GroupCog, group_name='fun'):
    """Cool fun commands"""

    def __init__(self, bot: RACBot) -> None:
        self.bot: RACBot = bot

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{SMILING FACE WITH OPEN MOUTH}')

    @commands.hybrid_command()
    async def textwall(self, ctx: Context, *, text: str):
        """Create a wall of text

        Args:
            ctx (Context): _description_
            text (str): The text to use

        Usage:
            !!textwall load of text
        """

        content: str = ''
        for i in range(len(text)):
            content += f'\n{text[i:]} {text[:i]}'

        await ctx.safe_reply(content)

    @commands.hybrid_command(aliases=['regional'])
    async def regionalify(self, ctx: Context, *, text: str):
        """Replace letters and numbers with regional indicator blocks

        Args:
            ctx (Context): _description_
            text (str): The text to convert into regional indicator blocks

        Usage:
            !!regionalify hello world
        """

        replacements: dict[str, str] = {
            '!': '❗',
            '?': '❓',
            '#': '#️⃣',
            '1': '1️⃣',
            '2': '2️⃣',
            '3': '3️⃣',
            '4': '4️⃣',
            '5': '5️⃣',
            '6': '6️⃣',
            '7': '7️⃣',
            '8': '8️⃣',
            '9': '9️⃣',
            '0': '0️⃣',
        }

        def convert(c: str) -> str:
            if c.isalpha():
                return f':regional_indicator_{c.lower()}:'
            elif c in replacements:
                return replacements[c]
            elif regional_pattern.match(c):
                return c
            return ' '
        
        content: str = ''.join([convert(c) for c in text])
        await ctx.safe_reply(content)


async def setup(bot: RACBot) -> None:
    await bot.add_cog(Fun(bot))