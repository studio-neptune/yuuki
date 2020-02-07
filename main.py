#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Star Yuuki Bot - Yuuki
    ~~~~~~~~~~~
     This is a main program in SYB.
     It`s belong to Star Yuuki(pYthon) Bot Project of Star Neptune Bot

    Version: v6.5.3

    Copyright(c) 2020 Star Inc. All Rights Reserved.
    The software licensed under Mozilla Public License Version 2.0
"""

from libs import Yuuki, Yuuki_Config

########################Initializing##########################

config = Yuuki_Config()

Console = Yuuki(config,1)
Console.cleanMyGroupInvitations()

###########################Start!#############################

print("Star Yuuki BOT - Start Successful!")

if __name__ == "__main__":
    Console.Main()
