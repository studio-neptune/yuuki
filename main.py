# -*- coding: utf-8 -*-
"""
    Star Yuuki Bot - Yuuki
    ~~~~~~~~~~~
     This is a main program in SYB.
     It`s belong to Star Yuuki(pYthon) Bot Project of Star Neptune Bot

    Version: v6.5

    Copyright(c) 2019 Star Inc. All Rights Reserved.
    The software licensed under Mozilla Public License Version 2.0
"""

Admin = [""]
KickLimit = 10
CancelLimit = 10
Language = "en"
LINE_ACCESS_KEY = ""
GroupMebers_Demand = 100
helper_LINE_ACCESS_KEYs = []

########################Initializing##########################
from libs import *

Connection = Yuuki_Connection()

Connection.connectInfo = {
    'Host': '',
    'Command_Path': '',
    'LongPoll_path': ''
}

Connection.connectHeader = {
    'X-Line-Application': '',
    'X-Line-Access': LINE_ACCESS_KEY,
    'User-Agent': ''
}

Settings = Yuuki_Settings()

Settings.config["Seq"] = 0
Settings.config["Admin"] = Admin
Settings.config["SecurityService"] = True
Settings.config["Hour_KickLimit"] = KickLimit
Settings.config["Hour_CancelLimit"] = CancelLimit
Settings.config["Default_Language"] = Language
Settings.config["GroupMebers_Demand"] = GroupMebers_Demand
Settings.config["helper_LINE_ACCESS_KEYs"] = helper_LINE_ACCESS_KEYs


Console = Yuuki(Settings, Connection)
Console.cleanMyGroupInvitations()

###########################Start!#############################
print("Star Yuuki BOT - Start Successful!")

if __name__ == "__main__":
    Console.Main()