# -*- coding: utf-8 -*-
"""
    Star Neptune Bot - Yuuki
    ~~~~~~~~~~~

    Star pYthon Bot = Star Yuuki Bot = SYB

    :copyright: (c) 2016 Star Inc.
"""
from api import *
from api.core.ttypes import Message
import time

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
   if len(syb._getGroupIdsInvited()) >= 1:
     try:
       gi = syb._getGroupIdsInvited()[0]
       gg = syb._getGroup(gi)
       syb._acceptGroupInvitation(gi)
       gm = gg.members
       ge = gg.invitee
       if gg.creator:
           gc = gg.creator
       else:
           gc = gg.members[0]
       if gi == kgroupid:
           log.write("<br>" + str(
               ts) + ": ReJoin: " + gg.name + " ->Admin/Members/Invites :" + gc.displayName + "(" + gc.mid + ")" + "/" + str(len(gm)) + "/" + str(len(ge)))
       elif "✘" in syb._getContacts([king])[0].displayName or len(gg.members) >= 100:
           log.write("<br>" + str(ts) + ": Join: " + gg.name + " ->Admin/Members/Invites :" + gc.displayName + "(" + gc.mid + ")" + "/" + str(len(gm)) + "/" + str(len(ge)))
           msg = '安安^^\n我是刀劍神域的絕劍呦><\n我叫作友紀，請多多指教OwO'
           text = Message(to=gi, text=msg.encode('utf-8'))
           syb.sendMessage(text)
           msg = '使用說明及最新消息請至\nhttp://line.me/ti/p/@niq6886v\n之主頁瀏覽，謝謝^^\n本群組管理員：' + gc.displayName
           text = Message(to=gi, text=msg.encode('utf-8'))
           syb.sendMessage(text)
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
     kgroup=syb._getGroup(kgroupid)
     kuser=gc.param2
     kcontact=gc.param3
     if kgroup.creator != None:
         k=kgroup.creator
         ka=k.mid
     else:
         k=kgroup.members[0]
         ka=k.mid
     if kuser in [ka,king,nc]:
      pass
     elif kcontact in syb._getBlockedContactIds():
      msg='除非管理員，否則不可以踢人呦^^'
      text = Message(to=kgroupid, text=msg.encode('utf-8'))
      syb.sendMessage(text)
      msg='被踢者在封鎖名單內！\n如有需要，請自行邀回：'
      text = Message(to=kgroupid, text=msg.encode('utf-8'))
      syb.sendMessage(text)
      kgroup.sendUser(kcontact)
     else:
      msg='除非管理員，否則不可以踢人呦^^'
      text = Message(to=kgroupid, text=msg.encode('utf-8'))
      syb.sendMessage(text)
      try:
       syb._kickoutFromGroup(kgroupid, [kuser])
       kist = 'Kick'
      except:
       msg='緊告！有人正在踢人！請進入群組檢查！\n##系統因限制無法踢人=='
       text = Message(to=kgroupid, text=msg.encode('utf-8'))
       syb.sendMessage(text)
       kist = 'NoKick'
      if kcontact == ka or kcontact == king or kcontact == ss:
          try:
              syb._inviteIntoGroup(kgroupid, kcontact)
          except:
              msg="請自行邀回0.0\n被踢者："
              text = Message(to=kgroupid, text=msg.encode('utf-8'))
              syb.sendMessage(text)
              text = Message(contentType=13, text='', contentMetadata = {'mid': kcontact,'displayName': 'Line User',}, to=kgroupid)
              syb.sendMessage(text)
      else:
          msg="請自行邀回0.0\n被踢者："
          text = Message(to=kgroupid, text=msg.encode('utf-8'))
          syb.sendMessage(text)
          text = Message(contentType=13, text='', contentMetadata = {'mid': kcontact,'displayName': 'Line User',}, to=kgroupid)
          syb.sendMessage(text)
      if kgroup.preventJoinByTicket == False:
          syb._changeGroupUrlStatus(kgroupid, False)
          ust = 'Yes'
      else:
          ust = 'No'
      if not kgroupid == None:
        log.write("<br>%s: Save: %s<br> ->Kicker/Kicked/Admin/Url :%s(%s)/%s/%s(%s)/%s" % (ts, kgroup.name, kuser, kist, kcontact, k.name, ka, ust))
 except:
     syb.login()
