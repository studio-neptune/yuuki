#!/usr/bin/python3
# coding=UTF-8

import \
    os, \
    time,\
    json, \
    random,\
    requests
from .core.ttypes import OpType

from .data_mds import listen as msd_listen

from .thread_control import Yuuki_Thread
from .thread_control import Yuuki_Multiprocess

class Yuuki_Data:
    def __init__(self, threading):
        self.threading = threading
        self.ThreadControl = Yuuki_Thread()
        MdsThreadControl = Yuuki_Multiprocess()

        # Data
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

        # Python MDS

        if self.threading:
            self.mdsHost = "http://localhost:2019/"
            self.mdsCode = "{}.{}".format(random.random(), time.time())
            MdsThreadControl.add(msd_listen, (self.mdsCode,))

            # MDS Sync

            time.sleep(1)
            requests.post(
                url=self.mdsHost,
                json={
                    "code": self.mdsCode,
                    "do": "SYC",
                    "path": self.Data
                }
            )

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

    def _mdsShake(self, do, path, data=None):
        if self.threading:
            mds = requests.post(
                url=self.mdsHost,
                json={
                    "code": self.mdsCode,
                    "do": do,
                    "path": path,
                    "data": data
                }
            )
            over = mds.json()
            assert_result = "mds - ERROR\n{} on {}".format(do, path)
            assert over["status"] == 200, assert_result
            return over
        else:
            status = {"status" : 0}
            return json.dumps(status)

    def _local_query(self, query_data):
        if type(query_data) is list:
            result = self.Data
            query_len = len(query_data)
            source_data = self.Data
            for count, key in enumerate(query_data):
                if key in source_data:
                    if count < (query_len - 1):
                        if type(source_data.get(key)) is dict:
                            source_data = source_data.get(key)
                        else:
                            result = 1
                            break
                    else:
                        result = source_data.get(key)
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

    def syncData(self):
        if self.threading:
            self.Data = self.getData([])
        for Type in self.DataType:
            with self.file(Type, "w", "Data") as f:
                f.write(json.dumps(self.Data[Type]))
        return self.getData(["Global","Power"])

    def updateData(self, path, data):
        if self.threading:
            self.ThreadExec(self._updateData, (path, data))
        else:
            self._updateData(path, data)

    def _updateData(self, path, data):
        assert path and type(path) is list, "Empty path - updateData"
        if len(path) == 1:
            origin_data = self.getData([])
            assert type(origin_data) is dict, "Error origin data type (1) - updateData"
            origin = origin_data.copy()
            origin[path[0]] = data
            path = []
        else:
            origin_data = self.getData(path[:-1])
            assert type(origin_data) is dict, "Error origin data type (2) - updateData"
            origin = origin_data.copy()
            origin[path[-1]] = data
            path = path[:-1]
        assert type(origin) is dict, "Error request data type - updateData"
        if self.threading:
            self._mdsShake("UPT", path, origin)
        else:
            self._local_update(path, origin)

    def updateLog(self, Type, Data):
        if self.threading:
            self.ThreadExec(self._updateLog, (Type, Data))
        else:
            self._updateLog(Type, Data)

    def _updateLog(self, Type, Data):
        with self.file(Type, "a", "Log") as f:
            f.write(self.LogType[Type] % Data)

    @staticmethod
    def getTime(time_format="%b %d %Y %H:%M:%S %Z"):
        Time = time.localtime(time.time())
        return time.strftime(time_format, Time)

    def getData(self, path):
        if self.threading:
            return self._mdsShake("GET", path).get("data")
        else:
            return self._local_query(path)

    def getGroup(self, GroupID):
        Groups = self.getData(["Group"])
        if len(Groups) > 0:
            GroupIDs = [Group for Group in Groups]
            if GroupID not in GroupIDs:
                self.updateData(["Group", GroupID], self.GroupType)
        else:
            self.updateData(["Group", GroupID], self.GroupType)
        return self.getData(["Group", GroupID])

    def getSEGroup(self, GroupID):
        GroupData = self.getGroup(GroupID)
        SEMode = GroupData.get("SEGroup")
        if SEMode is None:
            return None
        SEMode_ = {}
        for Mode in SEMode:
            SEMode_[int(Mode)] = SEMode[Mode]
        return SEMode_

    def limitDecrease(self, limit_type, userId):
        if self.threading:
            self._mdsShake("YLD", limit_type, userId)
        else:
            self.Data["LimitInfo"][limit_type][userId] -= 1
