# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from ..utils import Yuuki_StaticTools, Yuuki_DynamicTools


class Yuuki_JoinGroup:
    def __init__(self, Yuuki):
        """
            Event Type:
                NOTIFIED_INVITE_INTO_GROUP (13)
        """
        self.Yuuki = Yuuki
        self.Yuuki_DynamicTools = Yuuki_DynamicTools(self.Yuuki)

    def _accept(self, GroupID, GroupInfo, Inviter):
        GroupList = self.Yuuki.data.getData(["Global", "GroupJoined"])
        NewGroupList = GroupList.copy()
        NewGroupList.append(GroupID)
        self.Yuuki.data.updateData(
            ["Global", "GroupJoined"], NewGroupList)
        self.Yuuki_DynamicTools.sendText(
            GroupID,
            self.Yuuki.get_text("Helllo^^\nMy name is %s ><\nNice to meet you OwO") %
            (self.Yuuki.YuukiConfigs["name"],)
        )
        self.Yuuki_DynamicTools.sendText(
            GroupID,
            self.Yuuki.get_text("Type:\n\t%s/Help\nto get more information\n\nMain Admin of the Group:\n%s") %
            (
                self.Yuuki.YuukiConfigs["name"],
                Yuuki_StaticTools.sybGetGroupCreator(GroupInfo).displayName,
            )
        )
        self.Yuuki_DynamicTools.getGroupTicket(GroupID, self.Yuuki.MyMID, True)
        # Log
        self.Yuuki.data.updateLog(
            "JoinGroup", (self.Yuuki.data.getTime(), GroupInfo.name, GroupID, Inviter))

    def _reject(self, GroupID, Inviter):
        self.Yuuki_DynamicTools.sendText(
            GroupID,
            self.Yuuki.get_text("Sorry...\nThe number of members is not satisfied (%s needed)") %
            (self.Yuuki.YuukiConfigs["GroupMebers_Demand"],)
        )
        self.Yuuki_DynamicTools.getClient(self.Yuuki.MyMID).leaveGroup(self.Yuuki.Seq, GroupID)
        # Log
        self.Yuuki.data.updateLog(
            "JoinGroup", (self.Yuuki.data.getTime(), GroupID, "Not Join", Inviter))

    def _helper_check(self, ncMessage, GroupInvite, BlockedIgnore):
        if ncMessage.param1 in self.Yuuki.data.getData(["Global", "GroupJoined"]) and not BlockedIgnore:
            for userId in self.Yuuki.Connect.helper:
                if self.Yuuki_DynamicTools.checkInInvitationList(ncMessage, userId) or userId in GroupInvite:
                    self.Yuuki_DynamicTools.getClient(userId).acceptGroupInvitation(self.Yuuki.Seq, ncMessage.param1)
                    self.Yuuki_DynamicTools.getGroupTicket(ncMessage.param1, userId, True)
                    # Log
                    self.Yuuki.data.updateLog("JoinGroup", (
                        self.Yuuki.data.getTime(),
                        ncMessage.param1,
                        userId,
                        ncMessage.param2
                    ))

    def action(self, ncMessage):
        GroupInvite = []
        BlockedIgnore = ncMessage.param2 in self.Yuuki.data.getData(["BlackList"])
        if self.Yuuki_DynamicTools.checkInInvitationList(ncMessage) and not BlockedIgnore:
            GroupID = ncMessage.param1
            Inviter = ncMessage.param2
            GroupInfo = self.Yuuki_DynamicTools.getClient(
                self.Yuuki.MyMID).getGroup(GroupID)
            if GroupInfo.members:
                GroupMember = [Catched.mid for Catched in GroupInfo.members]
                GroupInfo.invitee = []
                if GroupInfo.invitee:
                    GroupInvite = [
                        Catched.mid for Catched in GroupInfo.invitee]
                self.Yuuki_DynamicTools.getClient(self.Yuuki.MyMID).acceptGroupInvitation(self.Yuuki.Seq, GroupID)
                if len(GroupMember) >= self.Yuuki.YuukiConfigs["GroupMebers_Demand"]:
                    self._accept(GroupID, GroupInfo, Inviter)
                else:
                    self._reject(GroupID, Inviter)
        self._helper_check(ncMessage, GroupInvite, BlockedIgnore)
        self.Yuuki.Security(ncMessage)
