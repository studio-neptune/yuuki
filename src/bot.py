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

from yuuki_core.ttypes import MIDType

from .client import AsyncLineClient
from .config import Config
from .data import DataStore
from .events.registry import Dispatcher
from .events.registry import registry as event_registry
from .i18n import Language
from .model import Group, Message, User
from .webadmin import WebAdmin

logger = logging.getLogger(__name__)

KICK = 1
CANCEL = 2
LIMIT_KINDS = {KICK: "kick", CANCEL: "cancel"}
LIMIT_MESSAGES = {KICK: "limit.kick", CANCEL: "limit.cancel"}


class Yuuki:
    """The bot: wiring of clients, store, i18n and the event registry."""

    name = "Yuuki"
    version = "v8.0"
    media_server = "https://obs.line-apps.com"

    def __init__(self, config: Config) -> None:
        self.config = config
        self.data = DataStore()
        self.i18n = Language(config.yuuki.default_language)
        self.registry = event_registry
        self.dispatcher = Dispatcher(self)
        self.power = True
        self.web_admin: WebAdmin | None = None

        self.client = AsyncLineClient(config.line)
        self.helpers: dict[str, AsyncLineClient] = {}
        self.profile: User | None = None

    # --- lifecycle ---

    @property
    def my_mid(self) -> str:
        assert self.profile is not None, "Bot is not started"
        return str(self.profile.mid)

    @property
    def all_account_ids(self) -> list[str]:
        return [self.my_mid, *self.helpers.keys()]

    def get_text(
        self, key: str, lang: str | None = None, **kwargs: object
    ) -> str:
        return self.i18n.gettext(key, lang, **kwargs)

    def greeting(self) -> str:
        return self.get_text("greeting", name=self.name)

    async def start(self) -> None:
        from . import events  # noqa: F401  (registers built-in handlers)

        await self.client.connect()
        self.profile = await self.client.get_profile()
        for token in self.config.yuuki.helper_tokens:
            helper = AsyncLineClient.for_helper(self.config.line, token)
            await helper.connect()
            helper_profile = await helper.get_profile()
            self.helpers[str(helper_profile.mid)] = helper

        self.data.store.global_data.security_service = (
            self.config.yuuki.security_service
        )
        self.data.store.global_data.group_joined = (
            await self.client.get_group_ids_joined()
        )
        self._reset_limits()
        self.data.save()

        if self.config.yuuki.webadmin_enabled:
            self._start_webadmin()

    def _start_webadmin(self) -> None:
        import uvicorn

        from .webadmin import WebAdmin

        port = self.config.yuuki.webadmin_port
        web_admin = WebAdmin(self)
        self.web_admin = web_admin
        server = uvicorn.Server(
            uvicorn.Config(
                web_admin.app, host="0.0.0.0", port=port, log_level="warning"
            )
        )
        asyncio.create_task(server.serve())
        print(
            "<*> Yuuki WebAdmin - Enable\n"
            f"<*> http://localhost:{port}\n"
            f"<*> Password: {web_admin.password}"
        )

    def _reset_limits(self) -> None:
        self.data.reset_limits(
            self.all_account_ids,
            self.config.yuuki.hour_kick_limit,
            self.config.yuuki.hour_cancel_limit,
        )

    async def shutdown(self) -> None:
        self.data.store.global_data.power = False
        self.data.save()
        await self.client.close()
        for helper in self.helpers.values():
            await helper.close()

    # --- clients ---

    def client_for(self, account: str | None) -> AsyncLineClient:
        if account is None or account == self.my_mid:
            return self.client
        assert account in self.helpers, f"No such helper account: {account}"
        return self.helpers[account]

    # --- messaging ---

    def send_to(self, message: Message) -> str:
        if (
            message.to_type == MIDType.USER
            and message.from_ is not None
        ):
            return message.from_
        assert message.to is not None
        return message.to

    async def reply_to(self, message: Message, text: str) -> None:
        await self.send_text(self.send_to(message), text)

    async def send_text(
        self, to: str, text: str, sender: str | None = None
    ) -> None:
        client = self.client_for(sender)
        await client.send_text(to, text)

    async def send_user(self, to: str, mid: str) -> None:
        await self.client.send_message(
            Message.contact_message(to, mid, "LINE User")
        )

    # --- group tools ---

    async def group_privilege(self, group: Group) -> list[str]:
        group_data = self.data.group_data(str(group.id))
        return [
            *self.config.yuuki.admin,
            str(group.owner.mid),
            *group_data.extend_admins,
        ]

    async def change_group_url_status(
        self, group: Group, status: bool, handler: str | None = None
    ) -> None:
        updated = group.model_copy(
            update={"prevent_join_by_ticket": not status}
        )
        await self.client_for(handler).update_group(updated)

    async def get_group_ticket(
        self, group_id: str, account: str, renew: bool = False
    ) -> str:
        group_data = self.data.group_data(group_id)
        ticket = group_data.group_tickets.get(account, "")
        if not ticket or renew:
            ticket = await self.client_for(account).reissue_group_ticket(group_id)
            group_data.group_tickets[account] = ticket
            self.data.save()
        return ticket

    async def leave_group(self, group: Group) -> None:
        await self.send_text(str(group.id), self.get_text("common.bye"))
        await self.client.leave_group(str(group.id))
        for account in self.helpers:
            if account in group.member_mids:
                await self.helpers[account].leave_group(str(group.id))
        joined = self.data.store.global_data.group_joined
        if group.id in joined:
            joined.remove(str(group.id))
        self.data.save()

    async def modify_group_member_list(
        self,
        action: int,
        group: Group,
        target: str,
        except_account: str | None = None,
    ) -> str:
        """Kick (1) or cancel-invite (2) a user, budget permitting.

        Returns the account that handled the action, or "None".
        """
        assert action in LIMIT_KINDS, "Invalid action code"
        kind = LIMIT_KINDS[action]
        if self.helpers:
            members_in = [
                mid for mid in group.member_mids if mid in self.all_account_ids
            ]
            accounts = self.data.limit_shuffled(kind, members_in)
            if not accounts:
                return "None"
            if except_account is not None:
                accounts = {
                    account: budget
                    for account, budget in accounts.items()
                    if account != except_account
                }
                if not accounts:
                    return "None"
            handler = max(accounts, key=lambda a: accounts[a])
        else:
            if except_account == self.my_mid:
                return "None"
            handler = self.my_mid
        budget = self.data.limit_of(kind, handler)
        if budget > 0:
            client = self.client_for(handler)
            if action == KICK:
                await client.kickout_from_group(str(group.id), [target])
            else:
                await client.cancel_group_invitation(str(group.id), [target])
            self.data.limit_decrease(kind, handler)
        else:
            await self.send_text(
                str(group.id), self.get_text(LIMIT_MESSAGES[action]), handler
            )
        return handler
