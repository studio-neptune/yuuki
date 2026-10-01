"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from __future__ import annotations

from pydantic import Field

from .base import ThriftModel
from .message import Message


class Operation(ThriftModel):
    """A long-poll operation pushed by LINE.

    Security-relevant layout, consistent across group events:
    param1 = group id, param2 = the acting user, param3 = the target.
    """

    revision: int | None = None
    created_time: int | None = Field(default=None, alias="createdTime")
    type: int | None = None
    req_seq: int | None = Field(default=None, alias="reqSeq")
    checksum: str | None = None
    status: int | None = None
    param1: str | None = None
    param2: str | None = None
    param3: str | None = None
    message: Message | None = None

    @property
    def op_type(self) -> int:
        assert self.type is not None, "Operation has no type"
        return self.type

    @property
    def group_id(self) -> str | None:
        return self.param1

    @property
    def actor(self) -> str | None:
        """The user who performed the action."""
        return self.param2

    @property
    def target(self) -> str | None:
        """The user(s) the action was performed on ('\\x1e'-separated lists)."""
        return self.param3
