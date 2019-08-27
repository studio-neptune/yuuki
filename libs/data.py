#!/usr/bin/python3
# coding=UTF-8

import os, time, json
from .core.ttypes import OpType

class Yuuki_Data:
    def __init__(self):

        # Data

        self.Data = {}

        self.GlobalType = {
            "LastResetLimitTime": None
        }

        self.GroupType = {
            "SEGroup": None,
            "Ext_Admin": [],
            "GroupTicket": {}
        }

        self.LimitType = {
            "KickLimit": {},
            "CancelLimit": {}
        }

        self.SEGroupType = {
            OpType.NOTIFIED_UPDATE_GROUP: False,
            OpType.NOTIFIED_INVITE_INTO_GROUP: False,
            OpType.NOTIFIED_ACCEPT_GROUP_INVITATION: False,
            OpType.NOTIFIED_KICKOUT_FROM_GROUP: False
        }

        self.DataType = {
            "Global": self.GlobalType,
            "Group": {},
            "LimitInfo": {},
            "BlackList": []
        }

        self.customData = {
            "Group": self.GroupType,
            "LimitInfo": self.LimitType
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

    def getData(self, Type, Query=None):
        if Query == None:
            return self.Data[Type]
        else:
            lastkey = None
            QueryData = self.Data[Type]
            for key in Query:
                if type(QueryData) == dict:
                    Catch = QueryData.get(key)
                    if lastkey in self.customData:
                        if type(self.customData[lastkey]) == dict:
                            QueryData[key] = self.customData[lastkey]
                            return QueryData[key]
                    elif key in Query:
                        lastkey = key
                        QueryData = Catch
            return QueryData

    def getLimit(self, Type):
        if Type == "Kick":
            Limit = {}
            for userId in self.getData("LimitInfo", "KickLimit"):
                Limit[userId] = int(self.getData("LimitInfo", ["KickLimit", userId]))
        elif Type == "Cancel":
            Limit = {}
            for userId in self.getData("LimitInfo", "CancelLimit"):
                Limit[userId] = int(self.getData("LimitInfo", ["CancelLimit", userId]))
        else:
            Limit = None
        return Limit

    def getSEGroup(self, GroupID):
        Group = self.getData("Group", GroupID)
        SEMode = Group["SEGroup"]
        if SEMode == None:
            return None
        SEMode_ = {}
        for Mode in SEMode:
            SEMode_[int(Mode)] = SEMode[Mode]
        return SEMode_
