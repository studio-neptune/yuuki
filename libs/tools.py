# -*- coding: utf-8 -*-
"""
Yuuki_Libs
(c) 2020 Star Inc.
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

import os
import sys
import json
import ntpath
import random
import requests
import traceback

from yuuki_core.ttypes import OpType, MIDType, ContentType, Group, Message


class Yuuki_StaticTools:
    @staticmethod
    def sybGetGroupCreator(groupInfo):
        """
        Get the LINE Group Creator
        :param groupInfo: LINE Group
        :return: LINE Contact
        """
        if groupInfo.creator is None:
            contact = groupInfo.members[0]
        else:
            contact = groupInfo.creator
        return contact

    @staticmethod
    def readCommandLine(msgs):
        """
        Read string list as a command line
        :param msgs: List of strings
        :return: string
        """
        reply_msg = " ".join(msgs).lstrip()
        return reply_msg

    @staticmethod
    def errorReport():
        """
        Report errors as tuple
        :return: tuple
        """
        err1, err2, err3 = sys.exc_info()
        traceback.print_tb(err3)
        tb_info = traceback.extract_tb(err3)
        filename, line, func, text = tb_info[-1]
        ErrorInfo = "occurred in\n{}\n\non line {}\nin statement {}".format(filename, line, text)
        return err1, err2, err3, ErrorInfo

    @staticmethod
    def securityForWhere(ncMessage):
        """
        Return arguments for security tasks
        :param ncMessage: Operation
        :return: tuple
        """
        if ncMessage.type == OpType.NOTIFIED_UPDATE_GROUP:
            return ncMessage.param1, ncMessage.param2, ncMessage.param3
        elif ncMessage.type == OpType.NOTIFIED_INVITE_INTO_GROUP:
            return ncMessage.param1, ncMessage.param2, ncMessage.param3
        elif ncMessage.type == OpType.NOTIFIED_ACCEPT_GROUP_INVITATION:
            return ncMessage.param1, ncMessage.param2, ncMessage.param3
        elif ncMessage.type == OpType.NOTIFIED_KICKOUT_FROM_GROUP:
            return ncMessage.param1, ncMessage.param2, ncMessage.param3

    @staticmethod
    def dictShuffle(dict_object, requirement=None):
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
    def sendToWho(ncMessage):
        """
        Get who to send with Operation
        :param ncMessage: Operation
        :return: string
        """
        if ncMessage.message.toType == MIDType.USER:
            return ncMessage.message.from_
        elif ncMessage.message.toType == MIDType.ROOM:
            return ncMessage.message.to
        elif ncMessage.message.toType == MIDType.GROUP:
            return ncMessage.message.to


class Yuuki_DynamicTools:
    def __init__(self, Yuuki):
        self.Yuuki = Yuuki
        self.Yuuki_StaticTools = Yuuki_StaticTools()

    def getClient(self, userId):
        """
        Get client by account userId
        :param userId: string
        :return: TalkServiceClient
        """
        if self.Yuuki.Threading:
            if userId == self.Yuuki.MyMID:
                (client, _) = self.Yuuki.Connect.connect()
                return client
            else:
                return self.Yuuki.Connect.helperThreadConnect(userId)
        else:
            Accounts = [self.Yuuki.client] + self.Yuuki.Connect.helper
            for count, AccountUserId in enumerate(self.Yuuki.AllAccountIds):
                if AccountUserId == userId:
                    return Accounts[count]

    def checkInInvitationList(self, ncMessage, userId=None):
        """
        Check If userId in Invitation List
        :param ncMessage: Operation
        :param userId: string
        :return: boolean
        """
        if userId is None:
            userId = self.Yuuki.MyMID
        if ncMessage.param3 == userId:
            inList = True
        elif "\x1e" in ncMessage.param3:
            if userId in ncMessage.param3.split("\x1e"):
                inList = True
            else:
                inList = False
        else:
            inList = False
        return inList

    def changeGroupUrlStatus(self, groupInfo, status, userId=None):
        """
        Change LINE Group URL Status
        :param groupInfo: Line Group
        :param status: boolean
        :param userId: string
        :return: None
        """
        result = Group()
        for key in groupInfo.__dict__:
            if key != "members" or key != "invitee":
                result.__dict__[key] = groupInfo.__dict__[key]
        result.preventJoinByTicket = not status
        if userId is not None:
            self.getClient(userId).updateGroup(self.Yuuki.Seq, result)
        else:
            self.getClient(self.Yuuki.MyMID).updateGroup(self.Yuuki.Seq, result)

    def configSecurityStatus(self, groupId, status):
        """
        Configure LINE Group Security Status for Yuuki
        :param groupId: string
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

        self.Yuuki.data.updateData(["Group", groupId, "SEGroup"], group_status)

    def cleanMyGroupInvitations(self):
        """
        Clean personal group invitations for LINE account
        :return: None
        """
        for client in [self.getClient(self.Yuuki.MyMID)] + self.Yuuki.Connect.helper:
            for cleanInvitations in client.getGroupIdsInvited():
                client.acceptGroupInvitation(self.Yuuki.Seq, cleanInvitations)
                client.leaveGroup(self.Yuuki.Seq, cleanInvitations)

    def getContact(self, userId):
        """
        Get LINE Contact information with userId
        :param userId: string
        :return: LINE Contact
        """
        if len(userId) == len(self.Yuuki.MyMID) and userId[0] == "u":
            # noinspection PyBroadException
            try:
                contactInfo = self.getClient(self.Yuuki.MyMID).getContact(userId)
            except:
                contactInfo = False
        else:
            contactInfo = False
        return contactInfo

    def getGroupTicket(self, groupId, userId, renew=False):
        """
        Get LINE Group Ticket with groupId and userId
        :param groupId: string
        :param userId: string
        :param renew: boolean
        :return: string
        """
        GroupTicket = ""
        GroupData = self.Yuuki.data.getGroup(groupId)
        if "GroupTicket" in GroupData:
            if GroupData["GroupTicket"].get(userId) is not None:
                GroupTicket = GroupData["GroupTicket"].get(userId)
        else:
            assert "Error JSON data type - GroupTicket"
        if GroupTicket == "" or renew:
            GroupTicket = self.getClient(userId).reissueGroupTicket(groupId)
            self.Yuuki.data.updateData(
                ["Group", groupId, "GroupTicket", userId], GroupTicket)
        return GroupTicket

    def limitReset(self):
        """
        Reset Yuuki modify LINE Group Member List limits
        :return: None
        """
        for userId in self.Yuuki.AllAccountIds:
            self.Yuuki.data.updateData(
                ["LimitInfo", "KickLimit", userId], self.Yuuki.KickLimit)
            self.Yuuki.data.updateData(
                ["LimitInfo", "CancelLimit", userId], self.Yuuki.CancelLimit)

    def modifyGroupMemberList(self, action, groupInfo, userId, exceptUserId=None):
        """
        Modify LINE Group Member List
        :param action: integer (1->kick 2->cancel)
        :param groupInfo: LINE Group
        :param userId: string
        :param exceptUserId: List of userId
        :return: string
        """
        actions = {1: "KickLimit", 2: "CancelLimit"}
        assert action in actions, "Invalid action code"
        if len(self.Yuuki.Connect.helper) >= 1:
            members = [member.mid for member in groupInfo.members if member.mid in self.Yuuki.AllAccountIds]
            accounts = self.Yuuki_StaticTools.dictShuffle(
                self.Yuuki.data.getData(["LimitInfo", actions[action]]), members)
            if len(accounts) == 0:
                return "None"
            if exceptUserId:
                accounts[exceptUserId] = -1
            helper = max(accounts, key=accounts.get)
        else:
            if exceptUserId == self.Yuuki.MyMID:
                return "None"
            helper = self.Yuuki.MyMID

        actions_func = {
            1: self.getClient(helper).cancelGroupInvitation,
            2: self.getClient(helper).cancelGroupInvitation
        }
        Limit = self.Yuuki.data.getData(["LimitInfo", actions[action], helper])
        if Limit > 0:
            actions_func[action](self.Yuuki.Seq, groupInfo.id, [userId])
            self.Yuuki.data.limitDecrease(actions[action], helper)
        else:
            self.sendText(groupInfo.id, self.Yuuki.get_text("Cancel Limit."))
        return helper

    def sendText(self, send_to, msg):
        """
        Send text to LINE Chat
        :param send_to: string
        :param msg: string
        :return: None
        """
        message = Message(to=send_to, text=msg)
        self.getClient(self.Yuuki.MyMID).sendMessage(self.Yuuki.Seq, message)

    def sendUser(self, send_to, userId):
        """
        Send LINE contact to LINE Chat
        :param send_to: string
        :param userId: string
        :return: None
        """
        message = Message(
            contentType=ContentType.CONTACT,
            text='',
            contentMetadata={
                'mid': userId,
                'displayName': 'LINE User',
            },
            to=send_to
        )
        self.getClient(self.Yuuki.MyMID).sendMessage(self.Yuuki.Seq, message)

    def sendMedia(self, send_to, send_type, path):
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
            message_id = self.getClient(self.Yuuki.MyMID).sendMessage(
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
            r = requests.post(
                url, headers=self.Yuuki.connectHeader, data=data, files=files)
            if r.status_code != 201:
                self.sendText(send_to, "Error!")
