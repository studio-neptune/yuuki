# -*- coding: utf-8 -*-
"""
    Star Neptune Bot - Yuuki
    ~~~~~~~~~~~

    Star pYthon Bot = Star Yuuki Bot = SYB

    :copyright: (c) 2016 Star Inc.
"""
from api import *
from api.core.ttypes import Message
import api.mu
import time, os

account=''
password=''
king=''
nc=''
sss=''
ss=''
s=''

try:
    syb = LineClient(account,password)
    print 'Login OK'
except:
    print "Login Failed"

gi=''
gg=''
gm=''
ge=''
kgroupid = ''
kgroup = ''
kuser = ''
kcontact = ''
localtime = time.asctime(time.localtime(time.time()))
log=open("yuuki-status","a+")
log.write("<br>"+localtime+": Start")
for gi in syb._getGroupIdsInvited():
  syb._acceptGroupInvitation(gi)
  syb._leaveGroup(gi)

while True:
 ts=time.asctime( time.localtime(time.time()) )
 try:
  gc=syb.sybKcheck()
  if gc==None or gc.param1 == kgroupid and gc.param2 == kuser and gc.param3 == kcontact:
   syb.revision = syb._getLastOpRevision()
   log = open("yuuki-status", "a+")
   if len(syb._getGroupIdsInvited()) >= 1:
     try:
       gi = syb._getGroupIdsInvited()[0]
       syb._acceptGroupInvitation(gi)
       gg = syb._getGroups([gi])[0]
       gm = gg.members
       ge = gg.invitee
       if gg.creator:
           gc = gg.creator
       else:
           gc = gg.members[0]
       if gi == kgroupid:
           log.write("<br>" + str(
               ts) + ": ReJoin: " + gg.name + " ->Admin/Members/Invites :" + gc.displayName + "(" + gc.mid + ")" + "/" + str(len(gm)) + "/" + str(len(ge)))
       elif "✘" in syb._getContacts([king])[0].displayName or len(gg.members) >= 50:
           syb.refreshGroups()
           log.write("<br>" + str(ts) + ": Join: " + gg.name + " ->Admin/Members/Invites :" + gc.displayName + "(" + gc.mid + ")" + "/" + str(len(gm)) + "/" + str(len(ge)))
           msg = '安安^^\n我是刀劍神域的絕劍呦><\n我叫作友紀，請多多指教OwO'
           syb.getGroupById(gi).sendMessage(msg)
           msg = '使用說明及最新消息請至\nhttp://line.me/ti/p/@niq6886v\n之主頁瀏覽，謝謝^^\n本群組管理員：' + gc.displayName
           syb.getGroupById(gi).sendMessage(msg)
           if not ss in gg.getMemberIds():
               pass
           else:
               pass
       else:
           log.write("<br>" + str(
               ts) + ": NoJoin: " + gg.name + " ->Admin/Members/Invites :" + gc.displayName + "(" + gc.mid + ")" + "/" + str(
               len(gm)) + "/" + str(len(ge)))
           syb._leaveGroup(gi)
     except:
        pass
   else:
       pass
  else:
     kgroupid=gc.param1
     kgroup=syb.getGroupById(kgroupid)
     kuser=gc.param2
     kcontact=gc.param3
     if kgroup.creator != None:
         k=kgroup.creator
         ka=k.id
     else:
         k=kgroup.members[0]
         ka=k.id
     if kuser in [ka,king,nc]:
      pass
     elif kcontact in syb._getBlockedContactIds():
      kgroup.sendMessage('除非管理員，否則不可以踢人呦^^')
      kgroup.sendMessage('被踢者在封鎖名單內！故無法邀請\n如有需要，請自行邀回：')
      kgroup.sendUser(kcontact)
     else:
      kgroup.sendMessage('除非管理員，否則不可以踢人呦^^')
      try:
       syb._kickoutFromGroup(kgroupid, [kuser])
       kist = 'Kick'
      except:
       kgroup.sendMessage('緊告！有人正在踢人！請進入群組檢查！\n##系統因限制無法踢人==')
       kist = 'NoKick'
      kgroup.sendMessage("請自行邀回0.0\n被踢者：")
      kgroup.sendUser(kcontact)
      if syb._getGroup(kgroupid).preventJoinByTicket == False:
          syb._changeGroupUrlStatus(kgroupid, False)
          ust = 'Yes'
      else:
          usr = 'No'
      log.write("<br>%s: Save: %s<br> ->Kicker/Kicked/Admin/Url :%s(%s)/%s/%s(%s)/%s") % (ts, kgroup.name, kuser, kist, kcontact, k.name, ka, ust)
 except:
     syb.login()
