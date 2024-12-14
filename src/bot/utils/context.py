from typing import Any, Union, Optional

import discord
from discord.ext import commands

import io


class ConfirmationView(discord.ui.View):
    def __init__(self, *, timeout: float, author_id: int, delete_after: bool) -> None:
        super().__init__(timeout=timeout)
        self.value: Optional[bool] = None
        self.delete_after: bool = delete_after
        self.author_id: int = author_id
        self.message: Optional[discord.Message] = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user and interaction.user.id == self.author_id:
            return True
        else:
            await interaction.response.send_message('This interaction is not for you.', ephemeral=True)
            return False

    async def on_timeout(self) -> None:
        if self.delete_after and self.message:
            await self.message.delete()

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        await interaction.response.defer()
        if self.delete_after:
            await interaction.delete_original_response()

        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        await interaction.response.defer()
        if self.delete_after:
            await interaction.delete_original_response()

        self.stop()


class Context(commands.Context):
    channel: Union[discord.VoiceChannel, discord.TextChannel, discord.Thread, discord.DMChannel]
    prefix: str
    command: commands.Command[Any, ..., Any]
    # bot: 'NotSoCensored'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return '<Context>'
    
    @discord.utils.cached_property
    def replied_reference(self) -> Optional[discord.MessageReference]:
        ref = self.message.reference
        if ref and isinstance(ref.resolved, discord.Message):
            return ref.resolved.to_reference()
        return None

    @discord.utils.cached_property
    def replied_message(self) -> Optional[discord.Message]:
        ref = self.message.reference
        if ref and isinstance(ref.resolved, discord.Message):
            return ref.resolved
        return None
    
    async def show_help(self, command: Any = None) -> None:
        '''Shows the help command for the specified command if given.

        If no command is given, then it'll show help for the current
        command.
        '''
        cmd = self.bot.get_command('help')
        command = command or self.command.qualified_name
        await self.invoke(cmd, command=command) # type: ignore

    async def prompt(
        self,
        message: str,
        *,
        timeout: float = 60.0,
        delete_after: bool = True,
        author_id: Optional[int] = None,
        reply: Optional[bool] = True
    ) -> Optional[bool]:
        """An interactive reaction confirmation dialog.

        Parameters
        -----------
        message: str
            The message to show along with the prompt.
        timeout: float
            How long to wait before returning.
        delete_after: bool
            Whether to delete the confirmation message after we're done.
        author_id: Optional[int]
            The member who should respond to the prompt. Defaults to the author of the
            Context's message.

        Returns
        --------
        Optional[bool]
            ``True`` if explicit confirm,
            ``False`` if explicit deny,
            ``None`` if deny due to timeout
        """

        author_id = author_id or self.author.id
        view = ConfirmationView(
            timeout=timeout,
            delete_after=delete_after,
            author_id=author_id,
        )
        if reply:
            view.message = await self.reply(message, view=view, ephemeral=delete_after)
        else:
            view.message = await self.send(message, view=view, ephemeral=delete_after)
        await view.wait()
        return view.value

    async def show_command_signature(self, reply: bool = True):
        if reply:
            await self.reply(f'```{self.prefix}{self.command.qualified_name} {self.command.signature}```')
        else:
            await self.send(f'```{self.prefix}{self.command.qualified_name} {self.command.signature}```')

    async def handle_error(self, code: int, error: Any):
        embed = discord.Embed(color=discord.Colour.red())
        embed.title = 'Command Error'
        embed.description = f'HTTP Exception: {code} ({error})'
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        await self.reply(embed=embed)

    async def handle_error_body(self, code: int, body: Any, detail: Optional[str] = None):
        embed = discord.Embed(color=discord.Colour.red())
        embed.title = 'Command Error'
        embed.description = f'HTTP Exception: {code} ({detail if detail else "No Status Detail"})'
        embed.add_field(name='Response Body', value=f'```js\n{body}```')
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        await self.reply(embed=embed)

    async def handle_error_no_http(self, error: Any):
        embed = discord.Embed(color=discord.Colour.red())
        embed.title = 'Command Error'
        embed.description = error
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        await self.reply(embed=embed)

    async def safe_reply(self, content: str, *, escape_mentions: bool = True, **kwargs) -> discord.Message:
        if escape_mentions:
            content = discord.utils.escape_mentions(content)

        if len(content) > 2000:
            fp = io.BytesIO(content.encode())
            kwargs.pop('file', None)
            return await self.reply(file=discord.File(fp, filename='message_too_long.txt'), **kwargs)
        else:
            return await self.reply(content)


class GuildContext(Context):
    author: discord.Member
    guild: discord.Guild
    channel: Union[discord.VoiceChannel, discord.TextChannel, discord.Thread]
    me: discord.Member
    prefix: str