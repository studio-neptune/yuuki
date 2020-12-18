# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from yuuki_core.ttypes import OpType

from ..tools import YuukiStaticTools, YuukiDynamicTools
from ..yuuki import Yuuki


def security_access_checker(function):
    def wrapper(*args):
        if not args[2].get("Security_Access"):
            return
        return function(*args)

    return wrapper


class YuukiSecurity:
    def __init__(self, handler: Yuuki):
        """
            Event Type:
                NOTIFIED_UPDATE_GROUP (11)
                NOTIFIED_INVITE_INTO_GROUP (13)
                NOTIFIED_ACCEPT_GROUP_INVITATION (17)
                NOTIFIED_KICKOUT_FROM_GROUP (19)
        """
        self.Yuuki = handler
        self.YuukiDynamicTools = YuukiDynamicTools(self.Yuuki)

    @security_access_checker
    def _notified_update_group(self, group, security_info, operation):
        if security_info["Another"] == '4':
            if not group.preventJoinByTicket and security_info["Action"] not in self.Yuuki.Connect.helper:
                self.Yuuki.thread_append(
                    self.YuukiDynamicTools.switch_group_url_status,
                    (group, False)
                )
                self.Yuuki.thread_append(
                    self.YuukiDynamicTools.send_text,
                    (security_info["GroupID"], self.Yuuki.get_text("DO NOT ENABLE THE GROUP URL STATUS, see you..."))
                )
                kicker = self.YuukiDynamicTools.modify_group_members(1, group, security_info["Action"])
                # Log
                self.Yuuki.data.update_log("KickEvent", (
                    self.Yuuki.data.get_time(),
                    group.name,
                    security_info["GroupID"],
                    kicker,
                    security_info["Action"],
                    security_info["Another"],
                    operation.type
                ))

    @security_access_checker
    def _notified_invite_into_group(self, group, security_info, operation):
        canceler = "None"
        if "\x1e" in security_info["Another"]:
            canceler = self._notified_invite_into_group_list(group, security_info, operation, canceler)
        elif security_info["Another"] not in self.Yuuki.AllAccountIds + security_info["GroupPrivilege"]:
            canceler = self._notified_invite_into_group_single(group, security_info, operation)
        if canceler != "None":
            self.YuukiDynamicTools.send_text(
                security_info["GroupID"],
                self.Yuuki.get_text("Do not invite anyone...thanks")
            )

    def _notified_invite_into_group_list(self, group, security_info, operation, canceler):
        for user_id in security_info["Another"].split("\x1e"):
            if user_id not in self.Yuuki.AllAccountIds + security_info["GroupPrivilege"]:
                if group.invitee and user_id in [user.mid for user in group.invitee]:
                    canceler = self.YuukiDynamicTools.modify_group_members(2, group, user_id)
                else:
                    canceler = self.YuukiDynamicTools.modify_group_members(1, group, user_id)
                    # Log
                    self.Yuuki.data.update_log("KickEvent", (
                        self.Yuuki.data.get_time(),
                        group.name,
                        security_info["GroupID"],
                        canceler,
                        security_info["Action"],
                        user_id,
                        operation.type * 10
                    ))
        # Log
        self.Yuuki.data.update_log("CancelEvent", (
            self.Yuuki.data.get_time(),
            group.name,
            security_info["GroupID"],
            canceler,
            security_info["Action"],
            security_info["Another"].replace("\x1e", ",")
        ))
        return canceler

    def _notified_invite_into_group_single(self, group, security_info, operation):
        if group.invitee and security_info["Another"] in [user.mid for user in group.invitee]:
            canceler = self.YuukiDynamicTools.modify_group_members(2, group, security_info["Another"])
        else:
            canceler = self.YuukiDynamicTools.modify_group_members(1, group, security_info["Another"])
            # Log
            self.Yuuki.data.update_log("KickEvent", (
                self.Yuuki.data.get_time(),
                group.name, security_info["GroupID"],
                canceler, security_info["Action"],
                security_info["Another"],
                operation.type * 10
            ))
        # Log
        self.Yuuki.data.update_log("CancelEvent", (
            self.Yuuki.data.get_time(),
            group.name,
            security_info["GroupID"],
            canceler,
            security_info["Action"],
            security_info["Another"]
        ))
        return canceler

    @security_access_checker
    def _notified_accept_group_invitation(self, group, security_info, operation):
        for user_id in self.Yuuki.data.get_data(["BlackList"]):
            if user_id == security_info["Action"]:
                self.Yuuki.thread_append(
                    self.YuukiDynamicTools.send_text,
                    (security_info["GroupID"], self.Yuuki.get_text("You are our blacklist. Bye~"))
                )
                kicker = self.YuukiDynamicTools.modify_group_members(1, group, security_info["Action"])
                # Log
                self.Yuuki.data.update_log("KickEvent", (
                    self.Yuuki.data.get_time(),
                    group.name,
                    security_info["GroupID"],
                    kicker,
                    kicker,
                    security_info["Action"],
                    operation.type
                ))

    def _notified_kickout_from_group(self, group, security_info, operation):
        if security_info["Action"] in self.Yuuki.Connect.helper:
            # Log
            self.Yuuki.data.update_log("KickEvent", (
                self.Yuuki.data.get_time(),
                group.name,
                security_info["GroupID"],
                security_info["Action"],
                security_info["Action"],
                security_info["Another"],
                operation.type * 10 + 1
            ))
        elif security_info["Another"] in self.Yuuki.AllAccountIds:
            kicker = "None"
            try:
                kicker = self.YuukiDynamicTools.modify_group_members(
                    1,
                    group,
                    security_info["Action"],
                    security_info["Another"]
                )
                self._notified_kickout_from_group_rescue(group, security_info, operation, kicker)
            except:
                self._notified_kickout_from_group_rescue_failure(group, security_info, operation, kicker)
            black_list = self.Yuuki.data.get_data(["BlackList"])
            if security_info["Action"] not in black_list:
                new_black_list = black_list.copy()
                new_black_list.append(security_info["Action"])
                self.Yuuki.data.update_data(["BlackList"], new_black_list)
                # Log
                self.Yuuki.data.update_log("BlackList", (
                    self.Yuuki.data.get_time(),
                    security_info["Action"],
                    security_info["GroupID"]
                ))
                self.Yuuki.thread_append(
                    self.YuukiDynamicTools.send_text,
                    (
                        security_info["Action"],
                        self.Yuuki.get_text("You had been blocked by our database.")
                    )
                )
        elif security_info["Security_Access"]:
            self._notified_kickout_from_group_normal(group, security_info, operation)

    def _notified_kickout_from_group_rescue(self, group, security_info, operation, kicker):
        # Log
        self.Yuuki.data.update_log("KickEvent", (
            self.Yuuki.data.get_time(),
            group.name,
            security_info["GroupID"],
            kicker,
            security_info["Action"],
            security_info["Another"],
            operation.type * 10 + 2
        ))
        assert kicker != "None", "No Helper Found"
        if group.preventJoinByTicket:
            self.Yuuki.thread_append(
                self.YuukiDynamicTools.switch_group_url_status,
                (group, True, kicker)
            )
        group_ticket = self.YuukiDynamicTools.get_group_ticket(
            security_info["GroupID"], kicker)
        try:
            self.YuukiDynamicTools.get_client(security_info["Another"]).acceptGroupInvitationByTicket(
                self.Yuuki.Seq,
                security_info["GroupID"],
                group_ticket
            )
        except:
            if group.preventJoinByTicket:
                self.YuukiDynamicTools.switch_group_url_status(
                    group,
                    True,
                    kicker
                )
            group_ticket = self.YuukiDynamicTools.get_group_ticket(
                security_info["GroupID"], kicker, True)
            self.YuukiDynamicTools.get_client(security_info["Another"]).acceptGroupInvitationByTicket(
                self.Yuuki.Seq,
                security_info["GroupID"],
                group_ticket
            )
        if group.preventJoinByTicket:
            self.Yuuki.thread_append(
                self.YuukiDynamicTools.switch_group_url_status, (group, False, security_info["Another"]))
        self.YuukiDynamicTools.get_group_ticket(
            security_info["GroupID"], security_info["Another"], True)

    def _notified_kickout_from_group_rescue_failure(self, group, security_info, operation, kicker):
        (err1, err2, err3, error_info) = YuukiStaticTools.report_error()
        for Root in self.Yuuki.Admin:
            self.YuukiDynamicTools.send_text(
                Root,
                "Star Yuuki BOT - SecurityService Failure\n\n%s\n%s\n%s\n\n%s" % (err1, err2, err3, error_info)
            )
        if security_info["Another"] == self.Yuuki.MyMID:
            group_list = self.Yuuki.data.get_data(["Global", "GroupJoined"])
            new_group_list = group_list.copy()
            new_group_list.remove(security_info["GroupID"])
            self.Yuuki.data.update_data(["Global", "GroupJoined"], new_group_list)
        # Log
        self.Yuuki.data.update_log("KickEvent", (
            self.Yuuki.data.get_time(),
            group.name,
            security_info["GroupID"],
            kicker,
            security_info["Action"],
            security_info["Another"],
            operation.type * 10 + 3
        ))

    def _notified_kickout_from_group_normal(self, group, security_info, operation):
        self.Yuuki.thread_append(self.YuukiDynamicTools.send_text, (
            security_info["GroupID"], self.Yuuki.get_text("DO NOT KICK, thank you ^^")))
        kicker = self.YuukiDynamicTools.modify_group_members(1, group, security_info["Action"])
        # Log
        self.Yuuki.data.update_log("KickEvent", (
            self.Yuuki.data.get_time(),
            group.name,
            security_info["GroupID"],
            kicker,
            security_info["Action"],
            security_info["Another"],
            operation.type
        ))
        self.Yuuki.thread_append(self.YuukiDynamicTools.send_text, (security_info["GroupID"], self.Yuuki.get_text(
            "The one who was been kicked:")))
        self.Yuuki.thread_append(
            self.YuukiDynamicTools.send_user, (security_info["GroupID"], security_info["Another"]))

    def action(self, operation):
        security_info = YuukiStaticTools.security_for_where(operation)

        group = self.YuukiDynamicTools.get_client(self.Yuuki.MyMID).getGroup(security_info["GroupID"])
        security_info["GroupPrivilege"] = [
            *self.Yuuki.Admin,
            YuukiStaticTools.get_group_creator(group).mid,
            *self.Yuuki.data.get_group(group.id)["Ext_Admin"]
        ]
        if security_info["Action"] in security_info["GroupPrivilege"] or \
                security_info["Another"] in security_info["GroupPrivilege"]:
            if operation.type != OpType.NOTIFIED_KICKOUT_FROM_GROUP:
                return
            elif security_info["Action"] in security_info["GroupPrivilege"]:
                return

        se_group = self.Yuuki.data.get_se_group(security_info["GroupID"])
        if se_group is None:
            security_info["Security_Access"] = self.Yuuki.data.get_data(["Global", "SecurityService"])
        elif se_group[operation.type]:
            security_info["Security_Access"] = se_group[operation.type]
        else:
            security_info["Security_Access"] = False

        if self.Yuuki.data.get_data(["Global", "SecurityService"]):
            {
                OpType.NOTIFIED_UPDATE_GROUP: self._notified_update_group,
                OpType.NOTIFIED_INVITE_INTO_GROUP: self._notified_invite_into_group,
                OpType.NOTIFIED_ACCEPT_GROUP_INVITATION: self._notified_accept_group_invitation,
                OpType.NOTIFIED_KICKOUT_FROM_GROUP: self._notified_kickout_from_group
            }[operation.type](group, security_info, operation)
