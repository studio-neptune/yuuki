# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from thrift.protocol import TCompactProtocol
from thrift.transport import THttpClient
from yuuki_core.TalkService import Client, TalkException

if TYPE_CHECKING:
    from .config import YuukiConfig

#           NC HighSpeed Library
try:
    from thrift.protocol import fastbinary
except ImportError:
    print("[No fast_binary using]")


class YuukiConnect:
    def __init__(self, configs: YuukiConfig):

        self.helper = {}

        self.host = configs.connect_info["Host"]
        self.com_path = configs.connect_info["Command_Path"]
        self.poll_path = configs.connect_info["LongPoll_path"]

        self.con_header = configs.connect_header

    def connect(self, listen_timeout=600000):
        transport = THttpClient.THttpClient(self.host + self.com_path)
        transport_in = THttpClient.THttpClient(self.host + self.poll_path)

        transport_in.setTimeout(listen_timeout)

        transport.setCustomHeaders(self.con_header)
        transport_in.setCustomHeaders(self.con_header)

        protocol = TCompactProtocol.TCompactProtocol(transport)
        protocol_in = TCompactProtocol.TCompactProtocol(transport_in)

        client = Client(protocol)
        listen = Client(protocol_in)

        transport.open()
        transport_in.open()

        return client, listen

    def helper_connect(self, auth_token):
        helper_connect_header = self.con_header.copy()
        helper_connect_header["X-Line-Access"] = auth_token

        transport = THttpClient.THttpClient(self.host + self.com_path)
        transport.setCustomHeaders(helper_connect_header)
        protocol = TCompactProtocol.TCompactProtocol(transport)
        client = Client(protocol)
        transport.open()

        try:
            profile = client.getProfile()
            self.helper[profile.mid] = {
                "client": client,
                "profile": profile
            }
            return True

        except TalkException:
            print("Error:\n%s\nNot Acceptable\n" % (auth_token,))
