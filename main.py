# -*- coding: utf-8 -*-
"""
    Star Yuuki Bot - Yuuki
    ~~~~~~~~~~~
     This is a main program in SYB.
     It`s belong to Star Yuuki(pYthon) Bot Project of Star Neptune Bot

    Version: v6.5.0

    Copyright(c) 2019 Star Inc. All Rights Reserved.
    The software licensed under Mozilla Public License Version 2.0
"""

Admin = [""]
Language = "en"
LINE_ACCESS_KEY = ""
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

Seq = 0
Console = Yuuki(Seq, Connection, helper_LINE_ACCESS_KEYs, Language, Admin)
Console.cleanMyGroupInvitations()

###########################Start!#############################
print("Star Yuuki BOT - Start Successful!")

if __name__ == "__main__":
    Console.Main()