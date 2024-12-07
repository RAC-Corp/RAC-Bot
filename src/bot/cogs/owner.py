from typing import Union, Callable, Awaitable, Any, Optional

import discord
from discord.ext import commands, tasks

import time
import textwrap
import io
import traceback
from contextlib import redirect_stdout

from racbot import RACBot
from utils.context import Context, GuildContext


class Owner(commands.Cog):
    """Owner-only commands"""

    def __init__(self, bot: RACBot) -> None:
        self.bot: RACBot = bot
        self._last_result: str = ''

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{NO ENTRY}')

    def cleanup_code(self, content: str) -> str:
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        return content.strip('` \n')
    
    def get_syntax_error(self, e: SyntaxError) -> str:
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'
    
    @commands.command()
    @commands.is_owner()
    async def say(self, ctx: Context, *, text: str):
        """Make me say something"""

        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.send(text)
    
    @commands.command(name='eval')
    @commands.is_owner()
    async def _eval(self, ctx: Context, *, body: str):
        """Evaluates code"""

        env: dict[str, Any] = {
            'bot': self.bot,
            'session': self.bot.session,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result,
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile: str = f'async def func():\n{textwrap.indent(body, "  ")}'

        await ctx.typing()
        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.reply(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.reply(f'```py\n{value}{traceback.format_exc()}\n```'.replace('AiUncensored', 'CloudflareAI'))
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.reply(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.reply(f'```py\n{value}{ret}\n```')
        
    @commands.command()
    @commands.is_owner()
    async def load(self, ctx: Context, module: str):
        """Loads a cog"""

        cog: str = f'cogs.{module}'
        try:
            await self.bot.load_extension(cog)
        except Exception as e:
            await ctx.handle_error(code=400, error=str(e))
        else:
            await ctx.reply(f'Loaded `{cog}`')

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx: Context, module: str):
        """Unloads a cog"""

        cog: str = f'cogs.{module}'
        try:
            await self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.handle_error(code=400, error=str(e))
        else:
            await ctx.reply(f'Unloaded `{cog}`')

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: Context, module: str):
        """Reloads a cog"""
        
        cog: str = f'cogs.{module}'
        try:
            await self.bot.reload_extension(cog)
        except Exception as e:
            await ctx.handle_error(code=400, error=str(e))
        else:
            await ctx.reply(f'Reloaded `{cog}`')

    @commands.group(invoke_without_command=True, hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    async def sync(self, ctx: GuildContext, guild_id: Optional[int], copy: bool = False) -> None:
        """Syncs the slash commands with the given guild"""

        if guild_id:
            guild = discord.Object(id=guild_id)
        else:
            guild = ctx.guild

        await ctx.typing()
        if copy:
            try:
                self.bot.tree.copy_global_to(guild=guild)
            except Exception as e:
                await ctx.handle_error(code=400, error=str(e))

        try:
            commands = await self.bot.tree.sync(guild=guild)
        except discord.HTTPException as e:
            await ctx.handle_error(code=e.status, error=e.text)
        except Exception as e:
            await ctx.handle_error(code=400, error=str(e))
        else:
            await ctx.reply(f'Successfully synced {len(commands)} commands')

    @sync.command(name='global', hidden=True)
    @commands.is_owner()
    async def sync_global(self, ctx: Context):
        """Syncs the commands globally"""

        await ctx.typing()
        try:
            commands = await self.bot.tree.sync(guild=None)
        except discord.HTTPException as e:
            await ctx.handle_error(code=e.status, error=e.text)
        except Exception as e:
            await ctx.handle_error(code=400, error=str(e))
        else:
            await ctx.reply(f'Successfully synced {len(commands)} commands')

    @commands.command()
    @commands.is_owner()
    async def reloadsync(self, ctx: Context, *, module: str):
        """Reloads a cog and syncs the slash commands"""

        cog: str = f'cogs.{module}'
        try:
            await self.bot.reload_extension(cog)
        except Exception as e:
            await ctx.handle_error(400, str(e))
        else:
            msg = await ctx.reply(f'Reloaded `{cog}`')
            await ctx.typing()
            try:
                commands = await self.bot.tree.sync(guild=None)
            except discord.HTTPException as e:
                await ctx.handle_error(e.status, e.text)
            except Exception as e:
                await ctx.handle_error(400, str(e))
            else:
                await msg.reply(f'Successfully synced {len(commands)} commands')


async def setup(bot: RACBot):
    await bot.add_cog(Owner(bot))