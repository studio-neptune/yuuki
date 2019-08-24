#!/usr/bin/python3
# coding=UTF-8

import os, time, json
from .core.ttypes import OpType

class Yuuki_Data:
    def __init__(self):

        # Data

        self.Data = {}

        self.DataType = {
            "Global":{
                "SecurityService":False,
            },
            "Group": {},
            "LimitInfo":{},
            "BlackList":[]
        }

        self.GroupType = {
            "SEGroup":None,
            "Ext_Admin":[]
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
                        json.loads(f.read())
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
            "JoinGroup":"<li>%s: %s(%s) -> Inviter: %s</li>"
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
        if type(Object) == list:
            if Input:
                Object.append(Data)
            else:
                Object.remove(Data)
        elif type(Object) == dict:
            Object[Input] = Data
        self.syncData()

    def updateLog(self, Type, Data):
        with self.file(Type, "a", "Log") as f:
            f.write(self.LogType[Type] % Data)

    def getTime(self, format="%b %d %Y %H:%M:%S %Z"):
        Time = time.localtime(time.time())
        return time.strftime(format, Time)

    def getData(self, Type):
        return self.Data[Type]

    def getLimit(self, Type):
        LimitInfo = self.getData("LimitInfo")
        if len(LimitInfo) != 2:
            LimitInfo = self.LimitType
        if Type == "Kick":
            return LimitInfo["KickLimit"]
        elif Type == "Cancel":
            return LimitInfo["CancelLimit"]

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
        SEMode = self.getGroup(GroupID)["SEGroup"]
        for Mode in SEMode:
            if type(Mode == str):
                SEMode[int(Mode)] = SEMode[Mode]
        return SEMode
