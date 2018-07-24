# -*- coding: utf-8 -*-
"""
    Star Yuuki Bot - Yuuki
    ~~~~~~~~~~~
     This is a main program in SYB.
     It`s belong to Star Yuuki(pYthon) Bot Project of Star Neptune Bot
    Version: v6.3.2
    Copyright(c) 2017 Star Inc. All Rights Reserved.
"""
from api import *
from api.core.ttypes import Message
import time, sys, requests

account=''
password=''
king='' # Administrator
nc='' # The UserID of NightCrazy(https://www.facebook.com/star.nightcrazy/)
sss='' # The UserID of Asuna(syb-ab)
ss='' # The UserID of  Second Security BOT(syb-sc)
s='' # The UserID of Yuuki(syb)
forsyb=''  # The UserID of Kirito(4syb)

try:
    syb = LineClient(account,password,refreshCacheDatas=False)
    print 'Login OK'
except:
    print "Login Failed"

lastrev=0
errortimes=0
allerrortimes=0
botkick=0
ks=0
kickban = 30
ked=''
kedcheck=0
kked=[]
kued=[]
kced=0
urljoined=''
works=[]
partblock=[]
partblocknew=0
ksreg=0
notKick=[]

localtime = time.asctime(time.localtime(time.time()))
log=open("yuuki-status","a+")
log.write("<br>"+localtime+": Start")
for gi in syb._getGroupIdsInvited():
  syb._acceptGroupInvitation(gi)
  syb._leaveGroup(gi)

authKey=open('../talk/yuuki-join','w')
authKey.write(syb.authToken)
authKey.close()
time.sleep(3)
authKey=open('../talk/sc-join','r')
key=authKey.read()
authKey.close()
time.sleep(3)
authKey=open('../../www/star_nep/4syb/.key','r')
kirito=authKey.read()
authKey.close()

lk=open('.lastkick','r')
strlk=lk.read()
if strlk != '':
 lastkick=int(strlk)
else:
 lastkick=0
lk.close()

lks=open('.kicks','r')
ks = len(lks.read())
lks.close()
lks=open('.kicks','w+')

ng=open('.ng','r')
notKick = ng.read().split("\n")
ng.close()
ng=open('.ng','w+')

bk=open('.blocklist','r')
blocklist = syb._getBlockedContactIds()
for x in eval("[%s]" % (bk.read(),)):
 blocklist.append(x)
bk=open('.blocklist','a+')

pb=open('.partblock','r')
for x in eval("[%s]" % (pb.read(),)):
 partblock.append(x)
 blocklist.append(x)
pb.close()

bt=open('.botlist','r')
botlist = eval("[%s]" % (bt.read(),))
bt=open('.botlist','a+')

syb.revision = syb._getLastOpRevision()

def SNB4sybURL(key='',gid='',url='',gki='',glv=''):
    urlworks = {"key":key,"gid":gid,"gur":url,"gki":gki,"glv":glv}
    urlover = requests.post(' ',urlworks) # The function need Star Inc. Business API. So Removed
    return urlover.text

def changeGroupUrlStatusByData(self, data, status):
    if status == True:
     msg=False
    else:
     msg=True
    message=data
    message.preventJoinByTicket=msg
    message.invitee=None
    message.members=None
    return self._client.send_updateGroup(0, message)

def sendMessage(self, toid, msg):
    text = Message(to=toid, text=msg.encode('utf-8'))
    self._client.send_sendMessage(0, text)

def sendUser(self, toid, mid):
    text = Message(contentType=13, text='',contentMetadata={'mid': mid, 'displayName': 'Line User',}, to=toid)
    self._client.send_sendMessage(0, text)

def sybGetGroupCreator(group):
    if group.creator == None:
     contact = group.members[0]
    else:
     contact = group.creator
    return contact

def newSybLog(self, when, logcode, gid, who, whoseid):
    self.write("<br>%s: %s: %s ->%s :%s" % (when,logcode,gid,who,whoseid))

