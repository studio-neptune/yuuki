#!/usr/bin/python3
# coding=UTF-8

import os, time,  \
       requests,   \
       json, ntpath,\
       random, traceback


from .core.TalkService import *
from .connection import Yuuki_Connect

from .data import Yuuki_Data

from .i18n import Yuuki_LangSetting

class Yuuki_Settings:
    """ Yuuki Custom Settings """

    config = {
        "Seq": 0,
        "Admin": [],
        "Hour_KickLimit": 10,
        "Hour_CancelLimit": 10,
        "Default_Language": "en",
        "GroupMebers_Demand": 100,
        "helper_LINE_ACCESS_KEYs": []
    }

class Yuuki:
    def __init__(self, Yuuki_Settings, Yuuki_Connection):
        self.YuukiConfigs = Yuuki_Settings.config

        self.Seq = self.YuukiConfigs["Seq"]
        self.Admin = self.YuukiConfigs["Admin"]

        self.KickLimit = self.YuukiConfigs["Hour_KickLimit"]
        self.CancelLimit = self.YuukiConfigs["Hour_CancelLimit"]

        self.data = Yuuki_Data()
        self.i18n = Yuuki_LangSetting(self.YuukiConfigs["Default_Language"])

        self.LINE_Media_server = "https://obs.line-apps.com"

        self.Connect = Yuuki_Connect(Yuuki_Connection)

        (self.client, self.listen) = self.Connect.connect()
        self.connectHeader = Yuuki_Connection.connectHeader

        for access in self.YuukiConfigs["helper_LINE_ACCESS_KEYs"]:
            self.Connect.helperConnect(access)


        for client in [self.client] + self.Connect.helper:
            if len(self.data.getData("LimitInfo")) != 2:
                self.data.updateData(self.data.getData("LimitInfo")["KickLimit"], client, self.KickLimit)
                self.data.updateData(self.data.getData("LimitInfo")["CancelLimit"], client, self.CancelLimit)

        self.MyMID = self.client.getProfile().mid

        global _
        _ = self.i18n._

    # Basic Func

    def exit(self, restart=False):
        if restart:
            with open(".cache.sh", "w") as c:
                c.write(sys.executable + " ./main.py")
            os.system("sh .cache.sh")
            os.system("rm .cache.sh")
            sys.exit(0)
        else:
            sys.exit(0)

    def sybGetGroupCreator(self, group):
        if group.creator == None:
            contact = group.members[0]
        else:
            contact = group.creator
        return contact

    def readCommandLine(self, msgs):
        replymsg = ""
        for msg in msgs:
            replymsg = replymsg + " " + msg
        return replymsg

    def checkInInvitationList(self, ncMessage, userId=None):
        if userId == None:
            userId = self.MyMID
        if ncMessage.param3 == userId:
            inList = True
        elif "\x1e" in ncMessage.param3:
            if self.MyMID in ncMessage.param3.split("\x1e"):
                inList = True
            else:
                inList = False
        else:
            inList = False
        return inList

    def changeGroupUrlStatus(self, group, stat):
        if stat == True:
            us = False
        else:
            us = True
        group.members, group.invitee = None, None
        group.preventJoinByTicket = us
        self.client.updateGroup(self.Seq, group)

    def enableSecurityStatus(self, groupId, status):
        group_status = self.data.SEGrouptype
        if 0 in status:
            group_status[OpType.NOTIFIED_UPDATE_GROUP] = True
        if 1 in status:
            group_status[OpType.NOTIFIED_INVITE_INTO_GROUP] = True
        if 2 in status:
            group_status[OpType.NOTIFIED_ACCEPT_GROUP_INVITATION] = True
        if 3 in status:
            group_status[OpType.NOTIFIED_KICKOUT_FROM_GROUP] = True

        self.data.updateData(self.data.getGroup(groupId), "SEGroup", group_status)

    def disableSecurityStatus(self, groupId, status):
        group_status = self.data.SEGrouptype
        if 0 in status:
            group_status[OpType.NOTIFIED_UPDATE_GROUP] = False
        if 1 in status:
            group_status[OpType.NOTIFIED_INVITE_INTO_GROUP] = False
        if 2 in status:
            group_status[OpType.NOTIFIED_ACCEPT_GROUP_INVITATION] = False
        if 3 in status:
            group_status[OpType.NOTIFIED_KICKOUT_FROM_GROUP] = False

        self.data.updateData(self.data.getGroup(groupId), "SEGroup", group_status)

    def cleanMyGroupInvitations(self):
        for cleanInvitations in self.client.getGroupIdsInvited():
            self.client.acceptGroupInvitation(self.Seq, cleanInvitations)
            self.client.leaveGroup(self.Seq, cleanInvitations)

    def getContact(self, userId):
        if len(userId) == len(self.userId) and userId[0] == "u":
            try:
                contactInfo = self.getContact(userId)
            except:
                contactInfo = False
        else:
            contactInfo = False
        return contactInfo

    def securityForWhere(self, Message):
        if Message.type == OpType.NOTIFIED_UPDATE_GROUP:
            return Message.param1
        elif Message.type == OpType.NOTIFIED_INVITE_INTO_GROUP:
            return Message.param1
        elif Message.type == OpType.NOTIFIED_ACCEPT_GROUP_INVITATION:
            return Message.param1
        elif Message.type == OpType.KICKOUT_FROM_GROUP:
            return Message.param1
        elif Message.type == OpType.NOTIFIED_KICKOUT_FROM_GROUP:
            return Message.param1

    def getClientByMid(self, userId):
        Accounts = [self.client] + self.Connect.helper
        for count, AccountUserId in enumerate([self.MyMID] + self.Connect.helper_ids):
            if AccountUserId == userId:
                return Accounts[count]

    def limitReset(self):
        for client in [self.client] + self.Connect.helper:
            if len(self.data.getData("LimitInfo")) != 2:
                self.data.updateData(self.data.getData("LimitInfo")["KickLimit"], client, self.KickLimit)
                self.data.updateData(self.data.getData("LimitInfo")["CancelLimit"], client, self.CancelLimit)

    def cancelSomeone(self, groupId, userId, exceptAccount=None):
        if len(self.Connect.helper) >= 1:
            accounts = self.data.getData("LimitInfo")["CancelLimit"]
            if exceptAccount:
                accounts[exceptAccount] = -1
            helper = max(accounts, key=accounts.get)
        else:
            helper = self.client

        if self.data.getData("LimitInfo")["CancelLimit"][helper] > 0:
            helper.cancelGroupInvitation(self.Seq, groupId, [userId])
            self.data.getData("LimitInfo")["CancelLimit"][helper] -= 1
            self.data.syncData()
        else:
            self.sendText(groupId, _("Cancel Limit."))

    def kickSomeone(self, groupId, userId, exceptAccount=None):
        if len(self.Connect.helper) >= 1:
            accounts = self.data.getData("LimitInfo")["KickLimit"]
            if exceptAccount:
                accounts[exceptAccount] = -1
            helper = max(accounts, key=accounts.get)
        else:
            helper = self.client

        if self.data.getData("LimitInfo")["KickLimit"][helper] > 0:
            helper.kickoutFromGroup(self.Seq, groupId, [userId])
            self.data.getData("LimitInfo")["KickLimit"][helper] -= 1
            self.data.syncData()
        else:
            self.sendText(groupId, _("Kick Limit."))

    def sendToWho(self, Message):
        if Message.message.toType == MIDType.USER:
            return Message.message.from_
        elif Message.message.toType == MIDType.ROOM:
            return Message.message.to
        elif Message.message.toType == MIDType.GROUP:
            return Message.message.to

    def sendText(self, toid, msg):
        message = Message(to=toid, text=msg)
        self.client.sendMessage(self.Seq, message)

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
        self.client.sendMessage(self.Seq, message)

    def sendMedia(self, toid, type, path):
        if os.path.exists(path):
            file_name = ntpath.basename(path)
            file_size = len(open(path, 'rb').read())
            message = Message(to=toid, text=None)
            message.contentType = type
            message.contentPreview = None
            message.contentMetadata = {
                'FILE_NAME': str(file_name),
                'FILE_SIZE': str(file_size),
            }
            if type == ContentType.FILE:
                media_name = file_name
            else:
                media_name = 'media'
            message_id = self.client.sendMessage(self.Seq, message).id
            files = {
                'file': open(path, 'rb'),
            }
            params = {
                'name': media_name,
                'oid': message_id,
                'size': file_size,
                'type': ContentType._VALUES_TO_NAMES[type].lower(),
                'ver': '1.0',
            }
            data = {
                'params': json.dumps(params)
            }
            url = self.LINE_Media_server + '/talk/m/upload.nhn'
            r = requests.post(url, headers=self.connectHeader, data=data, files=files)
            if r.status_code != 201:
                self.sendText(toid, "Error!")

    # Task

    def JoinGroup(self, ncMessage):
        """
            ToDo Type:
                NOTIFIED_INVITE_INTO_GROUP (13)
        """
        if self.checkInInvitationList(ncMessage):
            GroupID = ncMessage.param1
            Inviter = ncMessage.param2
            GroupInfo = self.client.getGroup(GroupID)
            GroupMember = [Catched.mid for Catched in GroupInfo.members]
            if GroupInfo.members:
                self.client.acceptGroupInvitation(self.Seq, GroupID)
                if len(GroupMember) >= self.YuukiConfigs["GroupMebers_Demand"]:
                    self.data.updateLog("JoinGroup", (self.data.getTime(), GroupInfo.name, GroupID, Inviter))
                    self.sendText(GroupID, _("Helllo^^\nMy name is Yuuki ><\nNice to meet you OwO"))
                    self.sendText(GroupID, _("Admin of the Group：\n%s") %
                                  (self.sybGetGroupCreator(GroupInfo).displayName,))
                    # Log
                else:
                    self.sendText(GroupID, _("Sorry...\nThe number of members is not satisfied (%s needed)") %
                                  (self.YuukiConfigs["GroupMebers_Demand"],))
                    self.client.leaveGroup(self.Seq, GroupID)
                    # Log
        for userId in self.Connect.helper_ids:
            if self.checkInInvitationList(ncMessage, userId):
                self.getClientByMid(userId).acceptGroupInvitation(self.Seq, GroupID)
                # Log
        self.Security(ncMessage)

    def Commands(self, ncMessage):
        """
            ToDo Type:
                RECEIVE_MESSAGE (26)
        """
        if 'BOT_CHECK' in ncMessage.message.contentMetadata:
            pass
        elif ncMessage.message.toType == MIDType.ROOM:
            self.client.leaveRoom(self.Seq, ncMessage.message.to)
        elif ncMessage.message.contentType == ContentType.NONE:
            msgSep = ncMessage.message.text.split(" ")
            if 'Yuuki/UserID' == ncMessage.message.text:
                self.sendText(self.sendToWho(ncMessage), _("LINE System UserID：\n") + ncMessage.message.from_)
            elif 'Yuuki/Speed' == ncMessage.message.text:
                Time1 = time.time()
                self.sendText(self.sendToWho(ncMessage), _("Testing..."))
                Time2 = time.time()
                self.sendText(self.sendToWho(ncMessage), _("Speed:\n%ss") % (Time2 - Time1,))
            elif 'Yuuki/Enable' == msgSep[0]:
                if ncMessage.message.toType == MIDType.GROUP:
                    status = []
                    for code in msgSep:
                        try:
                            status.append(int(code))
                        except:
                            pass
                    self.enableSecurityStatus(ncMessage.message.to, status)
                    self.sendText(ncMessage.message.to, _("Okay"))
            elif 'Yuuki/Disable' == msgSep[0]:
                if ncMessage.message.toType == MIDType.GROUP:
                    status = []
                    for code in msgSep:
                        try:
                            status.append(int(code))
                        except:
                            pass
                    self.disableSecurityStatus(ncMessage.message.to, status)
                    self.sendText(ncMessage.message.to, _("Okay"))
            elif 'Yuuki/Status' == ncMessage.message.text:
                if ncMessage.message.toType == MIDType.GROUP:
                    group_status = self.data.getSEGroup(ncMessage.message.to)
                    if group_status == None:
                        status = _("Disable without Initialize")
                    else:
                        status = _("URL:%s\nJoin:%s\nInvite:%s\nMembers:%s") % (
                            group_status[OpType.NOTIFIED_UPDATE_GROUP],
                            group_status[OpType.NOTIFIED_INVITE_INTO_GROUP],
                            group_status[OpType.NOTIFIED_ACCEPT_GROUP_INVITATION],
                            group_status[OpType.NOTIFIED_KICKOUT_FROM_GROUP],
                        )
                    self.sendText(self.sendToWho(ncMessage), status)
            elif 'Yuuki/Quit' == ncMessage.message.text:
                if ncMessage.message.toType == MIDType.GROUP:
                    self.sendText(ncMessage.message.to, _("Bye Bye"))
                    self.client.leaveGroup(self.Seq, ncMessage.message.to)
            elif 'Yuuki/Exit' == ncMessage.message.text:
                self.sendText(self.sendToWho(ncMessage), _("Exit."))
                self.exit()
            elif 'Yuuki/Com' == msgSep[0] and len(msgSep) != 1:
                if ncMessage.message.from_ in self.Admin:
                    ComMsg = self.readCommandLine(msgSep[1:len(msgSep)])
                    self.sendText(self.sendToWho(ncMessage), str(eval(ComMsg)))

    def Security(self, ncMessage):
        """
            ToDo Type:
                NOTIFIED_UPDATE_GROUP (11)
                NOTIFIED_INVITE_INTO_GROUP (13)
                NOTIFIED_ACCEPT_GROUP_INVITATION (17)
                NOTIFIED_KICKOUT_FROM_GROUP (19)
        """
        GroupID = self.securityForWhere(ncMessage)
        SEGroup = self.data.getSEGroup(GroupID)

        if SEGroup == None:
            return

        if SEGroup[ncMessage.type]:
            if ncMessage.type == OpType.NOTIFIED_UPDATE_GROUP:
                pass
            elif ncMessage.type == OpType.NOTIFIED_INVITE_INTO_GROUP:
                for userId in self.data.getData("BlackList"):
                    if self.checkInInvitationList(ncMessage, userId):
                        self.cancelSomeone(GroupID, userId)
                        # Log
            elif ncMessage.type == OpType.NOTIFIED_ACCEPT_GROUP_INVITATION:
                for userId in self.data.getData("BlackList"):
                    if userId == ncMessage.param2:
                        self.kickSomeone(GroupID, userId)
                        # Log
            elif ncMessage.type == OpType.NOTIFIED_KICKOUT_FROM_GROUP:
                if ncMessage.param2 in self.Connect.helper_ids:
                    # Log
                    pass
                else:
                    if ncMessage.param3 in [self.MyMID] + self.Connect.helper_ids:
                        try:
                            # Log
                            self.kickSomeone(GroupID, ncMessage.param2, self.getClientByMid(ncMessage.param3))
                        except:
                            # Log
                            pass
                        self.data.updateData(self.data.getData("BlackList"), True, ncMessage.param2)
                    else:
                        self.sendText(GroupID, _("Bye Bye"))
                        self.kickSomeone(GroupID, ncMessage.param2)

    # Main

    def Main(self):
        NoWork = 0
        catchedNews = []
        ncMessage = Operation()
        LastResetLimitTime = 0
        Revision = self.client.getLastOpRevision()
        while True:
            try:
                if NoWork == 300:
                    Revision = self.client.getLastOpRevision()
                catchedNews = self.listen.fetchOperations(Revision, 50)
                if catchedNews:
                    NoWork = 0
                    for ncMessage in catchedNews:
                        if ncMessage.type == OpType.NOTIFIED_INVITE_INTO_GROUP:
                            self.JoinGroup(ncMessage)
                        elif ncMessage.type == OpType.NOTIFIED_KICKOUT_FROM_GROUP:
                            self.Security(ncMessage)
                        elif ncMessage.type == OpType.RECEIVE_MESSAGE:
                            self.Commands(ncMessage)
                        if ncMessage.reqSeq != -1:
                            Revision = max(Revision, ncMessage.revision)
                else:
                    NoWork = NoWork + 1
            except SystemExit:
                self.exit()
            except EOFError:
                pass
            except:
                err1, err2, err3 = sys.exc_info()
                traceback.print_tb(err3)
                tb_info = traceback.extract_tb(err3)
                filename, line, func, text = tb_info[-1]
                ErrorInfo = "occurred in\n{}\n\non line {}\nin statement {}".format(filename, line, text)
                try:
                    if catchedNews and ncMessage:
                        Finded = False
                        for Catched in catchedNews:
                            if Catched.revision == ncMessage.revision:
                                Finded = True
                            if Finded:
                                Revision = Catched.revision
                                break
                        if not Finded:
                            Revision = self.client.getLastOpRevision()
                    for Root in self.Admin:
                        self.sendText(Root, "Star Yuuki BOT - Something was wrong...\nError:\n%s\n%s\n%s\n\n%s" %
                                     (err1, err2, err3, ErrorInfo))
                except:
                    print("Star Yuuki BOT - Damage!\nError:\n%s\n%s\n%s\n\n%s" % (err1, err2, err3, ErrorInfo))
                    self.exit()
