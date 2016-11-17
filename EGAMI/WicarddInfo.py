from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from enigma import eTimer
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Sources.List import List
from Components.Pixmap import Pixmap
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config, ConfigText, ConfigNumber, NoSave
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists
from os import system
from re import sub
pluginpath = '/usr/lib/enigma2/python/Plugins/Extensions/WicarddInfo'

class EGAMIWicarddMain(Screen):
    skin = '<screen position="center,center" size="390,360" title="Wicardd Info">\n\t\t    <widget source="list" render="Listbox" position="20,15" size="350,320" scrollbarMode="showOnDemand" >\n\t\t    <convert type="TemplatedMultiContent">\n\t\t      {"template": [MultiContentEntryText(pos = (50, 1), size = (300, 36), flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0),\n\t\t\t\t    MultiContentEntryPixmapAlphaTest(pos = (4, 2), size = (34, 34), png = 1),],\n\t\t\t\t    "fonts": [gFont("Regular", 24)],"itemHeight": 36\n\t\t      } </convert></widget>\n\t\t    <widget name="Linconn" position="0,325" size="390,35" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" />\n\t\t    </screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['list'] = List(self.list)
        self.updateList()
        self['Linconn'] = Label('Wait please connection to Wicardd in progress ...')
        self['Linconn'].hide()
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.KeyOk,
         'back': self.close})

    def updateList(self):
        self.list = []
        mypath = '/usr/share/enigma2/skin_default/egami_icons'
        mypixmap = mypath + '/ccc_clients.png'
        png = LoadPixmap(mypixmap)
        name = 'Reader 0'
        idx = 2
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + '/ccc_servers.png'
        png = LoadPixmap(mypixmap)
        name = 'Reader 1'
        idx = 3
        res = (name, png, idx)
        self.list.append(res)
        mypixmap = mypath + '/ccc_providers.png'
        png = LoadPixmap(mypixmap)
        name = 'Statistics'
        idx = 4
        res = (name, png, idx)
        self.list.append(res)
        self['list'].list = self.list

    def KeyOk(self):
        self.sel = self['list'].getCurrent()
        if self.sel:
            self.sel
            self.sel = self.sel[2]
        else:
            self.sel
        if self.sel == 0:
            self.session.open(EGAMIWicarddInfo)
        elif self.sel == 1:
            self.session.open(EGAMIWicarddUs)
        elif self.sel == 2:
            self.session.open(EGAMIWicarddReader0)
        elif self.sel == 3:
            self.session.open(EGAMIWicarddReader1)
        elif self.sel == 4:
            self.session.open(EGAMIWicarddStat)


class EGAMIWicarddReader0(Screen):
    skin = '\n\t<screen position="center,center" size="640,450" title="Wicardd Main Info">\n\t\t<widget name="infotext" position="10,10" size="620,410" font="Regular;22" halign="center" />\n\t\t<widget name="Linconn" position="0,420" size="680,30" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" />\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['infotext'] = Label()
        self['Linconn'] = Label('Wait please, while Wicardd reply ....')
        self['actions'] = ActionMap(['WizardActions'], {'ok': self.close,
         'back': self.close})
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.CCCconn)
        self.activityTimer.start(1, False)
        self.onClose.append(self.delTimer)

    def delTimer(self):
        del self.activityTimer

    def CCCconn(self):
        self.activityTimer.stop()
        url = 'http://127.0.0.1:8081/reader0'
        cmd = 'wget -O /tmp/cpanel.tmp ' + url
        rc = system(cmd)
        strview = ''
        if fileExists('/tmp/cpanel.tmp'):
            fileExists('/tmp/cpanel.tmp')
            f = open('/tmp/cpanel.tmp', 'r')
            for line in f.readlines():
                line = line.strip()
                line = line.replace('\n', '')
                line = line.replace('MainStatistics', 'Reader /dev/sci0')
                line = line.replace('R0[tuxbox]', '\n\n')
                line = line.replace('CAID', '\n\nCAID')
                line = line.replace('Back', '\n\n')
                line = line.replace('<br/>', '\n')
                line = line.replace('<br><br><br><br>', '\n\n')
                line = line.replace('</br>', '\n')
                line = sub('<br(\\s+/)?>', '\n', line)
                line = sub('<(.*?)>', '', line)
                strview += line

            f.close()
            system('rm -f /tmp/cpanel.tmp')
        else:
            fileExists('/tmp/cpanel.tmp')
            mybox = self.session.open(MessageBox, 'Sorry. Connection to Wicardd refused.\nCheck that Wicardd is running and your webinfo settings.', MessageBox.TYPE_INFO)
            mybox.setTitle('Info')
        self['Linconn'].hide()
        if strview.find('Version:') != -1:
            pos = strview.find('Version:')
            strview = '\nWelcome to Wicardd Info Plugin v. 0.2.\n\nWicardd ' + strview[pos:]
        self['infotext'].setText(strview)


