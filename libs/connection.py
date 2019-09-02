#!/usr/bin/python3
# coding=UTF-8

from .core.TalkService import Client

from thrift.transport import THttpClient
from thrift.protocol import TCompactProtocol

"""         NC HightSpeed Lib          """
try:
    from thrift.protocol import fastbinary
except:
    fastbinary = None
##########################################

class Yuuki_Connection:
    """ Connection Dict Type """

    connectInfo = {
        "Host": "",
        "Command_Path": "",
        "LongPoll_path": ""
    }

    connectHeader = {
        "X-Line-Application": "",
        "X-Line-Access": "",
        "User-Agent": ""
    }

class Yuuki_Connect:
    def __init__(self, Yuuki_Connection):

        self.host = Yuuki_Connection.connectInfo["Host"]
        self.com_path = Yuuki_Connection.connectInfo["Command_Path"]
        self.poll_path = Yuuki_Connection.connectInfo["LongPoll_path"]

        self.con_header = Yuuki_Connection.connectHeader

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
