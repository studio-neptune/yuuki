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

    def action(self, ncMessage):
        Security_Access = False

        (GroupID, Action, Another) = self.Yuuki_StaticTools.securityForWhere(ncMessage)
        SEGroup = self.Yuuki.data.getSEGroup(GroupID)

        GroupInfo = self.Yuuki_DynamicTools.getClient(
            self.Yuuki.MyMID).getGroup(GroupID)
        GroupPrivilege = self.Yuuki.Admin + [self.Yuuki_StaticTools.sybGetGroupCreator(GroupInfo).mid] + self.Yuuki.data.getGroup(GroupInfo.id)[
            "Ext_Admin"]

        if Action in GroupPrivilege or Another in GroupPrivilege:
            if ncMessage.type != OpType.NOTIFIED_KICKOUT_FROM_GROUP:
                return
            elif Action in GroupPrivilege:
                return

        if SEGroup is None:
            Security_Access = self.Yuuki.data.getData(
                ["Global", "SecurityService"])
        elif SEGroup[ncMessage.type]:
            Security_Access = SEGroup[ncMessage.type]

        if self.Yuuki.data.getData(["Global", "SecurityService"]):
            if ncMessage.type == OpType.NOTIFIED_UPDATE_GROUP and Security_Access:
                if Another == '4':
                    if not GroupInfo.preventJoinByTicket and Action not in self.Yuuki.Connect.helper_ids:
                        self.Yuuki.threadExec(
                            self.Yuuki_DynamicTools.changeGroupUrlStatus, (GroupInfo, False))
                        self.Yuuki.threadExec(self.Yuuki_DynamicTools.sendText, (GroupID, self.Yuuki.get_text(
                            "DO NOT ENABLE THE GROUP URL STATUS, see you...")))
                        Kicker = self.Yuuki_DynamicTools.modifyGroupMemberList(1, GroupInfo, Action)
                        # Log
                        self.Yuuki.data.updateLog("KickEvent", (
                            self.Yuuki.data.getTime(), GroupInfo.name, GroupID, Kicker, Action, Another, ncMessage.type))
            elif ncMessage.type == OpType.NOTIFIED_INVITE_INTO_GROUP and Security_Access:
                Canceler = "None"
                if "\x1e" in Another:
                    for userId in Another.split("\x1e"):
                        if userId not in self.Yuuki.AllAccountIds + GroupPrivilege:
                            if GroupInfo.invitee and userId in [user.mid for user in GroupInfo.invitee]:
                                Canceler = self.Yuuki_DynamicTools.modifyGroupMemberList(2, GroupInfo, userId)
                            else:
                                Canceler = self.Yuuki_DynamicTools.modifyGroupMemberList(1, GroupInfo, userId)
                                # Log
                                self.Yuuki.data.updateLog("KickEvent", (
                                    self.Yuuki.data.getTime(), GroupInfo.name, GroupID, Canceler, Action, userId,
                                    ncMessage.type * 10))
                    # Log
                    self.Yuuki.data.updateLog("CancelEvent", (
                        self.Yuuki.data.getTime(), GroupInfo.name, GroupID, Canceler, Action, Another.replace("\x1e", ",")))
                elif Another not in self.Yuuki.AllAccountIds + GroupPrivilege:
                    if GroupInfo.invitee and Another in [user.mid for user in GroupInfo.invitee]:
                        Canceler = self.Yuuki_DynamicTools.modifyGroupMemberList(2, GroupInfo, Another)
                    else:
                        Canceler = self.Yuuki_DynamicTools.modifyGroupMemberList(1, GroupInfo, Another)
                        # Log
                        self.Yuuki.data.updateLog("KickEvent", (
                            self.Yuuki.data.getTime(), GroupInfo.name, GroupID, Canceler, Action, Another,
                            ncMessage.type * 10))
                    # Log
                    self.Yuuki.data.updateLog("CancelEvent",
                                              (self.Yuuki.data.getTime(), GroupInfo.name, GroupID, Canceler, Action, Another))
                if Canceler != "None":
                    self.Yuuki_DynamicTools.sendText(
                        GroupID, self.Yuuki.get_text("Do not invite anyone...thanks"))
            elif ncMessage.type == OpType.NOTIFIED_ACCEPT_GROUP_INVITATION and Security_Access:
                for userId in self.Yuuki.data.getData(["BlackList"]):
                    if userId == Action:
                        self.Yuuki.threadExec(self.Yuuki_DynamicTools.sendText, (GroupID, self.Yuuki.get_text(
                            "You are our blacklist. Bye~")))
                        Kicker = self.Yuuki_DynamicTools.modifyGroupMemberList(1, GroupInfo, Action)
                        # Log
                        self.Yuuki.data.updateLog("KickEvent", (
                            self.Yuuki.data.getTime(), GroupInfo.name, GroupID, Kicker, Kicker, Action, ncMessage.type))
            elif ncMessage.type == OpType.NOTIFIED_KICKOUT_FROM_GROUP:
                if Action in self.Yuuki.Connect.helper_ids:
                    # Log
                    self.Yuuki.data.updateLog("KickEvent", (
                        self.Yuuki.data.getTime(), GroupInfo.name, GroupID, Action, Action, Another, ncMessage.type * 10 + 1))
                elif Another in self.Yuuki.AllAccountIds:
                    Kicker = "None"
                    try:
                        Kicker = self.Yuuki_DynamicTools.modifyGroupMemberList(1, GroupInfo, Action, Another)
                        # Log
                        self.Yuuki.data.updateLog("KickEvent", (
                            self.Yuuki.data.getTime(), GroupInfo.name, GroupID, Kicker, Action, Another,
                            ncMessage.type * 10 + 2))
                        assert Kicker != "None", "No Helper Found"
                        if GroupInfo.preventJoinByTicket:
                            self.Yuuki.threadExec(
                                self.Yuuki_DynamicTools.changeGroupUrlStatus, (GroupInfo, True, Kicker))
                        GroupTicket = self.Yuuki_DynamicTools.getGroupTicket(
                            GroupID, Kicker)
                        try:
                            self.Yuuki_DynamicTools.getClient(Another).acceptGroupInvitationByTicket(
                                self.Yuuki.Seq, GroupID, GroupTicket)
                        except:
                            if GroupInfo.preventJoinByTicket:
                                self.Yuuki_DynamicTools.changeGroupUrlStatus(
                                    GroupInfo, True, Kicker)
                            GroupTicket = self.Yuuki_DynamicTools.getGroupTicket(
                                GroupID, Kicker, True)
                            self.Yuuki_DynamicTools.getClient(Another).acceptGroupInvitationByTicket(
                                self.Yuuki.Seq, GroupID, GroupTicket)
                        if GroupInfo.preventJoinByTicket:
                            self.Yuuki.threadExec(
                                self.Yuuki_DynamicTools.changeGroupUrlStatus, (GroupInfo, False, Another))
                        self.Yuuki_DynamicTools.getGroupTicket(
                            GroupID, Another, True)
                    except:
                        (err1, err2, err3,
                         ErrorInfo) = self.Yuuki_StaticTools.errorReport()
                        for Root in self.Yuuki.Admin:
                            self.Yuuki_DynamicTools.sendText(Root, "Star Yuuki BOT - SecurityService Failure\n\n%s\n%s\n%s\n\n%s" %
                                                             (err1, err2, err3, ErrorInfo))
                        if Another == self.Yuuki.MyMID:
                            GroupList = self.Yuuki.data.getData(
                                ["Global", "GroupJoined"])
                            NewGroupList = GroupList.copy()
                            NewGroupList.remove(GroupID)
                            self.Yuuki.data.updateData(
                                ["Global", "GroupJoined"], NewGroupList)
                        # Log
                        self.Yuuki.data.updateLog("KickEvent", (
                            self.Yuuki.data.getTime(), GroupInfo.name, GroupID, Kicker, Action, Another,
                            ncMessage.type * 10 + 3))
                    BlackList = self.Yuuki.data.getData(["BlackList"])
                    if Action not in BlackList:
                        NewBlackList = BlackList.copy()
                        NewBlackList.append(Action)
                        self.Yuuki.data.updateData(["BlackList"], NewBlackList)
                        # Log
                        self.Yuuki.data.updateLog(
                            "BlackList", (self.Yuuki.data.getTime(), Action, GroupID))
                        self.Yuuki.threadExec(self.Yuuki_DynamicTools.sendText, (Action, self.Yuuki.get_text(
                            "You had been blocked by our database.")))
                elif Security_Access:
                    self.Yuuki.threadExec(self.Yuuki_DynamicTools.sendText, (
                        GroupID, self.Yuuki.get_text("DO NOT KICK, thank you ^^")))
                    Kicker = self.Yuuki_DynamicTools.modifyGroupMemberList(1, GroupInfo, Action)
                    # Log
                    self.Yuuki.data.updateLog("KickEvent", (
                        self.Yuuki.data.getTime(), GroupInfo.name, GroupID, Kicker, Action, Another, ncMessage.type))
                    self.Yuuki.threadExec(self.Yuuki_DynamicTools.sendText, (GroupID, self.Yuuki.get_text(
                        "The one who was been kicked:")))
                    self.Yuuki.threadExec(
                        self.Yuuki_DynamicTools.sendUser, (GroupID, Another))
