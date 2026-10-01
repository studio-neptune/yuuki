"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from yuuki_core.ttypes import OpType

from ..model import Message, Operation

if TYPE_CHECKING:
    from ..bot import Yuuki

logger = logging.getLogger(__name__)

EventHandler = Callable[["EventContext"], Awaitable[None]]
CommandHandler = Callable[["CommandContext"], Awaitable[None]]


@dataclass
class EventContext:
    """Everything a handler needs to process one operation."""

    bot: Yuuki
    operation: Operation

    @property
    def config(self):
        return self.bot.config

    @property
    def data(self):
        return self.bot.data

    @property
    def i18n(self):
        return self.bot.i18n

    def get_text(
        self, key: str, lang: str | None = None, **kwargs: object
    ) -> str:
        return self.bot.i18n.gettext(key, lang, **kwargs)

    async def reply(self, text: str) -> None:
        assert self.operation.message is not None
        await self.bot.reply_to(self.operation.message, text)


@dataclass
class CommandContext(EventContext):
    """Context of one user command message."""

    message: Message = field(default_factory=Message)
    args: list[str] = field(default_factory=list)

    @property
    def sender(self) -> str | None:
        return self.message.from_


class EventRegistry:
    """Central table of operation handlers and chat commands.

    Handlers are registered with decorators::

        @registry.on(OpType.NOTIFIED_KICKOUT_FROM_GROUP)
        async def handle(ctx: EventContext) -> None: ...

        @registry.command("help", help_text="Show help")
        async def help_cmd(ctx: CommandContext) -> None: ...
    """
    def __init__(self) -> None:
        self._handlers: dict[int, list[EventHandler]] = defaultdict(list)
        self._commands: dict[str, CommandHandler] = {}
        self._command_meta: dict[str, dict] = {}

    def on(self, op_type: int) -> Callable[[EventHandler], EventHandler]:
        def decorator(handler: EventHandler) -> EventHandler:
            self._handlers[op_type].append(handler)
            return handler

        return decorator

    def command(
        self,
        name: str,
        *,
        help_text: str = "",
        admin_only: bool = False,
    ) -> Callable[[CommandHandler], CommandHandler]:
        def decorator(handler: CommandHandler) -> CommandHandler:
            self._commands[name] = handler
            self._command_meta[name] = {
                "help": help_text,
                "admin_only": admin_only,
            }
            return handler

        return decorator

    def handlers_for(self, op_type: int) -> list[EventHandler]:
        return list(self._handlers.get(op_type, ()))

    def command_names(self) -> list[str]:
        return sorted(self._commands)

    def command_meta(self, name: str) -> dict:
        return self._command_meta.get(name, {})

    def get_command(self, name: str) -> CommandHandler | None:
        return self._commands.get(name)


# The process-wide registry; handler modules register on import.
registry = EventRegistry()


class Dispatcher:
    """Turns operations into handler tasks, isolating handler failures."""

    def __init__(self, bot: Yuuki) -> None:
        self.bot = bot
        self.registry: EventRegistry = bot.registry

    async def dispatch(self, operation: Operation) -> None:
        for handler in self.registry.handlers_for(operation.op_type):
            ctx = EventContext(bot=self.bot, operation=operation)
            try:
                await handler(ctx)
            except Exception:
                logger.exception(
                    "Event handler %s failed (op=%s)",
                    getattr(handler, "__name__", handler),
                    operation.op_type,
                )
        if operation.op_type == OpType.RECEIVE_MESSAGE:
            try:
                await self._dispatch_command(operation)
            except Exception:
                logger.exception("Message routing failed")

    async def _dispatch_command(self, operation: Operation) -> None:
        """Route one received message, mirroring the v6 pipeline.

        Guard blacklist and bot-check messages, auto-leave rooms,
        describe contacts, and parse "Yuuki/<Command>" text commands.
        """
        from yuuki_core.ttypes import ContentType, MIDType

        bot = self.bot
        message = operation.message
        if message is None:
            return
        blacklisted = bot.data.in_blacklist(str(message.to)) or (
            message.from_ is not None and bot.data.in_blacklist(message.from_)
        )
        if "BOT_CHECK" in message.content_metadata or blacklisted:
            return
        if message.to_type == MIDType.ROOM:
            assert message.to is not None
            await bot.client.leave_room(message.to)
            return
        if message.content_type == ContentType.CONTACT:
            await self._show_contact(message)
            return
        if message.content_type != ContentType.NONE:
            return
        await self._dispatch_text_command(message)

    async def _show_contact(self, message: Message) -> None:
        bot = self.bot
        mid = message.content_metadata.get("mid", "")
        contact = None
        if mid.startswith("u") and len(mid) == len(bot.my_mid):
            try:
                contact = await bot.client.get_contact(mid)
            except Exception:
                contact = None
        if contact is None:
            text = bot.get_text("common.not_found")
        elif bot.data.in_blacklist(str(contact.mid)):
            text = "{}\n{}".format(
                bot.get_text("blacklist.in_database"),
                contact.mid,
            )
        else:
            text = bot.get_text(
                "contact.info",
                name=contact.display_name,
                server=bot.media_server,
                picture=contact.picture_status,
                status=contact.status_message,
                mid=contact.mid,
            )
        await bot.reply_to(message, text)

    async def _dispatch_text_command(self, message: Message) -> None:
        if not message.text:
            return
        first = message.text.split(" ")[0]
        parts = first.split("/")
        if not parts or parts[0].lower() != self.bot.name.lower():
            return
        name = parts[1] if len(parts) > 1 else ""
        handler = self.registry.get_command(name) if name else None
        if handler is None:
            await self.bot.reply_to(message, self.bot.greeting())
            return
        rest = message.text.partition(" ")[2]
        ctx = CommandContext(
            bot=self.bot,
            operation=Operation(type=26, message=message),
            message=message,
            args=rest.split(),
        )
        try:
            await handler(ctx)
        except Exception:
            logger.exception("Command handler %s failed", name)
