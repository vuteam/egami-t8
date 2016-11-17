from enigma import eTimer, iServiceInformation, getDesktop
from Screens.Console import Console
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Label import Label
from Components.Pixmap import MultiPixmap
from Components.config import *
from Components.ConfigList import ConfigListScreen
from Components.UsageConfig import config
from ServiceReference import ServiceReference
from Tools.Directories import fileExists, pathExists
import os
from os import popen, listdir, system
from xml.dom import minidom
from EGAMI.EGAMI_addon_manager import EG_PrzegladaczAddonow, EGConnectionAnimation
from EGAMI.EGAMI_main import EgamiMainPanel
from EGAMI.EGAMI_tools import *

class EGExecute(Screen):
    skin = '\n\t\t<screen name="EGExecute" position="center,center" size="876,475">\n\t\t\t<widget name="linelist" position="5,5" size="750,470" />\n\t\t</screen>'

    def __init__(self, session, name, command):
        Screen.__init__(self, session)
        self.name = name
        self.onShown.append(self.setWindowTitle)
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'ok': self.close,
         'cancel': self.close}, -1)
        pipe = popen('{ ' + command + '; } 2>&1', 'r')
        self.linelist = pipe.readlines()
        result = pipe.close()
        self.offset = 0
        self.maxoffset = 0
        for x in self.linelist:
            if len(x) > self.maxoffset:
                self.maxoffset = len(x)

        self['linelist'] = MenuList(list=[], enableWrapAround=True)
        self.setList()

    def setWindowTitle(self):
        self.setTitle(self.name)

    def setList(self):
        if self['linelist'] is not None:
            if self.offset > 0:
                list = []
                for line in self.linelist:
                    list.append(line[self.offset:len(line)])

                self['linelist'].setList(list)
            else:
                self['linelist'].setList(self.linelist)
        return


class EGEmuInfoScript(Screen):
    skin = '\n\t\t<screen name="EGEmuInfoScript" position="center,center" size="560,405" title="EGAMI EmuInfo Tool" >\n\t\t\t<widget name="list" position="10,10" size="540,280" scrollbarMode="showOnDemand" />\n\t\t\t<ePixmap name="border" pixmap="/usr/lib/enigma2/python/EGAMI/icons/egami_icons/div-h.png" position="10,290" size="540,4"/>\n\t\t\t<widget name="statuslab" position="10,295" size="540,30" font="Regular;16" valign="center" noWrap="1" backgroundColor="#333f3f3f" foregroundColor="#FFC000" shadowOffset="-2,-2" shadowColor="black" />\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['statuslab'] = Label(_('N/A'))
        self.mlist = []
        self.populateSL()
        self['list'] = MenuList(self.mlist)
        self['list'].onSelectionChanged.append(self.schanged)
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.mygo,
         'back': self.close})
        self.onLayoutFinish.append(self.refr_sel)

    def refr_sel(self):
        self['list'].moveToIndex(1)
        self['list'].moveToIndex(0)

    def populateSL(self):
        self.scriptdesc = {}
        myscripts = listdir('/usr/scripts')
        for fil in myscripts:
            if fil.find('_emuinfo.sh') != -1:
                fil2 = fil[:-11]
                desc = 'N/A'
                f = open('/usr/scripts/' + fil, 'r')
                for line in f.readlines():
                    if line.find('#DESCRIPTION=') != -1:
                        line = line.strip()
                        desc = line[13:]

                f.close()
                self.mlist.append(fil2)
                self.scriptdesc[fil2] = desc

    def schanged(self):
        mysel = self['list'].getCurrent()
        mytext = ' ' + self.scriptdesc[mysel]
        self['statuslab'].setText(mytext)

    def mygo(self):
        mysel = self['list'].getCurrent()
        mysel2 = '/usr/scripts/' + mysel + '_emuinfo.sh'
        mytitle = _('EmuInfo Tool: ') + mysel
        self.session.open(EGExecute, _(mytitle), mysel2)


