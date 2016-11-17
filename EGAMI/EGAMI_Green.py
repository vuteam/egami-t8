from enigma import getDesktop
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.config import *
from Components.UsageConfig import *
from Components.ConfigList import *
from Components.PluginList import *
from Components.Sources.List import List
from Components.PluginComponent import plugins
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE
import os
from EGAMI.EGAMI_main import EGKernelInfo
from EGAMI.EGAMI_tools import getStbArch
from Plugins.Extensions.EGAMIPermanentClock.plugin import *
from boxbranding import getMachineBuild

class EGDecodingSetup(ConfigListScreen, Screen):

    def __init__(self, session, args = 0):
        Screen.__init__(self, session)
        self.skinName = ['Setup']
        Screen.setTitle(self, _('Decoding Setup'))
        list = []
        list.append(getConfigListEntry(_('Show No free tuner info'), config.usage.messageNoResources))
        list.append(getConfigListEntry(_('Show Tune failed info'), config.usage.messageTuneFailed))
        list.append(getConfigListEntry(_('Show No data on transponder info'), config.usage.messageNoPAT))
        list.append(getConfigListEntry(_('Show Service not found info'), config.usage.messageNoPATEntry))
        list.append(getConfigListEntry(_('Show Service invalid info'), config.usage.messageNoPMT))
        list.append(getConfigListEntry(_('Hide zap errors'), config.usage.hide_zap_errors))
        list.append(getConfigListEntry(_('Include EIT in http streams'), config.streaming.stream_eit))
        list.append(getConfigListEntry(_('Include AIT in http streams'), config.streaming.stream_ait))
        list.append(getConfigListEntry(_('Include ECM in http streams'), config.streaming.stream_ecm))
        list.append(getConfigListEntry(_('Include AIT in recordings'), config.recording.include_ait))
        list.append(getConfigListEntry(_('Include CI assignment'), config.misc.use_ci_assignment))
        list.append(getConfigListEntry(_('Descramble http streams'), config.streaming.descramble))
        self['key_red'] = Label(_('Exit'))
        self['key_green'] = Label(_('Save'))
        ConfigListScreen.__init__(self, list)
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'red': self.dontSaveAndExit,
         'green': self.saveAndExit,
         'cancel': self.dontSaveAndExit}, -1)

    def saveAndExit(self):
        if config.usage.dsemudmessages.value is not False:
            os.system('rm -rf /var/etc/.no_osd_messages')
        elif config.usage.dsemudmessages.value is not True:
            os.system('touch /var/etc/.no_osd_messages')
        if config.usage.messageYesPmt.value is not False:
            os.system('rm -rf /var/etc/.no_pmt_tmp')
        elif config.usage.messageYesPmt.value is not True:
            os.system('touch /var/etc/.no_pmt_tmp')
        for x in self['config'].list:
            x[1].save()

        config.usage.save()
        self.close()

    def dontSaveAndExit(self):
        for x in self['config'].list:
            x[1].cancel()

        self.close()


config.infobar = ConfigSubsection()
config.infobar.weatherEnabled = ConfigYesNo(default=True)
config.infobar.permanentClockPosition = ConfigSelection(choices=['<>'], default='<>')
config.infobar.Ecn = ConfigYesNo(default=True)
config.infobar.CamName = ConfigYesNo(default=True)
config.infobar.NetInfo = ConfigYesNo(default=True)
config.infobar.EcmInfo = ConfigYesNo(default=True)
config.infobar.CryptoBar = ConfigYesNo(default=True)

