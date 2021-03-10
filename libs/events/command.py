# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING

from yuuki_core.ttypes import MIDType, ContentType, OpType

from ..tools import StaticTools, DynamicTools

if TYPE_CHECKING:
    from ..yuuki import Yuuki


class Command:
    def __init__(self, handler: Yuuki):
        """
            Event Type:
                RECEIVE_MESSAGE (26)
        """
        self.Yuuki = handler
        self.DynamicTools = DynamicTools(self.Yuuki)

    def _help(self, operation):
        self.DynamicTools.send_text(
            StaticTools.send_to_who(operation),
            self.Yuuki.get_text(
                "%s\n\t%s\n\nCommands Info:\n%s\n\nPrivacy:\n%s\n\nMore Information:\n%s\n\n%s") %
            (
                self.Yuuki.configs["name"],
                self.Yuuki.configs["version"],
                self.Yuuki.configs["man_page"],
                self.Yuuki.configs["privacy_page"],
                self.Yuuki.configs["project_url"],
                self.Yuuki.configs["copyright"],
            )
        )

    def _version(self, operation):
        self.DynamicTools.send_text(
            StaticTools.send_to_who(operation),
            self.Yuuki.configs["version"]
        )

    def _user_id(self, operation):
        self.DynamicTools.send_text(
            StaticTools.send_to_who(operation),
            self.Yuuki.get_text("LINE System UserID:\n") + operation.message.from_
        )

    def _get_all_helper(self, operation):
        if operation.message.toType == MIDType.GROUP:
            group = self.DynamicTools \
                .get_client(self.Yuuki.MyMID) \
                .getGroup(operation.message.to)
            group_privilege = [
                *self.Yuuki.Admin,
                StaticTools.get_group_creator(group).mid,
                *self.Yuuki.data.get_group(group.id)["Ext_Admin"]
            ]
            if operation.message.from_ in group_privilege:
                for user_id in self.Yuuki.Connect.helper:
                    self.DynamicTools \
                        .send_user(StaticTools.send_to_who(operation), user_id)

    def _speed(self, operation):
        timer_start = time.time()
        self.DynamicTools.send_text(
            StaticTools.send_to_who(operation),
            self.Yuuki.get_text("Testing...")
        )
        timer_end = time.time()
        self.DynamicTools.send_text(
            StaticTools.send_to_who(operation),
            self.Yuuki.get_text("Speed:\n %s com/s") % (timer_end - timer_start,)
        )

    def _security_mode(self, operation):
        message_separated = operation.message.text.split(" ")
        if operation.message.from_ in self.Yuuki.Admin:
            if len(message_separated) == 2:
                if message_separated[1].isdigit() and 1 >= int(message_separated[1]) >= 0:
                    self.Yuuki.data.update_data(
                        ["Global", "SecurityService"], bool(message_separated[1]))
                    self.DynamicTools.send_text(
                        StaticTools.send_to_who(operation),
                        self.Yuuki.get_text("Okay")
                    )
                else:
                    self.DynamicTools.send_text(
                        StaticTools.send_to_who(operation),
                        self.Yuuki.get_text("Enable(True): 1\nDisable(False): 0")
                    )
            else:
                self.DynamicTools.send_text(
                    StaticTools.send_to_who(operation),
                    str(bool(self.Yuuki.data.get_data(["Global", "SecurityService"])))
                )

    def _switch(self, operation):
        if operation.message.toType == MIDType.GROUP:
            group = self.DynamicTools \
                .get_client(self.Yuuki.MyMID) \
                .getGroup(operation.message.to)
            group_privilege = [
                *self.Yuuki.Admin,
                StaticTools.get_group_creator(group).mid,
                *self.Yuuki.data.get_group(group.id)["Ext_Admin"]
            ]
            if not self.Yuuki.data.get_data(["Global", "SecurityService"]):
                self.DynamicTools.send_text(
                    StaticTools.send_to_who(operation),
                    self.Yuuki.get_text("SecurityService of %s was disable") % (self.Yuuki.configs["name"],)
                )
            elif operation.message.from_ in group_privilege:
                self._switch_action(operation)

    def _switch_action(self, operation):
        message_separated = operation.message.text.split(" ")
        status = []
        unknown_msg = []
        unknown_msg_text = ""
        for count, code in enumerate(message_separated):
            if code.isdigit() and 3 >= int(code) >= 0:
                status.append(int(code))
            elif count != 0:
                unknown_msg.append(code.strip())
        self.DynamicTools.config_security_status(
            operation.message.to, status)
        if unknown_msg:
            unknown_msg_text = ", ".join(unknown_msg)
        if status:
            self.DynamicTools.send_text(StaticTools.send_to_who(
                operation), self.Yuuki.get_text("Okay"))
        else:
            self.DynamicTools.send_text(StaticTools.send_to_who(
                operation), self.Yuuki.get_text("Not Found"))
        if unknown_msg_text != "":
            self.DynamicTools.send_text(
                StaticTools.send_to_who(operation),
                self.Yuuki.get_text("Notice: Unknown command line argument(s)") + f"\n({unknown_msg_text})"
            )

    def _disable_all(self, operation):
        if operation.message.toType == MIDType.GROUP:
            group = self.DynamicTools \
                .get_client(self.Yuuki.MyMID) \
                .getGroup(operation.message.to)
            group_privilege = [
                *self.Yuuki.Admin,
                StaticTools.get_group_creator(group).mid,
                *self.Yuuki.data.get_group(group.id)["Ext_Admin"]
            ]
            if not self.Yuuki.data.get_data(["Global", "SecurityService"]):
                self.DynamicTools.send_text(
                    StaticTools.send_to_who(operation),
                    self.Yuuki.get_text("SecurityService of %s was disable") % (self.Yuuki.configs["name"],)
                )
            elif operation.message.from_ in group_privilege:
                self.DynamicTools.config_security_status(operation.message.to, [])
                self.DynamicTools.send_text(
                    StaticTools.send_to_who(operation),
                    self.Yuuki.get_text("Okay")
                )

    def _ext_admin(self, operation):
        message_separated = operation.message.text.split(" ")
        if operation.message.toType == MIDType.GROUP:
            group = self.DynamicTools \
                .get_client(self.Yuuki.MyMID) \
                .getGroup(operation.message.to)
            group_privilege = [
                *self.Yuuki.Admin,
                StaticTools.get_group_creator(group).mid
            ]
            if len(message_separated) == 3:
                if operation.message.from_ in group_privilege:
                    if message_separated[1] == "add":
                        self._ext_admin_add(operation, message_separated, group)
                    elif message_separated[1] == "delete":
                        self._ext_admin_delete(operation, message_separated, group)
            else:
                self._ext_admin_query(operation, group)

    def _ext_admin_add(self, operation, message_separated, group):
        if message_separated[2] in [Member.mid for Member in group.members]:
            if message_separated[2] in self.Yuuki.data.get_group(group.id)["Ext_Admin"]:
                self.DynamicTools.send_text(
                    StaticTools.send_to_who(operation),
                    self.Yuuki.get_text("Added")
                )
            elif message_separated[2] not in self.Yuuki.data.get_data(["BlackList"]):
                origin = self.Yuuki.data.get_data(["Group", group.id, "Ext_Admin"])
                ext_admin_list = origin.copy()
                ext_admin_list.append(message_separated[2])
                self.Yuuki.data.update_data(["Group", group.id, "Ext_Admin"], ext_admin_list)
                self.DynamicTools.send_text(
                    StaticTools.send_to_who(operation),
                    self.Yuuki.get_text("Okay")
                )
            else:
                self.DynamicTools.send_text(
                    StaticTools.send_to_who(operation),
                    self.Yuuki.get_text("The User(s) was in our blacklist database.")
                )
        else:
            self.DynamicTools.send_text(
                StaticTools.send_to_who(operation),
                self.Yuuki.get_text("Wrong UserID or the guy is not in Group")
            )

    def _ext_admin_delete(self, operation, message_separated, group):
        if message_separated[2] in self.Yuuki.data.get_group(group.id)["Ext_Admin"]:
            origin = self.Yuuki.data.get_data(["Group", group.id, "Ext_Admin"])
            ext_admin_list = origin.copy()
            ext_admin_list.remove(message_separated[2])
            self.Yuuki.data.update_data(
                ["Group", group.id, "Ext_Admin"],
                ext_admin_list
            )
            self.DynamicTools.send_text(
                StaticTools.send_to_who(operation),
                self.Yuuki.get_text("Okay")
            )
        else:
            self.DynamicTools.send_text(
                StaticTools.send_to_who(operation),
                self.Yuuki.get_text("Not Found")
            )

    def _ext_admin_query(self, operation, group):
        if self.Yuuki.data.get_group(group.id)["Ext_Admin"]:
            status = ""
            status_added = []
            for member in group.members:
                if member.mid in self.Yuuki.data.get_group(group.id)["Ext_Admin"]:
                    status += f"{member.displayName}\n"
                    status_added.append(member.mid)
            for user_id in self.Yuuki.data.get_group(group.id)["Ext_Admin"]:
                if user_id not in status_added:
                    status += "{}: {}\n".format(
                        self.Yuuki.get_text("Unknown"),
                        user_id
                    )
            self.DynamicTools.send_text(
                StaticTools.send_to_who(operation),
                status + self.Yuuki.get_text("\nExtend Administrator(s)")
            )
        else:
            self.DynamicTools.send_text(
                StaticTools.send_to_who(operation),
                self.Yuuki.get_text("Not Found")
            )

    def _status(self, operation):
        if operation.message.toType == MIDType.GROUP:
            group = self.DynamicTools \
                .get_client(self.Yuuki.MyMID) \
                .getGroup(operation.message.to)
            group_status = self.Yuuki.data.get_se_group(operation.message.to)
            if not self.Yuuki.data.get_data(["Global", "SecurityService"]):
                status = self.Yuuki.get_text("SecurityService of %s was disable") % (self.Yuuki.configs["name"],)
            elif group_status is None:
                status = self.Yuuki.get_text("Default without Initialize\nMain Admin of the Group:\n%s") % \
                         (StaticTools.get_group_creator(group).displayName,)
            else:
                status = self.Yuuki.get_text(
                    "SecurityService is Listening on\n"
                    "\nURL:%s\nInvite:%s\nJoin:%s\nMembers:%s\n"
                    "\nMain Admin of the Group:\n%s") % \
                         (
                             group_status[OpType.NOTIFIED_UPDATE_GROUP],
                             group_status[OpType.NOTIFIED_INVITE_INTO_GROUP],
                             group_status[OpType.NOTIFIED_ACCEPT_GROUP_INVITATION],
                             group_status[OpType.NOTIFIED_KICKOUT_FROM_GROUP],
                             StaticTools.get_group_creator(
                                 group).displayName,
                         )
            self.DynamicTools.send_text(
                StaticTools.send_to_who(operation),
                status
            )

    def _group_backup(self, operation):
        if operation.message.toType == MIDType.GROUP:
            group = self.DynamicTools \
                .get_client(self.Yuuki.MyMID) \
                .getGroup(operation.message.to)
            group_privilege = [
                *self.Yuuki.Admin,
                StaticTools.get_group_creator(group).mid,
                *self.Yuuki.data.get_group(group.id)["Ext_Admin"]
            ]
            if operation.message.from_ in group_privilege:
                group_members = [user.mid for user in group.members]
                group_invitations = None
                if group.invitee:
                    group_invitations = [user.mid for user in group.invitee]
                output_info = {
                    "OriginID": group.id,
                    "Members": group_members,
                    "Invites": group_invitations
                }
                self.DynamicTools.send_text(
                    operation.message.from_, group.name)
                self.DynamicTools.send_text(
                    operation.message.from_, json.dumps(output_info))
                self.DynamicTools.send_text(
                    operation.message.to, self.Yuuki.get_text("Okay"))

    def _quit(self, operation):
        if operation.message.toType == MIDType.GROUP:
            group = self.DynamicTools \
                .get_client(self.Yuuki.MyMID) \
                .getGroup(operation.message.to)
            group_privilege = [
                *self.Yuuki.Admin,
                StaticTools.get_group_creator(group).mid
            ]
            if operation.message.from_ in group_privilege:
                self.DynamicTools.leave_group(group)

    def _exit(self, operation):
        if operation.message.from_ in self.Yuuki.Admin:
            self.DynamicTools.send_text(
                StaticTools.send_to_who(operation),
                self.Yuuki.get_text("Exit.")
            )
            self.Yuuki.exit()

    def _system_call(self, operation):
        message_separated = operation.message.text.split(" ")
        if operation.message.from_ in self.Yuuki.Admin:
            # noinspection PyBroadException
            try:
                command_message = StaticTools.read_commands(message_separated[1:len(message_separated)])
                reporting_message = str(eval(command_message))
            except:
                (err1, err2, err3, error_info) = StaticTools.report_error()
                reporting_message = f"Star Yuuki BOT - Eval Error:\n{err1}\n{err2}\n{err3}\n\n{error_info}"
            self.DynamicTools.send_text(StaticTools.send_to_who(operation), reporting_message)

    def _text(self, operation):
        yuuki_name = self.Yuuki.configs["name"]
        message_separated = operation.message.text.split(" ")[0].split("/")
        actions = {
            'Help': self._help,
            'Version': self._version,
            'UserID': self._user_id,
            'GetAllHelper': self._get_all_helper,
            'Speed': self._speed,
            'SecurityMode': self._security_mode,
            'Switch': self._switch,
            'DisableAll': self._disable_all,
            'ExtAdmin': self._ext_admin,
            'Status': self._status,
            'GroupBackup': self._group_backup,
            'Quit': self._quit,
            'Exit': self._exit,
            'SystemCall': self._system_call,
        }
        if yuuki_name == message_separated[0]:
            if len(message_separated) > 1 and message_separated[1] in actions:
                function_ = actions[message_separated[1]]
                if callable(function_):
                    return function_(operation)
            return self.DynamicTools.send_text(
                StaticTools.send_to_who(operation),
                self.Yuuki.get_text("Helllo^^\nMy name is %s ><\nNice to meet you OwO") % (yuuki_name,)
            )

    def _contact(self, operation):
        cache = operation.message.contentMetadata["mid"]
        contact_info = self.DynamicTools.get_contact(cache)
        if not contact_info:
            msg = self.Yuuki.get_text("Not Found")
        elif contact_info.mid in self.Yuuki.data.get_data(["BlackList"]):
            msg = "{}\n{}".format(
                self.Yuuki.get_text("The User(s) was in our blacklist database."),
                contact_info.mid
            )
        else:
            msg = self.Yuuki.get_text("Name:%s\nPicture URL:%s/%s\nStatusMessage:\n%s\nLINE System UserID:%s") % \
                  (
                      contact_info.displayName,
                      self.Yuuki.LINE_Media_server,
                      contact_info.pictureStatus,
                      contact_info.statusMessage,
                      contact_info.mid
                  )
        self.DynamicTools.send_text(StaticTools.send_to_who(operation), msg)

    def action(self, operation):
        blocked_user = (operation.message.to in self.Yuuki.data.get_data(["BlackList"])) or \
                       (operation.message.from_ in self.Yuuki.data.get_data(["BlackList"]))

        if ('BOT_CHECK' in operation.message.contentMetadata) or blocked_user:
            pass

        elif operation.message.toType == MIDType.ROOM:
            self.DynamicTools \
                .get_client(self.Yuuki.MyMID) \
                .leaveRoom(self.Yuuki.Seq, operation.message.to)

        elif operation.message.contentType == ContentType.NONE:
            self._text(operation)

        elif operation.message.contentType == ContentType.CONTACT:
            self._contact(operation)
