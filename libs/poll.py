# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import socket
import time

from yuuki_core.ttypes import Operation

from .tools import Yuuki_StaticTools, Yuuki_DynamicTools


class Yuuki_Poll:
    Power = True

    NoWork = 0
    NoWorkLimit = 5

    fetchNum = 50
    cacheOperations = []

    def __init__(self, Yuuki):
        self.Yuuki = Yuuki
        self.Yuuki_DynamicTools = Yuuki_DynamicTools(self.Yuuki)

    def _action(self):
        ncMessage = Operation()

        if time.localtime().tm_hour != self.Yuuki.data.getData(["Global", "LastResetLimitTime"]):
            self.Yuuki_DynamicTools.limitReset()
            self.Yuuki.data.updateData(["Global", "LastResetLimitTime"], time.localtime().tm_hour)

        if self.NoWork >= self.NoWorkLimit:
            self.NoWork = 0
            for ncMessage in self.cacheOperations:
                if ncMessage.reqSeq != -1 and ncMessage.revision > self.Yuuki.revision:
                    self.Yuuki.revision = ncMessage.revision
                    break
            if ncMessage.revision != self.Yuuki.revision:
                self.Yuuki.revision = self.Yuuki.client.getLastOpRevision()

        try:
            self.cacheOperations = self.Yuuki.listen.fetchOperations(self.Yuuki.revision, self.fetchNum)
        except socket.timeout:
            self.NoWork += 1

        if self.cacheOperations:
            self.NoWork = 0
            self.Yuuki.threadExec(self.Yuuki.taskDemux, (self.cacheOperations,))
            if len(self.cacheOperations) > 1:
                self.Yuuki.revision = max(self.cacheOperations[-1].revision, self.cacheOperations[-2].revision)

    def _exception(self):
        (err1, err2, err3, ErrorInfo) = Yuuki_StaticTools.errorReport()

        ncMessage = Operation()

        # noinspection PyBroadException
        try:
            for ncMessage in self.cacheOperations:
                if ncMessage.reqSeq != -1 and ncMessage.revision > self.Yuuki.revision:
                    self.Yuuki.revision = ncMessage.revision
                    break
            if ncMessage.revision != self.Yuuki.revision:
                self.Yuuki.revision = self.Yuuki.client.getLastOpRevision()
            for Root in self.Yuuki.Admin:
                self.Yuuki_DynamicTools.sendText(
                    Root,
                    "Star Yuuki BOT - Something was wrong...\nError:\n%s\n%s\n%s\n\n%s" %
                    (err1, err2, err3, ErrorInfo)
                )
        except:
            print("Star Yuuki BOT - Damage!\nError:\n%s\n%s\n%s\n\n%s" % (err1, err2, err3, ErrorInfo))
            self.Yuuki.exit()

    def init(self):
        self.Yuuki.data.updateData(["Global", "Power"], self.Power)

        if "LastResetLimitTime" not in self.Yuuki.data.getData(["Global"]):
            self.Yuuki.data.updateData(["Global", "LastResetLimitTime"], None)

        while self.Power:
            # noinspection PyBroadException
            try:
                self._action()
                try:
                    self.Power = self.Yuuki.data.syncData()
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
