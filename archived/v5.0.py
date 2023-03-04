# -*- coding: utf-8 -*-
"""
    Star Neptune Bot - Yuuki
    ~~~~~~~~~~~

    Star pYthon Bot = Star Yuuki Bot = SYB

    :copyright: (c) 2016 Star Inc.
"""
from api import *
import api.mu
import time, os

account=''
password=''
king=''
nc=''
ss=''

try:
    syb = LineClient(account,password)
except:
   print "Login Failed"

print 'Login OK'

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
  if "Error, Error, Error, Error, Error, Error, Error, Error," in open(".error-log","r").read():
   syb.getContactById(king).sendMessage("SafeMode On")
   time.sleep(180)
   if len(syb._getGroupIdsInvited()) >= 45:
    syb.getContactById(king).sendMessage("Security!")
    while True:
     if len(syb._getGroupIdsInvited()) >= 7:
      for gi in syb._getGroupIdsInvited():
       syb._acceptGroupInvitation(gi)
       syb._leaveGroup(gi)
     else:
      time.sleep(90)
   else:
    syb.getContactById(king).sendMessage("Program Off")
    os.system('~/k')
  try:
      gc=syb.sybKcheck()
  except:
      pass
  if gc==None or gc.param1 == kgroupid and gc.param2 == kuser and gc.param3 == kcontact:
   syb.revision = syb._getLastOpRevision()
   if len(syb._getGroupIdsInvited()) >= 1:
     gi = syb._getGroupIdsInvited()[0]
     syb._acceptGroupInvitation(gi)
     syb.refreshGroups()
     syb.refreshContacts()
     gg=syb.getGroupById(gi)
     gm = gg.members
     ge = gg.invitee
     log = open("yuuki-status", "a+")
     if gi == kgroupid:
       log.write("<br>" + str(ts) + ": ReJoin: " + gg.name + " ->Members/Invites :" + str(len(gm)) + "/" + str(len(ge)))
     elif "✘" in syb.getContactById(king).name or len(syb.getGroupById(gi).members) >= 50:
       log.write("<br>" + str(ts) + ": Join: " + gg.name + " ->Members/Invites :" + str(len(gm)) + "/" + str(len(ge)))
       gg.sendMessage('安安^^\n我是刀劍神域的絕劍呦><\n我叫作友紀，請多多指教OwO')
       #gg.sendMessage('((如果要我離開，請管理員直接踢我就可以了0.0\n##千萬不能踢我的姐姐\n##千萬不能踢我的姐姐\n##千萬不能踢我的姐姐\n不然我會請你出去XD')
       if gg.creator:
           gc=gg.creator
       else:
           gc = gg.members[0]
       syb.getGroupById(gi).sendMessage('本群組管理員：'+gc.name)
       if not ss in gg.getMemberIds():
           #syb._inviteIntoGroup(gi,[ss])
           pass
       else:
           pass
     else:
         log.write("<br>" + str(ts) + ": NoJoin: " + gg.name + " ->Members/Invites :" + str(len(gm)) + "/" + str(len(ge)))
         syb._leaveGroup(gi)
   else:
       pass
  else:
     log = open("yuuki-status", "a+")
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
     else:
      kgroup.sendMessage('除非管理員，否則不可以踢人呦^^')
      syb._kickoutFromGroup(kgroupid, [kuser])
      try:
       syb._findAndAddContactsByMid(kcontact)
       syb._inviteIntoGroup(kgroupid, [kcontact])
       bist='Back'
      except:
       kcgurl=api.mu.get(kcontact)
       if kcgurl == None:
           kcaurl='加入好友網址取得失敗'
       else:
           kcaurl=kcgurl
       kgroup.sendMessage("邀請受到官方限制，請自行邀回@@\n被踢者："+kcaurl)
       bist='NoBack'
      log.write("<br>" + str(ts) + ": Save: " + kgroup.name + "<br> ->Kicker/Kicked/Admin :" + kuser+ "/" + kcontact +"("+bist+")" + "/" +k.name+"("+ka+")")
 except:
     syb = LineClient(account,password)
     log = open("./.error-log", "a+")
     log.write("Error, ")
