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
            "BlackList":[]
        }

        self.GroupType = {
            "ID":"",
            "SEGroup":None,
            "Ext_Admin":[]
        }

        self.SEGrouptype = {
            OpType.NOTIFIED_UPDATE_GROUP:False,
            OpType.NOTIFIED_INVITE_INTO_GROUP:False,
            OpType.NOTIFIED_ACCEPT_GROUP_INVITATION:False,
            OpType.KICKOUT_FROM_GROUP:False,
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
                if f.read() != "":
                    self.Data[Type] = json.loads(f.read())
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

    def file(self, Type, Mode):
        return open(self.LogPath + self.LogName.format(Type), Mode)

    def updateData(self, Type, Input, Data):
        with self.file(Type, "r") as f:
            Data_ = json.loads(f.read())
        if type(self.DataType[Type]) == list:
            if Input:
                Data_.append(Data)
            else:
                Data_.remove(Data)
        elif type(self.DataType[Type]) == dict:
            Data_[Type][Input] = Data
        with self.file(Type, "w") as f:
            f.write(json.dumps(Data_))
        self.Data[Type] = Data_

    def updateLog(self, Type, Data):
        with self.file(Type, "a") as f:
            f.write(self.LogType[Type] % Data)

    def getTime(self, format="%b %d %Y %H:%M:%S %Z"):
        Time = time.localtime(time.time())
        return time.strftime(format, Time)

    def getData(self, Type):
        return self.Data[Type]

    def getDataGroupID(self, DataGroup):
        return DataGroup["ID"]

    def getGroup(self, GroupID):
        Groups = self.getData("Group")
        if len(Groups) > 0:
            GroupIDs = [self.getDataGroupID(Group) for Group in Groups]
            if GroupID in GroupIDs:
                return Groups[GroupID]
            else:
                return None

    def getSEGroup(self, GroupID):
        Group = self.getGroup(GroupID)
        if Group:
            return Group["SEGroup"]
        else:
            return None
