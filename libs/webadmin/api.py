# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from .reader import Yuuki_WebDataReader

class Yuuki_WebAdminAPI:
    def __init__(self, YuukiData):
        self.YukkiData = YuukiData
        self.Yuuki_DataHandle = Yuuki_WebDataReader(YuukiData)
        self.events = {
            "": self.nothing,
            "get_logs": self.get_logs,
            "get_groups_joined": self.get_groups_joined,
        }

    def init(self, **action):
        action.setdefault('task', "")
        action.setdefault('data', None)
        return self.events[action["task"]](action["data"])

    def get_groups_joined(self, **data):
        data.setdefault('data', None)
        return self.YukkiData.getData(["Global", "GroupJoined"])

    def get_logs(self, **data):
        data.setdefault('name', None)
        if data.get("name"):
            return self.Yuuki_DataHandle.get_log(data["name"])
        return self.Yuuki_DataHandle.get_all_logs()

    @staticmethod
    def nothing(data):
        if data:
            pass
