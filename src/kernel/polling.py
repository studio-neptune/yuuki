# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from yuuki_core.TalkService import Client
from ..model.operation import Operation


class Polling:
    count = 50
    revision = 0

    def set_count(self, count: int) -> "Polling":
        self.count = count
        return self

    def fetch(self, client: Client) -> Operation:
        operations = client.fetchOperations(self.revision, self.count)
        for operation in operations:
            yield Operation().from_prototype(operation)
