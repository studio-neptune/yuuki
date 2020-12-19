# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from __future__ import annotations

import socket
import time
from typing import TYPE_CHECKING

from yuuki_core.ttypes import Operation

from .tools import YuukiStaticTools, YuukiDynamicTools

if TYPE_CHECKING:
    from .yuuki import Yuuki


class YuukiPoll:
    Power = True

    NoWork = 0
    NoWorkLimit = 5

    fetchNum = 50
    cacheOperations = []

    def __init__(self, handler: Yuuki):
        self.Yuuki = handler
        self.YuukiDynamicTools = YuukiDynamicTools(handler)

    def _action(self):
        operation = Operation()

        if time.localtime().tm_hour != self.Yuuki.data.get_data(["Global", "LastResetLimitTime"]):
            self.YuukiDynamicTools.reset_limit()
            self.Yuuki.data.update_data(["Global", "LastResetLimitTime"], time.localtime().tm_hour)

        if self.NoWork >= self.NoWorkLimit:
            self.NoWork = 0
            for operation in self.cacheOperations:
                if operation.reqSeq != -1 and operation.revision > self.Yuuki.revision:
                    self.Yuuki.revision = operation.revision
                    break
            if operation.revision != self.Yuuki.revision:
                self.Yuuki.revision = self.Yuuki.client.getLastOpRevision()

        try:
            self.cacheOperations = self.Yuuki.listen.fetchOperations(self.Yuuki.revision, self.fetchNum)
        except socket.timeout:
            self.NoWork += 1

        if self.cacheOperations:
            self.NoWork = 0
            self.Yuuki.thread_append(self.Yuuki.task_executor, (self.cacheOperations,))
            if len(self.cacheOperations) > 1:
                self.Yuuki.revision = max(self.cacheOperations[-1].revision, self.cacheOperations[-2].revision)

    def _exception(self):
        (err1, err2, err3, error_info) = YuukiStaticTools.report_error()

        operation = Operation()

        # noinspection PyBroadException
        try:
            for operation in self.cacheOperations:
                if operation.reqSeq != -1 and operation.revision > self.Yuuki.revision:
                    self.Yuuki.revision = operation.revision
                    break
            if operation.revision != self.Yuuki.revision:
                self.Yuuki.revision = self.Yuuki.client.getLastOpRevision()
            for Root in self.Yuuki.Admin:
                self.YuukiDynamicTools.send_text(
                    Root,
                    "Star Yuuki BOT - Something was wrong...\nError:\n%s\n%s\n%s\n\n%s" %
                    (err1, err2, err3, error_info)
                )
        except:
            print("Star Yuuki BOT - Damage!\nError:\n%s\n%s\n%s\n\n%s" % (err1, err2, err3, error_info))
            self.Yuuki.exit()

    def init(self):
        self.Yuuki.data.update_data(["Global", "Power"], self.Power)

        if "LastResetLimitTime" not in self.Yuuki.data.get_data(["Global"]):
            self.Yuuki.data.update_data(["Global", "LastResetLimitTime"], None)

        while self.Power:
            # noinspection PyBroadException
            try:
                self._action()
                try:
                    self.Power = self.Yuuki.data.sync_data()
                except ConnectionRefusedError:
                    self.Power = False

            except SystemExit:
                self.Power = False

            except KeyboardInterrupt:
                self.Yuuki.exit()

            except EOFError:
                pass

            except:
                self._exception()
