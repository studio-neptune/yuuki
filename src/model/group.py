"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from __future__ import annotations

from pydantic import Field
from yuuki_core.ttypes import Group as Prototype

from .base import ThriftModel
from .user import User


class Group(ThriftModel):
    """A LINE group."""

    id: str | None = None
    name: str | None = None
    picture_status: str | None = Field(default=None, alias="pictureStatus")
    prevent_join_by_ticket: bool | None = Field(
        default=None, alias="preventJoinByTicket"
    )
    members: list[User] = Field(default_factory=list)
    invitee: list[User] = Field(default_factory=list)
    creator: User | None = None
    notification_disabled: bool | None = Field(
        default=None, alias="notificationDisabled"
    )

    def to_prototype(self) -> Prototype:
        return Prototype(
            id=self.id,
            name=self.name,
            pictureStatus=self.picture_status,
            preventJoinByTicket=self.prevent_join_by_ticket,
            members=[member.to_prototype() for member in self.members],
            invitee=[contact.to_prototype() for contact in self.invitee],
            creator=self.creator.to_prototype() if self.creator else None,
            notificationDisabled=self.notification_disabled,
        )

    @property
    def member_mids(self) -> list[str]:
        return [member.mid for member in self.members if member.mid]

    @property
    def invitee_mids(self) -> list[str]:
        return [contact.mid for contact in self.invitee if contact.mid]

    @property
    def owner(self) -> User:
        """The group creator, or the oldest member as a fallback."""
        if self.creator is not None and self.creator.mid:
            return self.creator
        assert self.members, "Group has no members"
        return self.members[0]