class EGInfoBarSetup(Screen, ConfigListScreen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skinName = ['Setup']
        Screen.setTitle(self, _('Infobar Setup'))
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self['description'] = Label(_('* = Restart Required'))
        self['key_red'] = Label(_('Exit'))
        self['key_green'] = Label(_('Save'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'green': self.keySave,
         'back': self.keyCancel,
         'red': self.keyCancel}, -2)
        self.list.append(getConfigListEntry(_('1st infobar timeout'), config.usage.infobar_timeout))
        self.list.append(getConfigListEntry(_('Show 2nd infobar'), config.usage.show_second_infobar))
        self.list.append(getConfigListEntry(_('Enable OK for channel selection'), config.usage.okbutton_mode))
        self.list.append(getConfigListEntry(_('Enable animation for infobar'), config.misc.enableAnimationInfobar))
        self.list.append(getConfigListEntry(_('Enable animation for moviebar'), config.misc.enableAnimationInfobarMovie))
        self.list.append(getConfigListEntry(_('Enable volume control with LEFT/RIGHT arrow buttons'), config.usage.volume_instead_of_channelselection))
        self.list.append(getConfigListEntry(_('Enable zapping with UP/DOWN arrow buttons'), config.usage.zap_with_arrow_buttons))
        self.list.append(getConfigListEntry(_('Infobar frontend data source'), config.usage.infobar_frontend_source))
        self.list.append(getConfigListEntry(_('Show PVR status in Movie Player'), config.usage.show_event_progress_in_servicelist))
        self.list.append(getConfigListEntry(_('Show channel number in infobar'), config.usage.show_infobar_channel_number))
        self.list.append(getConfigListEntry(_('Show infobar on channel change'), config.usage.show_infobar_on_zap))
        self.list.append(getConfigListEntry(_('Show infobar on skip forward/backward'), config.usage.show_infobar_on_skip))
        self.list.append(getConfigListEntry(_('Show infobar on event change'), config.usage.movieplayer_pvrstate))
        self.list.append(getConfigListEntry(_('Show infobar picons'), config.usage.showpicon))
        self.list.append(getConfigListEntry(_('Show Source Info'), config.infobar.Ecn))
        self.list.append(getConfigListEntry(_('Show SoftCam name'), config.infobar.CamName))
        self.list.append(getConfigListEntry(_('Show Netcard Info'), config.infobar.NetInfo))
        self.list.append(getConfigListEntry(_('Show ECM-Info'), config.infobar.EcmInfo))
        self.list.append(getConfigListEntry(_('Show Crypto-Bar'), config.infobar.CryptoBar))
        self.list.append(getConfigListEntry(_('Show EIT now/next in infobar'), config.usage.show_eit_nownext))
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def keySave(self):
        for x in self['config'].list:
            x[1].save()

        self.close()

    def keyCancel(self):
        for x in self['config'].list:
            x[1].cancel()

        self.close()


class EGClockSetup(Screen, ConfigListScreen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skinName = ['Setup']
        Screen.setTitle(self, _('Permanental Clock Setup'))
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self['description'] = Label(_('* = Restart Required'))
        self['key_red'] = Label(_('Exit'))
        self['key_green'] = Label(_('Save'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'green': self.keySave,
         'back': self.keyCancel,
         'red': self.keyCancel}, -2)
        self.list.append(getConfigListEntry(_('Show permanental clock'), config.plugins.PermanentClock.enabled))
        self.list.append(getConfigListEntry(_('\tSet clock position'), config.infobar.permanentClockPosition))
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.handleKeysLeftAndRight()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.handleKeysLeftAndRight()

    def handleKeysLeftAndRight(self):
        sel = self['config'].getCurrent()[1]
        if sel == config.infobar.permanentClockPosition:
            pClock.dialog.hide()
            self.session.openWithCallback(self.positionerCallback, PermanentClockPositioner)

    def positionerCallback(self, callback = None):
        pClock.showHide()

    def keySave(self):
        for x in self['config'].list:
            x[1].save()

        if pClock.dialog is None:
            pClock.gotSession(self.session)
        if config.plugins.PermanentClock.enabled.value == True:
            pClock.showHide()
        if config.plugins.PermanentClock.enabled.value == False:
            pClock.showHide()
        self.close()
        return

    def keyCancel(self):
        for x in self['config'].list:
            x[1].cancel()

        self.close()


class EGUpdateSetup(Screen, ConfigListScreen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skinName = ['Setup']
        Screen.setTitle(self, _('Update Setup'))
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self['description'] = Label(_('* = Restart Required'))
        self['key_red'] = Label(_('Exit'))
        self['key_green'] = Label(_('Save'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'green': self.keySave,
         'back': self.keyCancel,
         'save': self.keyCancel}, -2)
        self.list.append(getConfigListEntry(_('Prioritize updates of packages (--force-overwrite)'), config.usage.use_force_overwrite))
        self.list.append(getConfigListEntry(_('Use package maintainer config files'), config.usage.use_package_conffile))
        self.list.append(getConfigListEntry(_('Show popup message when update available'), config.usage.show_notification_for_updates))
        self.list.append(getConfigListEntry(_('Check update every (hours)'), config.usage.check_for_updates))
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def keySave(self):
        for x in self['config'].list:
            x[1].save()

        self.close()

    def keyCancel(self):
        for x in self['config'].list:
            x[1].cancel()

        self.close()


class EGGreenPanel(Screen):
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        skin = '<screen name="EGGreenPanel" position="center,100" size="1080,920" title="EGAMI Green Panel" >\n\t\t\t\t<widget source="list" render="Listbox" position="10,0" size="1070,830" zPosition="2" scrollbarMode="showOnDemand" transparent="1">\n\t\t\t\t      <convert type="TemplatedMultiContent">\n\t\t\t\t\t  {"template": [\n\t\t\t\t\t  MultiContentEntryText(pos = (175, 0), size = (950, 35), font=0, text = 0),\n\t\t\t\t\t  MultiContentEntryText(pos = (175, 38), size = (950, 28), font=1, text = 1),\n\t\t\t\t\t  MultiContentEntryPixmapAlphaTest(pos = (6, 5), size = (150, 60), png = 2),\n\t\t\t\t\t  ],\n\t\t\t\t\t  "fonts": [gFont("Regular", 32),gFont("Regular", 26)],\n\t\t\t\t\t  "itemHeight": 80\n\t\t\t\t\t  }\n\t\t\t\t      </convert>\n\t\t\t\t</widget>\n\t\t\t\t<ePixmap position="40,854" size="100,40" zPosition="0" pixmap="buttons/red.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<ePixmap position="220,854" size="100,40" zPosition="0" pixmap="buttons/green.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<ePixmap position="430,854" size="100,40" zPosition="0" pixmap="buttons/yellow.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<ePixmap position="740,854" size="100,40" zPosition="0" pixmap="buttons/blue.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<widget name="key_red" position="80,854" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="red" transparent="1" />\n\t\t\t\t<widget name="key_green" position="260,854" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="green" transparent="1" />\n\t\t\t\t<widget name="key_yellow" position="470,854" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="yellow" transparent="1" />\n\t\t\t\t<widget name="key_blue" position="780,854" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="blue" transparent="1" />\n\t\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen name="EGGreenPanel" position="center,center" size="700,560" title="EGAMI Green Panel" >\n\t\t\t\t<widget name="Addons" zPosition="4" position="50,520" size="140,40" halign="left" font="Regular;22" transparent="1" />\n\t\t\t\t<widget name="Extras" zPosition="4" position="230,520" size="140,40" halign="left" font="Regular;22" transparent="1" />\n\t\t\t\t<widget name="File Mode" zPosition="4" position="400,520" size="140,40" halign="left" font="Regular;22" transparent="1" />\n\t\t\t\t<widget name="Scripts" zPosition="4" position="580,520" size="140,40" halign="left" font="Regular;22" transparent="1"  />\n\t\t\t\t<ePixmap name="key_red_png" pixmap="skin_default/buttons/button_red.png" position="20,520" size="140,40" alphatest="on" />\n\t\t\t\t<ePixmap name="key_green_png" pixmap="skin_default/buttons/button_green.png" position="200,520" size="140,40" alphatest="on" />\n\t\t\t\t<ePixmap name="key_yellow_png" pixmap="skin_default/buttons/button_yellow.png" position="370,520" size="140,40" alphatest="on" />\n\t\t\t\t<ePixmap name="key_blue_png" pixmap="skin_default/buttons/button_blue.png" position="550,520" size="140,40" alphatest="on" />\n\t\t\t\t<widget source="list" render="Listbox" position="10,0" size="680,510" zPosition="2" scrollbarMode="showOnDemand" transparent="1">\n\t\t\t\t      <convert type="TemplatedMultiContent">\n\t\t\t\t\t  {"template": [\n\t\t\t\t\t  MultiContentEntryText(pos = (125, 0), size = (650, 24), font=0, text = 0),\n\t\t\t\t\t  MultiContentEntryText(pos = (125, 24), size = (650, 24), font=1, text = 1),\n\t\t\t\t\t  MultiContentEntryPixmapAlphaTest(pos = (6, 5), size = (100, 40), png = 2),\n\t\t\t\t\t  ],\n\t\t\t\t\t  "fonts": [gFont("Regular", 24),gFont("Regular", 20)],\n\t\t\t\t\t  "itemHeight": 50\n\t\t\t\t\t  }\n\t\t\t\t      </convert>\n\t\t\t\t</widget>\n\t\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('EGAMI Green Panel'))
        self.list = []
        self['list'] = List(self.list)
        self['key_red'] = Label(_('Addons'))
        self['key_green'] = Label(_('Panel'))
        self['key_yellow'] = Label(_('File Commander'))
        self['key_blue'] = Label(_('Scripts'))
        self.updateList()
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.save,
         'back': self.close,
         'red': self.Addons,
         'yellow': self.File,
         'green': self.Extras,
         'blue': self.Script}, -1)
        self.onFirstExecBegin.append(self.checkWarnings)

    def save(self):
        self.run()

    def run(self):
        mysel = self['list'].getCurrent()
        if mysel:
            plugin = mysel[3]
            plugin(session=self.session)

    def updateList(self):
        self.list = []
        self.pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
        for plugin in self.pluginlist:
            if plugin.icon is None:
                png = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/icons/plugin.png'))
            else:
                png = plugin.icon
            res = (plugin.name,
             plugin.description,
             png,
             plugin)
            self.list.append(res)

        self['list'].list = self.list
        return

    def reloadPluginList(self):
        plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
        self.updateList()

    def checkWarnings(self):
        if len(plugins.warnings):
            text = _('Some plugins are not available:\n')
            for pluginname, error in plugins.warnings:
                text += _('%s (%s)\n') % (pluginname, error)

            plugins.resetWarnings()
            self.session.open(MessageBox, text=text, type=MessageBox.TYPE_WARNING)

    def Addons(self):
        m = checkkernel()
        if m == 1:
            from EGAMI.EGAMI_addon_manager import EGAddonMenu
            self.session.openWithCallback(self.reloadPluginList, EGAddonMenu)
        else:
            self.session.open(MessageBox, _('Sorry: Wrong image in flash found. You have to install in flash EGAMI Image'), MessageBox.TYPE_INFO, 3)

    def File(self):
        m = checkkernel()
        if m == 1:
            from Plugins.Extensions.FileCommander.plugin import FileCommanderScreen
            self.session.open(FileCommanderScreen)
        else:
            self.session.open(MessageBox, _('Sorry: Wrong image in flash found. You have to install in flash EGAMI Image'), MessageBox.TYPE_INFO, 3)

    def Script(self):
        m = checkkernel()
        if m == 1:
            from EGAMI.EGAMI_main import EGScript
            self.session.open(EGScript)
        else:
            self.session.open(MessageBox, _('Sorry: Wrong image in flash found. You have to install in flash EGAMI Image'), MessageBox.TYPE_INFO, 3)

    def Extras(self):
        m = checkkernel()
        if m == 1:
            from EGAMI.EGAMI_main import EgamiMainPanel
            self.session.open(EgamiMainPanel)
        else:
            self.session.open(MessageBox, _('Sorry: Wrong image in flash found. You have to install in flash EGAMI Image'), MessageBox.TYPE_INFO, 3)


class EGKernelModules(Screen, ConfigListScreen):
    skin = '<screen position="240,190" size="800,340" title="EGAMI Kernel Modules Setup">\n\t\t<widget name="config" position="10,20" size="780,280" scrollbarMode="showOnDemand" />\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="200,293" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="440,293" size="140,40" alphatest="on" />\n\t\t<widget name="key_red" position="200,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="446,290" zPosition="1" size="200,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skinName = ['EGKernelModules', 'Setup']
        Screen.setTitle(self, _('Kernel Modules Setup'))
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self['key_red'] = Label(_('Exit'))
        self['key_green'] = Label(_('Save'))
        self['key_yellow'] = Label(_('Active Modules'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.close,
         'green': self.saveMyconf,
         'yellow': self.showMod,
         'back': self.close})
        self.updateList()

    def showMod(self):
        self.session.open(EGKernelInfo)

    def updateList(self):
        self.ftdi_sio = NoSave(ConfigYesNo(default=False))
        self.pl2303 = NoSave(ConfigYesNo(default=False))
        self.tun = NoSave(ConfigYesNo(default=False))
        if fileExists('/usr/bin/egami_modules.sh'):
            f = open('/usr/bin/egami_modules.sh', 'r')
            for line in f.readlines():
                if line.find('ftdi_sio') != -1:
                    self.ftdi_sio.value = True
                elif line.find('pl2303') != -1:
                    self.pl2303.value = True
                elif line.find('tun') != -1:
                    self.tun.value = True

            f.close()
        res = getConfigListEntry(_('Smargo & other Usb card readers chipset ftdi:'), self.ftdi_sio)
        self.list.append(res)
        res = getConfigListEntry(_('Other Usb card readers chipset pl2303:'), self.pl2303)
        self.list.append(res)
        res = getConfigListEntry(_('Tun module needed for Openvpn:'), self.tun)
        self.list.append(res)
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def saveMyconf(self):
        l1 = ''
        l2 = ''
        l3 = ''
        l4 = ''
        if self.ftdi_sio.value == True:
            l2 = 'modprobe ftdi_sio'
            os.system(l2)
        else:
            os.system('rmmod ftdi_sio')
        if self.pl2303.value == True:
            l3 = 'modprobe pl2303'
            os.system(l3)
        else:
            os.system('rmmod pl2303')
        if self.tun.value == True:
            l4 = 'modprobe tun'
            os.system(l4)
        else:
            os.system('rmmod tun')
        out = open('/usr/bin/egami_modules.sh', 'w')
        out.write('#!/bin/sh\n')
        if l1 != '':
            out.write(l1 + '\n')
        if l2 != '':
            out.write(l2 + '\n')
        if l3 != '':
            out.write(l3 + '\n')
        if l4 != '':
            out.write(l4 + '\n')
        out.close()
        os.system('chmod 0755 /usr/bin/egami_modules.sh')
        self.close()


class EGAMISpeedUpWizard(Screen, ConfigListScreen):
    skin = '<screen name="EGAMISpeedUpWizard" position="center,center" size="902,570" title="EGAMI Speed Up">\n\t\t\t<widget name="description" position="10,10" size="882,60" font="Regular;20" valign="top" transparent="1"/>\n\t\t\t<widget name="config" position="30,70" size="840,450" scrollbarMode="showOnDemand"/>\n\t\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="200,530" size="140,40" alphatest="on"/>\n\t\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="550,530" size="140,40" alphatest="on"/>\n\t\t\t<widget name="key_red" position="200,530" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t<widget name="key_green" position="550,530" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>\n\t\t  </screen>'

    def __init__(self, session, firstrun = False):
        Screen.__init__(self, session)
        self.skinName = ['EGAMISpeedUpWizard', 'Setup']
        Screen.setTitle(self, _('EGAMI Plugins Speed Up'))
        self.firstrun = firstrun
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self['description'] = Label(_('Retrieving data ...'))
        self['key_green'] = Label(_('Save'))
        self['key_red'] = Label(_('Exit'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'green': self.saveMypoints,
         'red': self.close,
         'back': self.close})
        self.pluglist = []
        self.pluglist.append(['IPTV Player - Polish', 'enigma2-plugin-extensions-iptvplayer'])
        self.pluglist.append(['FFMpeg', 'ffmpeg'])
        self.pluglist.append(['ExtPlayer3 - ServiceApp', 'enigma2-plugin-extensions-serviceapp'])
        self.pluglist.append(['XMLTV EPG Import', 'enigma2-plugin-extensions-epgimport'])
        self.pluglist.append(['CrossEPG', 'enigma2-plugin-systemplugins-crossepg'])
        self.pluglist.append(['MediaStream - Italy', 'GuidaTv'])
        if getMachineBuild() in 'vusolo4k':
            self.pluglist.append(['Chromium Browser & HbbTV', 'enigma2-plugin-extensions-webkithbbtv'])
        if getStbArch() in 'mipsel':
            self.pluglist.append(['Opera browser & HbbTV', 'enigma2-plugin-extensions-hbbtv'])
        self.pluglist.append(['Video Enhanced Setup', 'enigma2-plugin-systemplugins-videoenhancement'])
        self.pluglist.append(['SeasonDream Player - Russia', 'enigma2-plugin-seasondream'])
        self.pluglist.append(['Media Portal', 'enigma2-plugin-extensions-mediaportal-gst1'])
        self.pluglist.append(['Enhanced Movie Center', 'enigma2-plugin-extensions-enhancedmoviecenter'])
        self.pluglist.append(['DVD Player', 'enigma2-plugin-extensions-dvdplayer'])
        self.pluglist.append(['Subtitle Player', 'enigma2-plugin-extensions-subtitleplayer'])
        self.pluglist.append(['Remote Channel Stream - stream from other box', 'enigma2-plugin-extensions-remotechannelstreamconverter'])
        self.pluglist.append(['4G LTE Manager', 'enigma2-plugin-systemplugins-3gmodemmanager'])
        self.pluglist.append(['AutoBouquetsMaker', 'enigma2-plugin-systemplugins-autobouquetsmaker'])
        self.pluglist.append(['Fast Scan', 'enigma2-plugin-systemplugins-fastscan'])
        self.pluglist.append(['YouTube', 'enigma2-plugin-extensions-youtube'])
        self.pluglist.append(['Torrent Client', 'enigma2-plugin-extensions-transmission'])
        self.pluglist.append(['Sat>Ip', 'enigma2-plugin-extensions-satipclient'])
        self.pluglist.append(['EGAMI Weather', 'enigma2-plugin-extensions-accuweather'])
        self.pluglist.append(['Tuner Server', 'enigma2-plugin-extensions-tunerserver'])
        self.pluglist.append(['Dlna Browser (Djmount Client)', 'djmount'])
        self.pluglist.append(['MiniDlna UPnP Server', 'ushare'])
        self.pluglist.append(['Mediatomb UPnP Server (alternative)', 'mediatomb'])
        self.pluglist.append(['OpenVPN', 'openvpn'])
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.updateFeed2)
        self.updateFeed()

    def updateFeed(self):
        self.activityTimer.start(3)

    def updateFeed2(self):
        self.activityTimer.stop()
        if not fileExists('/var/volatile/tmp/official-all'):
            ret = os.system('opkg update')
        self.updateList()

    def updateList(self):
        self.list = []
        if fileExists('/tmp/egspeed.tmp'):
            os.remove('/tmp/egspeed.tmp')
        for plug in self.pluglist:
            cmd = 'opkg status %s >> /tmp/egspeed.tmp' % plug[1]
            os.system(cmd)

        for plug in self.pluglist:
            item = NoSave(ConfigSelection(default='Enabled', choices=[('Enabled', _('Enabled')), ('Disabled', _('Disabled'))]))
            installed = self.checkInst(plug[1])
            if installed == True:
                item.value = 'Enabled'
            else:
                item.value = 'Disabled'
            res = getConfigListEntry(_(plug[0]), item)
            self.list.append(res)

        self['config'].list = self.list
        self['config'].l.setList(self.list)
        self['description'].setText(_("Please disable ALL the plugins you don't need to use.\nThis will Speed Up Image Performance."))

    def checkInst(self, name):
        ret = False
        f = open('/tmp/egspeed.tmp', 'r')
        for line in f.readlines():
            if line.find(name) != -1:
                ret = True
                break

        f.close()
        return ret

    def saveMypoints(self):
        self.mycmdlist = []
        for x in self['config'].list:
            cmd = self.buildcoM(x[0], x[1].value)
            if cmd != '':
                self.mycmdlist.append(cmd)
                if cmd == 'opkg remove --force-depends --force-remove enigma2-plugin-seasondream':
                    self.mycmdlist.append('rm -rf /usr/lib/enigma2/python/Plugins/Extensions/Seasondream')
                elif cmd == 'opkg remove --force-depends --force-remove enigma2-plugin-extensions-hbbtv':
                    self.mycmdlist.append('opkg remove --force-depends --force-remove vuplus-opera-browser-util vuplus-opera-dumpait')
                    self.mycmdlist.append('rm -rf /usr/local/hbb-browser')
                elif cmd == 'opkg remove --force-depends --force-remove enigma2-plugin-extensions-vuplus-kodi':
                    self.mycmdlist.append('rm -rf /usr/lib/enigma2/python/Plugins/Extensions/Kodi')
                    self.mycmdlist.append('opkg remove --force-depends --force-remove enigma2-plugin-extensions-subssupport')
                elif cmd == 'opkg remove --force-depends --force-remove webkit-hbbtv-browser-vusolo4k':
                    self.mycmdlist.append('opkg remove --force-depends --force-remove enigma2-plugin-extensions-chromium vuplus-webkithbbtv-dumpait enigma2-plugin-extensions-webkithbbtv')
                    self.mycmdlist.append('rm -rf /usr/lib/enigma2/python/Plugins/Extensions/Chromium')
                    self.mycmdlist.append('rm -rf /usr/lib/enigma2/python/Plugins/Extensions/WebkitHbbTV')
                elif cmd == 'opkg install webkit-hbbtv-browser-vusolo4k':
                    self.mycmdlist.append('opkg install enigma2-plugin-extensions-chromium')
                elif cmd == 'opkg install enigma2-plugin-extensions-hbbtv':
                    self.mycmdlist = []
                    self.mycmdlist.append('opkg install enigma2-plugin-extensions-hbbtv')

        if len(self.mycmdlist) > 0:
            if self.firstrun == True:
                self.session.open(Console, title=_('EGAMI Speed Up'), cmdlist=self.mycmdlist, finishedCallback=self.allDone, closeOnSuccess=True)
            else:
                self.session.open(Console, title=_('EGAMI Speed Up'), cmdlist=self.mycmdlist, finishedCallback=self.allDone, closeOnSuccess=False)
        else:
            self.close()

    def buildcoM(self, name, what):
        cmd = ''
        for plug in self.pluglist:
            if plug[0] == name:
                installed = self.checkInst(plug[1])
                if what == 'Enabled' and installed == False:
                    cmd = 'opkg install %s' % plug[1]
                elif what == 'Disabled' and installed == True:
                    cmd = 'opkg remove --force-depends --force-remove %s' % plug[1]
                break

        return cmd

    def allDone(self):
        if self.firstrun == True:
            self.close()
        else:
            mybox = self.session.openWithCallback(self.hrestEn, MessageBox, _('Enigma2 will be now restarted for the changes to take effect.\nPress ok to continue'), MessageBox.TYPE_INFO)
            mybox.setTitle(_('Info'))

    def hrestEn(self, answer):
        self.session.open(TryQuitMainloop, 3)


