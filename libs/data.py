# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import json
import os
import random
import time

from tornado.httpclient import HTTPClient, HTTPRequest
from yuuki_core.ttypes import OpType

from .data_mds import PythonMDS
from .thread_control import Yuuki_Multiprocess
from .thread_control import Yuuki_Thread


class Yuuki_Data:
    # Data Struct Define

    Data = {}

    DataType = {
        "Global": {
            "LastResetLimitTime": None,
        },
        "Group": {},
        "LimitInfo": {},
        "BlackList": []
    }

    GroupType = {
        "SEGroup": None,
        "Ext_Admin": [],
        "GroupTicket": {}
    }

    LimitType = {
        "KickLimit": {},
        "CancelLimit": {}
    }

    SEGrouptype = {
        OpType.NOTIFIED_UPDATE_GROUP: False,
        OpType.NOTIFIED_INVITE_INTO_GROUP: False,
        OpType.NOTIFIED_ACCEPT_GROUP_INVITATION: False,
        OpType.NOTIFIED_KICKOUT_FROM_GROUP: False
    }

    DataPath = "data/"
    DataName = "{}.json"

    # Log Struct Define

    LogType = {
        "JoinGroup": "<li>%s: %s(%s) -> Inviter: %s</li>",
        "KickEvent": "<li>%s: %s(%s) -(%s)> Kicker: %s | Kicked: %s | Status: %s</li>",
        "CancelEvent": "<li>%s: %s(%s) -(%s)> Inviter: %s | Canceled: %s</li>",
        "BlackList": "<li>%s: %s(%s)</li>"
    }

    LogPath = "logs/"
    LogName = "{}.html"

    initHeader = "<title>{} - SYB</title>" \
                 "<meta charset='utf-8' />"

    def __init__(self, threading):
        self.threading = threading
        self.ThreadControl = Yuuki_Thread()
        self.MdsThreadControl = Yuuki_Multiprocess()
        self._Data_Initialize()

    def _Data_Initialize(self):
        if not os.path.isdir(self.DataPath):
            os.mkdir(self.DataPath)

        for data_type in self.DataType:
            name = self.DataPath + self.DataName.format(data_type)

            test_result = 0
            if not os.path.isfile(name):
                with open(name, "w") as f:
                    f.write("")
            else:
                with open(name, "r") as f:
                    try:
                        json.load(f)
                    except ValueError:
                        test_result = 1
            assert test_result == 0, "{}\nJson Test Error".format(name)

            with open(name, "r+") as f:
                text = f.read()
                if text != "":
                    self.Data[data_type] = json.loads(text)
                else:
                    self.Data[data_type] = self.DataType[data_type]
                    f.write(json.dumps(self.Data[data_type]))

        return self._MDS_Initialize()

    def _MDS_Initialize(self):
        if self.threading:
            mds = PythonMDS()
            self.mdsHost = "http://localhost:2019/"
            self.mdsCode = "{}.{}".format(random.random(), time.time())
            self.MdsThreadControl.add(mds.mds_listen, (self.mdsCode,))

            # MDS Sync

            time.sleep(1)
            self.mdsShake("SYC", self.Data)
        return self._Log_Initialize()

    def _Log_Initialize(self):
        if not os.path.isdir(self.LogPath):
            os.mkdir(self.LogPath)

        for Type in self.LogType:
            name = self.LogPath + self.LogName.format(Type)
            if not os.path.isfile(name):
                with open(name, "w") as f:
                    f.write(self.initHeader.format(Type))

    def ThreadExec(self, Function, args):
        if self.threading:
            self.ThreadControl.lock.acquire()
            self.ThreadControl.add(Function, args)
            self.ThreadControl.lock.release()
        else:
            Function(*args)

    def mdsShake(self, do, path, data=None):
        status = 0
        if self.threading:
            http_client = HTTPClient()
            http_request = HTTPRequest(
                url=self.mdsHost,
                method="POST",
                body=json.dumps({
                    "code": self.mdsCode,
                    "do": do,
                    "path": path,
                    "data": data
                })
            )
            response = http_client.fetch(http_request)
            over = json.loads(response.body)
            if "status" in over:
                status = over["status"]
            assert_result = "mds - ERROR {}\n{} on {}".format(status, do, path)
            assert status == 200, assert_result
            return over
        else:
            status = {"status": status}
            return json.dumps(status)

    def _local_query(self, query_data):
        if type(query_data) is list:
            result = self.Data
            query_len = len(query_data) - 1
            for count, key in enumerate(query_data):
                if key in result:
                    if count < query_len:
                        if type(result.get(key)) is not dict:
                            result = 1
                            break
                    result = result.get(key)
                else:
                    result = 2
                    break

            return result
        return 0

    def _local_update(self, path, data):
        over = self._local_query(path)
        if not str(over).isnumeric():
            over.update(data)
        return False

    def file(self, Type, Mode, Format):
        if Format == "Data":
            return open(self.DataPath + self.DataName.format(Type), Mode)
        elif Format == "Log":
            return open(self.LogPath + self.LogName.format(Type), Mode)

    def syncData(self):
        if self.threading:
            self.Data = self.getData([])
        for Type in self.DataType:
            with self.file(Type, "w", "Data") as f:
                f.write(json.dumps(self.Data[Type]))
        return self.getData(["Global", "Power"])

    def updateData(self, path, data):
        if self.threading:
            self.ThreadExec(self._updateData, (path, data))
        else:
            self._updateData(path, data)

    def _updateData(self, path, data):
        assert path and type(path) is list, "Empty path - updateData"
        if len(path) == 1:
            origin_data = self.getData([])
            assert type(origin_data) is dict, "Error origin data type (1) - updateData"
            origin = origin_data.copy()
            origin[path[0]] = data
            path = []
        else:
            origin_data = self.getData(path[:-1])
            assert type(origin_data) is dict, "Error origin data type (2) - updateData"
            origin = origin_data.copy()
            origin[path[-1]] = data
            path = path[:-1]
        assert type(origin) is dict, "Error request data type - updateData"
        if self.threading:
            self.mdsShake("UPT", path, origin)
        else:
            self._local_update(path, origin)

    def updateLog(self, Type, Data):
        if self.threading:
            self.ThreadExec(self._updateLog, (Type, Data))
        else:
            self._updateLog(Type, Data)

    def _updateLog(self, Type, Data):
        with self.file(Type, "a", "Log") as f:
            f.write(self.LogType[Type] % Data)

    @staticmethod
    def getTime(time_format="%b %d %Y %H:%M:%S %Z"):
        Time = time.localtime(time.time())
        return time.strftime(time_format, Time)

    def getData(self, path):
        if self.threading:
            return self.mdsShake("GET", path).get("data")
        else:
            return self._local_query(path)

    def getGroup(self, GroupID):
        Groups = self.getData(["Group"])
        if GroupID not in Groups:
            self.updateData(["Group", GroupID], self.GroupType)
            return self.GroupType
        return Groups.get(GroupID)

    def getSEGroup(self, GroupID):
        GroupData = self.getGroup(GroupID)
        SEMode = GroupData.get("SEGroup")
        if SEMode is None:
            return None
        SEMode_ = {}
        for Mode in SEMode:
            Num_Mode = int(Mode)
            SEMode_[Num_Mode] = SEMode[Mode]
        return SEMode_

    def limitDecrease(self, limit_type, userId):
        if self.threading:
            self.mdsShake("YLD", limit_type, userId)
        else:
            self.Data["LimitInfo"][limit_type][userId] -= 1