class EGSoftCamInfo(Screen):
    skin = '<screen name="EGSoftCamInfo" position="center,center" size="400,310" title="EGAMI Softcam Info" >\n      \t\t\t<widget name="menu" position="10,10" size="340,280" scrollbarMode="showOnDemand" />\n\t\t</screen>'

    def __init__(self, session, args = 0):
        Screen.__init__(self, session)
        self.menu = args
        list = []
        if pathExists('/usr/emu_scripts/'):
            softcams = listdir('/usr/emu_scripts/')
            for softcam in softcams:
                if 'cccam' in softcam.lower():
                    list.append((_('CCcam Info'), '1'))
                    break

        if pathExists('/usr/emu_scripts/'):
            softcams = listdir('/usr/emu_scripts/')
            for softcam in softcams:
                if 'oscam' in softcam.lower():
                    list.append((_('OScam Info'), '2'))
                    break

        if pathExists('/usr/emu_scripts/'):
            softcams = listdir('/usr/emu_scripts/')
            for softcam in softcams:
                if 'wicardd' in softcam.lower():
                    list.append((_('Wicardd Info'), '3'))
                    break

        list.append((_('User Scripts Info'), '4'))
        self['menu'] = MenuList(list)
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.go,
         'back': self.close,
         'exit': self.close}, -1)

    def go(self):
        returnValue = self['menu'].l.getCurrentSelection()[1]
        if returnValue is not None:
            if returnValue is '1':
                from Screens.CCcamInfo import CCcamInfoMain
                self.session.open(CCcamInfoMain)
            elif returnValue is '2':
                from Screens.OScamInfo import OscamInfoMenu
                self.session.open(OscamInfoMenu)
            elif returnValue is '3':
                from EGAMI.WicarddInfo import EGAMIWicarddMain
                self.session.open(EGAMIWicarddMain)
            elif returnValue is '4':
                self.session.open(EGEmuInfoScript)
        return


