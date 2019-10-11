#!/usr/bin/python3
# coding=UTF-8

import os, time, json
from .core.ttypes import OpType

from .thread_control import Yuuki_Thread
from .thread_control import Yuuki_Multiprocess

class Yuuki_Data:
    def __init__(self, threading):
        self.threading = threading
        self.ThreadControl = Yuuki_Thread()
        self.MpDataControl = Yuuki_Multiprocess()

        # Data
        if self.threading:
            self.Data = self.MpDataControl.dataManager.dict()
        else:
            self.Data = {}

        self.DataType = {
            "Global":{
                "LastResetLimitTime":None,
            },
            "Group": {},
            "LimitInfo":{},
            "BlackList":[]
        }

        self.GroupType = {
            "SEGroup":None,
            "Ext_Admin":[],
            "GroupTicket":{}
        }

        self.LimitType = {
            "KickLimit":{},
            "CancelLimit":{}
        }

        self.SEGrouptype = {
            OpType.NOTIFIED_UPDATE_GROUP:False,
            OpType.NOTIFIED_INVITE_INTO_GROUP:False,
            OpType.NOTIFIED_ACCEPT_GROUP_INVITATION:False,
            OpType.NOTIFIED_KICKOUT_FROM_GROUP:False
        }

        self.DataPath = "data/"
        self.DataName = "{}.json"

        if not os.path.isdir(self.DataPath):
            os.mkdir(self.DataPath)

        for Type in self.DataType:
            name = self.DataPath + self.DataName.format(Type)
            if not os.path.isfile(name):
                with open(name, "w") as f:
                    f.write("")
                Type = 0
            else:
                with open(name, "r") as f:
                    try:
                        json.load(f)
                        Type = 0
                    except ValueError:
                        Type = 1
            assert Type == 0, "{}\nJson Test Error".format(name)

        # Data Initialize

        for Type in self.DataType:
            name = self.DataPath + self.DataName.format(Type)
            with open(name, "r+") as f:
                text = f.read()
                if text != "":
                    self.Data[Type] = json.loads(text)
                else:
                    self.Data[Type] = self.DataType[Type]
                    f.write(json.dumps(self.Data[Type]))

        # Log

        self.LogType = {
            "JoinGroup":"<li>%s: %s(%s) -> Inviter: %s</li>",
            "KickEvent":"<li>%s: %s(%s) -(%s)> Kicker: %s | Kicked: %s | Status: %s</li>",
            "CancelEvent":"<li>%s: %s(%s) -(%s)> Inviter: %s | Canceled: %s</li>",
            "BlackList":"<li>%s: %s(%s)</li>"
        }

        self.LogPath = "logs/"
        self.LogName = "{}.html"

        self.initHeader = "<title>{} - SYB</title>" \
                          "<meta charset='utf-8' />"

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

    def file(self, Type, Mode, Format):
        if Format == "Data":
            return open(self.DataPath + self.DataName.format(Type), Mode)
        elif Format == "Log":
            return open(self.LogPath + self.LogName.format(Type), Mode)

    def syncData(self):
        for Type in self.DataType:
            with self.file(Type, "w", "Data") as f:
                f.write(json.dumps(self.Data[Type]))

    def updateData(self, Object, Input, Data):
        if self.threading:
            self.ThreadExec(self._updateData, (Object, Input, Data))
        else:
            self._updateData(Object, Input, Data)

    def _updateData(self, Object, Input, Data):
        if type(Object) == list:
            if Input:
                Object.append(Data)
            else:
                Object.remove(Data)
        elif type(Object) == dict:
            Object[Input] = Data

    def updateLog(self, Type, Data):
        if self.threading:
            self.ThreadExec(self._updateLog, (Type, Data))
        else:
            self._updateLog(Type, Data)

    def _updateLog(self, Type, Data):
        with self.file(Type, "a", "Log") as f:
            f.write(self.LogType[Type] % Data)

    def getTime(self, format="%b %d %Y %H:%M:%S %Z"):
        Time = time.localtime(time.time())
        return time.strftime(format, Time)

    def getData(self, Type):
        return self.Data[Type]

    def getLimit(self, Type):
        LimitInfo = self.getData("LimitInfo")
        if Type == "Kick":
            Limit = {}
            for Mode in LimitInfo["KickLimit"]:
                Limit[Mode] = int(LimitInfo["KickLimit"][Mode])
        elif Type == "Cancel":
            Limit = {}
            for Mode in LimitInfo["CancelLimit"]:
                Limit[Mode] = int(LimitInfo["CancelLimit"][Mode])
        else:
            Limit = None
        return Limit

    def getGroup(self, GroupID):
        Groups = self.getData("Group")
        if len(Groups) > 0:
            GroupIDs = [Group for Group in Groups]
            if GroupID not in GroupIDs:
                Groups[GroupID] = self.GroupType
        else:
            Groups[GroupID] = self.GroupType
        return Groups[GroupID]

    def getSEGroup(self, GroupID):
        SEMode = self.getGroup(GroupID).get("SEGroup")
        if SEMode == None:
            return None
        SEMode_ = {}
        for Mode in SEMode:
            SEMode_[int(Mode)] = SEMode[Mode]
        return SEMode_
