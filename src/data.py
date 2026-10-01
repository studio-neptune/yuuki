"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field
from yuuki_core.ttypes import OpType

SECURITY_OP_TYPES = (
    OpType.NOTIFIED_UPDATE_GROUP,
    OpType.NOTIFIED_INVITE_INTO_GROUP,
    OpType.NOTIFIED_ACCEPT_GROUP_INVITATION,
    OpType.NOTIFIED_KICKOUT_FROM_GROUP,
)


class GroupSecurity(BaseModel):
    """Per-group security switches, keyed by operation type."""

    switches: dict[int, bool] = Field(
        default_factory=lambda: {op: False for op in SECURITY_OP_TYPES}
    )

    def allows(self, op_type: int) -> bool:
        return self.switches.get(op_type, False)

    def configure(self, codes: list[int]) -> None:
        mapping = dict(zip(sorted(SECURITY_OP_TYPES), (0, 1, 2, 3), strict=False))
        code_to_op = {code: op for op, code in mapping.items()}
        for code in codes:
            op = code_to_op.get(code)
            if op is not None:
                self.switches[op] = True


class GroupData(BaseModel):
    """Persisted state of one group."""

    security: GroupSecurity | None = None
    extend_admins: list[str] = Field(default_factory=list)
    group_tickets: dict[str, str] = Field(default_factory=dict)


class LimitInfo(BaseModel):
    """Hourly action budget per account."""

    kick: dict[str, int] = Field(default_factory=dict)
    cancel: dict[str, int] = Field(default_factory=dict)


class GlobalData(BaseModel):
    power: bool = True
    security_service: bool = False
    last_reset_limit_time: int | None = None
    group_joined: list[str] = Field(default_factory=list)


class Store(BaseModel):
    global_data: GlobalData = Field(default_factory=GlobalData)
    groups: dict[str, GroupData] = Field(default_factory=dict)
    limits: LimitInfo = Field(default_factory=LimitInfo)
    blacklist: list[str] = Field(default_factory=list)


class LogType:
    """HTML log entry templates, kept compatible with the WebAdmin."""

    join_group = "<li>%s: %s(%s) -> Inviter: %s</li>"
    kick_event = (
        "<li>%s: %s(%s) -(%s)> Kicker: %s | Kicked: %s | Status: %s</li>"
    )
    cancel_event = (
        "<li>%s: %s(%s) -(%s)> Inviter: %s | Canceled: %s</li>"
    )
    blacklist = "<li>%s: %s(%s)</li>"


LOG_HEADERS = {
    "JoinGroup": "JoinGroup",
    "KickEvent": "KickEvent",
    "CancelEvent": "CancelEvent",
    "BlackList": "BlackList",
}


class DataStore:
    """Typed JSON-backed persistence for bot state and HTML logs."""

    def __init__(self, data_path: str = "data", log_path: str = "logs") -> None:
        self.data_path = Path(data_path)
        self.log_path = Path(log_path)
        self.store = self._load()

    # --- persistence ---

    def _file(self) -> Path:
        return self.data_path / "store.json"

    def _load(self) -> Store:
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.log_path.mkdir(parents=True, exist_ok=True)
        for name, title in LOG_HEADERS.items():
            log = self.log_path / (f"{name}.html")
            if not log.exists():
                log.write_text(
                    f"<title>{title} - SYB</title><meta charset='utf-8' />",
                    encoding="utf-8",
                )
        file = self._file()
        if not file.exists():
            return Store()
        return Store.model_validate(json.loads(file.read_text(encoding="utf-8")))

    def save(self) -> None:
        payload = self.store.model_dump_json()
        tmp = self._file().with_suffix(".json.tmp")
        tmp.write_text(payload, encoding="utf-8")
        os.replace(tmp, self._file())

    # --- logs ---

    def append_log(self, log_type: str, values: tuple) -> None:
        template = getattr(LogType, log_type.lower().replace("group", "_group"))
        line = template % values
        with open(
            self.log_path / (f"{log_type}.html"), "a", encoding="utf-8"
        ) as handle:
            handle.write(line)

    @staticmethod
    def now() -> str:
        return datetime.now(UTC).strftime("%b %d %Y %H:%M:%S UTC")

    # --- groups ---

    def group_data(self, group_id: str) -> GroupData:
        if group_id not in self.store.groups:
            self.store.groups[group_id] = GroupData()
        return self.store.groups[group_id]

    # --- blacklist ---

    def in_blacklist(self, mid: str) -> bool:
        return mid in self.store.blacklist

    def add_blacklist(self, mid: str) -> bool:
        """Add a user to the blacklist; return False if already present."""
        if mid in self.store.blacklist:
            return False
        self.store.blacklist.append(mid)
        return True

    # --- limits ---

    def reset_limits(
        self, accounts: list[str], kick_limit: int, cancel_limit: int
    ) -> None:
        for account in accounts:
            self.store.limits.kick[account] = kick_limit
            self.store.limits.cancel[account] = cancel_limit

    def limit_of(self, kind: str, account: str) -> int:
        return getattr(self.store.limits, kind).get(account, 0)

    def limit_decrease(self, kind: str, account: str) -> None:
        getattr(self.store.limits, kind)[account] -= 1

    def limit_shuffled(self, kind: str, allowed: list[str]) -> dict[str, int]:
        """Accounts with remaining budget, ordered randomly among equals."""
        import random

        candidates = {
            account: budget
            for account, budget in getattr(self.store.limits, kind).items()
            if account in allowed
        }
        items = list(candidates.items())
        random.shuffle(items)
        return dict(sorted(items, key=lambda kv: kv[1]))
