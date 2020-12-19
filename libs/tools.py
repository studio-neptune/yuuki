# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import json
import ntpath
import os
import random
import sys
import traceback

import requests
from .yuuki import Yuuki
from yuuki_core.ttypes import OpType, MIDType, ContentType, Group, Message


class YuukiStaticTools:
    @staticmethod
    def get_group_creator(group):
        """
        Get the LINE Group Creator
        :param group: LINE Group
        :return: LINE Contact
        """
        if group.creator is None:
            contact = group.members[0]
        else:
            contact = group.creator
        return contact

    @staticmethod
    def read_commands(list_):
        """
        Read string list as a command line
        :param list_: List of strings
        :return: string
        """
        reply_msg = " ".join(list_).lstrip()
        return reply_msg

    @staticmethod
    def report_error():
        """
        reporting_message errors as tuple
        :return: tuple
        """
        err1, err2, err3 = sys.exc_info()
        traceback.print_tb(err3)
        tb_info = traceback.extract_tb(err3)
        filename, line, func, text = tb_info[-1]
        error_info = f"occurred in\n{filename}\n\non line {line}\nin statement {text}"
        return err1, err2, err3, error_info

    @staticmethod
    def security_for_where(operation):
        """
        Return arguments for security tasks
        :param operation: Operation
        :return: tuple
        """
        if operation.type == OpType.NOTIFIED_UPDATE_GROUP or \
                operation.type == OpType.NOTIFIED_INVITE_INTO_GROUP or \
                operation.type == OpType.NOTIFIED_ACCEPT_GROUP_INVITATION or \
                operation.type == OpType.NOTIFIED_KICKOUT_FROM_GROUP:
            return {
                "GroupID": operation.param1,
                "Action": operation.param2,
                "Another": operation.param3,
            }

    @staticmethod
    def dict_shuffle(dict_object, requirement=None):
        """
        Shuffle dicts
        :param dict_object: dict
        :param requirement: list
        :return: dict
        """
        dict_key = [key for key in dict_object]
        random.shuffle(dict_key)
        result = {}
        for key in dict_key:
            if requirement is None:
                result[key] = dict_object[key]
            else:
                if key in requirement:
                    result[key] = dict_object[key]
        return result

    @staticmethod
    def send_to_who(operation):
        """
        Get who to send with Operation
        :param operation: Operation
        :return: string
        """
        if operation.message.toType == MIDType.USER:
            return operation.message.from_
        elif operation.message.toType == MIDType.ROOM:
            return operation.message.to
        elif operation.message.toType == MIDType.GROUP:
            return operation.message.to


