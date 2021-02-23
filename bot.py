# Standard Library
import logging
from datetime import datetime

# 3rd Party
import aiohttp
import discord
from discord.ext import commands

# Custom
import config
from cogs.utils import Context

DESCRIPTION = "Hello! I am a bot written by BMan#7583, with a focus around Moderation, Utility, Statistics."

log = logging.getLogger(__name__)

initial_extensions = []

def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = [f"<@!{user_id}> ", f"<@{user_id}> "]
    if msg.guild is None:
        base.extend(["!", "?"])
    else:
        base.extend(["!", "?"]) # This will turn into a Database call.
    return base

class OmniiBot(commands.Bot):
    """Subclassing a bot object so we can add custom functionality."""
    def __init__(self):
        allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True)
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=_prefix_callable,
            description=DESCRIPTION,
            pm_help=None,
            help_attrs=dict(hidden=True),
            fetch_offline_members=False,
            heartbeat_timeout=150.0,
            allowed_mentions=allowed_mentions,
            intents=intents)

        self.client_id = config.client_id
        self.session = aiohttp.ClientSession(loop=self.loop)

    async def on_ready(self):
        """Fires whenever the bot has an `on_ready` event. This can be called repeatedly during a bots life cycle."""
        if not hasattr(self, "uptime"):
            self.uptime = datetime.datetime.utcnow()

        print(f"Ready: {self.user} | ID: {self.user.id}")

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context) #! THIS NEEDS TO BE IMPLEMENTED.

        if ctx.command is None:
            return

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def close(self):
        await super().close()
        await self.session.close()

    def run(self):
        try:
            super().run(config.token, reconnect=True)
        except Exception as e:
            print(type(e), e)

    @property
    def config(self):
        return __import__("config")