class EmuManager(Screen):
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        skin = '<screen name="EmuManager" position="center,center" size="1040,680" >\n\t\t\t\t<widget name="choose_cam" position="180,10" size="280,35" font="Regular;32" />\n\t\t\t\t<widget name="config" position="530,10" itemHeight="50" font="Regular;28" size="180,30" transparent="1" />\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/EGAMI/icons/egami_icons/default_cam.png" position="500,8" size="800,60" transparent="1" alphatest="on"/>\n\t\t\t\t<widget name="lb_provider" position="180,75" size="280,28" font="Regular;28" />\n\t\t\t\t<widget name="lb_channel" position="180,110" size="280,28" font="Regular;28" />\n\t\t\t\t<widget name="lb_aspectratio" position="180,145" size="280,28" font="Regular;28" />\n\t\t\t\t<widget name="lb_videosize" position="180,180" size="280,28" font="Regular;28" />\n\t\t\t\t<widget name="ecminfo" position="180,225" size="400,290" font="Regular;28" />\n\t\t\t\t<ePixmap pixmap="skin_default/div-h.png" position="10,583" size="1000,4" />\n\t\t\t\t<ePixmap pixmap="skin_default/icons/dish_scan.png" zPosition="0" position="30,65" size="200,200" transparent="1" alphatest="on"/>\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/EGAMI/icons/egami_icons/icon_camd.png" zPosition="0" position="20,240" size="200,200" transparent="1" alphatest="on" />\n\t\t\t\t<ePixmap position="40,604" size="100,40" zPosition="0" pixmap="buttons/red.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<ePixmap position="200,604" size="100,40" zPosition="0" pixmap="buttons/green.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<ePixmap position="410,604" size="100,40" zPosition="0" pixmap="buttons/yellow.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<ePixmap position="690,604" size="100,40" zPosition="0" pixmap="buttons/blue.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<widget name="key_red" position="80,604" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="red" transparent="1" />\n\t\t\t\t<widget name="key_green" position="240,604" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="green" transparent="1" />\n\t\t\t\t<widget name="key_yellow" position="450,604" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="yellow" transparent="1" />\n\t\t\t\t<widget name="key_blue" position="730,604" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="blue" transparent="1" />\n\t\t\t</screen>'
    else:
        skin = '<screen name="EmuManager" position="center,center" size="780,550" >\n\t\t\t\t<widget name="choose_cam" position="180,10" size="280,30" font="Regular;22" />\n\t\t\t\t<widget name="config" position="410,10" size="180,30" transparent="1" />\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/EGAMI/icons/egami_icons/default_cam.png" position="380,8" size="800,60" transparent="1" alphatest="on"/>\n\t\t\t\t<widget name="lb_provider" position="180,75" size="280,20" font="Regular;18" />\n\t\t\t\t<widget name="lb_channel" position="180,95" size="280,20" font="Regular;18" />\n\t\t\t\t<widget name="lb_aspectratio" position="180,115" size="280,20" font="Regular;18" />\n\t\t\t\t<widget name="lb_videosize" position="180,135" size="280,20" font="Regular;18" />\n\t\t\t\t<widget name="ecminfo" position="180,215" size="400,290" font="Regular;18" />\n\t\t\t\t<ePixmap pixmap="skin_default/div-h.png" position="10,483" size="800,4" />\n\t\t\t\t<ePixmap pixmap="skin_default/icons/dish_scan.png" zPosition="0" position="30,55" size="200,200" transparent="1" alphatest="on"/>\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/EGAMI/icons/egami_icons/icon_camd.png" zPosition="0" position="20,225" size="200,200" transparent="1" alphatest="on" />\n\t\t\t\t<ePixmap position="40,504" size="100,40" zPosition="0" pixmap="skin_default/buttons/button_red.png" transparent="1" alphatest="on"/>\n\t\t\t\t<ePixmap position="200,504" size="100,40" zPosition="0" pixmap="skin_default/buttons/button_green.png" transparent="1" alphatest="on"/>\n\t\t\t\t<ePixmap position="360,504" size="100,40" zPosition="0" pixmap="skin_default/buttons/button_yellow.png" transparent="1" alphatest="on"/>\n\t\t\t\t<ePixmap position="550,504" size="100,40" zPosition="0" pixmap="skin_default/buttons/button_blue.png" transparent="1" alphatest="on"/>\n\t\t\t\t<widget name="key_red" position="60,504" zPosition="1" size="170,25" font="Regular;20" valign="top" halign="left" backgroundColor="red" transparent="1" />\n\t\t\t\t<widget name="key_green" position="220,504" zPosition="1" size="170,25" font="Regular;20" valign="top" halign="left" backgroundColor="green" transparent="1" />\n\t\t\t\t<widget name="key_yellow" position="380,504" zPosition="1" size="170,25" font="Regular;20" valign="top" halign="left" backgroundColor="yellow" transparent="1" />\n\t\t\t\t<widget name="key_blue" position="570,504" zPosition="1" size="170,25" font="Regular;20" valign="top" halign="left" backgroundColor="blue" transparent="1" />\n\t\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('EGAMI Blue Panel'))
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions', 'CiSelectionActions'], {'left': self.keyLeft,
         'right': self.keyRight,
         'ok': self.keyRed,
         'cancel': self.cancel,
         'red': self.keyRed,
         'green': self.keyGreen,
         'yellow': self.keyYellow,
         'blue': self.keyBlue}, -1)
        self.softcamchoices = []
        self['config'] = MenuList(self.softcamchoices)
        self.createSetup()
        self.onShow.append(self.createConfig)
        self.onShow.append(self.createSetup2)

    def createConfig(self):
        self.camnames = {}
        self.softcamchoices = []
        cams = listdir('/usr/emu_scripts')
        for fil in cams:
            if fil.find('Ncam_') != -1 or fil.find('EGcam_') != -1:
                f = open('/usr/emu_scripts/' + fil, 'r')
                for line in f.readlines():
                    line = line.strip()
                    if line.find('CAMNAME=') != -1:
                        name = line[9:-1]
                        self.softcamchoices.append(name)
                        self.camnames[name] = '/usr/emu_scripts/' + fil

                f.close()

        self['config'].setList(self.softcamchoices)

    def createSetup(self):
        self['choose_cam'] = Label(_('Set Default CAM'))
        self['key_red'] = Label(_('Save'))
        self['key_green'] = Label(_('Cam Info'))
        self['key_yellow'] = Label(_('Download Cam'))
        self['key_blue'] = Label(_('EGAMI Panel'))
        try:
            service = self.session.nav.getCurrentService()
            info = service and service.info()
            videosize = str(info.getInfo(iServiceInformation.sVideoWidth)) + 'x' + str(info.getInfo(iServiceInformation.sVideoHeight))
            aspect = info.getInfo(iServiceInformation.sAspect)
            if aspect in (1, 2, 5, 6, 9, 10, 13, 14):
                aspect = '4:3'
            else:
                aspect = '16:9'
            provider = info.getInfoString(iServiceInformation.sProvider)
            chname = ServiceReference(self.session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
            self['lb_provider'] = Label(_('Provider: ') + provider)
            self['lb_channel'] = Label(_('Name: ') + chname)
            self['lb_aspectratio'] = Label(_('Aspect Ratio: ') + aspect)
            self['lb_videosize'] = Label(_('Video Size: ') + videosize)
        except:
            self['lb_provider'] = Label(_('Provider: n/a'))
            self['lb_channel'] = Label(_('Name: n/a'))
            self['lb_aspectratio'] = Label(_('Aspect Ratio: n/a'))
            self['lb_videosize'] = Label(_('Video Size: n/a'))

        self['ecminfo'] = Label(readEcmFile())

    def createSetup2(self):
        self.defaultcam = '/usr/emu_scripts/EGcam_Ci.sh'
        if fileExists('/etc/EGCamConf'):
            f = open('/etc/EGCamConf', 'r')
            for line in f.readlines():
                parts = line.strip().split('|')
                if parts[0] == 'deldefault':
                    self.defaultcam = parts[1]

            f.close()
        self.defCamname = 'Common Interface'
        for c in self.camnames.keys():
            if self.camnames[c] == self.defaultcam:
                self.defCamname = c

        pos = 0
        for x in self.softcamchoices:
            if x == self.defCamname:
                self['config'].moveToIndex(pos)
                break
            pos += 1

    def keyLeft(self):
        self['config'].up()

    def keyRight(self):
        self['config'].down()

    def keyYellow(self):
        m = checkkernel()
        if m == 1:
            staturl = catalogXmlUrl()
            downfile = '/tmp/.catalog.xml'
            if fileExists(downfile):
                os.remove(downfile)
            self.session.openWithCallback(self.EGConnectionCallback, EGConnectionAnimation, staturl, downfile)
        else:
            self.session.open(MessageBox, _('Sorry: Wrong image in flash found. You have to install in flash EGAMI Image'), MessageBox.TYPE_INFO, 3)

    def keyBlue(self):
        m = checkkernel()
        if m == 1:
            self.session.open(EgamiMainPanel)
        else:
            self.session.open(MessageBox, _('Sorry: Wrong image in flash found. You have to install in flash EGAMI Image'), MessageBox.TYPE_INFO, 3)

    def EGConnectionCallback(self):
        downfile = '/tmp/.catalog.xml'
        if fileExists(downfile):
            self.session.open(EG_PrzegladaczAddonow, '/tmp/.catalog.xml')
        else:
            self.session.open(MessageBox, _('Sorry, Connection Failed'), MessageBox.TYPE_INFO)

    def myclose(self):
        self.close()

    def keyRed(self):
        m = checkkernel()
        if m == 1:
            emuname = self['config'].getCurrent()
            self.newcam = self.camnames[emuname]
            out = open('/etc/EGCamConf', 'w')
            out.write('deldefault|' + self.newcam + '\n')
            out.close()
            out = open('/etc/CurrentEGCamName', 'w')
            out.write(emuname)
            out.close()
            out = open('/etc/egami/emuname', 'w')
            out.write(emuname)
            out.close()
            cmd = 'cp -f ' + self.newcam + ' /usr/bin/StartEGCam'
            system(cmd)
            cmd = 'STOP_CAMD,' + self.defaultcam
            sendCmdtoEGEmuD(cmd)
            cmd = 'NEW_CAMD,' + self.newcam
            sendCmdtoEGEmuD(cmd)
            oldcam = self.camnames[emuname]
            self.session.openWithCallback(self.myclose, EGEmuManagerStarting, emuname)
            unload_modules(__name__)
        else:
            self.session.open(MessageBox, _('Sorry: Wrong image in flash found. You have to install in flash EGAMI Image'), MessageBox.TYPE_INFO, 3)

    def keyGreen(self):
        m = checkkernel()
        if m == 1:
            self.session.open(EGSoftCamInfo)
        else:
            self.session.open(MessageBox, _('Sorry: Wrong image in flash found. You have to install in flash EGAMI Image'), MessageBox.TYPE_INFO, 3)

    def cancel(self):
        unload_modules(__name__)
        self.close()


class EGEmuManagerStarting(Screen):
    skin = '\n\t\t<screen name="EGEmuManagerStarting" position="390,100" size="484,250" title="EGAMI" flags="wfNoBorder">\n\t\t    <widget name="starting" position="0,0" size="484,250" zPosition="-1" pixmaps="/usr/lib/enigma2/python/EGAMI/icons/egami_icons/startcam_1.png,/usr/lib/enigma2/python/EGAMI/icons/egami_icons/startcam_2.png,/usr/lib/enigma2/python/EGAMI/icons/egami_icons/startcam_3.png,/usr/lib/enigma2/python/EGAMI/icons/egami_icons/startcam_4.png,/usr/lib/enigma2/python/EGAMI/icons/egami_icons/startcam_5.png,/usr/lib/enigma2/python/EGAMI/icons/egami_icons/startcam_6.png,/usr/lib/enigma2/python/EGAMI/icons/egami_icons/startcam_7.png,/usr/lib/enigma2/python/EGAMI/icons/egami_icons/startcam_8.png,/usr/lib/enigma2/python/EGAMI/icons/egami_icons/startcam_9.png,/usr/lib/enigma2/python/EGAMI/icons/egami_icons/startcam_10.png,/usr/lib/enigma2/python/EGAMI/icons/egami_icons/startcam_11.png" transparent="1" />\n\t\t    <widget name="text" position="10,180" halign="center" size="460,60" zPosition="1" font="Regular;20" valign="top" transparent="1" />\n\t\t  </screen>'

    def __init__(self, session, title):
        Screen.__init__(self, session)
        msg = _('Please wait while starting\n') + title + '...'
        self['starting'] = MultiPixmap()
        self['text'] = Label(msg)
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.updatepix)
        self.onShow.append(self.startShow)
        self.onClose.append(self.delTimer)

    def startShow(self):
        self.curpix = 0
        self.count = 0
        self['starting'].setPixmapNum(0)
        self.activityTimer.start(10)

    def updatepix(self):
        self.activityTimer.stop()
        if self.curpix > 9:
            self.curpix = 0
        if self.count > 24:
            self.curpix = 10
        self['starting'].setPixmapNum(self.curpix)
        if self.count == 35:
            self.hide()
            self.close()
        self.activityTimer.start(140)
        self.curpix += 1
        self.count += 1

    def delTimer(self):
        del self.activityTimer
