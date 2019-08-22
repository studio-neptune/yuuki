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



class YuukiConnect:
    def __init__(self, Yuuki_Connection):

        self.host = Yuuki_Connection.connectInfo["Host"]
        self.com_path = Yuuki_Connection.connectInfo["Command_Path"]
        self.poll_path = Yuuki_Connection.connectInfo["LongPoll_path"]

        self.con_header = Yuuki_Connection.connectHeader

    def connect(self):
        transport = THttpClient.THttpClient(self.host + self.com_path)
        transport_in = THttpClient.THttpClient(self.host + self.poll_path)

        transport.setCustomHeaders(self.con_header)
        transport_in.setCustomHeaders(self.con_header)

        protocol = TCompactProtocol.TCompactProtocol(transport)
        protocol_in = TCompactProtocol.TCompactProtocol(transport_in)

        client = Client(protocol)
        listen = Client(protocol_in)

        transport.open()
        transport_in.open()

        return client, listen
