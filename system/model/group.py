# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from yuuki_core.TalkService import Client
from yuuki_core.ttypes import Group as Prototype
from .user import User


class Group(Prototype):
    def __init__(self, **kwargs) -> None:
        super(Group, self).__init__(kwargs)

    def kick(self, member: User, client: Client, seq: int = 0) -> bool:
        return client.kickoutFromGroup(seq, self.id, [member.mid])
