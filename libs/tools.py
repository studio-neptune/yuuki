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
    def sybGetGroupCreator(group):
        if group.creator is None:
            contact = group.members[0]
        else:
            contact = group.creator
        return contact

    @staticmethod
    def readCommandLine(msgs):
        replymsg = ""
        for msg in msgs:
            replymsg = replymsg + " " + msg
        return replymsg

    @staticmethod
    def errorReport():
        err1, err2, err3 = sys.exc_info()
        traceback.print_tb(err3)
        tb_info = traceback.extract_tb(err3)
        filename, line, func, text = tb_info[-1]
        ErrorInfo = "occurred in\n{}\n\non line {}\nin statement {}".format(
            filename, line, text)
        return err1, err2, err3, ErrorInfo

    @staticmethod
    def securityForWhere(ncMessage):
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

    def changeGroupUrlStatus(self, group, status, userId=None):
        result = Group()
        for key in group.__dict__:
            if key != "members" or key != "invitee":
                result.__dict__[key] = group.__dict__[key]
        if status:
            result.preventJoinByTicket = False
        else:
            result.preventJoinByTicket = True
        if userId is not None:
            self.getClient(userId).updateGroup(self.Yuuki.Seq, result)
        else:
            self.getClient(self.Yuuki.MyMID).updateGroup(
                self.Yuuki.Seq, result)

    def configSecurityStatus(self, groupId, status):
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
        for client in [self.getClient(self.Yuuki.MyMID)] + self.Yuuki.Connect.helper:
            for cleanInvitations in client.getGroupIdsInvited():
                client.acceptGroupInvitation(self.Yuuki.Seq, cleanInvitations)
                client.leaveGroup(self.Yuuki.Seq, cleanInvitations)

    def getContact(self, userId):
        if len(userId) == len(self.Yuuki.MyMID) and userId[0] == "u":
            try:
                contactInfo = self.getClient(
                    self.Yuuki.MyMID).getContact(userId)
            except:
                contactInfo = False
        else:
            contactInfo = False
        return contactInfo

    def getGroupTicket(self, GroupID, userId, renew=False):
        GroupTicket = ""
        GroupData = self.Yuuki.data.getGroup(GroupID)
        if "GroupTicket" in GroupData:
            if GroupData["GroupTicket"].get(userId) is not None:
                GroupTicket = GroupData["GroupTicket"].get(userId)
        else:
            assert "Error JSON data type - GroupTicket"
        if GroupTicket == "" or renew:
            GroupTicket = self.getClient(userId).reissueGroupTicket(GroupID)
            self.Yuuki.data.updateData(
                ["Group", GroupID, "GroupTicket", userId], GroupTicket)
        return GroupTicket

    def limitReset(self):
        for userId in self.Yuuki.AllAccountIds:
            self.Yuuki.data.updateData(
                ["LimitInfo", "KickLimit", userId], self.Yuuki.KickLimit)
            self.Yuuki.data.updateData(
                ["LimitInfo", "CancelLimit", userId], self.Yuuki.CancelLimit)

    def cancelSomeone(self, groupInfo, userId, exceptUserId=None):
        if len(self.Yuuki.Connect.helper) >= 1:
            members = [
                member.mid for member in groupInfo.members if member.mid in self.Yuuki.AllAccountIds]
            accounts = self.Yuuki_StaticTools.dictShuffle(
                self.Yuuki.data.getData(["LimitInfo", "CancelLimit"]), members)
            if len(accounts) == 0:
                return "None"
            if exceptUserId:
                accounts[exceptUserId] = -1
            helper = max(accounts, key=accounts.get)
        else:
            if exceptUserId == self.Yuuki.MyMID:
                return "None"
            helper = self.Yuuki.MyMID

        Limit = self.Yuuki.data.getData(["LimitInfo", "CancelLimit", helper])
        if Limit > 0:
            self.getClient(helper).cancelGroupInvitation(
                self.Yuuki.Seq, groupInfo.id, [userId])
            self.Yuuki.data.limitDecrease("CancelLimit", helper)
        else:
            self.sendText(groupInfo.id, self.Yuuki.get_text("Cancel Limit."))
        return helper

    def kickSomeone(self, groupInfo, userId, exceptUserId=None):
        if len(self.Yuuki.Connect.helper) >= 1:
            members = [
                member.mid for member in groupInfo.members if member.mid in self.Yuuki.AllAccountIds]
            accounts = self.Yuuki_StaticTools.dictShuffle(
                self.Yuuki.data.getData(["LimitInfo", "KickLimit"]), members)
            if len(accounts) == 0:
                return "None"
            if exceptUserId:
                accounts[exceptUserId] = -1
            helper = max(accounts, key=accounts.get)
        else:
            if exceptUserId == self.Yuuki.MyMID:
                return "None"
            helper = self.Yuuki.MyMID

        Limit = self.Yuuki.data.getData(["LimitInfo", "KickLimit", helper])
        if Limit > 0:
            self.getClient(helper).kickoutFromGroup(
                self.Yuuki.Seq, groupInfo.id, [userId])
            self.Yuuki.data.limitDecrease("KickLimit", helper)
        else:
            self.sendText(groupInfo.id, self.Yuuki.get_text("Kick Limit."))
        return helper

    def sendText(self, toid, msg):
        message = Message(to=toid, text=msg)
        self.getClient(self.Yuuki.MyMID).sendMessage(self.Yuuki.Seq, message)

    def sendUser(self, toid, userId):
        message = Message(
            contentType=ContentType.CONTACT,
            text='',
            contentMetadata={
                'mid': userId,
                'displayName': 'LINE User',
            },
            to=toid
        )
        self.getClient(self.Yuuki.MyMID).sendMessage(self.Yuuki.Seq, message)

    def sendMedia(self, send_to, send_type, path):
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