class EGAMISkinWizard(Screen, ConfigListScreen):
    skin = '<screen name="EGAMISkinWizard" position="center,center" size="902,570" title="EGAMI Skins Wizard">\n\t\t\t<widget name="description" position="10,10" size="882,60" font="Regular;20" valign="top" transparent="1"/>\n\t\t\t<widget name="config" position="30,70" size="840,450" scrollbarMode="showOnDemand"/>\n\t\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="200,530" size="140,40" alphatest="on"/>\n\t\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="550,530" size="140,40" alphatest="on"/>\n\t\t\t<widget name="key_red" position="200,530" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t<widget name="key_green" position="550,530" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>\n\t\t  </screen>'

    def __init__(self, session, firstrun = False):
        Screen.__init__(self, session)
        self.skinName = ['EGAMISkinsWizard', 'Setup']
        Screen.setTitle(self, _('EGAMI Skins Wizard'))
        self.firstrun = firstrun
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self['description'] = Label(_('Retrieving data ...'))
        self['key_red'] = Label(_('Install'))
        self['key_green'] = Label(_('Cancel'))
        self['key_yellow'] = Label(_('Preview'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.saveMypoints,
         'green': self.close,
         'back': self.close})
        self.pluglist = [['PinguTM Full HD', 'http://enigma-spark.com/egami/skins/PFHD.tar.gz'],
         ['NG FUll HD by PinguTM', 'http://enigma-spark.com/egami/skins/NGFHD.tar.gz'],
         ['eDreamy FullHD', 'enigma2-plugin-skins.egami-edreamyfhd'],
         ['Kraven HD', 'enigma2-plugin-skins-kravenhd'],
         ['PLiHD', 'enigma2-plugin-skins-pli-hd'],
         ['PLiHD Full Night', 'enigma2-plugin-skins-pli-hd-fullnight'],
         ['MyMetrix HD', 'enigma2-plugin-skins-metrix-atv'],
         ['BlackSpirit HD', 'enigma2-plugin-skins-blackspirit.hd'],
         ['Seven HD', 'enigma2-plugin-skins-sevenhd'],
         ['MyMetrix Full HD', 'enigma2-plugin-skins-openvix-metrixfhd'],
         ['YouViX Blue Full HD', 'enigma2-plugin-skins-openvix-youvix-blue'],
         ['YouViX Green Full HD', 'enigma2-plugin-skins-openvix-youvix-green'],
         ['YouViX Purple Full HD', 'enigma2-plugin-skins-openvix-youvix-purple']]
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.updateFeed2)
        self.updateFeed()

    def updateFeed(self):
        self.activityTimer.start(3)

    def updateFeed2(self):
        self.activityTimer.stop()
        if not fileExists('/var/volatile/tmp/official-all'):
            ret = os.system('opkg update')
        self.updateList()

    def updateList(self):
        self.list = []
        if fileExists('/tmp/egskin.tmp'):
            os.remove('/tmp/egskin.tmp')
        for plug in self.pluglist:
            cmd = 'opkg status %s >> /tmp/egskin.tmp' % plug[1]
            os.system(cmd)

        for plug in self.pluglist:
            item = NoSave(ConfigSelection(default='Enabled', choices=[('Enabled', _('Installed')), ('Disabled', _('Not Installed'))]))
            installed = self.checkInst(plug[1])
            if installed == True:
                item.value = 'Enabled'
            else:
                item.value = 'Disabled'
            res = getConfigListEntry(_(plug[0]), item)
            self.list.append(res)

        self['config'].list = self.list
        self['config'].l.setList(self.list)
        self['description'].setText(_("Please disable ALL the skins you don't need to use.\nThis will save free space in flash."))

    def checkInst(self, name):
        ret = False
        if name in 'http://enigma-spark.com/egami/skins/PFHD.tar.gz':
            if fileExists('/usr/share/enigma2/Pingu_FHD/skin.xml'):
                ret = True
        elif name in 'http://enigma-spark.com/egami/skins/NGFHD.tar.gz':
            if fileExists('/usr/share/enigma2/NG-FHD-Pingu/skin.xml'):
                ret = True
        else:
            f = open('/tmp/egskin.tmp', 'r')
            for line in f.readlines():
                if line.find(name) != -1:
                    ret = True
                    break

            f.close()
        return ret

    def saveMypoints(self):
        self.mycmdlist = []
        for x in self['config'].list:
            cmd = self.buildcoM(x[0], x[1].value)
            if cmd != '':
                self.mycmdlist.append(cmd)
                if cmd == 'opkg remove --force-depends --force-remove enigma2-plugin-seasondream':
                    self.mycmdlist.append('rm -rf /usr/lib/enigma2/python/Plugins/Extensions/Seasondream')

        if len(self.mycmdlist) > 0:
            if self.firstrun == True:
                self.session.open(Console, title=_('EGAMI Skin Wizard'), cmdlist=self.mycmdlist, finishedCallback=self.allDone, closeOnSuccess=True)
            else:
                self.session.open(Console, title=_('EGAMI Skin Wizard'), cmdlist=self.mycmdlist, finishedCallback=self.allDone, closeOnSuccess=False)
        else:
            self.close()

    def buildcoM(self, name, what):
        cmd = ''
        for plug in self.pluglist:
            if plug[0] == name:
                installed = self.checkInst(plug[1])
                if what == 'Enabled' and installed == False:
                    if plug[1].startswith('http://enigma-spark.com/egami/skins'):
                        cmd = 'wget -q ' + plug[1] + ' -O /tmp/Addon.tgz;cd /; tar -xz -f /tmp/Addon.tgz'
                    else:
                        cmd = 'opkg install %s' % plug[1]
                elif what == 'Disabled' and installed == True:
                    if plug[1] == 'http://enigma-spark.com/egami/skins/PFHD.tar.gz':
                        if fileExists('/usr/share/enigma2/Pingu_FHD/skin.xml'):
                            cmd = 'rm -rf /usr/share/enigma2/Pingu_FHD'
                    elif plug[1] == 'http://enigma-spark.com/egami/skins/NGFHD.tar.gz':
                        if fileExists('/usr/share/enigma2/NG-FHD-Pingu/skin.xml'):
                            cmd('rm -rf /usr/share/enigma2/NG-FHD-Pingu')
                    else:
                        cmd = 'opkg remove --force-depends --force-remove %s' % plug[1]
                break

        return cmd

    def allDone(self):
        if self.firstrun == True:
            self.close()
