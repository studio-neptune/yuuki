# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from yuuki_core.ttypes import Contact as Prototype


class User(Prototype):
    def __init__(self, **kwargs) -> None:
        super(User, self).__init__(kwargs)
