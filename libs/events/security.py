# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from ..tools import Yuuki_StaticTools, Yuuki_DynamicTools

from yuuki_core.ttypes import OpType


class Yuuki_Security:
    def __init__(self, Yuuki):
        """
            Event Type:
                NOTIFIED_UPDATE_GROUP (11)
                NOTIFIED_INVITE_INTO_GROUP (13)
                NOTIFIED_ACCEPT_GROUP_INVITATION (17)
                NOTIFIED_KICKOUT_FROM_GROUP (19)
        """
        self.Yuuki = Yuuki

        self.Yuuki_StaticTools = Yuuki_StaticTools()
        self.Yuuki_DynamicTools = Yuuki_DynamicTools(self.Yuuki)

    def NOTIFIED_UPDATE_GROUP(self, GroupInfo, SecurityInfo, ncMessage):
        if SecurityInfo["Another"] == '4':
            if not GroupInfo.preventJoinByTicket and SecurityInfo["Action"] not in self.Yuuki.Connect.helper_ids:
                self.Yuuki.threadExec(
                    self.Yuuki_DynamicTools.changeGroupUrlStatus,
                    (GroupInfo, False)
                )
                self.Yuuki.threadExec(
                    self.Yuuki_DynamicTools.sendText,
                    (SecurityInfo["GroupID"], self.Yuuki.get_text("DO NOT ENABLE THE GROUP URL STATUS, see you..."))
                )
                Kicker = self.Yuuki_DynamicTools.modifyGroupMemberList(1, GroupInfo, SecurityInfo["Action"])
                # Log
                self.Yuuki.data.updateLog("KickEvent", (
                    self.Yuuki.data.getTime(),
                    GroupInfo.name,
                    SecurityInfo["GroupID"],
                    Kicker,
                    SecurityInfo["Action"],
                    SecurityInfo["Another"],
                    ncMessage.type
                ))

    def NOTIFIED_INVITE_INTO_GROUP(self, GroupInfo, SecurityInfo, ncMessage):
        Canceler = "None"
        if "\x1e" in SecurityInfo["Another"]:
            for userId in SecurityInfo["Another"].split("\x1e"):
                if userId not in self.Yuuki.AllAccountIds + SecurityInfo["GroupPrivilege"]:
                    if GroupInfo.invitee and userId in [user.mid for user in GroupInfo.invitee]:
                        Canceler = self.Yuuki_DynamicTools.modifyGroupMemberList(2, GroupInfo, userId)
                    else:
                        Canceler = self.Yuuki_DynamicTools.modifyGroupMemberList(1, GroupInfo, userId)
                        # Log
                        self.Yuuki.data.updateLog("KickEvent", (
                            self.Yuuki.data.getTime(),
                            GroupInfo.name,
                            SecurityInfo["GroupID"],
                            Canceler,
                            SecurityInfo["Action"],
                            userId,
                            ncMessage.type * 10
                        ))
            # Log
            self.Yuuki.data.updateLog("CancelEvent", (
                self.Yuuki.data.getTime(),
                GroupInfo.name,
                SecurityInfo["GroupID"],
                Canceler,
                SecurityInfo["Action"],
                SecurityInfo["Another"].replace("\x1e", ",")
            ))
        elif SecurityInfo["Another"] not in self.Yuuki.AllAccountIds + SecurityInfo["GroupPrivilege"]:
            if GroupInfo.invitee and SecurityInfo["Another"] in [user.mid for user in GroupInfo.invitee]:
                Canceler = self.Yuuki_DynamicTools.modifyGroupMemberList(2, GroupInfo, SecurityInfo["Another"])
            else:
                Canceler = self.Yuuki_DynamicTools.modifyGroupMemberList(1, GroupInfo, SecurityInfo["Another"])
                # Log
                self.Yuuki.data.updateLog("KickEvent", (
                    self.Yuuki.data.getTime(), GroupInfo.name, SecurityInfo["GroupID"], Canceler, SecurityInfo["Action"], SecurityInfo["Another"],
                    ncMessage.type * 10))
            # Log
            self.Yuuki.data.updateLog("CancelEvent", (
                self.Yuuki.data.getTime(),
                GroupInfo.name,
                SecurityInfo["GroupID"],
                Canceler,
                SecurityInfo["Action"],
                SecurityInfo["Another"]
            ))
        if Canceler != "None":
            self.Yuuki_DynamicTools.sendText(
                SecurityInfo["GroupID"], self.Yuuki.get_text("Do not invite anyone...thanks"))

    def NOTIFIED_ACCEPT_GROUP_INVITATION(self, GroupInfo, SecurityInfo, ncMessage):
        for userId in self.Yuuki.data.getData(["BlackList"]):
            if userId == SecurityInfo["Action"]:
                self.Yuuki.threadExec(
                    self.Yuuki_DynamicTools.sendText,
                    (SecurityInfo["GroupID"], self.Yuuki.get_text("You are our blacklist. Bye~"))
                )
                Kicker = self.Yuuki_DynamicTools.modifyGroupMemberList(1, GroupInfo, SecurityInfo["Action"])
                # Log
                self.Yuuki.data.updateLog("KickEvent", (
                    self.Yuuki.data.getTime(),
                    GroupInfo.name,
                    SecurityInfo["GroupID"],
                    Kicker,
                    Kicker,
                    SecurityInfo["Action"],
                    ncMessage.type
                ))

    def NOTIFIED_KICKOUT_FROM_GROUP(self, GroupInfo, SecurityInfo, ncMessage):
        if SecurityInfo["Action"] in self.Yuuki.Connect.helper_ids:
            # Log
            self.Yuuki.data.updateLog("KickEvent", (
                self.Yuuki.data.getTime(),
                GroupInfo.name,
                SecurityInfo["GroupID"],
                SecurityInfo["Action"],
                SecurityInfo["Action"],
                SecurityInfo["Another"],
                ncMessage.type * 10 + 1
            ))
        elif SecurityInfo["Another"] in self.Yuuki.AllAccountIds:
            Kicker = "None"
            try:
                Kicker = self.Yuuki_DynamicTools.modifyGroupMemberList(
                    1,
                    GroupInfo,
                    SecurityInfo["Action"],
                    SecurityInfo["Another"]
                )
                # Log
                self.Yuuki.data.updateLog("KickEvent", (
                    self.Yuuki.data.getTime(),
                    GroupInfo.name,
                    SecurityInfo["GroupID"],
                    Kicker,
                    SecurityInfo["Action"],
                    SecurityInfo["Another"],
                    ncMessage.type * 10 + 2
                ))
                assert Kicker != "None", "No Helper Found"
                if GroupInfo.preventJoinByTicket:
                    self.Yuuki.threadExec(
                        self.Yuuki_DynamicTools.changeGroupUrlStatus,
                        (GroupInfo, True, Kicker)
                    )
                GroupTicket = self.Yuuki_DynamicTools.getGroupTicket(
                    SecurityInfo["GroupID"], Kicker)
                try:
                    self.Yuuki_DynamicTools.getClient(SecurityInfo["Another"]).acceptGroupInvitationByTicket(
                        self.Yuuki.Seq,
                        SecurityInfo["GroupID"],
                        GroupTicket
                    )
                except:
                    if GroupInfo.preventJoinByTicket:
                        self.Yuuki_DynamicTools.changeGroupUrlStatus(
                            GroupInfo,
                            True,
                            Kicker
                        )
                    GroupTicket = self.Yuuki_DynamicTools.getGroupTicket(
                        SecurityInfo["GroupID"], Kicker, True)
                    self.Yuuki_DynamicTools.getClient(SecurityInfo["Another"]).acceptGroupInvitationByTicket(
                        self.Yuuki.Seq,
                        SecurityInfo["GroupID"],
                        GroupTicket
                    )
                if GroupInfo.preventJoinByTicket:
                    self.Yuuki.threadExec(
                        self.Yuuki_DynamicTools.changeGroupUrlStatus, (GroupInfo, False, SecurityInfo["Another"]))
                self.Yuuki_DynamicTools.getGroupTicket(
                    SecurityInfo["GroupID"], SecurityInfo["Another"], True)
            except:
                (err1, err2, err3, ErrorInfo) = self.Yuuki_StaticTools.errorReport()
                for Root in self.Yuuki.Admin:
                    self.Yuuki_DynamicTools.sendText(
                        Root,
                        "Star Yuuki BOT - SecurityService Failure\n\n%s\n%s\n%s\n\n%s" % (err1, err2, err3, ErrorInfo)
                    )
                if SecurityInfo["Another"] == self.Yuuki.MyMID:
                    GroupList = self.Yuuki.data.getData(["Global", "GroupJoined"])
                    NewGroupList = GroupList.copy()
                    NewGroupList.remove(SecurityInfo["GroupID"])
                    self.Yuuki.data.updateData(["Global", "GroupJoined"], NewGroupList)
                # Log
                self.Yuuki.data.updateLog("KickEvent", (
                    self.Yuuki.data.getTime(),
                    GroupInfo.name,
                    SecurityInfo["GroupID"],
                    Kicker,
                    SecurityInfo["Action"],
                    SecurityInfo["Another"],
                    ncMessage.type * 10 + 3
                ))
            BlackList = self.Yuuki.data.getData(["BlackList"])
            if SecurityInfo["Action"] not in BlackList:
                NewBlackList = BlackList.copy()
                NewBlackList.append(SecurityInfo["Action"])
                self.Yuuki.data.updateData(["BlackList"], NewBlackList)
                # Log
                self.Yuuki.data.updateLog(
                    "BlackList", (self.Yuuki.data.getTime(), SecurityInfo["Action"], SecurityInfo["GroupID"]))
                self.Yuuki.threadExec(self.Yuuki_DynamicTools.sendText, (SecurityInfo["Action"], self.Yuuki.get_text(
                    "You had been blocked by our database.")))
        elif SecurityInfo["Security_Access"]:
            self.Yuuki.threadExec(self.Yuuki_DynamicTools.sendText, (
                SecurityInfo["GroupID"], self.Yuuki.get_text("DO NOT KICK, thank you ^^")))
            Kicker = self.Yuuki_DynamicTools.modifyGroupMemberList(1, GroupInfo, SecurityInfo["Action"])
            # Log
            self.Yuuki.data.updateLog("KickEvent", (
                self.Yuuki.data.getTime(), GroupInfo.name, SecurityInfo["GroupID"], Kicker, SecurityInfo["Action"], SecurityInfo["Another"], ncMessage.type))
            self.Yuuki.threadExec(self.Yuuki_DynamicTools.sendText, (SecurityInfo["GroupID"], self.Yuuki.get_text(
                "The one who was been kicked:")))
            self.Yuuki.threadExec(
                self.Yuuki_DynamicTools.sendUser, (SecurityInfo["GroupID"], SecurityInfo["Another"]))

    def action(self, ncMessage):
        SecurityInfo = self.Yuuki_StaticTools.securityForWhere(ncMessage)

        GroupInfo = self.Yuuki_DynamicTools.getClient(self.Yuuki.MyMID).getGroup(SecurityInfo["GroupID"])
        SecurityInfo["GroupPrivilege"] = self.Yuuki.Admin +\
                         [self.Yuuki_StaticTools.sybGetGroupCreator(GroupInfo).mid] +\
                         self.Yuuki.data.getGroup(GroupInfo.id)["Ext_Admin"]

        if SecurityInfo["Action"] in SecurityInfo["GroupPrivilege"] or\
                SecurityInfo["Another"] in SecurityInfo["GroupPrivilege"]:
            if ncMessage.type != OpType.NOTIFIED_KICKOUT_FROM_GROUP:
                return
            elif SecurityInfo["Action"] in SecurityInfo["GroupPrivilege"]:
                return

        SEGroup = self.Yuuki.data.getSEGroup(SecurityInfo["GroupID"])
        if SEGroup is None:
            SecurityInfo["Security_Access"] = self.Yuuki.data.getData(["Global", "SecurityService"])
        elif SEGroup[ncMessage.type]:
            SecurityInfo["Security_Access"] = SEGroup[ncMessage.type]
        else:
            SecurityInfo["Security_Access"] = False

        if self.Yuuki.data.getData(["Global", "SecurityService"]):
            {
                OpType.NOTIFIED_UPDATE_GROUP: self.NOTIFIED_UPDATE_GROUP,
                OpType.NOTIFIED_INVITE_INTO_GROUP: self.NOTIFIED_INVITE_INTO_GROUP,
                OpType.NOTIFIED_ACCEPT_GROUP_INVITATION: self.NOTIFIED_ACCEPT_GROUP_INVITATION,
                OpType.NOTIFIED_KICKOUT_FROM_GROUP: self.NOTIFIED_KICKOUT_FROM_GROUP
            }[ncMessage.type](GroupInfo, SecurityInfo, ncMessage)