class EGAMIWicarddReader1(Screen):
    skin = '\n\t<screen position="center,center" size="640,450" title="Wicardd Main Info">\n\t\t<widget name="infotext" position="10,10" size="620,410" font="Regular;22" halign="center" />\n\t\t<widget name="Linconn" position="0,420" size="680,30" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" />\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['infotext'] = Label()
        self['Linconn'] = Label('Wait please, while Wicardd reply ....')
        self['actions'] = ActionMap(['WizardActions'], {'ok': self.close,
         'back': self.close})
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.CCCconn)
        self.activityTimer.start(1, False)
        self.onClose.append(self.delTimer)

    def delTimer(self):
        del self.activityTimer

    def CCCconn(self):
        self.activityTimer.stop()
        url = 'http://127.0.0.1:8081/reader1'
        cmd = 'wget -O /tmp/cpanel.tmp ' + url
        rc = system(cmd)
        strview = ''
        if fileExists('/tmp/cpanel.tmp'):
            fileExists('/tmp/cpanel.tmp')
            f = open('/tmp/cpanel.tmp', 'r')
            for line in f.readlines():
                line = line.strip()
                line = line.replace('\n', '')
                line = line.replace('MainStatistics', 'Reader /dev/sci1')
                line = line.replace('R0[tuxbox]', '\n\n')
                line = line.replace('CAID', '\n\nCAID')
                line = line.replace('Back', '\n\n')
                line = line.replace('<br/>', '\n')
                line = line.replace('<br><br><br><br>', '\n\n')
                line = line.replace('</br>', '\n')
                line = sub('<br(\\s+/)?>', '\n', line)
                line = sub('<(.*?)>', '', line)
                strview += line

            f.close()
            system('rm -f /tmp/cpanel.tmp')
        else:
            fileExists('/tmp/cpanel.tmp')
            mybox = self.session.open(MessageBox, 'Sorry. Connection to Wicardd refused.\nCheck that Wicardd is running and your webinfo settings.', MessageBox.TYPE_INFO)
            mybox.setTitle('Info')
        self['Linconn'].hide()
        if strview.find('Version:') != -1:
            pos = strview.find('Version:')
            strview = '\nWelcome to Wicardd Info Plugin v. 0.2.\n\nWicardd ' + strview[pos:]
        self['infotext'].setText(strview)


class EGAMIWicarddStat(Screen):
    skin = '\n\t<screen position="center,center" size="640,450" title="Wicardd Stat Info">\n\t\t<widget name="infotext" position="10,10" size="620,410" font="Regular;22" halign="center" />\n\t\t<widget name="Linconn" position="0,420" size="680,30" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" />\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['infotext'] = Label()
        self['Linconn'] = Label('Wait please, while Wicardd reply ....')
        self['actions'] = ActionMap(['WizardActions'], {'ok': self.close,
         'back': self.close})
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.CCCconn)
        self.activityTimer.start(1, False)
        self.onClose.append(self.delTimer)

    def delTimer(self):
        del self.activityTimer

    def CCCconn(self):
        self.activityTimer.stop()
        url = 'http://127.0.0.1:8081/stat'
        cmd = 'wget -O /tmp/cpanel.tmp ' + url
        rc = system(cmd)
        strview = ''
        if fileExists('/tmp/cpanel.tmp'):
            fileExists('/tmp/cpanel.tmp')
            f = open('/tmp/cpanel.tmp', 'r')
            for line in f.readlines():
                line = line.strip()
                line = line.replace('\n', '')
                line = line.replace('MainStatistics', '\n\n')
                line = line.replace('Reader', '\n\nReader  ')
                line = line.replace('R0[tuxbox]', '\n\nR0[tuxbox]  ')
                line = line.replace('R1[tuxbox]', '\nR1[tuxbox]  ')
                line = line.replace('R2[newcamd525]', '\nR2[newcamd525]  ')
                line = line.replace('R3[newcamd525]', '\nR3[newcamd525]  ')
                line = line.replace('R4[newcamd525]', '\nR4[newcamd525]  ')
                line = line.replace('R5[newcamd525]', '\nR5[newcamd525]  ')
                line = line.replace('Server', '\n\nServer  ')
                line = line.replace('bytes', '  bytes ')
                line = line.replace('\n\nS0[newcamd525]', '\nS2[newcamd525]  ')
                line = line.replace('S1[newcamd525]', '\nS3[newcamd525]  ')
                line = line.replace('S2[newcamd525]', '\nS4[newcamd525]  ')
                line = line.replace('S3[newcamd525]', '\nS5[newcamd525]  ')
                line = line.replace('<br/>', '\n')
                line = line.replace('<br><br><br><br>', '\n\n')
                line = line.replace('</br>', '\n')
                line = sub('<br(\\s+/)?>', '\n', line)
                line = sub('<(.*?)>', '', line)
                strview += line

            f.close()
            system('rm -f /tmp/cpanel.tmp')
        else:
            fileExists('/tmp/cpanel.tmp')
            mybox = self.session.open(MessageBox, 'Sorry. Connection to Wicardd refused.\nCheck that Wicardd is running and your webinfo settings.', MessageBox.TYPE_INFO)
            mybox.setTitle('Info')
        self['Linconn'].hide()
        if strview.find('Version:') != -1:
            pos = strview.find('Version:')
            strview = '\nWelcome to Wicardd Info Plugin v. 0.2.\n\nWicardd ' + strview[pos:]
        self['infotext'].setText(strview)
