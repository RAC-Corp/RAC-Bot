from typing import Union

import discord
from discord.ext import commands

from collections import defaultdict
import logging
import aiohttp
import asyncio
import datetime

from utils.config import Config
from utils.context import Context


extensions: tuple[str, ...] = (
    'cogs.meta',
    'cogs.owner',
    # 'cogs.roblox',
    'cogs.utility',
)


class RACBot(commands.Bot): # change later to AutoShardedBot
    user: discord.ClientUser
    bot_app_info: discord.AppInfo

    def __init__(self) -> None:
        allowed_mentions = discord.AllowedMentions(
            replied_user=False,
            everyone=False,
            roles=False,
        )
        intents = discord.Intents(
            members=True,
            messages=True,
            message_content=True,
            guilds=True
        )
        super().__init__(
            command_prefix=commands.when_mentioned_or('r.'),
            allowed_mentions=allowed_mentions,
            intents=intents,
            strip_after_prefix=True,
            case_insensitive=True,
            pm_help=None,
            help_attrs=dict(hidden=True),
            chunk_guilds_at_startup=False,
            heartbeat_timeout=150.0,
            enable_debug_events=True
        )

        self.resumes: defaultdict[int, list[datetime.datetime]] = defaultdict(list)
        self.identifies: defaultdict[int, list[datetime.datetime]] = defaultdict(list)

        self.activity: discord.Activity = discord.Activity(
            name='for r.', 
            type=discord.ActivityType.watching
        )
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.config = Config

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner
    
    def _clear_gateway_data(self) -> None:
        one_week_ago: datetime.datetime = discord.utils.utcnow() - datetime.timedelta(days=7)
        for shard_id, dates in self.identifies.items():
            to_remove: list = [index for index, dt in enumerate(dates) if dt < one_week_ago]
            for index in reversed(to_remove):
                del dates[index]

        for shard_id, dates in self.resumes.items():
            to_remove: list = [index for index, dt in enumerate(dates) if dt < one_week_ago]
            for index in reversed(to_remove):
                del dates[index]

    async def before_identify_hook(self, shard_id: int, *, initial: bool) -> None:
        self._clear_gateway_data()
        self.identifies[shard_id].append(discord.utils.utcnow())
        await super().before_identify_hook(shard_id, initial=initial)

    async def on_shard_resumed(self, shard_id: int) -> None:
        self.logger.info('Shard ID %s has resumed...', shard_id)
        self.resumes[shard_id].append(discord.utils.utcnow())

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = discord.utils.utcnow()

        self.logger.info('Ready: %s (ID: %s)', self.user, self.user.id)

    async def get_context(self, origin: Union[discord.Interaction, discord.Message], /, *, cls = Context) -> Context:
        return await super().get_context(origin, cls=cls)
    
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        await self.process_commands(message)

    async def setup_hook(self) -> None:
        timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(
            total=30,
            connect=5,
            sock_connect=5,
            sock_read=10
        )
        self.session: aiohttp.ClientSession = aiohttp.ClientSession(timeout=timeout)
        
        for extension in extensions:
            try:
                await self.load_extension(extension)
            except:
                self.logger.exception(f'failed to load extension {extension}')

    async def start(self) -> None:
        await super().start(self.config.token())

    async def close(self) -> None:
        await self.session.close()
        await super().close()

    async def on_command_error(self, ctx: Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandInvokeError):
            original = error.original
            if not isinstance(original, discord.HTTPException):
                self.logger.exception('In %s:', ctx.command.qualified_name, exc_info=original)
            if ctx.author.id == ctx.bot.owner_id:
                await ctx.handle_error_no_http(str(error))
            else:
                await ctx.handle_error(500, 'woops')
        elif isinstance(error, (commands.BadArgument, commands.MissingRequiredArgument, commands.ArgumentParsingError)):
            await ctx.show_command_signature()
        elif isinstance(error, commands.BotMissingPermissions):
            perms = error.missing_permissions
            command = ctx.command if ctx.command else 'This command'
            await ctx.reply(f'⚠ `{command}` requires the bot to have `{", ".join(perms)}` for it to work.')
        elif isinstance(error, commands.MissingPermissions):
            perms = error.missing_permissions
            command = ctx.command if ctx.command else 'This command'
            await ctx.reply(f'⚠ `{command}` requires you to have `{", ".join(perms)}` for it to work.')
        elif isinstance(error, commands.NSFWChannelRequired):
            command = ctx.command if ctx.command else 'This command'
            await ctx.reply(f'⚠ `{command}` requires the channel to be an NSFW channel for it to work.')
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f'You are on cooldown. Try again in {error.cooldown.per} seconds.')