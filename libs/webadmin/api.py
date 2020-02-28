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
    def __init__(self, Yuuki, WebAdmin_Handle):
        self.Yuuki = Yuuki
        self.WebAdmin = WebAdmin_Handle
        self.YuukiData = self.Yuuki.data
        self.Yuuki_DataHandle = Yuuki_WebDataReader(self.YuukiData)
        self.events = {
            "": self.nothing,
            "get_logs": self.get_logs,
            "get_helpers": self.get_helpers,
            "get_groups_joined": self.get_groups_joined,
            "shutdown": self.shutdown,
        }

    def action(self, *, task="", data=None):
        return self.events[task](data)

    def get_groups_joined(self, data):
        if data:
            pass
        return self.YuukiData.getData(["Global", "GroupJoined"])

    def get_helpers(self, data):
        if data:
            pass
        return self.Yuuki.Connect.helper_ids

    def get_logs(self, data):
        return self.Yuuki_DataHandle.get_logs(data)

    def shutdown(self, data):
        if data:
            pass
        return self.Yuuki.exit()

    def command_shutdown(self):
        self.WebAdmin.wa_shutdown()

    @staticmethod
    def nothing(data):
        if data:
            pass
