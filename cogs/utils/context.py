import asyncio

from discord.ext import commands

YES = "<:yes:809619191883235328>"
NO = "<:no:809619202398224415>"
NONE = "<:warning:809619232848478230>"

class Context(commands.Context):
    """Subclassing context so we can add custom attributes and methods."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def session(self):
        return self.bot.session

    async def prompt(self, message, *, timeout=60.0, delete_after=True, author_id=None):
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

        if not self.channel.permissions_for(self.me).add_reactions:
            raise RuntimeError("Bot does not have permission to add reactions.")

        fmt = f"{message}\n\nReact with {YES} to confirm or {NO} to deny."

        author_id = author_id or self.author.id
        msg = await self.send(fmt)

        confirm = None

        def check(payload):
            nonlocal confirm

            if payload.message_id != msg.id or payload.user_id != author_id:
                return False

            codepoint = str(payload.emoji)

            if codepoint == YES:
                confirm = True
                return True
            elif codepoint == NO:
                confirm = False
                return True

            return False

        for emoji in (YES, NO):
            await msg.add_reaction(emoji)

        try:
            await self.bot.wait_for("raw_reaction_add", check=check, timeout=timeout)
        except asyncio.TimeoutError:
            confirm = None

        try:
            if delete_after:
                await msg.delete()

        finally:
            return confirm

    def tick(self, opt, label=None):
        """Will return an emoji based on 1 of 3 options. True, False, None [Checkmark, Cross Mark, and Warning] Respectfully."""
        lookup = {
            True: YES,
            False: NO,
            None: NONE
        }
        emoji = lookup.get(opt, NO)
        if label is not None:
            return f"{emoji}: {label}"
        return emoji

    async def show_help(self, command=None):
        """Shows the help command for the specified command if given.
        If no command is given, then it'll show help for the current
        command.
        """
        cmd = self.bot.get_command('help')
        command = command or self.command.qualified_name
        await self.invoke(cmd, command=command)
