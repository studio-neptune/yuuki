# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import time

from yuuki_core.ttypes import ContentType

from ..tools import Yuuki_DynamicTools


class Yuuki_Callback:
    def __init__(self, Yuuki):
        """
            Event Type:
                SEND_MESSAGE(25)
        """
        self.Yuuki = Yuuki
        self.Yuuki_DynamicTools = Yuuki_DynamicTools(self.Yuuki)

    def _shutdown(self, ncMessage):
        self.Yuuki.Thread_Control.add(self._shutdown_reply, (ncMessage,))
        self.Yuuki.exit()

    def _shutdown_reply(self, ncMessage):
        time.sleep(1)
        self.Yuuki_DynamicTools.sendText(
            ncMessage.message.to,
            self.Yuuki.get_text("Exit.")
        )

    def _text(self, ncMessage):
        actions = {
            '[Yuuki] Remote Shutdown': self._shutdown,
        }
        if ncMessage.message.text in actions:
            actions[ncMessage.message.text](ncMessage)

    def action(self, ncMessage):
        if ncMessage.message.contentType == ContentType.NONE:
            self._text(ncMessage)
