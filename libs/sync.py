#!/usr/bin/python3
# coding=UTF-8

from simplegist.simplegist import Simplegist


class Yuuki_Sync_Config:
    """ Connection Dict Type """

    username = ""
    api_token = ""


class Yuuki_Sync:
    def __init__(self, Yuuki_Data, Yuuki_Sync_Config):

        self.file_names = []

        for name in Yuuki_Data.LogType:
            self.file_names.append(
                Yuuki_Data.LogPath + Yuuki_Data.LogName.format(name)
            )

        for name in Yuuki_Data.DataType:
            self.file_names.append(
                Yuuki_Data.DataPath + Yuuki_Data.DataName.format(name)
            )

        self.client = Simplegist(
            username=Yuuki_Sync_Config.username,
            api_token=Yuuki_Sync_Config.api_token
        )

    def initialize(self):
        pass

    def synchronize(self):
        pass

    def upload(self):
        pass

    def download(self):
        pass
