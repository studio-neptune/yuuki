# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from ..tools import YuukiStaticTools, YuukiDynamicTools

from ..yuuki import Yuuki


class YuukiJoinGroup:
    def __init__(self, handler: Yuuki):
        """
            Event Type:
                NOTIFIED_INVITE_INTO_GROUP (13)
        """
        self.Yuuki = handler
        self.YuukiDynamicTools = YuukiDynamicTools(self.Yuuki)

    def _accept(self, group_id, group, inviter):
        group_list = self.Yuuki.data.get_data(["Global", "GroupJoined"])
        new_group_list = group_list.copy()
        new_group_list.append(group_id)
        self.Yuuki.data.update_data(
            ["Global", "GroupJoined"], new_group_list)
        self.YuukiDynamicTools.send_text(
            group_id,
            self.Yuuki.get_text("Helllo^^\nMy name is %s ><\nNice to meet you OwO") %
            (self.Yuuki.configs["name"],)
        )
        self.YuukiDynamicTools.send_text(
            group_id,
            self.Yuuki.get_text("Type:\n\t%s/Help\nto get more information\n\nMain Admin of the Group:\n%s") %
            (
                self.Yuuki.configs["name"],
                YuukiStaticTools.get_group_creator(group).displayName,
            )
        )
        self.YuukiDynamicTools.get_group_ticket(group_id, self.Yuuki.MyMID, True)
        # Log
        self.Yuuki.data.update_log(
            "JoinGroup", (self.Yuuki.data.get_time(), group.name, group_id, inviter))

    def _reject(self, group_id, inviter):
        self.YuukiDynamicTools.send_text(
            group_id,
            self.Yuuki.get_text("Sorry...\nThe number of members is not satisfied (%s needed)") %
            (self.Yuuki.configs["GroupMembers_Demand"],)
        )
        self.YuukiDynamicTools.get_client(self.Yuuki.MyMID).leave_group(self.Yuuki.Seq, group_id)
        # Log
        self.Yuuki.data.update_log(
            "JoinGroup", (self.Yuuki.data.get_time(), group_id, "Not Join", inviter))

    def _check_helper(self, operation, group_invitations, blocked_user):
        if operation.param1 in self.Yuuki.data.get_data(["Global", "GroupJoined"]) and not blocked_user:
            for user_id in self.Yuuki.Connect.helper:
                if self.YuukiDynamicTools.check_invitation(operation, user_id) or user_id in group_invitations:
                    self.YuukiDynamicTools.get_client(user_id).acceptGroupInvitation(self.Yuuki.Seq, operation.param1)
                    self.YuukiDynamicTools.get_group_ticket(operation.param1, user_id, True)
                    # Log
                    self.Yuuki.data.update_log("JoinGroup", (
                        self.Yuuki.data.get_time(),
                        operation.param1,
                        user_id,
                        operation.param2
                    ))

    def action(self, operation):
        group_invitations = []
        blocked_user = operation.param2 in self.Yuuki.data.get_data(["BlackList"])
        if self.YuukiDynamicTools.check_invitation(operation) and not blocked_user:
            group_id = operation.param1
            inviter = operation.param2
            group = self.YuukiDynamicTools.get_client(
                self.Yuuki.MyMID).getGroup(group_id)
            group_member = [user.mid for user in group.members] if group.members else []
            group_invitations = [user.mid for user in group.invitee] if group.invitee else []
            self.YuukiDynamicTools.get_client(self.Yuuki.MyMID).acceptGroupInvitation(self.Yuuki.Seq, group_id)
            if len(group_member) >= self.Yuuki.configs["GroupMembers_Demand"]:
                self._accept(group_id, group, inviter)
            else:
                self._reject(group_id, inviter)
        self._check_helper(operation, group_invitations, blocked_user)
        self.Yuuki.Security(operation)
