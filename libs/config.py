# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import yaml


class Yuuki_Config:
    """ Configure Yuuki """

    connectInfo = {
        "Host": "",
        "Command_Path": "",
        "LongPoll_path": "",
    }

    connectHeader = {
        "X-Line-Application": "",
        "X-Line-Access": "",
        "User-Agent": ""
    }

    systemConfig = {
        "name": "Yuuki",
        "version": "v6.5.3-alpha",
        "version_check": True,
        "project_url": "https://tinyurl.com/syb-yuuki",
        "man_page": "https://tinyurl.com/yuuki-manual",
        "privacy_page": "OpenSource - Licensed under MPL 2.0",
        "copyright": "(c)2020 Star Inc.",

        "Seq": 0,
        "Admin": [],
        "SecurityService": False,
        "Hour_KickLimit": 10,
        "Hour_CancelLimit": 10,
        "Default_Language": "en",
        "GroupMebers_Demand": 100,
        "helper_LINE_ACCESS_KEYs": [],
    }

    def __init__(self, config_path="config.yaml"):
        with open(config_path, "r") as configfile:
            config = yaml.load(configfile, Loader=yaml.BaseLoader)

        if "Yuuki" in config:
            for key in config["Yuuki"]:
                if key in self.systemConfig:
                    self.systemConfig[key] = config["Yuuki"][key]

        if "Server" in config.get("LINE"):
            for key in config["LINE"]["Server"]:
                if key in self.systemConfig:
                    self.connectInfo[key] = config["LINE"]["Server"][key]

        if "Account" in config.get("LINE"):
            for key in config["LINE"]["Account"]:
                if key in ["X-Line-Application", "User-Agent"]:
                    config["LINE"]["Account"][key] = config["LINE"]["Account"][key].replace("\\t","\t")
                if key in self.systemConfig:
                    self.connectHeader[key] = config["LINE"]["Account"][key]

        if "helper_LINE_ACCESS_KEYs" in config.get("LINE"):
            self.systemConfig["helper_LINE_ACCESS_KEYs"] = config["LINE"]["helper_LINE_ACCESS_KEYs"]
