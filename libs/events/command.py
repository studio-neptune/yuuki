# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

import json
import time

from yuuki_core.ttypes import MIDType, ContentType, OpType

from ..tools import Yuuki_StaticTools, Yuuki_DynamicTools


class Yuuki_Command:
    def __init__(self, Yuuki):
        """
            Event Type:
                RECEIVE_MESSAGE (26)
        """
        self.Yuuki = Yuuki

        self.Yuuki_StaticTools = Yuuki_StaticTools()
        self.Yuuki_DynamicTools = Yuuki_DynamicTools(self.Yuuki)

    def _Help(self, ncMessage):
        self.Yuuki_DynamicTools.sendText(
            self.Yuuki_StaticTools.sendToWho(ncMessage),
            self.Yuuki.get_text(
                "%s\n\t%s\n\nCommands Info:\n%s\n\nPrivacy:\n%s\n\nMore Information:\n%s\n\n%s") %
            (
                self.Yuuki.YuukiConfigs["name"],
                self.Yuuki.YuukiConfigs["version"],
                self.Yuuki.YuukiConfigs["man_page"],
                self.Yuuki.YuukiConfigs["privacy_page"],
                self.Yuuki.YuukiConfigs["project_url"],
                self.Yuuki.YuukiConfigs["copyright"],
            )
        )

    def _Version(self, ncMessage):
        self.Yuuki_DynamicTools.sendText(self.Yuuki_StaticTools.sendToWho(
            ncMessage), self.Yuuki.YuukiConfigs["version"])

    def _UserID(self, ncMessage):
        self.Yuuki_DynamicTools.sendText(self.Yuuki_StaticTools.sendToWho(
            ncMessage), self.Yuuki.get_text("LINE System UserID:\n") + ncMessage.message.from_)

    def _GetAllHelper(self, ncMessage):
        if ncMessage.message.toType == MIDType.GROUP:
            GroupInfo = self.Yuuki_DynamicTools.getClient(
                self.Yuuki.MyMID).getGroup(ncMessage.message.to)
            GroupPrivilege = self.Yuuki.Admin + [self.Yuuki_StaticTools.sybGetGroupCreator(GroupInfo).mid] + \
                             self.Yuuki.data.getGroup(GroupInfo.id)["Ext_Admin"]
            if ncMessage.message.from_ in GroupPrivilege:
                for userId in self.Yuuki.Connect.helper_ids:
                    self.Yuuki_DynamicTools.sendUser(
                        self.Yuuki_StaticTools.sendToWho(ncMessage), userId)

    def _Speed(self, ncMessage):
        Time1 = time.time()
        self.Yuuki_DynamicTools.sendText(self.Yuuki_StaticTools.sendToWho(
            ncMessage), self.Yuuki.get_text("Testing..."))
        Time2 = time.time()
        self.Yuuki_DynamicTools.sendText(self.Yuuki_StaticTools.sendToWho(
            ncMessage), self.Yuuki.get_text("Speed:\n %s com/s") % (Time2 - Time1,))

    def _SecurityMode(self, ncMessage):
        msgSep = ncMessage.message.text.split(" ")
        if ncMessage.message.from_ in self.Yuuki.Admin:
            if len(msgSep) == 2:
                if msgSep[1].isdigit() and 1 >= int(msgSep[1]) >= 0:
                    self.Yuuki.data.updateData(
                        ["Global", "SecurityService"], bool(msgSep[1]))
                    self.Yuuki_DynamicTools.sendText(self.Yuuki_StaticTools.sendToWho(
                        ncMessage), self.Yuuki.get_text("Okay"))
                else:
                    self.Yuuki_DynamicTools.sendText(self.Yuuki_StaticTools.sendToWho(
                        ncMessage), self.Yuuki.get_text("Enable(True): 1\nDisable(False): 0"))
            else:
                self.Yuuki_DynamicTools.sendText(self.Yuuki_StaticTools.sendToWho(ncMessage),
                                                 str(bool(
                                                     self.Yuuki.data.getData(["Global", "SecurityService"]))))

    def _Switch(self, ncMessage):
        if ncMessage.message.toType == MIDType.GROUP:
            GroupInfo = self.Yuuki_DynamicTools.getClient(
                self.Yuuki.MyMID).getGroup(ncMessage.message.to)
            GroupPrivilege = self.Yuuki.Admin + [self.Yuuki_StaticTools.sybGetGroupCreator(GroupInfo).mid] + \
                             self.Yuuki.data.getGroup(GroupInfo.id)["Ext_Admin"]
            if not self.Yuuki.data.getData(["Global", "SecurityService"]):
                self.Yuuki_DynamicTools.sendText(
                    self.Yuuki_StaticTools.sendToWho(ncMessage),
                    self.Yuuki.get_text("SecurityService of %s was disable") % (self.Yuuki.YuukiConfigs["name"],)
                )
            elif ncMessage.message.from_ in GroupPrivilege:
                self._Switch_action(ncMessage)

    def _Switch_action(self, ncMessage):
        msgSep = ncMessage.message.text.split(" ")
        status = []
        unknown_msg = []
        unknown_msgtext = ""
        for count, code in enumerate(msgSep):
            if code.isdigit() and 3 >= int(code) >= 0:
                status.append(int(code))
            elif count != 0:
                unknown_msg.append(code.strip())
        self.Yuuki_DynamicTools.configSecurityStatus(
            ncMessage.message.to, status)
        if unknown_msg:
            unknown_msgtext = ", ".join(unknown_msg)
        if status:
            self.Yuuki_DynamicTools.sendText(self.Yuuki_StaticTools.sendToWho(
                ncMessage), self.Yuuki.get_text("Okay"))
        else:
            self.Yuuki_DynamicTools.sendText(self.Yuuki_StaticTools.sendToWho(
                ncMessage), self.Yuuki.get_text("Not Found"))
        if unknown_msgtext != "":
            self.Yuuki_DynamicTools.sendText(
                self.Yuuki_StaticTools.sendToWho(ncMessage),
                self.Yuuki.get_text(
                    "Notice: Unknown command line argument(s)") + "\n({})".format(unknown_msgtext)
            )

    def _DisableAll(self, ncMessage):
        if ncMessage.message.toType == MIDType.GROUP:
            GroupInfo = self.Yuuki_DynamicTools.getClient(
                self.Yuuki.MyMID).getGroup(ncMessage.message.to)
            GroupPrivilege = self.Yuuki.Admin + [self.Yuuki_StaticTools.sybGetGroupCreator(GroupInfo).mid] + \
                             self.Yuuki.data.getGroup(GroupInfo.id)["Ext_Admin"]
            if not self.Yuuki.data.getData(["Global", "SecurityService"]):
                self.Yuuki_DynamicTools.sendText(
                    self.Yuuki_StaticTools.sendToWho(ncMessage),
                    self.Yuuki.get_text("SecurityService of %s was disable") % (self.Yuuki.YuukiConfigs["name"],)
                )
            elif ncMessage.message.from_ in GroupPrivilege:
                self.Yuuki_DynamicTools.configSecurityStatus(
                    ncMessage.message.to, [])
                self.Yuuki_DynamicTools.sendText(self.Yuuki_StaticTools.sendToWho(
                    ncMessage), self.Yuuki.get_text("Okay"))

    def _ExtAdmin(self, ncMessage):
        msgSep = ncMessage.message.text.split(" ")
        if ncMessage.message.toType == MIDType.GROUP:
            GroupInfo = self.Yuuki_DynamicTools.getClient(
                self.Yuuki.MyMID).getGroup(ncMessage.message.to)
            GroupPrivilege = self.Yuuki.Admin + \
                             [self.Yuuki_StaticTools.sybGetGroupCreator(GroupInfo).mid]
            if len(msgSep) == 3:
                if ncMessage.message.from_ in GroupPrivilege:
                    if msgSep[1] == "add":
                        self._ExtAdmin_Add(ncMessage, msgSep, GroupInfo)
                    elif msgSep[1] == "delete":
                        self._ExtAdmin_Delete(ncMessage, msgSep, GroupInfo)
            else:
                self._ExtAdmin_Query(ncMessage, GroupInfo)

    def _ExtAdmin_Add(self, ncMessage, msgSep, GroupInfo):
        if msgSep[2] in [Member.mid for Member in GroupInfo.members]:
            if msgSep[2] in self.Yuuki.data.getGroup(GroupInfo.id)["Ext_Admin"]:
                self.Yuuki_DynamicTools.sendText(
                    self.Yuuki_StaticTools.sendToWho(ncMessage),
                    self.Yuuki.get_text("Added")
                )
            elif msgSep[2] not in self.Yuuki.data.getData(["BlackList"]):
                origin = self.Yuuki.data.getData(
                    ["Group", GroupInfo.id, "Ext_Admin"])
                ext_admin_list = origin.copy()
                ext_admin_list.append(msgSep[2])
                self.Yuuki.data.updateData(
                    ["Group", GroupInfo.id, "Ext_Admin"], ext_admin_list)
                self.Yuuki_DynamicTools.sendText(self.Yuuki_StaticTools.sendToWho(
                    ncMessage), self.Yuuki.get_text("Okay"))
            else:
                self.Yuuki_DynamicTools.sendText(self.Yuuki_StaticTools.sendToWho(ncMessage),
                                                 self.Yuuki.get_text(
                                                     "The User(s) was in our blacklist database."))
        else:
            self.Yuuki_DynamicTools.sendText(self.Yuuki_StaticTools.sendToWho(ncMessage),
                                             self.Yuuki.get_text(
                                                 "Wrong UserID or the guy is not in Group"))

    def _ExtAdmin_Delete(self, ncMessage, msgSep, GroupInfo):
        if msgSep[2] in self.Yuuki.data.getGroup(GroupInfo.id)["Ext_Admin"]:
            origin = self.Yuuki.data.getData(["Group", GroupInfo.id, "Ext_Admin"])
            ext_admin_list = origin.copy()
            ext_admin_list.remove(msgSep[2])
            self.Yuuki.data.updateData(
                ["Group", GroupInfo.id, "Ext_Admin"], ext_admin_list)
            self.Yuuki_DynamicTools.sendText(
                self.Yuuki_StaticTools.sendToWho(ncMessage),
                self.Yuuki.get_text("Okay")
            )
        else:
            self.Yuuki_DynamicTools.sendText(self.Yuuki_StaticTools.sendToWho(
                ncMessage), self.Yuuki.get_text("Not Found"))

    def _ExtAdmin_Query(self, ncMessage, GroupInfo):
        if self.Yuuki.data.getGroup(GroupInfo.id)["Ext_Admin"]:
            status = ""
            status_added = []
            for member in GroupInfo.members:
                if member.mid in self.Yuuki.data.getGroup(GroupInfo.id)["Ext_Admin"]:
                    status += "{}\n".format(member.displayName)
                    status_added.append(member.mid)
            for userId in self.Yuuki.data.getGroup(GroupInfo.id)["Ext_Admin"]:
                if userId not in status_added:
                    status += "{}: {}\n".format(
                        self.Yuuki.get_text("Unknown"), userId)
            self.Yuuki_DynamicTools.sendText(
                self.Yuuki_StaticTools.sendToWho(ncMessage),
                status + self.Yuuki.get_text("\nExtend Administrator(s)")
            )
        else:
            self.Yuuki_DynamicTools.sendText(self.Yuuki_StaticTools.sendToWho(
                ncMessage), self.Yuuki.get_text("Not Found"))

    def _Status(self, ncMessage):
        if ncMessage.message.toType == MIDType.GROUP:
            GroupInfo = self.Yuuki_DynamicTools.getClient(
                self.Yuuki.MyMID).getGroup(ncMessage.message.to)
            group_status = self.Yuuki.data.getSEGroup(
                ncMessage.message.to)
            if not self.Yuuki.data.getData(["Global", "SecurityService"]):
                status = self.Yuuki.get_text("SecurityService of %s was disable") % (
                    self.Yuuki.YuukiConfigs["name"],
                )
            elif group_status is None:
                status = self.Yuuki.get_text("Default without Initialize\nMain Admin of the Group:\n%s") % (
                    self.Yuuki_StaticTools.sybGetGroupCreator(
                        GroupInfo).displayName,
                )
            else:
                status = self.Yuuki.get_text(
                    "SecurityService is Listening on\n\nURL:%s\nInvite:%s\nJoin:%s\nMembers:%s\n\nMain Admin of the Group:\n%s") % (
                             group_status[OpType.NOTIFIED_UPDATE_GROUP],
                             group_status[OpType.NOTIFIED_INVITE_INTO_GROUP],
                             group_status[OpType.NOTIFIED_ACCEPT_GROUP_INVITATION],
                             group_status[OpType.NOTIFIED_KICKOUT_FROM_GROUP],
                             self.Yuuki_StaticTools.sybGetGroupCreator(
                                 GroupInfo).displayName,
                         )
            self.Yuuki_DynamicTools.sendText(
                self.Yuuki_StaticTools.sendToWho(ncMessage), status)

    def _GroupBackup(self, ncMessage):
        if ncMessage.message.toType == MIDType.GROUP:
            GroupInfo = self.Yuuki_DynamicTools.getClient(
                self.Yuuki.MyMID).getGroup(ncMessage.message.to)
            GroupPrivilege = self.Yuuki.Admin + [self.Yuuki_StaticTools.sybGetGroupCreator(GroupInfo).mid] + \
                             self.Yuuki.data.getGroup(GroupInfo.id)["Ext_Admin"]
            if ncMessage.message.from_ in GroupPrivilege:
                GroupMembers = [User.mid for User in GroupInfo.members]
                GroupInvites = None
                if GroupInfo.invitee:
                    GroupInvites = [
                        User.mid for User in GroupInfo.invitee]
                LayoutInfo = {
                    "OriginID": GroupInfo.id,
                    "Members": GroupMembers,
                    "Invites": GroupInvites
                }
                self.Yuuki_DynamicTools.sendText(
                    ncMessage.message.from_, GroupInfo.name)
                self.Yuuki_DynamicTools.sendText(
                    ncMessage.message.from_, json.dumps(LayoutInfo))
                self.Yuuki_DynamicTools.sendText(
                    ncMessage.message.to, self.Yuuki.get_text("Okay"))

    def _Quit(self, ncMessage):
        if ncMessage.message.toType == MIDType.GROUP:
            GroupInfo = self.Yuuki_DynamicTools.getClient(
                self.Yuuki.MyMID).getGroup(ncMessage.message.to)
            GroupPrivilege = self.Yuuki.Admin + \
                             [self.Yuuki_StaticTools.sybGetGroupCreator(
                                 GroupInfo).mid]
            if ncMessage.message.from_ in GroupPrivilege:
                self.Yuuki_DynamicTools.sendText(self.Yuuki_StaticTools.sendToWho(
                    ncMessage), self.Yuuki.get_text("Bye Bye"))
                self.Yuuki_DynamicTools.getClient(
                    self.Yuuki.MyMID).leaveGroup(self.Yuuki.Seq, GroupInfo.id)
                for userId in self.Yuuki.Connect.helper_ids:
                    if userId in [member.mid for member in GroupInfo.members]:
                        self.Yuuki_DynamicTools.getClient(
                            userId).leaveGroup(self.Yuuki.Seq, GroupInfo.id)
            GroupList = self.Yuuki.data.getData(
                ["Global", "GroupJoined"])
            NewGroupList = GroupList.copy()
            NewGroupList.remove(GroupInfo.id)
            self.Yuuki.data.updateData(
                ["Global", "GroupJoined"], NewGroupList)

    def _Exit(self, ncMessage):
        if ncMessage.message.from_ in self.Yuuki.Admin:
            self.Yuuki_DynamicTools.sendText(self.Yuuki_StaticTools.sendToWho(
                ncMessage), self.Yuuki.get_text("Exit."))
            self.Yuuki.exit()

    def _Com(self, ncMessage):
        msgSep = ncMessage.message.text.split(" ")
        if ncMessage.message.from_ in self.Yuuki.Admin:
            # noinspection PyBroadException
            try:
                ComMsg = self.Yuuki_StaticTools.readCommandLine(msgSep[1:len(msgSep)])
                Report = str(eval(ComMsg))
            except:
                (err1, err2, err3, ErrorInfo) = self.Yuuki_StaticTools.errorReport()
                Report = "Star Yuuki BOT - Eval Error:\n%s\n%s\n%s\n\n%s" % (err1, err2, err3, ErrorInfo)
            self.Yuuki_DynamicTools.sendText(
                self.Yuuki_StaticTools.sendToWho(ncMessage), Report)

    def _text(self, ncMessage):
        Yuuki_Name = self.Yuuki.YuukiConfigs["name"]
        msgSep = ncMessage.message.text.split(" ")[0].split("/")
        actions = {
            'Help': self._Help,
            'Version': self._Version,
            'UserID': self._UserID,
            'GetAllHelper': self._GetAllHelper,
            'Speed': self._Speed,
            'SecurityMode': self._SecurityMode,
            'Switch': self._Switch,
            'DisableAll': self._DisableAll,
            'ExtAdmin': self._ExtAdmin,
            'Status': self._Status,
            'GroupBackup': self._GroupBackup,
            'Quit': self._Quit,
            'Exit': self._Exit,
            'Com': self._Com,
        }
        if Yuuki_Name == msgSep[0] and msgSep[1] in actions:
            actions[msgSep[1]](ncMessage)

    def _contact(self, ncMessage):
        cache = ncMessage.message.contentMetadata["mid"]
        contactInfo = self.Yuuki_DynamicTools.getContact(cache)
        if not contactInfo:
            msg = self.Yuuki.get_text("Not Found")
        elif contactInfo.mid in self.Yuuki.data.getData(["BlackList"]):
            msg = "{}\n{}".format(self.Yuuki.get_text(
                "The User(s) was in our blacklist database."), contactInfo.mid)
        else:
            msg = self.Yuuki.get_text("Name:%s\nPicture URL:%s/%s\nStatusMessage:\n%s\nLINE System UserID:%s") % \
                  (contactInfo.displayName, self.Yuuki.LINE_Media_server, contactInfo.pictureStatus,
                   contactInfo.statusMessage, contactInfo.mid)
        self.Yuuki_DynamicTools.sendText(
            self.Yuuki_StaticTools.sendToWho(ncMessage), msg)

    def action(self, ncMessage):
        BlockedIgnore = (ncMessage.message.to in self.Yuuki.data.getData(["BlackList"])) or \
                        (ncMessage.message.from_ in self.Yuuki.data.getData(["BlackList"]))

        if ('BOT_CHECK' in ncMessage.message.contentMetadata) or BlockedIgnore:
            pass

        elif ncMessage.message.toType == MIDType.ROOM:
            self.Yuuki_DynamicTools.getClient(
                self.Yuuki.MyMID
            ).leaveRoom(
                self.Yuuki.Seq, ncMessage.message.to
            )

        elif ncMessage.message.contentType == ContentType.NONE:
            self._text(ncMessage)

        elif ncMessage.message.contentType == ContentType.CONTACT:
            self._contact(ncMessage)
