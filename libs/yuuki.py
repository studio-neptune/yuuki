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

from git import Repo
from yuuki_core.ttypes import OpType

from .config import YuukiConfig
from .connection import YuukiConnect
from .data import YuukiData
from .events import YuukiCommand, YuukiJoinGroup, YuukiSecurity, YuukiCallback
from .i18n import Yuuki_LangSetting
from .poll import YuukiPoll
from .thread_control import YuukiMultiprocess
from .webadmin.server import YuukiWebAdmin


class Yuuki:
    def __init__(self, yuuki_config: YuukiConfig):

        self.Connect = YuukiConnect(yuuki_config)
        self.configs = yuuki_config.system_config

        # Static_Variable
        self.Thread_Control = YuukiMultiprocess()

        self.Seq = self.configs["Seq"]
        self.Admin = self.configs["Admin"]
        self.Threading = self.configs["Advanced"]
        self.KickLimit = self.configs["Hour_KickLimit"]
        self.CancelLimit = self.configs["Hour_CancelLimit"]
        self.i18n = Yuuki_LangSetting(self.configs["Default_Language"])

        self.LINE_Media_server = "https://obs.line-apps.com"

        self._version_check()

    def _version_check(self):
        git_result = "Unknown"
        origin_url = "https://github.com/star-inc/star_yuuki_bot.git"

        if self.configs["version_check"]:
            git_remote = Repo('.').remote()
            update_status = git_remote.fetch()[0]
            if update_status.flags == 64:
                git_result = "New version found."
            elif update_status.flags == 4:
                git_result = "This is the latest version."
            origin_url = "\n".join(git_remote.urls)

        return self._announce_dog(git_result, origin_url)

    def _announce_dog(self, git_result, origin_url):
        print(
            "\n{} {}\n"
            "\t===\n\n"
            "<*> {}\n\n"
            "Update Origin:\n"
            "\t{}\n\n\t\t\t\t\t"
            "{}\n\t{}\n".format(
                self.configs["name"],
                self.configs["version"],
                git_result,
                origin_url,
                self.configs["copyright"],
                "\t==" * 5
            )
        )
        self._login_line()

    def _login_line(self):
        (self.client, self.listen) = self.Connect.connect()

        if self.configs.get("helper_LINE_ACCESS_KEYs"):
            for access in self.configs["helper_LINE_ACCESS_KEYs"]:
                self.Connect.helper_connect(access)

        # Dynamic Variable
        self.get_text = self.i18n.gettext

        self.JoinGroup = YuukiJoinGroup(self).action
        self.Command = YuukiCommand(self).action
        self.Security = YuukiSecurity(self).action
        self.Callback = YuukiCallback(self).action

        mds_port = self.configs["MDS_Port"]
        self.data = YuukiData(self.Threading, mds_port)

        self.data.update_data(["Global", "GroupJoined"], self.client.getGroupIdsJoined())
        self.data.update_data(["Global", "SecurityService"], self.configs["SecurityService"])
        self._initialize()

    def _initialize(self):
        self.profile = self.client.getProfile()
        self.MyMID = self.profile.mid
        self.revision = self.client.getLastOpRevision()

        self.AllAccountIds = [self.MyMID]

        for user_id in self.Connect.helper:
            self.AllAccountIds.append(user_id)

        if len(self.data.get_data(["LimitInfo"])) != 2:
            self.data.update_data(["LimitInfo"], self.data.LimitType)
        self._setup_web_admin()

    def _setup_web_admin(self):
        if self.Threading and self.configs.get("WebAdmin"):
            wa_port = self.configs["WebAdmin_Port"]
            password = str(hash(random.random()))
            self.web_admin = YuukiWebAdmin(self, wa_port)
            self.web_admin.set_password(password)
            self.Thread_Control.add(self.web_admin.wa_listen)
            print(
                "<*> Yuuki WebAdmin - Enable\n"
                "<*> http://localhost:{}\n"
                "<*> Password: {}\n".format(wa_port, password)
            )
        else:
            print("<*> Yuuki WebAdmin - Disable\n")

    def exit(self, restart=False):
        print("System Exit")
        while self.data.sync_data():
            self.data.update_data(["Global", "Power"], False)
        if self.Threading:
            self.data.mds_shake("EXT", None, None)
            time.sleep(1)
            self.data.MdsThreadControl.stop("mds_listen")
            if self.configs.get("WebAdmin"):
                self.data.MdsThreadControl.stop("wa_listen")
        if restart:
            self.__restart()
        sys.exit(0)

    @staticmethod
    def __restart():
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

    def thread_append(self, function, args):
        if self.Threading:
            self.Thread_Control.add(function, args)
        else:
            function(*args)

    def task_executor(self, operations):
        for operation in operations:
            if operation.type == OpType.NOTIFIED_INVITE_INTO_GROUP:
                self.thread_append(self.JoinGroup, (operation,))
            elif operation.type == OpType.NOTIFIED_KICKOUT_FROM_GROUP:
                self.thread_append(self.Security, (operation,))
            elif operation.type == OpType.NOTIFIED_ACCEPT_GROUP_INVITATION:
                self.thread_append(self.Security, (operation,))
            elif operation.type == OpType.NOTIFIED_UPDATE_GROUP:
                self.thread_append(self.Security, (operation,))
            elif operation.type == OpType.RECEIVE_MESSAGE:
                self.thread_append(self.Command, (operation,))
            elif operation.type == OpType.SEND_MESSAGE:
                self.thread_append(self.Callback, (operation,))

    def main(self):
        handle = YuukiPoll(self)
        handle.init()
