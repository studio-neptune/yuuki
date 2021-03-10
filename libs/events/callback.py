# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from __future__ import annotations

import time
from typing import TYPE_CHECKING

from yuuki_core.ttypes import ContentType

from ..tools import DynamicTools

if TYPE_CHECKING:
    from ..yuuki import Yuuki


class Callback:
    def __init__(self, handler: Yuuki):
        """
            Event Type:
                SEND_MESSAGE(25)
        """
        self.Yuuki = handler
        self.DynamicTools = DynamicTools(self.Yuuki)

    def _shutdown(self, operation):
        self.Yuuki.Thread_Control.add(self._shutdown_reply, (operation,))
        self.Yuuki.exit()

    def _shutdown_reply(self, operation):
        time.sleep(1)
        self.DynamicTools.send_text(
            operation.message.to,
            self.Yuuki.get_text("Exit.")
        )

    def _text(self, operation):
        actions = {
            '[Yuuki] Remote Shutdown': self._shutdown,
        }
        if operation.message.text in actions:
            function_ = actions[operation.message.text]
            if callable(function_):
                function_(operation)

    def action(self, operation):
        if operation.message.contentType == ContentType.NONE:
            self._text(operation)
