# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from thrift.protocol import TCompactProtocol
from thrift.transport import THttpClient

from yuuki_core.TalkService import Client

#           NC HighSpeed Library
try:
    from thrift.protocol import fastbinary
except ImportError:
    print("[No fast_binary using]")


class Yuuki_Connect:
    def __init__(self, Yuuki_Configs):

        self.host = Yuuki_Configs.connectInfo["Host"]
        self.com_path = Yuuki_Configs.connectInfo["Command_Path"]
        self.poll_path = Yuuki_Configs.connectInfo["LongPoll_path"]

        self.con_header = Yuuki_Configs.connectHeader

        self.helper = []
        self.helper_ids = []
        self.helper_authTokens = {}

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

    def helperConnect(self, LINE_ACCESS_KEY):
        helper_ConnectHeader = self.con_header.copy()
        helper_ConnectHeader["X-Line-Access"] = LINE_ACCESS_KEY

        transport = THttpClient.THttpClient(self.host + self.com_path)
        transport.setCustomHeaders(helper_ConnectHeader)
        protocol = TCompactProtocol.TCompactProtocol(transport)
        client = Client(protocol)
        transport.open()

        # noinspection PyBroadException
        try:
            profile = client.getProfile()

            self.helper.append(client)
            self.helper_ids.append(profile.mid)
            self.helper_authTokens[profile.mid] = LINE_ACCESS_KEY

            return True
        except:
            print("Error:\n%s\nNot Acceptable\n" % (LINE_ACCESS_KEY,))

    def helperThreadConnect(self, userId):
        if userId in self.helper_authTokens:
            LINE_ACCESS_KEY = self.helper_authTokens.get(userId)
        else:
            return None

        helper_ConnectHeader = self.con_header.copy()
        helper_ConnectHeader["X-Line-Access"] = LINE_ACCESS_KEY

        transport = THttpClient.THttpClient(self.host + self.com_path)
        transport.setCustomHeaders(helper_ConnectHeader)
        protocol = TCompactProtocol.TCompactProtocol(transport)
        client = Client(protocol)
        transport.open()

        return client