while True:
 ts=time.asctime( time.localtime(time.time()) )
 if allerrortimes == 229:
  try:
   sendMessage(syb,king,"Safe Mode Start!\nError:\n%s\n%s\n%s" % (err1,err2,err3))
  except:
   syb.login()
   sendMessage(syb,king,"Safe Mode Start!\nError:\n%s\n%s\n%s" % (err1,err2,err3))
  sys.exit(0)
 elif errortimes == 1:
  syb.revision = max(syb.revision,lastrev)
  errortimes = 0
  allerrortimes = allerrortimes +1
  try:
   sendMessage(syb,king,"System Error\nTimes: %s\n\nError:\n%s\n%s\n%s" % (allerrortimes,err1,err2,err3))
  except:
   syb.login()
   sendMessage(syb,king,"System Error\nTimes: %s\n\nError:\n%s\n%s\n%s" % (allerrortimes,err1,err2,err3))
  if allerrortimes != 1:
   time.sleep(60)
   if over != None and works != []:
    works.remove(over)
  syb.revision = syb._getLastOpRevision()
 try:
  if works == []:
   ncover = syb._fetchOperations(syb.revision,50)
  else:
   ncover=None
  logcode = None
  glist = None
  over = None
  if ncover != None:
   if ncover != []:
    if ncover[-1].revision == -1:
     lastrev = ncover[-2].revision
    else:
     lastrev = ncover[-1].revision
    for nc in ncover:
     if nc.type == 19:
      works.append(nc)
      if kedcheck == 1:
       if over.param2 == sss:
        kedcheck = 0
     elif nc.type == 11 or nc.type == 13 or nc.type == 17:
      works.append(nc)
    if kedcheck == 1:
     kedcheck = 2
  if kedcheck == 2:
   if ks == 0:
    ks = 1
    ksreg = 0
   else:
    ks = 99
    kedcheck = 0
  if partblocknew == 1:
   pb = open('.partblocklist', 'w')
   pb.write(str(partblock))
   pb.close()
  if ks == 1 and ksreg == 0:
   x=time.localtime(time.time()).tm_min
   lk=open('.lastkick','w+')
   lastkick=x
   lk.write(str(x))
   lk.close()
   ksreg=1
  if time.localtime(time.time()).tm_min == lastkick:
   lks.close()
   ksreg=0
   ks=0
   lks = open('.kicks', 'w+')
  if time.localtime(time.time()).tm_min == 0:
   if partblock != []:
    for x in partblock:
     blocklist.remove(x)
   partblock = []
   pb = open('.partblocklist', 'w')
   pb.close()
   notKick=[]
   ng.close()
   ng = open('.ng', 'w+')
  if kced == 5:
   kued = []
  else:
   kced=kced+1
  if works != []:
   over=works[0]
  if over == None:
   syb.revision = max(syb.revision,lastrev)
  elif over.type == 17:
   if over.param2 != forsyb:
    kued=[over.param1,over.param2]
   kced=0
   if over.param2 in blocklist:
    if ks <= kickban:
     syb._client.send_kickoutFromGroup(0,over.param1,[over.param2])
     kedcheck=1
     ks=ks+1
     lks.write("+")
    else:
     sendMessage(syb,over.param1,'請注意！目前有遭系統封鎖之人員進入！\n程序由於Line Corp.限制\n目前無法踢人！請注意此群組！\nhttp://line.me/ti/p/@niq6886v')
    newSybLog(log, ts, 'Kick',over.param1,'Blocked',over.param2)
    syb._changeGroupUrlStatus(over.param1,False)
   works.remove(over)
   syb.revision = max(syb.revision,lastrev)
  elif over.type == 11:
   if over.param3 == '1':
    gg=syb._getGroup(over.param1)
    if gg.name == 'Yuuki OFF' and syb.profile.id in [x.mid for x in gg.members]:
     if over.param2 != sybGetGroupCreator(gg).mid:
      syb._changeGroupName(over.param1,'No way!')
     else:
      newSybLog(log, ts, 'OFF',over.param1,'Changer',over.param2)
      sendMessage(syb,over.param1,'所有功能已關閉，可放心移除任何成員(包含我QAQQ)')
    if gg.name == 'Yuuki SC' or gg.name == 'SA Kingdom':
     if over.param2 != sybGetGroupCreator(gg).mid and gg.name == 'Yuuki SC':
      syb._changeGroupName(over.param1,'Group`s Admin Only!')
     else:
      if gg.preventJoinByTicket == True:
       changeGroupUrlStatusByData(syb,gg,True)
      SNB4sybURL(key=key,gid=over.param1,url=syb._renewGroupUrl(over.param1))
      changeGroupUrlStatusByData(syb,gg,False)
      newSybLog(log, ts, 'SC',over.param1,'Changer',over.param2)
      urljoined=over.param1
   works.remove(over)
   syb.revision = max(syb.revision,lastrev)
  elif over.type == 19:
   if [over.param1,over.param2] == kued or over.param2 in botlist:
    ogn = 'Yuuki OFF'
    if botkick == 2:
     if ks <= kickban:
      syb._client.send_kickoutFromGroup(0,over.param1,[over.param2])
      kedcheck=1
      ks=ks+1
      lks.write("+")
     else:
      BotKickE=BotKickE+1
      if BotKickE == 2:
       if gg.preventJoinByTicket == True:
        changeGroupUrlStatusByData(syb,gg,True)
       SNB4sybURL(key=kirito,gid=over.param1,url=syb._renewGroupUrl(over.param1),glv='yes')
       changeGroupUrlStatusByData(syb,gg,False)
       BotKickE=0
      else:
       sendMessage(syb,over.param1,'請注意！目前有新加入者正在移除成員\n程序由於Line Corp.限制\n目前無法踢人！請注意此群組！\nhttp://line.me/ti/p/@niq6886v')
     if over.param2 in partblock:
      partblock.remove(over.param2)
      partblocknew=1
      blocklist.remove(over.param2)
     if over.param2 not in botlist:
      bt.write('"%s",' % (over.param2,))
     if over.param2 not in blocklist:
      sendMessage(syb, over.param2, '您目前已被本程序封鎖\n如有任何問題，請洽詢\nhttp://line.me/ti/p/@niq6886v')
      syb._blockContact(over.param2)
      blocklist.append(over.param2)
      bk.write('"%s",' % (over.param2,))
     newSybLog(log, ts, 'Block',over.param1,'Bot',over.param2)
    botkick=botkick+1
   else:
    botkick=0
    gg=syb._getGroup(over.param1)
    ogn=gg.name
   if ogn == 'Yuuki OFF' or over.param2 == king or over.param2 == nc or over.param2 == sss or over.param2 == ss or over.param2 == s or over.param2 == forsyb:
    pass
   else:
     if over.param3 == syb.profile.id:
      if over.param2 in partblock:
       partblock.remove(over.param2)
       partblocknew=1
       blocklist.remove(over.param2)
      if over.param2 not in blocklist:
       sendMessage(syb,over.param2,'您目前已被本程序封鎖\n如有任何問題，請洽詢\nhttp://line.me/ti/p/@niq6886v')
       syb._blockContact(over.param2)
       blocklist.append(over.param2)
       bk.write('"%s",' % (over.param2,))
      newSybLog(log, ts, 'Block',over.param1,'Blocked',over.param2)
     elif over.param3 == ss:
      if ks <= kickban:
       syb._client.send_kickoutFromGroup(0,over.param1,[over.param2])
       kedcheck=1
       ks=ks+1
       lks.write("+")
       gki=''
      else:
       gki=over.param2
      if gg.preventJoinByTicket == True:
       gg.preventJoinByTicket = False
       changeGroupUrlStatusByData(syb,gg,True)
      SNB4sybURL(key=key,gid=over.param1,url=syb._renewGroupUrl(over.param1),gki=gki)
      if over.param2 in partblock:
       partblock.remove(over.param2)
       partblocknew=1
       blocklist.remove(over.param2)
      if over.param2 not in blocklist:
       sendMessage(syb,over.param2,'您目前已被本程序封鎖\n如有任何問題，請洽詢\nhttp://line.me/ti/p/@niq6886v')
       syb._blockContact(over.param2)
       blocklist.append(over.param2)
       bk.write('"%s",' % (over.param2,))
      newSybLog(log, ts, 'SCBlock',over.param1,'Blocked',over.param2)
     else:
      if syb.profile.id in [x.mid for x in gg.members]:
       if ks <= kickban:
        sendMessage(syb,over.param1,'如果你是系統認定的群組管理員，請先停用我\nP.S.把群名改成(區分大小寫)：Yuuki OFF\n反正，掰掰囉><\nhttp://line.me/ti/p/@niq6886v')
        sendUser(syb,over.param1,over.param2)
        syb._client.send_kickoutFromGroup(0,over.param1,[over.param2])
        kedcheck=1
        ks=ks+1
        lks.write("+")
        sendMessage(syb,over.param1,'被踢者：')
        sendUser(syb,over.param1,over.param3)
       else:
        sendMessage(syb,over.param1,'請注意！目前有人正在移除成員\n程序由於Line Corp.限制\n目前無法踢人！請注意此群組！\nhttp://line.me/ti/p/@niq6886v')
        if [over.param1,over.param2] != kked:
         sendMessage(syb,over.param1,'以下分別為：\n踢人者/被踢者')
         sendUser(syb,over.param1,over.param2)
         sendUser(syb,over.param1,over.param3)
        else:
         sendMessage(syb,over.param1,'以下為被踢者')
         sendUser(syb,over.param1,over.param3)
        notKick.append(over.param1)
        ng.write(over.param1+'\n')
        inElist=0
        for x in notKick:
         if x == over.param1:
          inElist=inElist+1
        if inElist == 10:
         if gg.preventJoinByTicket == True:
          gg.preventJoinByTicket = False
          changeGroupUrlStatusByData(syb,gg,True)
         sendMessage(syb,over.param1,'警戒！目前此群組已進入管制模式\n嚴禁執行任何有關成員名單更變之動作\nP.S.整點時解除\nhttp://line.me/ti/p/@niq6886v')
         SNB4sybURL(key=kirito,gid=over.param1,url=syb._renewGroupUrl(over.param1),gki=over.param2,glv='yes')
         sendMessage(syb,over.param2,'此功能尚未啟用...\nhttp://line.me/ti/p/@niq6886v')
         if over.param2 not in blocklist:
          sendMessage(syb,over.param2,'您目前已被本程序封鎖\n如有任何問題，請洽詢\nhttp://line.me/ti/p/@niq6886v')
          syb._blockContact(over.param2)
          blocklist.append(over.param2)
          bk.write('"%s",' % (over.param2,))
          newSybLog(log, ts, 'Block',over.param1,'Warning',over.param2)
         for x in notKick:
          if x == over.param1:
           notKick.remove(x)
        elif inElist == 5:
         sendMessage(syb,over.param1,'警告！目前此群組即將進入管制模式\n將嚴禁任何人員踢人、邀請等相關動作\n請勿再嘗試剔除任何成員\nhttp://line.me/ti/p/@niq6886v')
     if gg.preventJoinByTicket == False:
      changeGroupUrlStatusByData(syb,gg,False)
     newSybLog(log, ts, 'Kick',over.param1,'Kicker/Kicked','%s/%s' % (over.param2,over.param3,))
   ked=over.param1
   kked=[over.param1,over.param2]
   works.remove(over)
   syb.revision = max(syb.revision,lastrev)
  elif over.type == 13:
   inlist = False
   if over.param3 == syb.profile.id:
    inlist = True
   elif "\x1e" in over.param3:
    glist = over.param3.split("\x1e")
    if syb.profile.id in glist:
     inlist = True
   if glist != None or over.param3 in botlist:
    blocked = []
    if glist != None:
     if syb.profile.id not in glist:
      for x in glist:
       if x in botlist:
        blocked=glist
        break
    else:
     blocked=[over.param3]
    if blocked != []:
     inlist = False
     syb._client.send_cancelGroupInvitation(0,over.param1, blocked)
     if over.param2 not in blocklist:
      partblock.append(over.param2)
      partblocknew=1
      blocklist.append(over.param2)
      sendMessage(syb,over.param2,'由於您疑似邀請到了惡意解散群組程式\n您目前已被本程序暫時性封鎖\n請耐心等候至整點，名單會自動移除\n\n如有任何問題，請洽詢\nhttp://line.me/ti/p/@niq6886v')
     newSybLog(log, ts, 'Cancel', over.param1, 'BOT_Inviter', over.param2)
   if inlist == True:
    try:
     gg=syb._getGroup(over.param1)
     if over.param1 == ked:
      pass
     elif len(gg.members) <= 100:
      if king in [x.mid for x in gg.members]:
       for x in gg.members:
        if x.mid == king:
         kingname=x.displayName
       if "✘" not in kingname:
        inlist = False
      else:
       inlist = False
    except:
     inlist=False
    try:
     if syb.profile.id in [x.mid for x in gg.invitee] and inlist == True:
      syb._client.send_acceptGroupInvitation(0,over.param1)
      newSybLog(log, ts, 'Join',over.param1,'Inviter',over.param2)
      sendMessage(syb,over.param1,'安安^^\n我是絕劍呦><\n請多多指教OwO')
      sendMessage(syb,over.param1,'我隸屬於千本桜帝国(TW)呦\n使用說明及最新消息請至\nhttp://line.me/ti/p/@niq6886v\n之主頁瀏覽，謝謝^^\n也歡迎造訪千本桜帝国(TW)官網\nhttp://sa-kingdom.ml/tw\n本群組管理員：\n%s' % (sybGetGroupCreator(gg).displayName,))
     else:
      if syb.profile.id in [x.mid for x in gg.invitee]:
       syb._client.send_acceptGroupInvitation(0,over.param1)
       sendMessage(syb,over.param1,'不好意思...\n此群組人數未滿100人')
       syb._client.send_leaveGroup(0,over.param1)
      newSybLog(log, ts, 'NoJoin',over.param1,'Inviter',over.param2)
    except:
     newSybLog(log, ts, 'NoJoin(E)',over.param1,'Inviter',over.param2)
   if glist != None or over.param3 in blocklist:
    blocked=[]
    if glist != None:
     for x in glist:
      if x in blocklist:
       blocked.append(x)
    else:
     blocked=[over.param3]
    if blocked != []:
     syb._client.send_cancelGroupInvitation(0,over.param1,blocked)
     newSybLog(log, ts, 'Cancel',over.param1,'Blocked',over.param2)
   works.remove(over)
   syb.revision = max(syb.revision,lastrev)
  else:
   if over != None:
    works.remove(over)
   syb.revision = max(syb.revision,lastrev)
 except EOFError:
  pass
 except:
  errortimes = errortimes + 1
  err1, err2, err3 = sys.exc_info()
