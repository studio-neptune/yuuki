# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import multiprocessing
import threading


class Yuuki_Thread:
    def __init__(self):
        self.lock = threading.Lock()

    @staticmethod
    def add(Yuuki_Func, args=()):
        added_thread = threading.Thread(name=Yuuki_Func.__name__, target=Yuuki_Func, args=args)
        added_thread.start()

    @staticmethod
    def getThreadInfo():
        print(threading.active_count())
        print(threading.enumerate())
        print("{} add Threading\n".format(threading.current_thread()))


class Yuuki_Multiprocess:
    @staticmethod
    def add(Yuuki_Func, args=()):
        added_multiprocess = multiprocessing.Process(name=Yuuki_Func.__name__, target=Yuuki_Func, args=args)
        added_multiprocess.start()
