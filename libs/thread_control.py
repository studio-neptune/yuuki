#!/usr/bin/python3
# coding=UTF-8

import threading, multiprocessing

class Yuuki_Thread:
    def __init__(self):
        self.lock = threading.Lock()

    def add(self, Yuuki_Func, args=()):
        added_thread = threading.Thread(name=Yuuki_Func.__name__, target=Yuuki_Func, args=args)
        added_thread.start()

    def getThreadInfo(self):
        print(threading.active_count())
        print(threading.enumerate())
        print("{} add Threading\n".format(threading.current_thread()))

class Yuuki_Multiprocess:
    def add(self, Yuuki_Func, args=()):
        added_multiprocess = multiprocessing.Process(name=Yuuki_Func.__name__, target=Yuuki_Func, args=args)
        added_multiprocess.start()
