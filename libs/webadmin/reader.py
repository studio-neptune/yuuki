# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2019 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from bs4 import BeautifulSoup


class Yuuki_WebDataReader:
    def __init__(self, Yuuki_Data):
        self.handle = Yuuki_Data

    def get_log(self, name):
        if name not in self.handle.LogType:
            return {"status": 404}
        with open(
                self.handle.LogPath
                +
                self.handle.LogName.format(name)
        ) as file:
            html_doc = file.read()
        parser = BeautifulSoup(html_doc, 'html.parser')
        events = parser.find_all('li')
        return {name: [result.string for result in events]}

    def get_all_logs(self):
        logs = {}

        for name in self.handle.LogType:
            with open(
                    self.handle.LogPath
                    +
                    self.handle.LogName.format(name)
            ) as file:
                html_doc = file.read()
            parser = BeautifulSoup(html_doc, 'html.parser')
            events = parser.find_all('li')
            logs[name] = [result.string for result in events]

        return logs
