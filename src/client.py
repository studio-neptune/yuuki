"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from __future__ import annotations

import asyncio
import logging
from typing import cast

from thrift.protocol import TCompactProtocol
from thrift.transport import THttpClient
from yuuki_core.TalkService import Client

from .config import LineSettings
from .model import Group, Message, Operation, User

logger = logging.getLogger(__name__)

DEFAULT_LISTEN_TIMEOUT = 600_000  # milliseconds


class LineClientError(Exception):
    """Raised when the LINE API transport fails."""


class AsyncLineClient:
    """Async wrapper over the synchronous thrift LINE client.

    The thrift client is blocking, so every call runs in a worker thread
    guarded by a per-transport lock, keeping the event loop responsive.
    """

    def __init__(
        self, settings: LineSettings, *, listen_timeout: int = DEFAULT_LISTEN_TIMEOUT
    ) -> None:
        self._settings = settings
        self._listen_timeout = listen_timeout
        self._client: Client | None = None
        self._listen_client: Client | None = None
        self._client_lock = asyncio.Lock()
        self._listen_lock = asyncio.Lock()
        self._transport = None
        self._listen_transport = None
        self._protocol = None
        self._listen_protocol = None

    @classmethod
    def for_helper(cls, settings: LineSettings, token: str) -> AsyncLineClient:
        return cls(settings.with_token(token))

    def _build_channel(self, path: str, timeout: int | None = None):
        """Build a (transport, protocol) pair for one endpoint."""
        url = self._settings.server.host + path
        transport = THttpClient.THttpClient(url)
        if timeout is not None:
            transport.setTimeout(timeout)
        transport.setCustomHeaders(self._settings.headers)
        protocol = TCompactProtocol.TCompactProtocol(transport)
        return transport, protocol

    async def connect(self) -> None:
        assert self._client is None, "Client already connected"
        loop = asyncio.get_running_loop()
        self._transport, self._protocol = self._build_channel(
            self._settings.server.command_path
        )
        self._listen_transport, self._listen_protocol = self._build_channel(
            self._settings.server.long_poll_path, self._listen_timeout
        )
        self._client = Client(self._protocol)
        self._listen_client = Client(self._listen_protocol)
        await loop.run_in_executor(None, self._transport.open)
        await loop.run_in_executor(None, self._listen_transport.open)

    async def close(self) -> None:
        loop = asyncio.get_running_loop()
        for transport in (self._transport, self._listen_transport):
            if transport is not None:
                await loop.run_in_executor(None, transport.close)
        self._client = None
        self._listen_client = None
        self._transport = None
        self._listen_transport = None
        self._protocol = None
        self._listen_protocol = None
        self._protocol = None
        self._listen_protocol = None

    async def _call(
        self, name: str, *args: object, listen: bool = False
    ) -> object:
        client = self._listen_client if listen else self._client
        lock = self._listen_lock if listen else self._client_lock
        if client is None:
            raise LineClientError("Client is not connected")
        loop = asyncio.get_running_loop()
        async with lock:
            try:
                return await loop.run_in_executor(
                    None, lambda: getattr(client, name)(*args)
                )
            except Exception as exc:
                raise LineClientError(f"{name} failed: {exc!r}") from exc

    # --- operations ---

    async def fetch_operations(
        self, revision: int, count: int = 50
    ) -> list[Operation]:
        prototypes = cast(
            "list[object]",
            await self._call(
                "fetchOperations", revision, count, listen=True
            ),
        )
        return [Operation.from_prototype(p) for p in prototypes]

    async def get_last_op_revision(self) -> int:
        return cast("int", await self._call("getLastOpRevision"))

    # --- contacts ---

    async def get_profile(self) -> User:
        return User.from_prototype(await self._call("getProfile"))

    async def get_contact(self, mid: str) -> User:
        return User.from_prototype(await self._call("getContact", mid))

    async def get_contacts(self, mids: list[str]) -> list[User]:
        prototypes = cast(
            "list[object]", await self._call("getContacts", mids)
        )
        return [User.from_prototype(p) for p in prototypes]

    # --- groups ---

    async def get_group(self, group_id: str) -> Group:
        return Group.from_prototype(await self._call("getGroup", group_id))

    async def get_groups(self, group_ids: list[str]) -> list[Group]:
        prototypes = cast(
            "list[object]", await self._call("getGroups", group_ids)
        )
        return [Group.from_prototype(p) for p in prototypes]

    async def get_group_ids_joined(self) -> list[str]:
        return cast("list[str]", await self._call("getGroupIdsJoined"))

    async def update_group(self, group: Group, seq: int = 0) -> None:
        await self._call("updateGroup", seq, group.to_prototype())

    async def kickout_from_group(
        self, group_id: str, member_mids: list[str], seq: int = 0
    ) -> None:
        await self._call("kickoutFromGroup", seq, group_id, member_mids)

    async def invite_into_group(
        self, group_id: str, contact_mids: list[str], seq: int = 0
    ) -> None:
        await self._call("inviteIntoGroup", seq, group_id, contact_mids)

    async def cancel_group_invitation(
        self, group_id: str, invitee_mids: list[str], seq: int = 0
    ) -> None:
        await self._call("cancelGroupInvitation", seq, group_id, invitee_mids)

    async def accept_group_invitation(self, group_id: str, seq: int = 0) -> None:
        await self._call("acceptGroupInvitation", seq, group_id)

    async def accept_group_invitation_by_ticket(
        self, group_id: str, ticket_id: str, seq: int = 0
    ) -> None:
        await self._call("acceptGroupInvitationByTicket", seq, group_id, ticket_id)

    async def reject_group_invitation(self, group_id: str, seq: int = 0) -> None:
        await self._call("rejectGroupInvitation", seq, group_id)

    async def leave_group(self, group_id: str, seq: int = 0) -> None:
        await self._call("leaveGroup", seq, group_id)

    async def leave_room(self, room_id: str, seq: int = 0) -> None:
        await self._call("leaveRoom", seq, room_id)

    async def reissue_group_ticket(self, group_id: str, seq: int = 0) -> str:
        return cast(
            "str", await self._call("reissueGroupTicket", seq, group_id)
        )

    # --- messages ---

    async def send_message(self, message: Message, seq: int = 0) -> Message:
        sent = await self._call("sendMessage", seq, message.to_prototype())
        return Message.from_prototype(sent)

    async def send_text(self, to: str, text: str, seq: int = 0) -> Message:
        return await self.send_message(Message.text_message(to, text), seq)
