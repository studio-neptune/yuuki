# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) Neptune Studio.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from yuuki_core.ttypes import Operation as Prototype


class Operation(Prototype):
    def __init__(self, **kwargs) -> None:
        super(Operation, self).__init__(kwargs)

    def from_prototype(self, prototype: Prototype) -> "Operation":
        super(Operation, self).__init__(**prototype.__dict__)
        return self
