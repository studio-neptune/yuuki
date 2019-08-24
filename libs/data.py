#!/usr/bin/python3
# coding=UTF-8

import os, time

class Yuuki_Data:
    def __init__(self):
        self.LogType = {
            "JoinGroup":"<li>%s: %s(%s) -> Inviter: %s</li>"
        }

        self.LogPath = "logs/"
        self.LogName = "{}.html"

        self.initHeader = "<title>{} - SYB</title>" \
                          "<meta charset='utf-8' />"

        for Type in self.LogType:
            name = self.LogPath + self.LogName.format(Type)
            if os.path.isfile(name):
                with open(name, "w") as f:
                    f.write(self.initHeader.format(Type))

    def logFile(self, Type, Mode):
        return open(self.LogPath + self.LogName.format(Type), Mode)

    def updateLog(self, Type, Data):
        with self.logFile(Type, "a") as f:
            f.write(self.LogType[Type] % Data)

    def getTime(self, format="%b %d %Y %H:%M:%S %Z"):
        Time = time.localtime(time.time())
        return time.strftime(format, Time)
