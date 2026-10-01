"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from __future__ import annotations

from pydantic import Field, field_validator
from yuuki_core.ttypes import Message as Prototype

from .base import ThriftModel


class Message(ThriftModel):
    """A LINE message, as received or to be sent."""

    from_: str | None = Field(default=None, alias="from_")
    to: str | None = None
    to_type: int | None = Field(default=None, alias="toType")
    id: str | None = None
    created_time: int | None = Field(default=None, alias="createdTime")
    text: str | None = None
    content_type: int | None = Field(default=None, alias="contentType")
    content_metadata: dict[str, str] = Field(
        default_factory=dict, alias="contentMetadata"
    )

    @field_validator("content_metadata", mode="before")
    @classmethod
    def _empty_metadata(cls, value: object) -> dict[str, str]:
        if value is None:
            return {}
        assert isinstance(value, dict)
        return {str(k): str(v) for k, v in value.items()}

    def to_prototype(self) -> Prototype:
        return Prototype(
            from_=self.from_,
            to=self.to,
            toType=self.to_type,
            id=self.id,
            createdTime=self.created_time,
            text=self.text,
            contentType=self.content_type,
            contentMetadata=self.content_metadata,
        )

    @classmethod
    def text_message(cls, to: str, text: str) -> Message:
        return cls(to=to, text=text)

    @classmethod
    def contact_message(cls, to: str, mid: str, display_name: str) -> Message:
        return cls(
            to=to,
            text="",
            contentType=2,  # ContentType.CONTACT
            contentMetadata={"mid": mid, "displayName": display_name},
        )
