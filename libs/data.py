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
from .thread_control import YuukiMultiprocess
from .thread_control import YuukiThread


class YuukiData:
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

    def __init__(self, threading, mds_port):
        self.threading = threading
        self.mds_port = mds_port
        self.ThreadControl = YuukiThread()
        self.MdsThreadControl = YuukiMultiprocess()
        self._data_initialize()

    def _data_initialize(self):
        if not os.path.isdir(self.DataPath):
            os.mkdir(self.DataPath)

        for data_type in self.DataType:
            name = self.DataPath + self.DataName.format(data_type)

            if not os.path.isfile(name):
                with open(name, "w") as f:
                    self.Data[data_type] = self.DataType[data_type]
                    json.dump(self.Data[data_type], f)
            else:
                with open(name, "r") as f:
                    try:
                        self.Data[data_type] = json.load(f)
                    except ValueError:
                        assert "{}\nJson Test Error".format(name)

        return self._mds_initialize()

    def _mds_initialize(self):
        if self.threading:
            mds = PythonMDS(self.mds_port)
            self.mdsHost = "http://localhost:{}/".format(self.mds_port)
            self.mdsCode = "{}.{}".format(random.random(), time.time())
            self.MdsThreadControl.add(mds.mds_listen, (self.mdsCode,))

            # MDS Sync

            time.sleep(1)
            self.mds_shake("SYC", self.Data)
        return self._log_initialize()

    def _log_initialize(self):
        if not os.path.isdir(self.LogPath):
            os.mkdir(self.LogPath)

        for Type in self.LogType:
            name = self.LogPath + self.LogName.format(Type)
            if not os.path.isfile(name):
                with open(name, "w") as f:
                    f.write(self.initHeader.format(Type))

    def thread_append(self, function_, args):
        if self.threading:
            self.ThreadControl.lock.acquire()
            self.ThreadControl.add(function_, args)
            self.ThreadControl.lock.release()
        else:
            function_(*args)

    def mds_shake(self, do, path, data=None):
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

    def sync_data(self):
        if self.threading:
            self.Data = self.get_data([])
        for Type in self.DataType:
            with self.file(Type, "w", "Data") as f:
                json.dump(self.Data[Type], f)
        return self.get_data(["Global", "Power"])

    def update_data(self, path, data):
        if self.threading:
            self.thread_append(self._update_data, (path, data))
        else:
            self._update_data(path, data)

    def _update_data(self, path, data):
        assert path and type(path) is list, "Empty path - update_data"
        if len(path) == 1:
            origin_data = self.get_data([])
            assert type(origin_data) is dict, "Error origin data type (1) - update_data"
            origin = origin_data.copy()
            origin[path[0]] = data
            path = []
        else:
            origin_data = self.get_data(path[:-1])
            assert type(origin_data) is dict, "Error origin data type (2) - update_data"
            origin = origin_data.copy()
            origin[path[-1]] = data
            path = path[:-1]
        assert type(origin) is dict, "Error request data type - update_data"
        if self.threading:
            self.mds_shake("UPT", path, origin)
        else:
            self._local_update(path, origin)

    def update_log(self, type_, data):
        if self.threading:
            self.thread_append(self._update_log, (type_, data))
        else:
            self._update_log(type_, data)

    def _update_log(self, type_, data):
        with self.file(type_, "a", "Log") as f:
            f.write(self.LogType[type_] % data)

    @staticmethod
    def get_time(time_format="%b %d %Y %H:%M:%S %Z"):
        time_ = time.localtime(time.time())
        return time.strftime(time_format, time_)

    def get_data(self, path):
        if self.threading:
            return self.mds_shake("GET", path).get("data")
        else:
            return self._local_query(path)

    def get_group(self, group_id):
        group_ids = self.get_data(["Group"])
        if group_id not in group_ids:
            self.update_data(["Group", group_ids], self.GroupType)
            return self.GroupType
        return group_ids.get(group_ids)

    def get_se_group(self, group_id):
        group = self.get_group(group_id)
        mode = group.get("SEGroup")
        if mode is None:
            return None
        mode_ = {}
        for mode__ in mode:
            mode_num = int(mode__)
            mode_[mode_num] = mode[mode__]
        return mode_

    def trigger_limit(self, limit_type, user_id):
        if self.threading:
            self.mds_shake("YLD", limit_type, user_id)
        else:
            self.Data["LimitInfo"][limit_type][user_id] -= 1
