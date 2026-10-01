"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from __future__ import annotations

from pydantic import Field
from yuuki_core.ttypes import Contact as Prototype

from .base import ThriftModel


class User(ThriftModel):
    """A LINE contact / user."""

    mid: str | None = None
    display_name: str | None = Field(default=None, alias="displayName")
    picture_status: str | None = Field(default=None, alias="pictureStatus")
    status_message: str | None = Field(default=None, alias="statusMessage")

    def to_prototype(self) -> Prototype:
        return Prototype(
            mid=self.mid,
            displayName=self.display_name,
            pictureStatus=self.picture_status,
            statusMessage=self.status_message,
        )
