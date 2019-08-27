#!/usr/bin/python3
# coding=UTF-8

import os, time,  \
       requests,   \
       json, ntpath,\
       traceback


from .core.TalkService import *
from .connection import Yuuki_Connect

from .data import Yuuki_Data

from .i18n import Yuuki_LangSetting

class Yuuki_Settings:
    """ Yuuki Custom Settings """

    config = {
        "name": "Yuuki",
        "version": "v6.5.0-alpha_RC2",
        "project_url": "https://tinyurl.com/syb-yuuki",
        "man_page": "None",
        "privacy_page": "OpenSource - Licensed under MPL 2.0",
        "copyright": "(c)2019 Star Inc.",

        "Seq": 0,
        "Admin": [],
        "SecurityService": False,
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

        self.SecurityService = self.YuukiConfigs["SecurityService"]

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

    def changeGroupUrlStatus(self, group, status, userId=None):
        if status == True:
            group.preventJoinByTicket = False
        else:
            group.preventJoinByTicket = True
        group.members, group.invitee = None, None
        if userId != None:
            self.getClientByMid(userId).updateGroup(self.Seq, group)
        else:
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

        self.data.updateData(self.data.getData("Group", groupId), "SEGroup", group_status)

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

        self.data.updateData(self.data.getData("Group", groupId), "SEGroup", group_status)

    def cleanMyGroupInvitations(self):
        for cleanInvitations in self.client.getGroupIdsInvited():
            self.client.acceptGroupInvitation(self.Seq, cleanInvitations)
            self.client.leaveGroup(self.Seq, cleanInvitations)

    def getContact(self, userId):
        if len(userId) == len(self.MyMID) and userId[0] == "u":
            try:
                contactInfo = self.client.getContact(userId)
            except:
                contactInfo = False
        else:
            contactInfo = False
        return contactInfo

    def securityForWhere(self, Message):
        if Message.type == OpType.NOTIFIED_UPDATE_GROUP:
            return Message.param1, Message.param2, Message.param3
        elif Message.type == OpType.NOTIFIED_INVITE_INTO_GROUP:
            return Message.param1, Message.param2, Message.param3
        elif Message.type == OpType.NOTIFIED_ACCEPT_GROUP_INVITATION:
            return Message.param1, Message.param2, Message.param3
        elif Message.type == OpType.NOTIFIED_KICKOUT_FROM_GROUP:
            return Message.param1, Message.param2, Message.param3

    def getClientByMid(self, userId):
        Accounts = [self.client] + self.Connect.helper
        for count, AccountUserId in enumerate([self.MyMID] + self.Connect.helper_ids):
            if AccountUserId == userId:
                return Accounts[count]

    def getGroupTicket(self, GroupID, userId):
        GroupTicket = self.data.getData("Group", [GroupID, "GroupTicket"], 3)
        if GroupTicket == "":
            GroupTicket = self.getClientByMid(userId).reissueGroupTicket(GroupID)
            self.data.updateData(self.data.getData("Group", [GroupID, "GroupTicket"], 3), userId, GroupTicket)
        return GroupTicket

    def limitReset(self, reconnect=False):
        for userId in [self.MyMID] + self.Connect.helper_ids:
            if reconnect:
                if userId not in self.data.getLimit("Kick"):
                    self.data.updateData(self.data.getData("LimitInfo", "KickLimit"), userId, self.KickLimit)
                if userId not in self.data.getLimit("Cancel"):
                    self.data.updateData(self.data.getData("LimitInfo", "CancelLimit"), userId, self.CancelLimit)
            else:
                self.data.updateData(self.data.getData("LimitInfo", "KickLimit"), userId, self.KickLimit)
                self.data.updateData(self.data.getData("LimitInfo", "CancelLimit"), userId, self.CancelLimit)

    def cancelSomeone(self, groupId, userId, exceptUserId=None):
        if len(self.Connect.helper) >= 1:
            accounts = self.data.getLimit("Cancel")
            if exceptUserId:
                accounts[exceptUserId] = -1
            helper = max(accounts, key=accounts.get)
        else:
            if exceptUserId == self.MyMID:
                return
            helper = self.MyMID

        Limit = self.data.getLimit("Cancel")[helper]
        if Limit > 0:
            self.getClientByMid(helper).cancelGroupInvitation(self.Seq, groupId, [userId])
            self.data.updateData(self.data.getData("LimitInfo", "CancelLimit"), helper, Limit - 1)
        else:
            self.sendText(groupId, _("Cancel Limit."))

    def kickSomeone(self, groupId, userId, exceptUserId=None):
        if len(self.Connect.helper) >= 1:
            accounts = self.data.getLimit("Kick")
            if exceptUserId:
                accounts[exceptUserId] = -1
            helper = max(accounts, key=accounts.get)
        else:
            if exceptUserId == self.MyMID:
                return "None"
            helper = self.MyMID

        Limit = self.data.getLimit("Kick")[helper]
        if Limit > 0:
            self.getClientByMid(helper).kickoutFromGroup(self.Seq, groupId, [userId])
            self.data.updateData(self.data.getData("LimitInfo", "KickLimit"), helper, Limit - 1)
        else:
            self.sendText(groupId, _("Kick Limit."))
        return helper

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
        BlockedIgnore = ncMessage.param2 in self.data.getData("BlackList")
        if self.checkInInvitationList(ncMessage) and not BlockedIgnore:
            GroupID = ncMessage.param1
            Inviter = ncMessage.param2
            GroupInfo = self.client.getGroup(GroupID)
            GroupMember = [Catched.mid for Catched in GroupInfo.members]
            if GroupInfo.members:
                self.client.acceptGroupInvitation(self.Seq, GroupID)
                if len(GroupMember) >= self.YuukiConfigs["GroupMebers_Demand"]:
                    self.sendText(GroupID, _("Helllo^^\nMy name is %s ><\nNice to meet you OwO") % self.YuukiConfigs["name"])
                    self.sendText(GroupID, _("Type:\n\t%s/Help\nto get more information\n\nAdmin of the Group:\n%s") %
                                  (self.YuukiConfigs["name"], self.sybGetGroupCreator(GroupInfo).displayName,))
                    self.getGroupTicket(GroupID, self.MyMID)
                    # Log
                    self.data.updateLog("JoinGroup", (self.data.getTime(), GroupInfo.name, GroupID, Inviter))
                else:
                    self.sendText(GroupID, _("Sorry...\nThe number of members is not satisfied (%s needed)") %
                                  (self.YuukiConfigs["GroupMebers_Demand"],))
                    self.client.leaveGroup(self.Seq, GroupID)
                    # Log
                    self.data.updateLog("JoinGroup", (self.data.getTime(), GroupID, "Not Join", Inviter))
        if not BlockedIgnore:
            for userId in self.Connect.helper_ids:
                if self.checkInInvitationList(ncMessage, userId):
                    self.getClientByMid(userId).acceptGroupInvitation(self.Seq, ncMessage.param1)
                    self.getGroupTicket(ncMessage.param1, userId)
                    # Log
                    self.data.updateLog("JoinGroup", (self.data.getTime(), ncMessage.param1, userId, ncMessage.param2))
        self.Security(ncMessage)

    def Commands(self, ncMessage):
        """
            ToDo Type:
                RECEIVE_MESSAGE (26)
        """
        BlockedIgnore = (ncMessage.message.to in self.data.getData("BlackList")) or (ncMessage.message.from_ in self.data.getData("BlackList"))
        if ('BOT_CHECK' in ncMessage.message.contentMetadata) or BlockedIgnore:
            pass
        elif ncMessage.message.toType == MIDType.ROOM:
            self.client.leaveRoom(self.Seq, ncMessage.message.to)
        elif ncMessage.message.contentType == ContentType.NONE:
            msgSep = ncMessage.message.text.split(" ")
            if self.YuukiConfigs["name"] + '/Help' == ncMessage.message.text:
                self.sendText(self.sendToWho(ncMessage), _("%s\n\t%s\n\nCommands Info:\n%s\n\nPrivacy:\n%s\n\nMore Information:\n%s\n\n%s") %
                              (self.YuukiConfigs["name"], self.YuukiConfigs["version"],
                               self.YuukiConfigs["man_page"], self.YuukiConfigs["privacy_page"],
                               self.YuukiConfigs["project_url"], self.YuukiConfigs["copyright"]))
            elif self.YuukiConfigs["name"] + '/Version' == ncMessage.message.text:
                self.sendText(self.sendToWho(ncMessage), self.YuukiConfigs["version"])
            elif self.YuukiConfigs["name"] + '/UserID' == ncMessage.message.text:
                self.sendText(self.sendToWho(ncMessage), _("LINE System UserID：\n") + ncMessage.message.from_)
            elif self.YuukiConfigs["name"] + '/Speed' == ncMessage.message.text:
                Time1 = time.time()
                self.sendText(self.sendToWho(ncMessage), _("Testing..."))
                Time2 = time.time()
                self.sendText(self.sendToWho(ncMessage), _("Speed:\n%ss") % (Time2 - Time1,))
            elif self.YuukiConfigs["name"] + '/SecurityMode' == msgSep[0]:
                if ncMessage.message.from_ in self.Admin:
                    if len(msgSep) == 2:
                        try:
                            status = int(msgSep[1])
                            self.SecurityService = bool(status)
                        except:
                            pass
                    else:
                        self.sendText(self.sendToWho(ncMessage), str(bool(self.SecurityService)))
            elif self.YuukiConfigs["name"] + '/Enable' == msgSep[0]:
                if ncMessage.message.toType == MIDType.GROUP:
                    GroupInfo = self.client.getGroup(ncMessage.message.to)
                    GroupPrivilege = self.Admin + [self.sybGetGroupCreator(GroupInfo).mid] + self.data.getData("Group", GroupInfo.id)["Ext_Admin"]
                    if ncMessage.message.from_ in GroupPrivilege:
                        status = []
                        for code in msgSep:
                            try:
                                status.append(int(code))
                            except:
                                pass
                        self.enableSecurityStatus(ncMessage.message.to, status)
                        self.sendText(self.sendToWho(ncMessage), _("Okay"))
            elif self.YuukiConfigs["name"] + '/Disable' == msgSep[0]:
                if ncMessage.message.toType == MIDType.GROUP:
                    GroupInfo = self.client.getGroup(ncMessage.message.to)
                    GroupPrivilege = self.Admin + [self.sybGetGroupCreator(GroupInfo).mid] + self.data.getData("Group", GroupInfo.id)["Ext_Admin"]
                    if ncMessage.message.from_ in GroupPrivilege:
                        status = []
                        for code in msgSep:
                            try:
                                status.append(int(code))
                            except:
                                pass
                        self.disableSecurityStatus(ncMessage.message.to, status)
                        self.sendText(self.sendToWho(ncMessage), _("Okay"))
            elif self.YuukiConfigs["name"] + '/ExtAdmin' == msgSep[0]:
                if ncMessage.message.toType == MIDType.GROUP:
                    GroupInfo = self.client.getGroup(ncMessage.message.to)
                    GroupPrivilege = self.Admin + [self.sybGetGroupCreator(GroupInfo).mid]
                    if ncMessage.message.from_ in GroupPrivilege and len(msgSep) == 3:
                        if msgSep[1] == "add":
                            if msgSep[2] in [Member.mid for Member in GroupInfo.members]:
                                if msgSep[2] in self.data.getData("Group", GroupInfo.id)["Ext_Admin"]:
                                    self.sendText(self.sendToWho(ncMessage), _("Added"))
                                elif msgSep[2] not in self.data.getData("BlackList"):
                                    self.data.updateData(self.data.getData("Group", GroupInfo.id)["Ext_Admin"], True, msgSep[2])
                                    self.sendText(self.sendToWho(ncMessage), _("Okay"))
                                else:
                                    self.sendText(self.sendToWho(ncMessage), _("The User(s) was in our blacklist database."))
                            else:
                                self.sendText(self.sendToWho(ncMessage), _("Wrong UserID or the guy is not in Group"))
                        elif msgSep[1] == "delete":
                            if msgSep[2] in self.data.getData("Group", GroupInfo.id)["Ext_Admin"]:
                                self.data.updateData(self.data.getData("Group", GroupInfo.id)["Ext_Admin"], False, msgSep[2])
                                self.sendText(self.sendToWho(ncMessage), _("Okay"))
                            else:
                                self.sendText(self.sendToWho(ncMessage), _("Not Found"))
                    else:
                        self.sendText(self.sendToWho(ncMessage), str(self.data.getData("Group", GroupInfo.id)["Ext_Admin"]))
            elif self.YuukiConfigs["name"] + '/Status' == ncMessage.message.text:
                if ncMessage.message.toType == MIDType.GROUP:
                    GroupInfo = self.client.getGroup(ncMessage.message.to)
                    group_status = self.data.getSEGroup(ncMessage.message.to)
                    if group_status == None:
                        status = _("Default without Initialize\nAdmin of the Group：\n%s") % (
                            self.sybGetGroupCreator(GroupInfo).displayName,
                        )
                    else:
                        status = _("URL:%s\nInvite:%s\nJoin:%s\nMembers:%s\n\nAdmin of the Group：\n%s") % (
                            group_status[OpType.NOTIFIED_UPDATE_GROUP],
                            group_status[OpType.NOTIFIED_INVITE_INTO_GROUP],
                            group_status[OpType.NOTIFIED_ACCEPT_GROUP_INVITATION],
                            group_status[OpType.NOTIFIED_KICKOUT_FROM_GROUP],
                            self.sybGetGroupCreator(GroupInfo).displayName,
                        )
                    self.sendText(self.sendToWho(ncMessage), status)
            elif self.YuukiConfigs["name"] + '/Quit' == ncMessage.message.text:
                if ncMessage.message.toType == MIDType.GROUP:
                    GroupInfo = self.client.getGroup(ncMessage.message.to)
                    GroupPrivilege = self.Admin + [self.sybGetGroupCreator(GroupInfo).mid] + self.data.getData("Group", GroupInfo.id)["Ext_Admin"]
                    if ncMessage.message.from_ in GroupPrivilege:
                        self.sendText(self.sendToWho(ncMessage), _("Bye Bye"))
                        self.client.leaveGroup(self.Seq, GroupInfo.id)
                        for userId in self.Connect.helper_ids:
                            if userId in [member.mid for member in GroupInfo.members]:
                                self.getClientByMid(userId).leaveGroup(self.Seq, GroupInfo.id)
            elif self.YuukiConfigs["name"] + '/Exit' == ncMessage.message.text:
                if ncMessage.message.from_ in self.Admin:
                    self.sendText(self.sendToWho(ncMessage), _("Exit."))
                    self.exit()
            elif self.YuukiConfigs["name"] + '/Com' == msgSep[0] and len(msgSep) != 1:
                if ncMessage.message.from_ in self.Admin:
                    ComMsg = self.readCommandLine(msgSep[1:len(msgSep)])
                    self.sendText(self.sendToWho(ncMessage), str(eval(ComMsg)))
        elif ncMessage.message.contentType == ContentType.CONTACT:
            Catched = ncMessage.message.contentMetadata["mid"]
            contactInfo = self.getContact(Catched)
            if contactInfo == False:
                msg = _("Not Found")
            elif contactInfo.mid in self.data.getData("BlackList"):
                msg = "{}\n{}".format(_("The User(s) was in our blacklist database."), contactInfo.mid)
            else:
                msg = _("Name:%s\nPicture URL:%s/%s\nStatusMessage:\n%s\nLINE System UserID:%s") % \
                      (contactInfo.displayName, self.LINE_Media_server, contactInfo.pictureStatus,
                       contactInfo.statusMessage, contactInfo.mid)
            self.sendText(self.sendToWho(ncMessage), msg)

    def Security(self, ncMessage):
        """
            ToDo Type:
                NOTIFIED_UPDATE_GROUP (11)
                NOTIFIED_INVITE_INTO_GROUP (13)
                NOTIFIED_ACCEPT_GROUP_INVITATION (17)
                NOTIFIED_KICKOUT_FROM_GROUP (19)
        """
        Security_Access = False

        (GroupID, Action, Another) = self.securityForWhere(ncMessage)
        SEGroup = self.data.getSEGroup(GroupID)

        GroupInfo = self.client.getGroup(GroupID)
        GroupPrivilege = self.Admin + [self.sybGetGroupCreator(GroupInfo).mid] + self.data.getData("Group", GroupInfo.id)["Ext_Admin"]

        if Action in GroupPrivilege or Another in GroupPrivilege:
            return

        if SEGroup == None:
            Security_Access = self.SecurityService
        elif SEGroup[ncMessage.type]:
            Security_Access = SEGroup[ncMessage.type]

        if Security_Access and self.SecurityService:
            if ncMessage.type == OpType.NOTIFIED_UPDATE_GROUP:
                if Another == '4':
                    if not GroupInfo.preventJoinByTicket:
                        self.changeGroupUrlStatus(GroupInfo, False)
                        self.sendText(GroupID, _("DO NOT TOUCH THE GROUP URL SETTINGs, see you..."))
                        Kicker = self.kickSomeone(GroupID, Action)
                        # Log
                        self.data.updateLog("KickEvent", (self.data.getTime(), GroupInfo.name, GroupID, Kicker, Action, Another, ncMessage.type))
            elif ncMessage.type == OpType.NOTIFIED_INVITE_INTO_GROUP:
                Canceler = "None"
                if "\x1e" in Another:
                    for userId in Another.split("\x1e"):
                        if userId not in [self.MyMID] + self.Connect.helper_ids + GroupPrivilege:
                            Canceler = self.cancelSomeone(GroupID, userId)
                    # Log
                    self.data.updateLog("CancelEvent", (self.data.getTime(), GroupInfo.name, GroupID, Canceler, Action, Another.replace("\x1e", ",")))
                elif Another not in [self.MyMID] + self.Connect.helper_ids + GroupPrivilege:
                    Canceler = self.cancelSomeone(GroupID, Another)
                    # Log
                    self.data.updateLog("CancelEvent", (self.data.getTime(), GroupInfo.name, GroupID, Canceler, Action, Another))
                if Canceler != "None":
                    self.sendText(GroupID, _("Do not invite anyone...thanks"))
            elif ncMessage.type == OpType.NOTIFIED_ACCEPT_GROUP_INVITATION:
                for userId in self.data.getData("BlackList"):
                    if userId == Action:
                        self.sendText(GroupID, _("You are our blacklist. Bye~"))
                        Kicker = self.kickSomeone(GroupID, userId)
                        # Log
                        self.data.updateLog("KickEvent", (self.data.getTime(), GroupInfo.name, GroupID, Kicker, Kicker, Action, ncMessage.type))
            elif ncMessage.type == OpType.NOTIFIED_KICKOUT_FROM_GROUP:
                if Action in self.Connect.helper_ids:
                    # Log
                    self.data.updateLog("KickEvent", (self.data.getTime(), GroupInfo.name, GroupID, Action, Action, Another, ncMessage.type*10+1))
                else:
                    if Another in [self.MyMID] + self.Connect.helper_ids:
                        Kicker = "None"
                        try:
                            Kicker = self.kickSomeone(GroupID, Action, Another)
                            # Log
                            self.data.updateLog("KickEvent", (self.data.getTime(), GroupInfo.name, GroupID, Kicker, Action, Another, ncMessage.type*10+2))
                            if GroupInfo.preventJoinByTicket:
                                self.changeGroupUrlStatus(GroupInfo, True, Kicker)
                            GroupTicket = self.getGroupTicket(GroupID)
                            if GroupInfo.preventJoinByTicket:
                                self.changeGroupUrlStatus(GroupInfo, False, Kicker)
                            self.getClientByMid(Another).acceptGroupInvitationByTicket(self.Seq, GroupID, GroupTicket)
                        except:
                            # Log
                            self.data.updateLog("KickEvent", (self.data.getTime(), GroupInfo.name, GroupID, Kicker, Action, Another, ncMessage.type*10+3))
                        self.data.updateData(self.data.getData("BlackList"), True, Action)
                        # Log
                        self.data.updateLog("BlackList", (self.data.getTime(), Action, GroupID))
                        self.sendText(Action, _("You had been blocked by our database."))
                    else:
                        self.sendText(GroupID, _("DO NOT KICK, thank you ^^"))
                        Kicker = self.kickSomeone(GroupID, Action)
                        # Log
                        self.data.updateLog("KickEvent", (self.data.getTime(), GroupInfo.name, GroupID, Kicker, Action, Another, ncMessage.type))
        elif self.SecurityService:
            if ncMessage.type == OpType.NOTIFIED_INVITE_INTO_GROUP:
                Canceler = "None"
                for userId in self.data.getData("BlackList"):
                    if self.checkInInvitationList(ncMessage, userId):
                        Canceler = self.cancelSomeone(GroupID, userId)
                        # Log
                        self.data.updateLog("CancelEvent", (self.data.getTime(), GroupInfo.name, GroupID, Canceler, Action, Another))
                if Canceler != "None":
                    self.sendText(GroupID, _("The User(s) was in our blacklist database."))
            elif ncMessage.type == OpType.NOTIFIED_ACCEPT_GROUP_INVITATION:
                for userId in self.data.getData("BlackList"):
                    if userId == Action:
                        self.sendText(GroupID, _("You are our blacklist. Bye~"))
                        Kicker = self.kickSomeone(GroupID, userId)
                        # Log
                        self.data.updateLog("KickEvent", (self.data.getTime(), GroupInfo.name, GroupID, Kicker, Kicker, Action, ncMessage.type))

    # Main

    def Main(self):
        NoWork = 0
        catchedNews = []
        ncMessage = Operation()
        Revision = self.client.getLastOpRevision()
        if time.localtime().tm_hour == self.data.getData("Global", "LastResetLimitTime"):
            self.limitReset(True)
        while True:
            try:
                if time.localtime().tm_hour != self.data.getData("Global", "LastResetLimitTime"):
                    self.limitReset()
                    self.data.updateData(self.data.getData("Global"), "LastResetLimitTime", time.localtime().tm_hour)
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
                        elif ncMessage.type == OpType.NOTIFIED_ACCEPT_GROUP_INVITATION:
                            self.Security(ncMessage)
                        elif ncMessage.type == OpType.NOTIFIED_UPDATE_GROUP:
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
