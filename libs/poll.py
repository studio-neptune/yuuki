# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

import time
import socket
import requests

from .tools import Yuuki_StaticTools, Yuuki_DynamicTools

from yuuki_core.ttypes import Operation

class Yuuki_Poll:
    def __init__(self, Yuuki):
        self.Yuuki = Yuuki

        self.Yuuki_StaticTools = Yuuki_StaticTools()
        self.Yuuki_DynamicTools = Yuuki_DynamicTools(self.Yuuki)
        
        self.NoWork = 0
        self.NoWorkLimit = 5

        self.fetchNum = 50
        self.cacheOperations = []
        self.ncMessage = Operation()


    def init(self):
        self.Power = True
        self.Yuuki.data.updateData(["Global", "self.Power"], self.Power)

        if "LastResetLimitTime" not in self.Yuuki.data.getData(["Global"]):
            self.Yuuki.data.updateData(["Global", "LastResetLimitTime"], None)

        while self.Power:
            # noinspection PyBroadException
            try:
                if time.localtime().tm_hour != self.Yuuki.data.getData(["Global", "LastResetLimitTime"]):
                    self.Yuuki_DynamicTools.limitReset()
                    self.Yuuki.data.updateData(["Global", "LastResetLimitTime"], time.localtime().tm_hour)

                if self.NoWork >= self.NoWorkLimit:
                    self.NoWork = 0
                    for self.ncMessage in self.cacheOperations:
                        if self.ncMessage.reqSeq != -1 and self.ncMessage.revision > self.Yuuki.revision:
                            self.Yuuki.revision = self.ncMessage.revision
                            break
                    if self.ncMessage.revision != self.Yuuki.revision:
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

                self.Power = self.Yuuki.data.syncData()

            except requests.exceptions.ConnectionError:
                self.Power = False

            except SystemExit:
                self.Power = False

            except KeyboardInterrupt:
                self.Yuuki.exit()

            except EOFError:
                pass

            except:
                (err1, err2, err3, ErrorInfo) = self.Yuuki_StaticTools.errorReport()
                # noinspection PyBroadException
                try:
                    for self.ncMessage in self.cacheOperations:
                        if self.ncMessage.reqSeq != -1 and self.ncMessage.revision > self.Yuuki.revision:
                            self.Yuuki.revision = self.ncMessage.revision
                            break
                    if self.ncMessage.revision != self.Yuuki.revision:
                        self.Yuuki.revision = self.Yuuki.client.getLastOpRevision()
                    for Root in self.Yuuki.Admin:
                        self.Yuuki.sendText(Root, "Star Yuuki BOT - Something was wrong...\nError:\n%s\n%s\n%s\n\n%s" %
                                      (err1, err2, err3, ErrorInfo))
                except:
                    print("Star Yuuki BOT - Damage!\nError:\n%s\n%s\n%s\n\n%s" % (err1, err2, err3, ErrorInfo))
                    self.Yuuki.exit()