class YuukiDynamicTools:
    def __init__(self, handler: Yuuki):
        self.Yuuki = handler

    def get_client(self, user_id):
        """
        Get client by account user_id
        :param user_id: string
        :return: TalkServiceClient
        """
        if user_id == self.Yuuki.MyMID:
            return self.Yuuki.client
        return self.Yuuki.Connect.helper[user_id].get("client")

    def check_invitation(self, operation, user_id=None):
        """
        Check If user_id in Invitation List
        :param operation: Operation
        :param user_id: string
        :return: boolean
        """
        if user_id is None:
            user_id = self.Yuuki.MyMID
        if operation.param3 == user_id:
            return True
        elif "\x1e" in operation.param3:
            if user_id in operation.param3.split("\x1e"):
                return True
        return False

    def switch_group_url_status(self, group, status, handler_id=None):
        """
        Change LINE Group URL Status
        :param group: Line Group
        :param status: boolean
        :param handler_id: string
        :return: None
        """
        result = Group()
        for key in group.__dict__:
            if key != "members" or key != "invitee":
                result.__dict__[key] = group.__dict__[key]
        result.preventJoinByTicket = not status
        handler = self.Yuuki.MyMID if handler_id is None else handler_id
        self.get_client(handler).updateGroup(self.Yuuki.Seq, result)

    def config_security_status(self, group_id, status):
        """
        Configure LINE Group Security Status for Yuuki
        :param group_id: string
        :param status: boolean
        :return: None
        """
        group_status = self.Yuuki.data.SEGrouptype
        if 0 in status:
            group_status[OpType.NOTIFIED_UPDATE_GROUP] = True
        if 1 in status:
            group_status[OpType.NOTIFIED_INVITE_INTO_GROUP] = True
        if 2 in status:
            group_status[OpType.NOTIFIED_ACCEPT_GROUP_INVITATION] = True
        if 3 in status:
            group_status[OpType.NOTIFIED_KICKOUT_FROM_GROUP] = True

        self.Yuuki.data.update_data(["Group", group_id, "SEGroup"], group_status)

    def clean_my_group_invitations(self):
        """
        Clean personal group invitations for LINE account
        :return: None
        """
        for client in [self.get_client(user_id) for user_id in self.Yuuki.MyMID + self.Yuuki.Connect.helper.keys()]:
            for cleanInvitations in client.getGroupIdsInvited():
                client.acceptGroupInvitation(self.Yuuki.Seq, cleanInvitations)
                client.leave_group(self.Yuuki.Seq, cleanInvitations)

    def leave_group(self, group):
        """
        Leave a group by its group information object
        :param group: Line Group
        :return: None
        """
        self.send_text(group.id, self.Yuuki.get_text("Bye Bye"))
        self.get_client(self.Yuuki.MyMID).leave_group(self.Yuuki.Seq, group.id)
        for user_id in self.Yuuki.Connect.helper:
            if user_id in [member.mid for member in group.members]:
                self.get_client(user_id).leave_group(self.Yuuki.Seq, group.id)
        group_list = self.Yuuki.data.get_data(["Global", "GroupJoined"])
        new_group_list = group_list.copy()
        new_group_list.remove(group.id)
        self.Yuuki.data.update_data(["Global", "GroupJoined"], new_group_list)

    def get_contact(self, user_id):
        """
        Get LINE Contact information with user_id
        :param user_id: string
        :return: LINE Contact
        """
        if len(user_id) == len(self.Yuuki.MyMID) and user_id.startswith("u"):
            # noinspection PyBroadException
            try:
                return self.get_client(self.Yuuki.MyMID).getContact(user_id)
            except:
                return False
        return False

    def get_group_ticket(self, group_id, user_id, renew=False):
        """
        Get LINE Group Ticket with group_id and user_id
        :param group_id: string
        :param user_id: string
        :param renew: boolean
        :return: string
        """
        group_ticket = ""
        group = self.Yuuki.data.get_group(group_id)
        if "GroupTicket" in group:
            if group["GroupTicket"].get(user_id) is not None:
                group_ticket = group["GroupTicket"].get(user_id)
        else:
            assert "Error JSON data type - GroupTicket"
        if group_ticket == "" or renew:
            group_ticket = self.get_client(user_id).reissuegroup_ticket(group_id)
            self.Yuuki.data.update_data(["Group", group_id, "GroupTicket", user_id], group_ticket)
        return group_ticket

    def reset_limit(self):
        """
        Reset Yuuki modify LINE Group Member List limits
        :return: None
        """
        for user_id in self.Yuuki.AllAccountIds:
            self.Yuuki.data.update_data(
                ["LimitInfo", "KickLimit", user_id], self.Yuuki.KickLimit)
            self.Yuuki.data.update_data(
                ["LimitInfo", "CancelLimit", user_id], self.Yuuki.CancelLimit)

    def modify_group_members(self, action, group, user_id, except_user_id=None):
        """
        Modify LINE Group Member List
        :param action: integer (1->kick 2->cancel)
        :param group: LINE Group
        :param user_id: string
        :param except_user_id: List of user_id
        :return: string
        """
        actions = {
            1: {
                "command": "KickLimit",
                "message": "Kick Limit.",
                "function": lambda handler_id: self.get_client(handler_id).kickoutFromGroup
            },
            2: {
                "command": "CancelLimit",
                "message": "Cancel Limit.",
                "function": lambda handler_id: self.get_client(handler_id).cancelGroupInvitation
            }
        }
        assert action in actions, "Invalid action code"
        if len(self.Yuuki.Connect.helper) >= 1:
            members = [member.mid for member in group.members if member.mid in self.Yuuki.AllAccountIds]
            accounts = YuukiStaticTools.dict_shuffle(
                self.Yuuki.data.get_data(["LimitInfo", actions[action].get("command")]), members)
            if len(accounts) == 0:
                return "None"
            if except_user_id:
                accounts[except_user_id] = -1
            helper = max(accounts, key=accounts.get)
        else:
            if except_user_id == self.Yuuki.MyMID:
                return "None"
            helper = self.Yuuki.MyMID
        limit = self.Yuuki.data.get_data(["LimitInfo", actions[action].get("command"), helper])
        if limit > 0:
            actions[action].get("function")(helper)(self.Yuuki.Seq, group.id, [user_id])
            self.Yuuki.data.trigger_limit(actions[action].get("command"), helper)
        else:
            self.send_text(group.id, self.Yuuki.get_text(actions[action].get("message")), helper)
        return helper

    def send_text(self, send_to, msg, sender_id=None):
        """
        Send text to LINE Chat
        :param send_to: The target to received
        :param msg: The message hope to send
        :param sender_id: The client specified to send the message
        :return: None
        """
        message = Message(to=send_to, text=msg)
        sender = self.Yuuki.MyMID if sender_id is None else sender_id
        self.get_client(sender).sendMessage(self.Yuuki.Seq, message)

    def send_user(self, send_to, user_id):
        """
        Send LINE contact to LINE Chat
        :param send_to: string
        :param user_id: string
        :return: None
        """
        message = Message(
            contentType=ContentType.CONTACT,
            text='',
            contentMetadata={
                'mid': user_id,
                'displayName': 'LINE User',
            },
            to=send_to
        )
        self.get_client(self.Yuuki.MyMID).sendMessage(self.Yuuki.Seq, message)

    def send_media(self, send_to, send_type, path):
        """
        Send media file to LINE Chat
        :param send_to: string
        :param send_type: string
        :param path: string
        :return: None
        """
        if os.path.exists(path):
            file_name = ntpath.basename(path)
            file_size = len(open(path, 'rb').read())
            message = Message(to=send_to, text=None)
            message.contentType = send_type
            message.contentPreview = None
            message.contentMetadata = {
                'FILE_NAME': str(file_name),
                'FILE_SIZE': str(file_size),
            }
            if send_type == ContentType.FILE:
                media_name = file_name
            else:
                media_name = 'media'
            message_id = self.get_client(self.Yuuki.MyMID).sendMessage(
                self.Yuuki.Seq, message).id
            files = {
                'file': open(path, 'rb'),
            }
            params = {
                'name': media_name,
                'oid': message_id,
                'size': file_size,
                'type': ContentType._VALUES_TO_NAMES[send_type].lower(),
                'ver': '1.0',
            }
            data = {
                'params': json.dumps(params)
            }
            url = self.Yuuki.LINE_Media_server + '/talk/m/upload.nhn'
            r = requests.post(url, headers=self.Yuuki.Connect.con_header, data=data, files=files)
            if r.status_code != 201:
                self.send_text(send_to, "Error!")
