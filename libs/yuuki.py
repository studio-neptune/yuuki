#!/usr/bin/python3
# coding=UTF-8

import socket, \
       os, time,  \
       json, ntpath, \
       random, requests, \
       platform, traceback

from git import Repo

try:
    from .core.TalkService import *
except ImportError:
    print(
        "It's necessary to install \"core\" for LINE connection,\n"
        "Please read the \"README.md\" first."
    )

from .connection import Yuuki_Connect
from .data import Yuuki_Data
from .i18n import Yuuki_LangSetting
from .thread_control import Yuuki_Multiprocess

class Yuuki_Settings:
    """ Yuuki Custom Settings """

    config = {
        "name": "Yuuki",
        "version": "v6.5.2",
        "version_check": True,
        "project_url": "https://tinyurl.com/syb-yuuki",
        "man_page": "https://tinyurl.com/yuuki-manual",
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
    def __init__(self, Yuuki_Settings, Yuuki_Connection, threading=False):

        # Static Variable

        self.YuukiConfigs = Yuuki_Settings.config

        self.Threading = threading
        self.Thread_Control = Yuuki_Multiprocess()
 
        self.Seq = self.YuukiConfigs["Seq"]
        self.Admin = self.YuukiConfigs["Admin"]

        self.KickLimit = self.YuukiConfigs["Hour_KickLimit"]
        self.CancelLimit = self.YuukiConfigs["Hour_CancelLimit"]

        self.i18n = Yuuki_LangSetting(self.YuukiConfigs["Default_Language"])

        self.LINE_Media_server = "https://obs.line-apps.com"

        self.Connect = Yuuki_Connect(Yuuki_Connection)

        # Version Check
        git_result = "Unknown"
        origin_url = "https://github.com/star-inc/star_yuuki_bot.git"

        if self.YuukiConfigs["version_check"]:
            try:
                GitRemote = Repo('.').remote()
                UpdateStatus = GitRemote.fetch()[0]
                if UpdateStatus.flags == 64:
                    git_result = "New version found."
                elif UpdateStatus.flags == 4:
                    git_result = "This is the latest version."
            except:
                git_result = "Something was wrong."

        # Announce Dog
        print(
            "\n{} {}\n"
            "\t===\n\n"
            "<*> {}\n\n"
            "More Information:\n"
            "{}\n\n\t\t\t\t\t"
            "{}\n\t{}\n"   .format(
                self.YuukiConfigs["name"],
                self.YuukiConfigs["version"],
                git_result,
                origin_url,
                self.YuukiConfigs["copyright"],
                "\t==" * 5
            )
        )

        # LINE Login

        (self.client, self.listen) = self.Connect.connect()
        self.connectHeader = Yuuki_Connection.connectHeader

        for access in self.YuukiConfigs["helper_LINE_ACCESS_KEYs"]:
            self.Connect.helperConnect(access)

        # Dynamic Variable

        self.data = Yuuki_Data(self.Threading)

        self.data.updateData(["Global","GroupJoined"], self.client.getGroupIdsJoined())
        self.data.updateData(["Global","SecurityService"], self.YuukiConfigs["SecurityService"])

        # Initialize

        self.MyMID = self.client.getProfile().mid
        self.revision = self.client.getLastOpRevision()

        self.AllAccountIds = [self.MyMID] + self.Connect.helper_ids

        if len(self.data.getData(["LimitInfo"])) != 2:
            self.data.updateData(["LimitInfo"], self.data.LimitType)

        global _

        _ = self.i18n._

    # Basic Func

    def getClient(self, userId):
        if self.Threading:
            if userId == self.MyMID:
                (client, _) = self.Connect.connect()
                return client
            else:
                return self.Connect.helperThreadConnect(userId)
        else:
            Accounts = [self.client] + self.Connect.helper
            for count, AccountUserId in enumerate(self.AllAccountIds):
                if AccountUserId == userId:
                    return Accounts[count]

    def exit(self, restart=False):
        print("System Exit")
        self.data.updateData(["Global", "Power"], False)
        if self.Threading:
            try:
                self.data._mdsShake("EXT", "")
            except:
                pass
        if restart:
            if platform.system() == "Windows":
                with open("cache.bat", "w") as c:
                    c.write(sys.executable + " ./main.py")
                os.system("cache.bat")
                os.system("del cache.bat")
            elif platform.system() == "Linux":
                with open(".cache.sh", "w") as c:
                    c.write(sys.executable + " ./main.py")
                os.system("sh .cache.sh")
                os.system("rm .cache.sh")
            else:
                print("Star Yuuki BOT - Restart Error\n\nUnknown Platform")
        sys.exit(0)

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

    def checkInInvitationList(self, ncMessage, userId=None):
        if userId is None:
            userId = self.MyMID
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
            self.getClient(userId).updateGroup(self.Seq, result)
        else:
            self.getClient(self.MyMID).updateGroup(self.Seq, result)

    def configSecurityStatus(self, groupId, status):
        group_status = self.data.SEGrouptype
        if 0 in status:
            group_status[OpType.NOTIFIED_UPDATE_GROUP] = True
        if 1 in status:
            group_status[OpType.NOTIFIED_INVITE_INTO_GROUP] = True
        if 2 in status:
            group_status[OpType.NOTIFIED_ACCEPT_GROUP_INVITATION] = True
        if 3 in status:
            group_status[OpType.NOTIFIED_KICKOUT_FROM_GROUP] = True

        self.data.updateData(["Group", groupId, "SEGroup"], group_status)

    @staticmethod
    def errorReport():
        err1, err2, err3 = sys.exc_info()
        traceback.print_tb(err3)
        tb_info = traceback.extract_tb(err3)
        filename, line, func, text = tb_info[-1]
        ErrorInfo = "occurred in\n{}\n\non line {}\nin statement {}".format(filename, line, text)
        return err1, err2, err3, ErrorInfo

    def cleanMyGroupInvitations(self):
        for client in [self.getClient(self.MyMID)] + self.Connect.helper:
            for cleanInvitations in client.getGroupIdsInvited():
                client.acceptGroupInvitation(self.Seq, cleanInvitations)
                client.leaveGroup(self.Seq, cleanInvitations)

    def getContact(self, userId):
        if len(userId) == len(self.MyMID) and userId[0] == "u":
            try:
                contactInfo = self.getClient(self.MyMID).getContact(userId)
            except:
                contactInfo = False
        else:
            contactInfo = False
        return contactInfo

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

    def getGroupTicket(self, GroupID, userId, renew=False):
        GroupTicket = ""
        GroupData = self.data.getGroup(GroupID)
        if "GroupTicket" in GroupData:
            if GroupData["GroupTicket"].get(userId) is not None:
                GroupTicket = GroupData["GroupTicket"].get(userId)
        else:
            assert "Error JSON data type - GroupTicket"
        if GroupTicket == "" or renew:
            GroupTicket = self.getClient(userId).reissueGroupTicket(GroupID)
            self.data.updateData(["Group", GroupID, "GroupTicket", userId], GroupTicket)
        return GroupTicket

    def limitReset(self):
        for userId in self.AllAccountIds:
            self.data.updateData(["LimitInfo", "KickLimit", userId], self.KickLimit)
            self.data.updateData(["LimitInfo", "CancelLimit", userId], self.CancelLimit)

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

    def cancelSomeone(self, groupInfo, userId, exceptUserId=None):
        if len(self.Connect.helper) >= 1:
            members = [member.mid for member in groupInfo.members if member.mid in self.AllAccountIds]
            accounts = self.dictShuffle(self.data.getData(["LimitInfo", "CancelLimit"]), members)
            if len(accounts) == 0:
                return "None"
            if exceptUserId:
                accounts[exceptUserId] = -1
            helper = max(accounts, key=accounts.get)
        else:
            if exceptUserId == self.MyMID:
                return "None"
            helper = self.MyMID

        Limit = self.data.getData(["LimitInfo", "CancelLimit", helper])
        if Limit > 0:
            self.getClient(helper).cancelGroupInvitation(self.Seq, groupInfo.id, [userId])
            self.data.limitDecrease("CancelLimit", helper)
        else:
            self.sendText(groupInfo.id, _("Cancel Limit."))
        return helper

    def kickSomeone(self, groupInfo, userId, exceptUserId=None):
        if len(self.Connect.helper) >= 1:
            members = [member.mid for member in groupInfo.members if member.mid in self.AllAccountIds]
            accounts = self.dictShuffle(self.data.getData(["LimitInfo", "KickLimit"]), members)
            if len(accounts) == 0:
                return "None"
            if exceptUserId:
                accounts[exceptUserId] = -1
            helper = max(accounts, key=accounts.get)
        else:
            if exceptUserId == self.MyMID:
                return "None"
            helper = self.MyMID

        Limit = self.data.getData(["LimitInfo", "KickLimit", helper])
        if Limit > 0:
            self.getClient(helper).kickoutFromGroup(self.Seq, groupInfo.id, [userId])
            self.data.limitDecrease("KickLimit", helper)
        else:
            self.sendText(groupInfo.id, _("Kick Limit."))
        return helper

    @staticmethod
    def sendToWho(ncMessage):
        if ncMessage.message.toType == MIDType.USER:
            return ncMessage.message.from_
        elif ncMessage.message.toType == MIDType.ROOM:
            return ncMessage.message.to
        elif ncMessage.message.toType == MIDType.GROUP:
            return ncMessage.message.to

    def sendText(self, toid, msg):
        message = Message(to=toid, text=msg)
        self.getClient(self.MyMID).sendMessage(self.Seq, message)

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
        self.getClient(self.MyMID).sendMessage(self.Seq, message)

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
            message_id = self.getClient(self.MyMID).sendMessage(self.Seq, message).id
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
            url = self.LINE_Media_server + '/talk/m/upload.nhn'
            r = requests.post(url, headers=self.connectHeader, data=data, files=files)
            if r.status_code != 201:
                self.sendText(send_to, "Error!")

    def Thread_Exec(self, Function, args):
        if self.Threading:
            self.Thread_Control.add(Function, args)
        else:
            Function(*args)

    # Task

    def taskDemux(self, catchedNews):
        for ncMessage in catchedNews:
            if ncMessage.type == OpType.NOTIFIED_INVITE_INTO_GROUP:
                self.Thread_Exec(self.JoinGroup, (ncMessage,))
            elif ncMessage.type == OpType.NOTIFIED_KICKOUT_FROM_GROUP:
                self.Thread_Exec(self.Security, (ncMessage,))
            elif ncMessage.type == OpType.NOTIFIED_ACCEPT_GROUP_INVITATION:
                self.Thread_Exec(self.Security, (ncMessage,))
            elif ncMessage.type == OpType.NOTIFIED_UPDATE_GROUP:
                self.Thread_Exec(self.Security, (ncMessage,))
            elif ncMessage.type == OpType.RECEIVE_MESSAGE:
                self.Thread_Exec(self.Commands, (ncMessage,))

    def JoinGroup(self, ncMessage):
        """
            Event Type:
                NOTIFIED_INVITE_INTO_GROUP (13)
        """
        GroupInvite = []
        BlockedIgnore = ncMessage.param2 in self.data.getData(["BlackList"])
        if self.checkInInvitationList(ncMessage) and not BlockedIgnore:
            GroupID = ncMessage.param1
            Inviter = ncMessage.param2
            GroupInfo = self.getClient(self.MyMID).getGroup(GroupID)
            if GroupInfo.members:
                GroupMember = [Catched.mid for Catched in GroupInfo.members]
                GroupInfo.invitee = []
                if GroupInfo.invitee:
                    GroupInvite = [Catched.mid for Catched in GroupInfo.invitee]
                self.getClient(self.MyMID).acceptGroupInvitation(self.Seq, GroupID)
                if len(GroupMember) >= self.YuukiConfigs["GroupMebers_Demand"]:
                    GroupList = self.data.getData(["Global", "GroupJoined"])
                    NewGroupList = GroupList.copy()
                    NewGroupList.append(GroupID)
                    self.data.updateData(["Global", "GroupJoined"], NewGroupList)
                    self.sendText(GroupID, _("Helllo^^\nMy name is %s ><\nNice to meet you OwO") % self.YuukiConfigs["name"])
                    self.sendText(GroupID, _("Type:\n\t%s/Help\nto get more information\n\nMain Admin of the Group:\n%s") %
                                  (self.YuukiConfigs["name"], self.sybGetGroupCreator(GroupInfo).displayName,))
                    self.getGroupTicket(GroupID, self.MyMID, True)
                    # Log
                    self.data.updateLog("JoinGroup", (self.data.getTime(), GroupInfo.name, GroupID, Inviter))
                else:
                    self.sendText(GroupID, _("Sorry...\nThe number of members is not satisfied (%s needed)") %
                                  (self.YuukiConfigs["GroupMebers_Demand"],))
                    self.getClient(self.MyMID).leaveGroup(self.Seq, GroupID)
                    # Log
                    self.data.updateLog("JoinGroup", (self.data.getTime(), GroupID, "Not Join", Inviter))
        if ncMessage.param1 in self.data.getData(["Global", "GroupJoined"]) and not BlockedIgnore:
            for userId in self.Connect.helper_ids:
                if self.checkInInvitationList(ncMessage, userId) or userId in GroupInvite:
                    self.getClient(userId).acceptGroupInvitation(self.Seq, ncMessage.param1)
                    self.getGroupTicket(ncMessage.param1, userId, True)
                    # Log
                    self.data.updateLog("JoinGroup", (self.data.getTime(), ncMessage.param1, userId, ncMessage.param2))
        self.Security(ncMessage)

    def Commands(self, ncMessage):
        """
            Event Type:
                RECEIVE_MESSAGE (26)
        """
        BlockedIgnore = (ncMessage.message.to in self.data.getData(["BlackList"])) or (ncMessage.message.from_ in self.data.getData(["BlackList"]))
        if ('BOT_CHECK' in ncMessage.message.contentMetadata) or BlockedIgnore:
            pass
        elif ncMessage.message.toType == MIDType.ROOM:
            self.getClient(self.MyMID).leaveRoom(self.Seq, ncMessage.message.to)
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
                self.sendText(self.sendToWho(ncMessage), _("LINE System UserID:\n") + ncMessage.message.from_)

            elif self.YuukiConfigs["name"] + '/GetAllHelper' == ncMessage.message.text:
                if ncMessage.message.toType == MIDType.GROUP:
                    GroupInfo = self.getClient(self.MyMID).getGroup(ncMessage.message.to)
                    GroupPrivilege = self.Admin + [self.sybGetGroupCreator(GroupInfo).mid] + self.data.getGroup(GroupInfo.id)["Ext_Admin"]
                    if ncMessage.message.from_ in GroupPrivilege:
                        for userId in self.Connect.helper_ids:
                            self.sendUser(self.sendToWho(ncMessage), userId)

            elif self.YuukiConfigs["name"] + '/Speed' == ncMessage.message.text:
                Time1 = time.time()
                self.sendText(self.sendToWho(ncMessage), _("Testing..."))
                Time2 = time.time()
                self.sendText(self.sendToWho(ncMessage), _("Speed:\n %s com/s") % (Time2 - Time1,))

            elif self.YuukiConfigs["name"] + '/SecurityMode' == msgSep[0]:
                if ncMessage.message.from_ in self.Admin:
                    if len(msgSep) == 2:
                        if msgSep[1].isdigit() and 1 >= int(msgSep[1]) >= 0:
                            self.data.updateData(["Global", "SecurityService"], bool(msgSep[1]))
                            self.sendText(self.sendToWho(ncMessage), _("Okay"))
                        else:
                            self.sendText(self.sendToWho(ncMessage), _("Enable(True): 1\nDisable(False): 0"))
                    else:
                        self.sendText(self.sendToWho(ncMessage), str(bool(self.data.getData(["Global", "SecurityService"]))))

            elif self.YuukiConfigs["name"] + '/Switch' == msgSep[0] and len(msgSep) != 1:
                if ncMessage.message.toType == MIDType.GROUP:
                    GroupInfo = self.getClient(self.MyMID).getGroup(ncMessage.message.to)
                    GroupPrivilege = self.Admin + [self.sybGetGroupCreator(GroupInfo).mid] + self.data.getGroup(GroupInfo.id)["Ext_Admin"]
                    if not self.data.getData(["Global", "SecurityService"]):
                        self.sendText(self.sendToWho(ncMessage),
                                      _("SecurityService of %s was disable") % (self.YuukiConfigs["name"],))
                    elif ncMessage.message.from_ in GroupPrivilege:
                        status = []
                        unknown_msg = []
                        unknown_msgtext = ""
                        for count, code in enumerate(msgSep):
                            if code.isdigit() and 3 >= int(code) >= 0:
                                status.append(int(code))
                            elif count != 0:
                                unknown_msg.append(code.strip())
                        self.configSecurityStatus(ncMessage.message.to, status)
                        if unknown_msg:
                            unknown_msgtext = ", ".join(unknown_msg)
                        if status:
                            self.sendText(self.sendToWho(ncMessage), _("Okay"))
                        else:
                            self.sendText(self.sendToWho(ncMessage), _("Not Found"))
                        if unknown_msgtext != "":
                            self.sendText(self.sendToWho(ncMessage), _("Notice: Unknown command line argument(s)") + "\n({})".format(unknown_msgtext))

            elif self.YuukiConfigs["name"] + '/DisableAll' == ncMessage.message.text:
                if ncMessage.message.toType == MIDType.GROUP:
                    GroupInfo = self.getClient(self.MyMID).getGroup(ncMessage.message.to)
                    GroupPrivilege = self.Admin + [self.sybGetGroupCreator(GroupInfo).mid] + self.data.getGroup(GroupInfo.id)["Ext_Admin"]
                    if not self.data.getData(["Global", "SecurityService"]):
                        self.sendText(self.sendToWho(ncMessage), _("SecurityService of %s was disable") % (self.YuukiConfigs["name"],))
                    elif ncMessage.message.from_ in GroupPrivilege:
                        self.configSecurityStatus(ncMessage.message.to, [])
                        self.sendText(self.sendToWho(ncMessage), _("Okay"))

            elif self.YuukiConfigs["name"] + '/ExtAdmin' == msgSep[0]:
                if ncMessage.message.toType == MIDType.GROUP:
                    GroupInfo = self.getClient(self.MyMID).getGroup(ncMessage.message.to)
                    GroupPrivilege = self.Admin + [self.sybGetGroupCreator(GroupInfo).mid]
                    if len(msgSep) == 3:
                        if ncMessage.message.from_ in GroupPrivilege:
                            if msgSep[1] == "add":
                                if msgSep[2] in [Member.mid for Member in GroupInfo.members]:
                                    if msgSep[2] in self.data.getGroup(GroupInfo.id)["Ext_Admin"]:
                                        self.sendText(self.sendToWho(ncMessage), _("Added"))
                                    elif msgSep[2] not in self.data.getData(["BlackList"]):
                                        origin = self.data.getData(["Group", GroupInfo.id,"Ext_Admin"])
                                        ext_admin_list = origin.copy()
                                        ext_admin_list.append(msgSep[2])
                                        self.data.updateData(["Group", GroupInfo.id,"Ext_Admin"], ext_admin_list)
                                        self.sendText(self.sendToWho(ncMessage), _("Okay"))
                                    else:
                                        self.sendText(self.sendToWho(ncMessage), _("The User(s) was in our blacklist database."))
                                else:
                                    self.sendText(self.sendToWho(ncMessage), _("Wrong UserID or the guy is not in Group"))
                            elif msgSep[1] == "delete":
                                if msgSep[2] in self.data.getGroup(GroupInfo.id)["Ext_Admin"]:
                                    origin = self.data.getData(["Group", GroupInfo.id,"Ext_Admin"])
                                    ext_admin_list = origin.copy()
                                    ext_admin_list.remove(msgSep[2])
                                    self.data.updateData(["Group", GroupInfo.id,"Ext_Admin"], ext_admin_list)
                                    self.sendText(self.sendToWho(ncMessage), _("Okay"))
                                else:
                                    self.sendText(self.sendToWho(ncMessage), _("Not Found"))
                    else:
                        if self.data.getGroup(GroupInfo.id)["Ext_Admin"]:
                            status = ""
                            status_added = []
                            for member in GroupInfo.members:
                                if member.mid in self.data.getGroup(GroupInfo.id)["Ext_Admin"]:
                                    status += "{}\n".format(member.displayName)
                                    status_added.append(member.mid)
                            for userId in self.data.getGroup(GroupInfo.id)["Ext_Admin"]:
                                if userId not in status_added:
                                    status += "{}: {}\n".format(_("Unknown"), userId)
                            self.sendText(self.sendToWho(ncMessage), status + _("\nExtend Administrator(s)"))
                        else:
                            self.sendText(self.sendToWho(ncMessage), _("Not Found"))

            elif self.YuukiConfigs["name"] + '/Status' == ncMessage.message.text:
                if ncMessage.message.toType == MIDType.GROUP:
                    GroupInfo = self.getClient(self.MyMID).getGroup(ncMessage.message.to)
                    group_status = self.data.getSEGroup(ncMessage.message.to)
                    if not self.data.getData(["Global", "SecurityService"]):
                        status = _("SecurityService of %s was disable") % (
                            self.YuukiConfigs["name"],
                        )
                    elif group_status is None:
                        status = _("Default without Initialize\nMain Admin of the Group:\n%s") % (
                            self.sybGetGroupCreator(GroupInfo).displayName,
                        )
                    else:
                        status = _("SecurityService is Listening on\n\nURL:%s\nInvite:%s\nJoin:%s\nMembers:%s\n\nMain Admin of the Group:\n%s") % (
                            group_status[OpType.NOTIFIED_UPDATE_GROUP],
                            group_status[OpType.NOTIFIED_INVITE_INTO_GROUP],
                            group_status[OpType.NOTIFIED_ACCEPT_GROUP_INVITATION],
                            group_status[OpType.NOTIFIED_KICKOUT_FROM_GROUP],
                            self.sybGetGroupCreator(GroupInfo).displayName,
                        )
                    self.sendText(self.sendToWho(ncMessage), status)

            elif self.YuukiConfigs["name"] + '/GroupBackup' == ncMessage.message.text:
                if ncMessage.message.toType == MIDType.GROUP:
                    GroupInfo = self.getClient(self.MyMID).getGroup(ncMessage.message.to)
                    GroupPrivilege = self.Admin + [self.sybGetGroupCreator(GroupInfo).mid] + self.data.getGroup(GroupInfo.id)["Ext_Admin"]
                    if ncMessage.message.from_ in GroupPrivilege:
                        GroupMembers = [User.mid for User in GroupInfo.members]
                        GroupInvites = None
                        if GroupInfo.invitee:
                            GroupInvites = [User.mid for User in GroupInfo.invitee]
                        LayoutInfo = {
                            "OriginID": GroupInfo.id,
                            "Members": GroupMembers,
                            "Invites": GroupInvites
                        }
                        self.sendText(ncMessage.message.from_, GroupInfo.name)
                        self.sendText(ncMessage.message.from_, json.dumps(LayoutInfo))
                        self.sendText(ncMessage.message.to, _("Okay"))

            elif self.YuukiConfigs["name"] + '/Quit' == ncMessage.message.text:
                if ncMessage.message.toType == MIDType.GROUP:
                    GroupInfo = self.getClient(self.MyMID).getGroup(ncMessage.message.to)
                    GroupPrivilege = self.Admin + [self.sybGetGroupCreator(GroupInfo).mid]
                    if ncMessage.message.from_ in GroupPrivilege:
                        self.sendText(self.sendToWho(ncMessage), _("Bye Bye"))
                        self.getClient(self.MyMID).leaveGroup(self.Seq, GroupInfo.id)
                        for userId in self.Connect.helper_ids:
                            if userId in [member.mid for member in GroupInfo.members]:
                                self.getClient(userId).leaveGroup(self.Seq, GroupInfo.id)
                    GroupList = self.data.getData(["Global", "GroupJoined"])
                    NewGroupList = GroupList.copy()
                    NewGroupList.remove(GroupInfo.id)
                    self.data.updateData(["Global", "GroupJoined"], NewGroupList)

            elif self.YuukiConfigs["name"] + '/Exit' == ncMessage.message.text:
                if ncMessage.message.from_ in self.Admin:
                    self.sendText(self.sendToWho(ncMessage), _("Exit."))
                    self.exit()

            elif self.YuukiConfigs["name"] + '/Com' == msgSep[0] and len(msgSep) != 1:
                if ncMessage.message.from_ in self.Admin:
                    try:
                        ComMsg = self.readCommandLine(msgSep[1:len(msgSep)])
                        Report = str(eval(ComMsg))
                    except:
                        (err1, err2, err3, ErrorInfo) = self.errorReport()
                        Report = "Star Yuuki BOT - Eval Error:\n%s\n%s\n%s\n\n%s" % (err1, err2, err3, ErrorInfo)
                    self.sendText(self.sendToWho(ncMessage), Report)

        elif ncMessage.message.contentType == ContentType.CONTACT:
            Catched = ncMessage.message.contentMetadata["mid"]
            contactInfo = self.getContact(Catched)
            if not contactInfo:
                msg = _("Not Found")
            elif contactInfo.mid in self.data.getData(["BlackList"]):
                msg = "{}\n{}".format(_("The User(s) was in our blacklist database."), contactInfo.mid)
            else:
                msg = _("Name:%s\nPicture URL:%s/%s\nStatusMessage:\n%s\nLINE System UserID:%s") % \
                      (contactInfo.displayName, self.LINE_Media_server, contactInfo.pictureStatus,
                       contactInfo.statusMessage, contactInfo.mid)
            self.sendText(self.sendToWho(ncMessage), msg)

    def Security(self, ncMessage):
        """
            Event Type:
                NOTIFIED_UPDATE_GROUP (11)
                NOTIFIED_INVITE_INTO_GROUP (13)
                NOTIFIED_ACCEPT_GROUP_INVITATION (17)
                NOTIFIED_KICKOUT_FROM_GROUP (19)
        """
        Security_Access = False

        (GroupID, Action, Another) = self.securityForWhere(ncMessage)
        SEGroup = self.data.getSEGroup(GroupID)

        GroupInfo = self.getClient(self.MyMID).getGroup(GroupID)
        GroupPrivilege = self.Admin + [self.sybGetGroupCreator(GroupInfo).mid] + self.data.getGroup(GroupInfo.id)["Ext_Admin"]

        if Action in GroupPrivilege or Another in GroupPrivilege:
            if ncMessage.type != OpType.NOTIFIED_KICKOUT_FROM_GROUP:
                return
            elif Action in GroupPrivilege:
                return

        if SEGroup is None:
            Security_Access = self.data.getData(["Global", "SecurityService"])
        elif SEGroup[ncMessage.type]:
            Security_Access = SEGroup[ncMessage.type]

        if self.data.getData(["Global", "SecurityService"]):
            if ncMessage.type == OpType.NOTIFIED_UPDATE_GROUP and Security_Access:
                if Another == '4':
                    if not GroupInfo.preventJoinByTicket and Action not in self.Connect.helper_ids:
                        self.Thread_Exec(self.changeGroupUrlStatus, (GroupInfo, False))
                        self.Thread_Exec(self.sendText, (GroupID, _("DO NOT ENABLE THE GROUP URL STATUS, see you...")))
                        Kicker = self.kickSomeone(GroupInfo, Action)
                        # Log
                        self.data.updateLog("KickEvent", (self.data.getTime(), GroupInfo.name, GroupID, Kicker, Action, Another, ncMessage.type))
            elif ncMessage.type == OpType.NOTIFIED_INVITE_INTO_GROUP and Security_Access:
                Canceler = "None"
                if "\x1e" in Another:
                    for userId in Another.split("\x1e"):
                        if userId not in self.AllAccountIds + GroupPrivilege:
                            if GroupInfo.invitee and userId in [user.mid for user in GroupInfo.invitee]:
                                Canceler = self.cancelSomeone(GroupInfo, userId)
                            else:
                                Canceler = self.kickSomeone(GroupInfo, userId)
                                # Log
                                self.data.updateLog("KickEvent", (self.data.getTime(), GroupInfo.name, GroupID, Canceler, Action, userId, ncMessage.type*10))
                    # Log
                    self.data.updateLog("CancelEvent", (self.data.getTime(), GroupInfo.name, GroupID, Canceler, Action, Another.replace("\x1e", ",")))
                elif Another not in self.AllAccountIds + GroupPrivilege:
                    if GroupInfo.invitee and Another in [user.mid for user in GroupInfo.invitee]:
                        Canceler = self.cancelSomeone(GroupInfo, Another)
                    else:
                        Canceler = self.kickSomeone(GroupInfo, Another)
                        # Log
                        self.data.updateLog("KickEvent", (self.data.getTime(), GroupInfo.name, GroupID, Canceler, Action, Another, ncMessage.type*10))
                    # Log
                    self.data.updateLog("CancelEvent", (self.data.getTime(), GroupInfo.name, GroupID, Canceler, Action, Another))
                if Canceler != "None":
                    self.sendText(GroupID, _("Do not invite anyone...thanks"))
            elif ncMessage.type == OpType.NOTIFIED_ACCEPT_GROUP_INVITATION and Security_Access:
                for userId in self.data.getData(["BlackList"]):
                    if userId == Action:
                        self.Thread_Exec(self.sendText, (GroupID, _("You are our blacklist. Bye~")))
                        Kicker = self.kickSomeone(GroupInfo, Action)
                        # Log
                        self.data.updateLog("KickEvent", (self.data.getTime(), GroupInfo.name, GroupID, Kicker, Kicker, Action, ncMessage.type))
            elif ncMessage.type == OpType.NOTIFIED_KICKOUT_FROM_GROUP:
                if Action in self.Connect.helper_ids:
                    # Log
                    self.data.updateLog("KickEvent", (self.data.getTime(), GroupInfo.name, GroupID, Action, Action, Another, ncMessage.type*10+1))
                elif Another in self.AllAccountIds:
                    Kicker = "None"
                    try:
                        Kicker = self.kickSomeone(GroupInfo, Action, Another)
                        # Log
                        self.data.updateLog("KickEvent", (self.data.getTime(), GroupInfo.name, GroupID, Kicker, Action, Another, ncMessage.type*10+2))
                        assert Kicker != "None", "No Helper Found"
                        if GroupInfo.preventJoinByTicket:
                            self.Thread_Exec(self.changeGroupUrlStatus, (GroupInfo, True, Kicker))
                        GroupTicket = self.getGroupTicket(GroupID, Kicker)
                        try:
                            self.getClient(Another).acceptGroupInvitationByTicket(self.Seq, GroupID, GroupTicket)
                        except:
                            if GroupInfo.preventJoinByTicket:
                                self.changeGroupUrlStatus(GroupInfo, True, Kicker)
                            GroupTicket = self.getGroupTicket(GroupID, Kicker, True)
                            self.getClient(Another).acceptGroupInvitationByTicket(self.Seq, GroupID, GroupTicket)
                        if GroupInfo.preventJoinByTicket:
                            self.Thread_Exec(self.changeGroupUrlStatus, (GroupInfo, False, Another))
                        self.getGroupTicket(GroupID, Another, True)
                    except:
                        (err1, err2, err3, ErrorInfo) = self.errorReport()
                        for Root in self.Admin:
                            self.sendText(Root, "Star Yuuki BOT - SecurityService Failure\n\n%s\n%s\n%s\n\n%s" %
                                          (err1, err2, err3, ErrorInfo))
                        if Another == self.MyMID:
                            GroupList = self.data.getData(["Global", "GroupJoined"])
                            NewGroupList = GroupList.copy()
                            NewGroupList.remove(GroupID)
                            self.data.updateData(["Global", "GroupJoined"], NewGroupList)
                        # Log
                        self.data.updateLog("KickEvent", (self.data.getTime(), GroupInfo.name, GroupID, Kicker, Action, Another, ncMessage.type*10+3))
                    BlackList = self.data.getData(["BlackList"])
                    if Action not in BlackList:
                        NewBlackList = BlackList.copy()
                        NewBlackList.append(Action)
                        self.data.updateData(["BlackList"], NewBlackList)
                        # Log
                        self.data.updateLog("BlackList", (self.data.getTime(), Action, GroupID))
                        self.Thread_Exec(self.sendText, (Action, _("You had been blocked by our database.")))
                elif Security_Access:
                    self.Thread_Exec(self.sendText, (GroupID, _("DO NOT KICK, thank you ^^")))
                    Kicker = self.kickSomeone(GroupInfo, Action)
                    # Log
                    self.data.updateLog("KickEvent", (self.data.getTime(), GroupInfo.name, GroupID, Kicker, Action, Another, ncMessage.type))
                    self.Thread_Exec(self.sendText, (GroupID, _("The one who was been kicked:")))
                    self.Thread_Exec(self.sendUser, (GroupID, Another))

    # Main

    def Main(self):
        NoWork = 0
        NoWorkLimit = 5

        fetchNum = 50
        cacheOperations = []
        ncMessage = Operation()

        if "LastResetLimitTime" not in self.data.getData(["Global"]):
            self.data.updateData(["Global", "LastResetLimitTime"], None)

        Power = True
        self.data.updateData(["Global","Power"], Power)

        while Power:
            try:
                if time.localtime().tm_hour != self.data.getData(["Global", "LastResetLimitTime"]):
                    self.limitReset()
                    self.data.updateData(["Global", "LastResetLimitTime"], time.localtime().tm_hour)

                if NoWork >= NoWorkLimit:
                    NoWork = 0
                    for ncMessage in cacheOperations:
                        if ncMessage.reqSeq != -1 and ncMessage.revision > self.revision:
                            self.revision = ncMessage.revision
                            break
                    if ncMessage.revision != self.revision:
                        self.revision = self.client.getLastOpRevision()

                try:
                    cacheOperations = self.listen.fetchOperations(self.revision, fetchNum)
                except socket.timeout:
                    NoWork += 1

                if cacheOperations:
                    NoWork = 0
                    self.Thread_Exec(self.taskDemux, (cacheOperations,))
                    if len(cacheOperations) > 1:
                        self.revision = max(cacheOperations[-1].revision, cacheOperations[-2].revision)

                Power = self.data.syncData()

            except requests.exceptions.ConnectionError:
                Power = False

            except SystemExit:
                Power = False

            except KeyboardInterrupt:
                self.exit()

            except EOFError:
                pass

            except:
                (err1, err2, err3, ErrorInfo) = self.errorReport()
                try:
                    for ncMessage in cacheOperations:
                        if ncMessage.reqSeq != -1 and ncMessage.revision > self.revision:
                            self.revision = ncMessage.revision
                            break
                    if ncMessage.revision != self.revision:
                        self.revision = self.client.getLastOpRevision()
                    for Root in self.Admin:
                        self.sendText(Root, "Star Yuuki BOT - Something was wrong...\nError:\n%s\n%s\n%s\n\n%s" %
                                     (err1, err2, err3, ErrorInfo))
                except:
                    print("Star Yuuki BOT - Damage!\nError:\n%s\n%s\n%s\n\n%s" % (err1, err2, err3, ErrorInfo))
                    self.exit()
