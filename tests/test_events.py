"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from collections.abc import Iterator

import pytest
from yuuki_core.ttypes import ContentType, MIDType, OpType

from src.bot import Yuuki
from src.config import Config, LineAccountSettings, LineServerSettings, LineSettings
from src.data import DataStore
from src.events.registry import (
    CommandContext,
    Dispatcher,
    EventContext,
    EventRegistry,
)
from src.model import Message, Operation


class FakeBot(Yuuki):
    """A Yuuki without a LINE connection."""

    def __init__(self) -> None:  # noqa: D107 - test stub
        self.config = Config()
        self.config.line = LineSettings(
            server=LineServerSettings(),
            account=LineAccountSettings(),
        )
        self.data = DataStore(
            data_path="/tmp/yuuki-test-data", log_path="/tmp/yuuki-test-logs"
        )
        self.registry = EventRegistry()
        self.dispatcher = Dispatcher(self)
        self.sent: list[tuple[str, str]] = []

    def greeting(self) -> str:
        return "HELLO"

    async def send_text(
        self, to: str, text: str, sender: str | None = None
    ) -> None:  # noqa: D102
        self.sent.append((to, text))

    async def reply_to(self, message: Message, text: str) -> None:  # noqa: D102
        self.sent.append((self.send_to(message), text))


@pytest.fixture
def bot() -> Iterator[FakeBot]:
    yield FakeBot()


def make_receive(
    text: str, to: str = "g1", from_: str = "u1", to_type: int = MIDType.GROUP
) -> Operation:
    message = Message(
        from_=from_,
        to=to,
        toType=to_type,
        text=text,
        contentType=ContentType.NONE,
        contentMetadata={},
    )
    return Operation(type=OpType.RECEIVE_MESSAGE, message=message)


async def test_command_registration_and_dispatch(bot: FakeBot) -> None:
    calls = []

    @bot.registry.command("Ping", help_text="ping")
    async def ping(ctx: CommandContext) -> None:
        calls.append(ctx.args)

    operation = make_receive("Yuuki/Ping a b")
    assert operation.message is not None
    await bot.dispatcher._dispatch_text_command(operation.message)
    assert calls == [["a", "b"]]


async def test_unknown_command_greets(bot: FakeBot) -> None:
    operation = make_receive("Yuuki/Nope")
    assert operation.message is not None
    await bot.dispatcher._dispatch_text_command(operation.message)
    assert bot.sent == [("g1", "HELLO")]


async def test_plain_name_greets(bot: FakeBot) -> None:
    operation = make_receive("Yuuki")
    assert operation.message is not None
    await bot.dispatcher._dispatch_text_command(operation.message)
    assert bot.sent == [("g1", "HELLO")]


async def test_non_command_ignored(bot: FakeBot) -> None:
    operation = make_receive("hello world")
    assert operation.message is not None
    await bot.dispatcher._dispatch_text_command(operation.message)
    assert bot.sent == []


async def test_blacklisted_message_ignored(bot: FakeBot) -> None:
    bot.data.add_blacklist("u1")
    called = []

    @bot.registry.command("Ping")
    async def ping(ctx: CommandContext) -> None:
        called.append(1)

    await bot.dispatcher.dispatch(make_receive("Yuuki/Ping"))
    assert called == []
    assert bot.sent == []


async def test_room_message_triggers_leave(bot: FakeBot) -> None:
    class FakeClient:
        async def leave_room(
            self, room_id: str, seq: int = 0
        ) -> None:
            bot.sent.append(("left", room_id))

    bot.client = FakeClient()  # type: ignore[assignment]
    operation = make_receive("hello", to="r1", to_type=MIDType.ROOM)
    await bot.dispatcher.dispatch(operation)
    assert ("left", "r1") in bot.sent


async def test_event_handler_dispatch(bot: FakeBot) -> None:
    seen = []

    @bot.registry.on(OpType.NOTIFIED_KICKOUT_FROM_GROUP)
    async def on_kick(ctx: EventContext) -> None:
        seen.append(ctx.operation.op_type)

    operation = Operation(type=OpType.NOTIFIED_KICKOUT_FROM_GROUP)
    await bot.dispatcher.dispatch(operation)
    assert seen == [OpType.NOTIFIED_KICKOUT_FROM_GROUP]


async def test_failing_handler_is_isolated(bot: FakeBot) -> None:
    seen = []

    @bot.registry.on(200)
    async def boom(ctx: EventContext) -> None:
        raise RuntimeError("boom")

    @bot.registry.on(200)
    async def ok(ctx: EventContext) -> None:
        seen.append(1)

    await bot.dispatcher.dispatch(Operation(type=200))
    assert seen == [1]
