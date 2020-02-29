# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import os
import platform
import random
import sys
import time

import requests
from git import Repo
from yuuki_core.ttypes import OpType

from .connection import Yuuki_Connect
from .data import Yuuki_Data
from .events import Yuuki_Command, Yuuki_JoinGroup, Yuuki_Security, Yuuki_Callback
from .i18n import Yuuki_LangSetting
from .poll import Yuuki_Poll
from .thread_control import Yuuki_Multiprocess
from .webadmin.server import Yuuki_WebAdmin


class Yuuki:
    def __init__(self, Yuuki_Settings):

        self.Connect = Yuuki_Connect(Yuuki_Settings)
        self.YuukiConfigs = Yuuki_Settings.systemConfig

        # Static_Variable
        self.Thread_Control = Yuuki_Multiprocess()

        self.Seq = self.YuukiConfigs["Seq"]
        self.Admin = self.YuukiConfigs["Admin"]
        self.Threading = self.YuukiConfigs["Advanced"]
        self.KickLimit = self.YuukiConfigs["Hour_KickLimit"]
        self.CancelLimit = self.YuukiConfigs["Hour_CancelLimit"]
        self.i18n = Yuuki_LangSetting(self.YuukiConfigs["Default_Language"])

        self.LINE_Media_server = "https://obs.line-apps.com"

        self._Version_Check()

    def _Version_Check(self):
        git_result = "Unknown"
        origin_url = "https://github.com/star-inc/star_yuuki_bot.git"

        if self.YuukiConfigs["version_check"]:
            # noinspection PyBroadException
            try:
                git_remote = Repo('.').remote()
                update_status = git_remote.fetch()[0]
                if update_status.flags == 64:
                    git_result = "New version found."
                elif update_status.flags == 4:
                    git_result = "This is the latest version."
            except:
                git_result = "Something was wrong."

        return self._Announce_Dog(git_result, origin_url)

    def _Announce_Dog(self, git_result, origin_url):
        print(
            "\n{} {}\n"
            "\t===\n\n"
            "<*> {}\n\n"
            "More Information:\n"
            "{}\n\n\t\t\t\t\t"
            "{}\n\t{}\n".format(
                self.YuukiConfigs["name"],
                self.YuukiConfigs["version"],
                git_result,
                origin_url,
                self.YuukiConfigs["copyright"],
                "\t==" * 5
            )
        )
        self._LINE_Login()

    def _LINE_Login(self):
        (self.client, self.listen) = self.Connect.connect()

        if self.YuukiConfigs.get("helper_LINE_ACCESS_KEYs"):
            for access in self.YuukiConfigs["helper_LINE_ACCESS_KEYs"]:
                self.Connect.helperConnect(access)

        # Dynamic Variable
        self.get_text = self.i18n.gettext

        self.JoinGroup = Yuuki_JoinGroup(self).action
        self.Command = Yuuki_Command(self).action
        self.Security = Yuuki_Security(self).action
        self.Callback = Yuuki_Callback(self).action

        self.data = Yuuki_Data(self.Threading)

        self.data.updateData(["Global", "GroupJoined"], self.client.getGroupIdsJoined())
        self.data.updateData(["Global", "SecurityService"], self.YuukiConfigs["SecurityService"])
        self._Initialize()

    def _Initialize(self):
        self.profile = self.client.getProfile()
        self.MyMID = self.profile.mid
        self.revision = self.client.getLastOpRevision()

        self.AllAccountIds = [self.MyMID] + self.Connect.helper_ids

        if len(self.data.getData(["LimitInfo"])) != 2:
            self.data.updateData(["LimitInfo"], self.data.LimitType)
        self._Setup_WebAdmin()

    def _Setup_WebAdmin(self):
        if self.Threading and self.YuukiConfigs.get("WebAdmin"):
            password = str(hash(random.random()))
            self.shutdown_password = str(hash(random.random()))
            self.web_admin = Yuuki_WebAdmin(self)
            self.web_admin.set_password(password)
            self.web_admin.set_shutdown_password(self.shutdown_password)
            self.Thread_Control.add(self.web_admin.wa_listen)
            print(
                "<*> Yuuki WebAdmin - Enable\n"
                "<*> http://localhost:2020\n"
                "<*> Password: {}\n".format(password)
            )
        else:
            print("<*> Yuuki WebAdmin - Disable\n")

    def exit(self, restart=False):
        print("System Exit")
        while self.data.syncData():
            self.data.updateData(["Global", "Power"], False)
        if self.Threading:
            self.data.mdsShake("EXT", None, None)
            time.sleep(1)
            self.data.MdsThreadControl.stop("mds_listen")
            if self.YuukiConfigs.get("WebAdmin"):
                requests.get(
                    "http://localhost:2020/api/shutdown/{}".format(self.shutdown_password)
                )
                time.sleep(1)
                self.data.MdsThreadControl.stop("wa_listen")
        if restart:
            if platform.system() == "Windows":
                with open("cache.bat", "w") as c:
                    c.write(sys.executable + " ./main.py")
                os.system("cache.bat")
                os.system("del cache.bat")
            elif platform.system() == "Linux":
                with open(".cache.sh", "w") as c:
                    c.write(sys.executable + " ./main.py")
                os.system("sh .cache.sh")
                os.system("rm .cache.sh")
            else:
                print("Star Yuuki BOT - Restart Error\n\nUnknown Platform")
        sys.exit(0)

    def threadExec(self, function, args):
        if self.Threading:
            self.Thread_Control.add(function, args)
        else:
            function(*args)

    def taskDemux(self, catched_news):
        for ncMessage in catched_news:
            if ncMessage.type == OpType.NOTIFIED_INVITE_INTO_GROUP:
                self.threadExec(self.JoinGroup, (ncMessage,))
            elif ncMessage.type == OpType.NOTIFIED_KICKOUT_FROM_GROUP:
                self.threadExec(self.Security, (ncMessage,))
            elif ncMessage.type == OpType.NOTIFIED_ACCEPT_GROUP_INVITATION:
                self.threadExec(self.Security, (ncMessage,))
            elif ncMessage.type == OpType.NOTIFIED_UPDATE_GROUP:
                self.threadExec(self.Security, (ncMessage,))
            elif ncMessage.type == OpType.RECEIVE_MESSAGE:
                self.threadExec(self.Command, (ncMessage,))
            elif ncMessage.type == OpType.SEND_MESSAGE:
                self.threadExec(self.Callback, (ncMessage,))

    def main(self):
        handle = Yuuki_Poll(self)
        handle.init()
