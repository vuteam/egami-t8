from enigma import eTimer, getDesktop, getEnigmaVersionString
from Components.About import about
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from EGAMI.EGAMI_tools import runBackCmd, unload_modules, wyszukaj_re, checkkernel 
from Components.Button import Button
from Components.ActionMap import ActionMap, NumberActionMap
from Components.GUIComponent import *
from Components.MenuList import MenuList
from Components.Input import Input
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap, MultiPixmap
from Components.config import *
from Components.ConfigList import ConfigListScreen
from Components.SystemInfo import SystemInfo
from Components import Harddisk
from Tools.Directories import fileExists
from os import popen, system, listdir, chdir, mkdir, getcwd, rename as os_rename, remove as os_remove, path, makedirs, walk, statvfs, remove
from time import time, strftime, localtime
import commands
import datetime
from boxbranding import getBoxType, getMachineBrand, getMachineName, getDriverDate, getImageVersion, getImageBuild, getBrandOEM, getMachineBuild, getImageFolder, getMachineUBINIZE, getMachineMKUBIFS, getMachineMtdKernel, getMachineMtdRoot, getMachineKernelFile, getMachineRootFile, getImageFileSystem
VERSION = 'Version 7.2.X EGAMI'
HaveGZkernel = True
if getMachineBuild() in ('vusolo4k', 'spark', 'spark7162', 'hd51', 'hd52'):
    HaveGZkernel = False

def Freespace(dev):
    statdev = statvfs(dev)
    space = statdev.f_bavail * statdev.f_frsize / 1024
    print '[FULL BACKUP] Free space on %s = %i kilobytes' % (dev, space)
    return space


class EGAMIBackupPanel(Screen):
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        skin = '\n\t\t\t<screen name="EGAMIBackupPanel" position="center,center" size="1040,680" >\n\t\t\t\t<widget name="label1" position="10,10" size="840,30" zPosition="1" halign="center" font="Regular;32" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t\t<widget name="label2" position="10,80" size="840,290" zPosition="1" font="Regular;26" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t\t<widget name="label3" position="10,110" size="1020,290" zPosition="1" font="Regular;26" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t\t<widget name="list" itemHeight="50" font="Regular;28" position="10,170" size="840,290" scrollbarMode="showOnDemand"/>\n\t\t\t\t<ePixmap position="40,604" size="100,40" zPosition="0" pixmap="buttons/red.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<ePixmap position="200,604" size="100,40" zPosition="0" pixmap="buttons/green.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<ePixmap position="460,604" size="100,40" zPosition="0" pixmap="buttons/yellow.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<widget name="key_red" position="80,604" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="red" transparent="1" />\n\t\t\t\t<widget name="key_green" position="240,604" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="green" transparent="1" />\n\t\t\t\t<widget name="key_yellow" position="510,604" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="yellow" transparent="1" />\n\t\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen name="EGAMIBackupPanel" position="center,center" size="902,380" title="EGAMI Image Backup Panel - STEP 1" >\n\t\t\t      <widget name="label1" position="10,10" size="840,30" zPosition="1" halign="center" font="Regular;25" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t      <widget name="label2" position="10,80" size="840,290" zPosition="1" font="Regular;20" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t      <widget name="label3" position="10,110" size="840,290" zPosition="1" font="Regular;20" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t      <widget name="list" position="10,170" size="840,290" scrollbarMode="showOnDemand"/>\n\t\t\t      <ePixmap pixmap="skin_default/buttons/yellow.png" position="72,290" size="140,40" alphatest="on" />\n\t\t\t      <ePixmap pixmap="skin_default/buttons/blue.png" position="284,290" size="140,40" alphatest="on" />\n\t\t\t      <widget name="key_yellow" position="72,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t\t      <widget name="key_blue" position="284,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t\t</screen>'

    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('EGAMI Backup Panel'))
        m = checkkernel()
        if m == 1:
            print 'EGAMI Valid'
        else:
            self.close()
        self['label1'] = Label(_('1. STEP - Choose option RESTORE / BACKUP'))
        self['label2'] = Label(_('There is not any EGAMI Backup file on connected devices!'))
        self['label3'] = Label(_(''))
        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label(_('Restore EGAMI'))
        self['key_yellow'] = Label(_('Backup EGAMI'))
        self.mlist = []
        self['list'] = MenuList(self.mlist)
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'red': self.closeMenu,
         'cancel': self.closeMenu,
         'yellow': self.backuP,
         'green': self.restorE})
        self.onLayoutFinish.append(self.updateT)

    def closeMenu(self):
        self.close(True)

    def myclose(self):
        self.close(False)

    def updateT(self):
        self.mybackupfile = ''
        mytext = _('There is not any EGAMI Backup file on connected devices!')
        mytext2 = _(' ')
        myfile = ''
        if fileExists('/etc/egami/.egamibackup_location'):
            fileExists('/etc/egami/.egamibackup_location')
            f = open('/etc/egami/.egamibackup_location', 'r')
            mypath = f.readline().strip()
            f.close()
            myscripts = listdir(mypath)
            for fil in myscripts:
                if fil.find('_EGAMI_Backup.egi') != -1:
                    mytext = 'There is EGAMI Backup file:'
                    mytext2 = 'Date:                      Device:                             Name:'

        else:
            fileExists('/etc/egami/.egamibackup_location')
        if myfile == '':
            myfile = self.scan_mediA()
        if fileExists('/etc/egami/.egamibackup_files'):
            fileExists('/etc/egami/.egamibackup_files')
            f = open('/etc/egami/.egamibackup_files', 'r')
            mypath = f.readline().strip()
            f.close()
            if fileExists(mypath):
                mytext = 'There is EGAMI Backup file:'
                mytext2 = 'Date:                      Device:                             Name:'
        else:
            fileExists('/etc/egami/.egamibackup_location')
        self['label2'].setText(_(mytext))
        self['label3'].setText(_(mytext2))

    def scan_mediA(self):
        out = open('/etc/egami/.egamibackup_files', 'w')
        backup = 'ok'
        mylist = ['/media/hdd',
         '/media/cf',
         '/media/card',
         '/media/usb',
         '/media/usb2',
         '/media/usb3']
        for dic in mylist:
            if not fileExists(dic):
                mkdir(dic)
            myscripts = listdir(dic)
            for fil in myscripts:
                if fil.find('_EGAMI_Backup.egi') != -1:
                    fil2 = fil[9:-4]
                    date = fil[0:8]
                    plik = dic + '/' + date + '_' + fil2 + '.egi\n'
                    out.write(plik)
                    plik2 = date + '            ' + dic + '/        ' + '        ' + fil2
                    self.mlist.append((plik2, plik, dic))

        out.close()
        self['list'].setList(self.mlist)

    def backuP(self):
        m = checkkernel()
        if m == 1:
            check = False
            if fileExists('/proc/mounts'):
                fileExists('/proc/mounts')
                f = open('/proc/mounts', 'r')
                for line in f.readlines():
                    if line.find('/media/cf') != -1:
                        check = True
                        continue
                    if line.find('/media/usb') != -1:
                        check = True
                        continue
                    if line.find('/media/usb2') != -1:
                        check = True
                        continue
                    if line.find('/media/usb3') != -1:
                        check = True
                        continue
                    if line.find('/media/card') != -1:
                        check = True
                        continue
                    if line.find('/hdd') != -1:
                        check = True
                        continue

                f.close()
            else:
                fileExists('/proc/mounts')
            if check == False:
                self.session.open(MessageBox, _('Sorry, there is not any connected devices in your STB.\nPlease connect HDD or USB to store/restore Your EGAMI Backup!'), MessageBox.TYPE_INFO)
            else:
                self.session.openWithCallback(self.myclose, EGAMIBackupPanel_Step2)
        else:
            self.session.open(MessageBox, _('Sorry: Wrong image in flash found. You have to install in flash EGAMI Image'), MessageBox.TYPE_INFO, 3)

    def restorE(self):
        m = checkkernel()
        if m == 1:
            check = False
            if fileExists('/proc/mounts'):
                fileExists('/proc/mounts')
                f = open('/proc/mounts', 'r')
                for line in f.readlines():
                    if line.find('/media/cf') != -1:
                        check = True
                        continue
                    if line.find('/media/usb') != -1:
                        check = True
                        continue
                    if line.find('/media/usb2') != -1:
                        check = True
                        continue
                    if line.find('/media/usb3') != -1:
                        check = True
                        continue
                    if line.find('/media/card') != -1:
                        check = True
                        continue
                    if line.find('/hdd') != -1:
                        check = True
                        continue

                f.close()
            else:
                fileExists('/proc/mounts')
            if check == False:
                self.session.open(MessageBox, _('Sorry, there is not any connected devices in your STB.\nPlease connect HDD or USB to store/restore Your EGAMI Backup!'), MessageBox.TYPE_INFO)
            else:
                try:
                    backup_file = self['list'].l.getCurrentSelection()[1]
                    if backup_file != '':
                        message = _('Do you really want to restore the EGAMI Backup:\n ') + self.mybackupfile + ' ?'
                        self.session.openWithCallback(self.restorE_2, MessageBox, message, MessageBox.TYPE_YESNO)
                    else:
                        system('umount /media/egamibackup_location')
                        system('rmdir /media/egamibackup_location')
                        self.session.open(MessageBox, _('Sorry, EGAMI Backup not found.'), MessageBox.TYPE_INFO)
                except:
                    self.session.open(MessageBox, _('Sorry, there is not any connected devices in your STB.\nPlease connect HDD or USB to store/restore Your EGAMI Backup!'), MessageBox.TYPE_INFO)

        else:
            self.session.open(MessageBox, _('Sorry: Wrong image in flash found. You have to install in flash EGAMI Image'), MessageBox.TYPE_INFO, 3)

    def restorE_2(self, answer):
        if answer is True:
            backup_file = self['list'].l.getCurrentSelection()[1]
            backup_path = self['list'].l.getCurrentSelection()[2]
            self.session.open(EGAMIRestorePanel_Step1, backup_file, backup_path)


class EGAMIBackupPanel_Step2(Screen):
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        skin = '\n\t\t\t<screen name="EGAMIBackupPanel_Step2" position="center,center" size="1040,680" >\n\t\t\t\t<widget name="label1" position="10,10" size="840,30" zPosition="1" halign="center" font="Regular;32" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t\t<widget name="label2" position="10,80" size="840,290" zPosition="1" font="Regular;26" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t\t<widget name="config" itemHeight="50" font="Regular;28" position="10,170" size="840,290" scrollbarMode="showOnDemand"/>\n\t\t\t\t<ePixmap position="40,604" size="100,40" zPosition="0" pixmap="buttons/red.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<ePixmap position="200,604" size="100,40" zPosition="0" pixmap="buttons/green.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<widget name="key_red" position="80,604" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="red" transparent="1" />\n\t\t\t\t<widget name="key_green" position="240,604" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="green" transparent="1" />\n\t\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen name="EGAMIBackupPanel_Step2" position="center,center" size="902,380" >\n\t\t\t      <widget name="label1" position="10,10" size="840,30" zPosition="1" halign="center" font="Regular;25" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t      <widget name="label2" position="10,80" size="840,290" zPosition="1" halign="center" font="Regular;20" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t      <widget name="config" position="130,160" size="450,290" scrollbarMode="showOnDemand"/>\n\t\t\t      <ePixmap pixmap="skin_default/buttons/yellow.png" position="200,340" size="140,40" alphatest="on"/>\n\t\t\t      <ePixmap pixmap="skin_default/buttons/green.png" position="550,340" size="140,40" alphatest="on"/>\n\t\t\t      <widget name="key_yellow" position="200,340" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t      <widget name="key_green" position="550,340" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>\n\t\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('EGAMI Backup Location - STEP 2'))
        self.list = []
        self['config'] = MenuList(self.list)
        self['key_green'] = Label(_('Backup EGAMI'))
        self['key_red'] = Label(_('Cancel'))
        self['label1'] = Label(_('2. STEP - Choose backup location'))
        self['label2'] = Label(_('Here is the list of mounted devices in Your STB\nPlease choose a device where You would like to keep Your backup:'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'green': self.saveMysets,
         'red': self.close,
         'back': self.close})
        self.updateList()

    def updateList(self):
        mycf, myusb, myusb2, myusb3, mysd, myhdd = ('', '', '', '', '', '')
        myoptions = []
        if fileExists('/proc/mounts'):
            fileExists('/proc/mounts')
            f = open('/proc/mounts', 'r')
            for line in f.readlines():
                if line.find('/media/cf') != -1:
                    mycf = '/media/cf/'
                    continue
                if line.find('/media/usb') != -1:
                    myusb = '/media/usb/'
                    continue
                if line.find('/media/usb2') != -1:
                    myusb2 = '/media/usb2/'
                    continue
                if line.find('/media/usb3') != -1:
                    myusb3 = '/media/usb3/'
                    continue
                if line.find('/media/card') != -1:
                    mysd = '/media/card/'
                    continue
                if line.find('/hdd') != -1:
                    myhdd = '/media/hdd/'
                    continue

            f.close()
        else:
            fileExists('/proc/mounts')
        if mycf:
            mycf
            self.list.append((_('CF card mounted in:        ') + mycf, mycf))
        else:
            mycf
        if myusb:
            myusb
            self.list.append((_('USB device mounted in:     ') + myusb, myusb))
        else:
            myusb
        if myusb2:
            myusb2
            self.list.append((_('USB 2 device mounted in:   ') + myusb2, myusb2))
        else:
            myusb2
        if myusb3:
            myusb3
            self.list.append((_('USB 3 device mounted in:   ') + myusb3, myusb3))
        else:
            myusb3
        if mysd:
            mysd
            self.list.append((_('SD card mounted in:         ') + mysd, mysd))
        else:
            mysd
        if myhdd:
            myhdd
            self.list.append((_('HDD mounted in:               ') + myhdd, myhdd))
        else:
            myhdd
        self['config'].setList(self.list)

    def myclose(self):
        self.close()

    def saveMysets(self):
        mysel = self['config'].getCurrent()
        out = open('/etc/egami/.egamibackup_location', 'w')
        out.write(mysel[1])
        out.close()
        if fileExists('/etc/egami/.egamibackup_location'):
            fileExists('/etc/egami/.egamibackup_location')
            self.session.openWithCallback(self.myclose, EGAMIBackupPanel_Step3)
        else:
            fileExists('/etc/egami/.egamibackup_location')
            self.session.open(MessageBox, _('You have to setup backup location.'), MessageBox.TYPE_INFO)


class EGAMIBackupPanel_Step3(Screen):
    skin = '\n\t\t<screen name="EGAMIBackupPanel_Step3" position="center,center" size="484,250" flags="wfNoBorder">\n\t\t      <widget name="status" position="0,0" size="484,250" zPosition="-1" pixmaps="/usr/lib/enigma2/python/EGAMI/icons/egami_icons/backup_1.png,egami_icons/backup_2.png,egami_icons/backup_3.png,egami_icons/backup_4.png,egami_icons/backup_5.png,egami_icons/backup_6.png"  />\n\t\t      <widget name="label" position="0,200" halign="center" size="484,60" zPosition="1" font="Regular;20" valign="top" transparent="1" />\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('EGAMI Backup in progress...'))
        self['status'] = MultiPixmap()
        self['status'].setPixmapNum(0)
        self['label'] = Label('')
        self.mylist = ['Libraries',
         'Firmwares',
         'Binaries',
         'SoftCams',
         'Scripts',
         'Bootlogos',
         'Uninstall files',
         'General Settings',
         'Cron',
         'Settings Channels Bouquets',
         'Openvpn',
         'Satellites Terrestrial',
         'Plugins',
         'END']
        self.mytmppath = '/media/hdd/'
        if fileExists('/etc/egami/.egamibackup_location'):
            fileExists('/etc/egami/.egamibackup_location')
            f = open('/etc/egami/.egamibackup_location', 'r')
            self.mytmppath = f.readline().strip()
            f.close()
        else:
            fileExists('/etc/egami/.egamibackup_location')
        self.mytmppath += 'egamibackup_location'
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.updatepix)
        self.onShow.append(self.startShow)
        self.onClose.append(self.delTimer)
        system('rm -rf ' + self.mytmppath)
        system('mkdir ' + self.mytmppath)
        system('mkdir ' + self.mytmppath + '/etc')
        system('mkdir ' + self.mytmppath + '/lib')
        system('mkdir ' + self.mytmppath + '/usr')
        system('mkdir ' + self.mytmppath + '/scripts')
        system('mkdir ' + self.mytmppath + '/media')
        system('mkdir ' + self.mytmppath + '/media/hdd')
        system('mkdir ' + self.mytmppath + '/media/usb')
        system('mkdir ' + self.mytmppath + '/media/usb2')
        system('mkdir ' + self.mytmppath + '/media/usb3')
        configfile.save()

    def startShow(self):
        self.curpix = 0
        self.count = 0
        self.procesS()

    def updatepix(self):
        self.activityTimer.stop()
        self['status'].setPixmapNum(self.curpix)
        self.curpix += 1
        if self.curpix == 6:
            self.curpix = 0
            self.procesS()
        else:
            self.activityTimer.start(150)

    def procesS(self):
        cur = self.mylist[self.count]
        self['label'].setText(cur)
        if cur == 'Libraries':
            ret = system('mkdir ' + self.mytmppath + '/list')
            ret = system("opkg list-installed | grep lib | awk '{print $1}' > " + self.mytmppath + '/list/libs.list')
        elif cur == 'Firmwares':
            ret = system('cp -rf /lib/firmware ' + self.mytmppath + '/lib')
            ret = system('mkdir ' + self.mytmppath + '/lib/modules')
            ret = system('cp -rf /lib/modules/* ' + self.mytmppath + '/lib/modules')
            ret = system('rm -rf ' + self.mytmppath + '/lib/modules/' + about.getKernelVersionString() + '/extra')
        elif cur == 'Binaries':
            ret = system('cp -fdr /usr/bin ' + self.mytmppath + '/usr')
            ret = system('rm -rf ' + self.mytmppath + '/usr/bin/enigma2*')
            ret = system('rm -rf ' + self.mytmppath + '/usr/bin/gst*')
            ret = system('rm -rf ' + self.mytmppath + '/usr/bin/dbus*')
            ret = system('rm -rf ' + self.mytmppath + '/usr/bin/opkg*')
            ret = system('rm -rf ' + self.mytmppath + '/usr/bin/python*')
            ret = system('rm -rf ' + self.mytmppath + '/usr/bin/stream*')
            ret = system('rm -rf ' + self.mytmppath + '/usr/bin/ntfs*')
            ret = system('rm -rf ' + self.mytmppath + '/usr/bin/pil*')
            ret = system('rm -rf ' + self.mytmppath + '/usr/bin/*procps*')
            ret = system('rm -rf ' + self.mytmppath + '/usr/bin/get*')
        elif cur == 'SoftCams':
            ret = system('cp -rf /usr/emu_scripts ' + self.mytmppath + '/usr')
            ret = system('cp -rf /usr/keys ' + self.mytmppath + '/usr')
            ret = system('cp -rf /usr/scce ' + self.mytmppath + '/usr')
            ret = system('cp -rf /usr/scam ' + self.mytmppath + '/usr')
            ret = system('cp -rf /usr/tuxbox ' + self.mytmppath + '/usr')
        elif cur == 'Scripts':
            ret = system('cp -rf /usr/scripts ' + self.mytmppath + '/usr')
            ret = system('cp -rf /scripts/* ' + self.mytmppath + '/scripts')
        elif cur == 'Bootlogos':
            ret = system('mkdir ' + self.mytmppath + '/usr/share')
            ret = system('cp -f /usr/share/*.mvi ' + self.mytmppath + '/usr/share')
        elif cur == 'Uninstall files':
            ret = system('mkdir ' + self.mytmppath + '/usr/tuxbox')
            ret = system('cp -rf /usr/uninstall ' + self.mytmppath + '/usr')
            ret = system('cp -rf /usr/tuxbox/uninstall_emu ' + self.mytmppath + '/usr/tuxbox/')
        elif cur == 'General Settings':
            ret = system('mkdir ' + self.mytmppath + '/media/hdd')
            ret = system('mkdir ' + self.mytmppath + '/media/usb')
            ret = system('mkdir ' + self.mytmppath + '/media/usb2')
            ret = system('mkdir ' + self.mytmppath + '/media/usb3')
            ret = system('cp -rf /media/hdd/crossepg ' + self.mytmppath + '/media/hdd')
            ret = system('cp -rf /media/usb/crossepg ' + self.mytmppath + '/media/usb')
            ret = system('cp -rf /media/usb2/crossepg ' + self.mytmppath + '/media/usb2')
            ret = system('cp -rf /media/usb3/crossepg ' + self.mytmppath + '/media/usb3')
            ret = system('mkdir ' + self.mytmppath + '/etc/network')
            ret = system('cp -f /etc/* ' + self.mytmppath + '/etc')
            ret = system('cp -rf /etc/egami ' + self.mytmppath + '/etc')
            ret = system('cp -f /etc/network/interfaces ' + self.mytmppath + '/etc/network')
            ret = system('cp -f /etc/passwd ' + self.mytmppath + '/etc/passwd')
            ret = system('cp -f /etc/inadyn.conf ' + self.mytmppath + '/etc/inadyn.conf')
            ret = system('cp -rf /etc/MultiQuickButton ' + self.mytmppath + '/etc')
        elif cur == 'Cron':
            ret = system('cp -rf /etc/cron ' + self.mytmppath + '/etc')
        elif cur == 'Settings Channels Bouquets':
            ret = system('mkdir ' + self.mytmppath + '/usr/share/enigma2')
            ret = system('cp -rf /etc/enigma2 ' + self.mytmppath + '/etc')
            ret = system('cp -f /usr/share/enigma2/keymap.xml ' + self.mytmppath + '/usr/share/enigma2/')
        elif cur == 'Openvpn':
            ret = system('cp -rf /etc/openvpn ' + self.mytmppath + '/etc')
        elif cur == 'Satellites Terrestrial':
            ret = system('cp -rf /etc/tuxbox ' + self.mytmppath + '/etc')
        elif cur == 'Plugins':
            ret = system('mkdir -p ' + self.mytmppath + '/usr/lib/enigma2')
            ret = system('mkdir -p ' + self.mytmppath + '/usr/lib/enigma2/python')
            ret = system('mkdir -p ' + self.mytmppath + '/usr/lib/enigma2/python/Plugins')
            ret = system('cp -rf /usr/lib/enigma2/python/Plugins/Extensions ' + self.mytmppath + '/usr/lib/enigma2/python/Plugins')
            ret = system('cp -rf /usr/lib/enigma2/python/Plugins/SystemPlugins ' + self.mytmppath + '/usr/lib/enigma2/python/Plugins')
            ret = system('mkdir ' + self.mytmppath + '/list')
            ret = system("opkg list-installed | grep enigma2-plugin-extensions- | awk '{print $1}' > " + self.mytmppath + '/list/extensions.list')
            ret = system("opkg list-installed | grep enigma2-plugin-systemplugins- | awk '{print $1}' > " + self.mytmppath + '/list/systemplugins.list')
            self['label'].setText('Plugins')
        if cur != 'END':
            self.count += 1
            self.activityTimer.start(100)
        else:
            mydir = getcwd()
            chdir(self.mytmppath)
            cmd = 'tar -cf EGAMI_Backup.tar etc lib media usr scripts list'
            rc = system(cmd)
            import datetime
            import time
            now = datetime.datetime.now()
            czas = now.strftime('%Y%m%d')
            filename = '../' + czas + '_EGAMI_Backup.egi'
            os_rename('EGAMI_Backup.tar', filename)
            chdir(mydir)
            self.session.open(MessageBox, _('EGAMI Backup complete! Please wait...'), MessageBox.TYPE_INFO, timeout=4)
            self.close()

    def delTimer(self):
        del self.activityTimer
        system('rm -rf ' + self.mytmppath)


class EGAMIRestorePanel_Step1(Screen, ConfigListScreen):
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        skin = '\n\t\t\t<screen name="EGAMIRestorePanel_Step1" position="center,center" size="1040,880" >\n\t\t\t\t<widget name="config" itemHeight="50" font="Regular;28" position="10,10" size="1020,750" scrollbarMode="showOnDemand"/>\n\t\t\t\t<ePixmap position="40,804" size="100,40" zPosition="0" pixmap="buttons/red.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<ePixmap position="200,804" size="100,40" zPosition="0" pixmap="buttons/green.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<widget name="key_red" position="80,804" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="red" transparent="1" />\n\t\t\t\t<widget name="key_green" position="240,804" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="green" transparent="1" />\n\t\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen name="EGAMIRestorePanel_Step1" position="center,center" size="902,550" title="EGAMI Backup Restore - STEP 1">\n\t\t\t      <widget name="config" position="30,10" size="840,510" scrollbarMode="showOnDemand"/>\n\t\t\t      <ePixmap pixmap="skin_default/buttons/blue.png" position="380,510" size="140,40" alphatest="on"/>\n\t\t\t      <widget name="key_blue" position="380,510" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t      <ePixmap pixmap="skin_default/buttons/green.png" position="550,510" size="140,40" alphatest="on"/>\n\t\t\t      <widget name="key_green" position="550,510" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>\n\t\t\t</screen>'

    def __init__(self, session, mypath, backpath):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('EGAMI Backup Restore - STEP 1'))
        self.mypath = mypath
        self.backpath = backpath
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self['key_green'] = Label(_('Restore'))
        self['key_red'] = Label(_('Cancel'))
        self['actions'] = ActionMap(['EGActions', 'OkCancelActions', 'WizardActions'], {'green': self.Continue,
         'ok': self.Continue,
         'cancel': self.cancel,
         'red': self.cancel})
        self.updateList()

    def cancel(self):
        self.close()

    def updateList(self):
        blist = ['Password',
         'Devices',
         'Network',
         'Cron',
         'Password',
         'Keymaps',
         'Nfs',
         'Openvpn',
         'Inadyn',
         'Httpd',
         'Uninstall files',
         'Settings Channels Bouquets',
         'Satellites Terrestrial',
         'SoftCams',
         'Scripts',
         'Bootlogo',
         'Plugins Extensions',
         'System Plugins']
        for x in blist:
            item = NoSave(ConfigYesNo(default=True))
            item2 = getConfigListEntry(x, item)
            self.list.append(item2)

        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def Continue(self):
        mylist = ['start',
         'extract',
         'lib',
         'lib/firmware',
         'usr/lib',
         'usr/bin',
         'etc']
        for x in self['config'].list:
            if x[1].value == True:
                mylist.append(x[0])
                continue

        mylist.append('END')
        self.session.open(EGAMIRestorePanel_Step2, self.mypath, mylist, self.backpath)
        self.close()


class EGAMIRestorePanel_Step2(Screen):
    skin = '\n\t\t<screen name="EGAMIRestorePanel_Step2" position="center,center" size="484,250" title="EGAMI Restore in progress..." flags="wfNoBorder">\n\t\t\t<widget name="status" position="0,0" size="484,250" zPosition="-1" pixmaps="/usr/lib/enigma2/python/EGAMI/icons/egami_icons/restore_1.png,egami_icons/restore_2.png,egami_icons/restore_3.png,egami_icons/restore_4.png,egami_icons/restore_5.png,egami_icons/restore_6.png"  />\n\t\t\t<widget name="label" position="0,200" halign="center" size="484,60" zPosition="1" font="Regular;20" valign="top" transparent="1" />\n\t\t</screen>'

    def __init__(self, session, mypath, mylist, myback):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('EGAMI Restore in progress...'))
        self.mytext = 'Files extraction in progress...'
        self['status'] = MultiPixmap()
        self['status'].setPixmapNum(0)
        self['label'] = Label('')
        self.mypath = myback + '/egamibackup_location'
        self.mybackupfile = mypath
        self.mylist = mylist
        self.count = 0
        self.go = False
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions', 'DirectionActions'], {'ok': self.hrestBox})
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.updatepix)
        self.onShow.append(self.startShow)
        self.onClose.append(self.delTimer)

    def startShow(self):
        self.curpix = 0
        self.count = 0
        self.procesS()

    def updatepix(self):
        self.activityTimer.stop()
        self['status'].setPixmapNum(self.curpix)
        self.curpix += 1
        if self.curpix == 6:
            self.curpix = 0
            self.procesS()
        else:
            self.activityTimer.start(150)

    def procesS(self):
        cur = self.mylist[self.count]
        self['label'].setText(self.mytext)
        if cur == 'start':
            self.mytext = 'Archive Extraction'
        if cur == 'extract':
            system('mkdir ' + self.mypath)
            mydir = getcwd()
            chdir(self.mypath)
            cmd = 'tar -xf ' + self.mybackupfile
            rc = system(cmd)
            chdir(mydir)
        elif cur == 'lib':
            self.mytext = 'Merge directory ' + cur
            ret = self.mergediR('/lib')
        elif cur == 'lib/firmware':
            self.mytext = 'Merge directory ' + cur
            ret = self.mergediR('/lib/firmware')
        elif cur == 'usr/lib':
            self.mytext = 'Merge directory ' + cur
            ret = self.mergediR('/usr/lib')
        elif cur == 'usr/bin':
            self.mytext = 'Merge directory ' + cur
            ret = self.mergediR('/usr/bin')
        elif cur == 'etc':
            self.mytext = 'Merge directory ' + cur
            ret = self.mergediR('/etc')
        elif cur == 'Password':
            self.mytext = 'Restore ' + cur
            ret = system('cp -f ' + self.mypath + '/etc/passwd /etc/')
        elif cur == 'Devices':
            self.mytext = 'Restore ' + cur
            ret = system('cp -f ' + self.mypath + '/etc/fstab /etc/')
            ret = system('cp -f ' + self.mypath + '/scripts/dev_mount_script.sh /scripts/')
        elif cur == 'Network':
            self.mytext = 'Restore ' + cur
            ret = system('cp -f ' + self.mypath + '/etc/resolv.conf /etc/')
            ret = system('cp -f ' + self.mypath + '/etc/wpa_supplicant.conf /etc/')
            ret = system('cp -f ' + self.mypath + '/etc/network/interfaces /etc/network/')
        elif cur == 'Cron':
            self.mytext = 'Restore ' + cur
            ret = system('cp -rf ' + self.mypath + '/etc/cron /etc/')
        elif cur == 'Password':
            self.mytext = 'Restore ' + cur
            ret = system('cp -rf ' + self.mypath + '/etc/passwd /etc/')
        elif cur == 'Keymaps':
            self.mytext = 'Restore ' + cur
            system('cp -f ' + self.mypath + '/usr/share/enigma2/keymap.xml /usr/share/enigma2/')
        elif cur == 'Nfs':
            self.mytext = 'Restore ' + cur
            ret = system('cp -f ' + self.mypath + '/scripts/nfs_server_script.sh /scripts/')
        elif cur == 'Openvpn':
            self.mytext = 'Restore ' + cur
            ret = system('cp -f ' + self.mypath + '/scripts/openvpn_script.sh /scripts/')
            ret = system('cp -rf ' + self.mypath + '/etc/openvpn /etc/')
        elif cur == 'Inadyn':
            self.mytext = 'Restore ' + cur
            ret = system('cp -f ' + self.mypath + '/scripts/inadyn_script.sh /scripts/')
            ret = system('cp -f ' + self.mypath + '/etc/inadyn.conf /etc/')
        elif cur == 'Httpd':
            self.mytext = 'Restore ' + cur
            ret = system('cp -f ' + self.mypath + '/scripts/httpd_script.sh /scripts/')
        elif cur == 'Uninstall files':
            self.mytext = 'Restore ' + cur
            ret = system('cp -rf ' + self.mypath + '/usr/uninstall /usr/')
            ret = system('cp -rf ' + self.mypath + '/usr/tuxbox/* /usr/tuxbox')
        elif cur == 'Settings Channels Bouquets':
            self.mytext = 'Restore ' + cur
            ret = system('cp -rf ' + self.mypath + '/etc/enigma2 /etc/')
        elif cur == 'Satellites Terrestrial':
            self.mytext = 'Restore ' + cur
            ret = system('cp -rf ' + self.mypath + '/etc/tuxbox /etc/')
        elif cur == 'SoftCams':
            self.mytext = 'Restore ' + cur
            ret = system('cp -rf ' + self.mypath + '/usr/emu_scripts /usr/')
            ret = system('cp -rf ' + self.mypath + '/usr/keys /usr/')
            ret = system('cp -rf ' + self.mypath + '/usr/scce /usr/')
            ret = system('cp -rf ' + self.mypath + '/etc/tuxbox/config /etc/tuxbox/')
        elif cur == 'Scripts':
            self.mytext = 'Restore ' + cur
            ret = system('cp -rf ' + self.mypath + '/usr/scripts /usr/')
        elif cur == 'Bootlogo':
            self.mytext = 'Restore ' + cur
            ret = system('cp -f ' + self.mypath + '/usr/share/*.mvi /usr/share/')
        elif cur == 'Plugins Extensions':
            self.mytext = 'Merge ' + cur
            ret = self.mergepluginS('Extensions')
        elif cur == 'System Plugins':
            self.mytext = 'Merge ' + cur
            ret = self.mergepluginS('SystemPlugins')
        if cur != 'END':
            self.count += 1
            self.activityTimer.start(100)
        else:
            self.mytext = 'Restore Complete. Click OK to restart the box\n'
            self['label'].setText(_(self.mytext))
            ret = system('umount /media/egamibackup_location')
            ret = system('rmdir /media/egamibackup_location')
            ret = system('rm -rf ' + self.mypath)
            self.go = True

    def mergediR(self, path):
        try:
            opath = self.mypath + path
            destpath = path
            odir = listdir(opath)
            destdir = listdir(destpath)
            for fil in odir:
                if fil not in destdir:
                    f = opath + '/' + fil
                    system('cp -rf ' + f + ' ' + destpath + '/')
                    continue

        except:
            return 0

        return 0

    def mergepluginS(self, pdir):
        opath = self.mypath + '/usr/lib/enigma2/python/Plugins/' + pdir
        destpath = '/usr/lib/enigma2/python/Plugins/' + pdir
        try:
            odir = listdir(opath)
            destdir = listdir(destpath)
            for fil in odir:
                if fil not in destdir:
                    f = opath + '/' + fil
                    system('cp -rf ' + f + ' ' + destpath + '/')
                    continue

            if pdir == 'Extensions':
                path = self.mypath + '/list/extensions.list'
                if fileExists(path):
                    system('opkg update')
                    with open(path, 'r') as infile:
                        data = infile.read()
                    my_list = data.splitlines()
                    for x in my_list:
                        installed = self.checkInst(x)
                        if installed == False:
                            cmd = 'opkg install --force-overwrite ' + x
                            system(cmd)

            if pdir == 'SystemPlugins':
                path = self.mypath + '/list/systemplugins.list'
                if fileExists(path):
                    system('opkg update')
                    with open(path, 'r') as infile:
                        data = infile.read()
                    my_list = data.splitlines()
                    for x in my_list:
                        installed = self.checkInst(x)
                        if installed == False:
                            cmd = 'opkg install --force-overwrite ' + x
                            system(cmd)

        except:
            return 0

        return 0

    def checkInst(self, name):
        ret = False
        system('opkg status ' + name + ' > /tmp/checkInst.tmp')
        f = open('/tmp/checkInst.tmp', 'r')
        for line in f.readlines():
            if line.find(name) != -1:
                ret = True
                break

        f.close()
        return ret

    def delTimer(self):
        del self.activityTimer

    def hrestBox(self):
        if self.go == True:
            system('reboot -f')


class EGFullBackup(Screen, ConfigListScreen):
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        skin = '\n\t\t\t<screen name="EGFullBackup" position="center,center" size="1040,680" >\n\t\t\t\t<widget name="label1" position="10,10" size="840,30" zPosition="1" halign="center" font="Regular;32" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t\t<widget name="label2" position="10,80" size="840,290" zPosition="1" font="Regular;26" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t\t<widget name="config" itemHeight="50" font="Regular;28" position="10,170" size="840,290" scrollbarMode="showOnDemand"/>\n\t\t\t\t<ePixmap position="40,604" size="100,40" zPosition="0" pixmap="buttons/red.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<ePixmap position="200,604" size="100,40" zPosition="0" pixmap="buttons/green.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<widget name="key_red" position="80,604" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="red" transparent="1" />\n\t\t\t\t<widget name="key_green" position="240,604" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="green" transparent="1" />\n\t\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen name="EGFullBackup" position="center,center" size="902,380" >\n\t\t\t      <widget name="label1" position="10,10" size="840,30" zPosition="1" halign="center" font="Regular;25" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t      <widget name="label2" position="10,80" size="840,290" zPosition="1" halign="center" font="Regular;20" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t      <widget name="config" position="130,160" size="450,290" scrollbarMode="showOnDemand"/>\n\t\t\t      <ePixmap pixmap="skin_default/buttons/yellow.png" position="200,340" size="140,40" alphatest="on"/>\n\t\t\t      <ePixmap pixmap="skin_default/buttons/green.png" position="550,340" size="140,40" alphatest="on"/>\n\t\t\t      <widget name="key_yellow" position="200,340" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t      <widget name="key_green" position="550,340" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>\n\t\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.selection = 0
        self.list = self.list_files('/boot')
        Screen.setTitle(self, _('EGAMI Full Image Backup'))
        m = checkkernel()
        if m == 1:
            print 'EGAMI Valid'
        else:
            self.close()
        self.MODEL = getBoxType()
        self.OEM = getBrandOEM()
        self.MACHINEBUILD = getMachineBuild()
        self.MACHINENAME = getMachineName()
        self.MACHINEBRAND = getMachineBrand()
        self.IMAGEFOLDER = getImageFolder()
        self.UBINIZE_ARGS = getMachineUBINIZE()
        self.MKUBIFS_ARGS = getMachineMKUBIFS()
        self.MTDKERNEL = getMachineMtdKernel()
        self.MTDROOTFS = getMachineMtdRoot()
        self.ROOTFSBIN = getMachineRootFile()
        self.KERNELBIN = getMachineKernelFile()
        self.ROOTFSTYPE = getImageFileSystem()
        print '[FULL BACKUP] BOX MACHINEBUILD = >%s<' % self.MACHINEBUILD
        print '[FULL BACKUP] BOX MACHINENAME = >%s<' % self.MACHINENAME
        print '[FULL BACKUP] BOX MACHINEBRAND = >%s<' % self.MACHINEBRAND
        print '[FULL BACKUP] BOX MODEL = >%s<' % self.MODEL
        print '[FULL BACKUP] OEM MODEL = >%s<' % self.OEM
        print '[FULL BACKUP] IMAGEFOLDER = >%s<' % self.IMAGEFOLDER
        print '[FULL BACKUP] UBINIZE = >%s<' % self.UBINIZE_ARGS
        print '[FULL BACKUP] MKUBIFS = >%s<' % self.MKUBIFS_ARGS
        print '[FULL BACKUP] MTDKERNEL = >%s<' % self.MTDKERNEL
        print '[FULL BACKUP] MTDROOTFS = >%s<' % self.MTDROOTFS
        print '[FULL BACKUP] ROOTFSTYPE = >%s<' % self.ROOTFSTYPE
        self.list = []
        self['config'] = MenuList(self.list)
        self['key_green'] = Label(_('Full Backup'))
        self['key_red'] = Label(_('Cancel'))
        if SystemInfo['HaveMultiBoot']:
            self['key_yellow'] = Label(_('STARTUP'))
            self['info-multi'] = Label(_('You can select with yellow the OnlineFlash Image\n or select Recovery to create a USB Disk Image for clean Install.'))
        else:
            self['key_yellow'] = Label(' ')
            self['info-multi'] = Label(' ')
        self['label1'] = Label(_('1. STEP - Choose backup location'))
        self['label2'] = Label(_('Here is the list of mounted devices in Your STB\nPlease choose a device where You would like to keep Your backup:'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'green': self.saveMysets,
         'red': self.close,
         'yellow': self.yellow,
         'back': self.close})
        self.deviceok = True
        self.updateList()

    def updateList(self):
        mycf, myusb, myusb2, myusb3, mysd, myhdd = ('', '', '', '', '', '')
        myoptions = []
        if fileExists('/proc/mounts'):
            fileExists('/proc/mounts')
            f = open('/proc/mounts', 'r')
            for line in f.readlines():
                if line.find('/media/cf') != -1:
                    mycf = '/media/cf/'
                    continue
                if line.find('/media/usb') != -1:
                    myusb = '/media/usb/'
                    continue
                if line.find('/media/usb2') != -1:
                    myusb2 = '/media/usb2/'
                    continue
                if line.find('/media/usb3') != -1:
                    myusb3 = '/media/usb3/'
                    continue
                if line.find('/media/card') != -1:
                    mysd = '/media/card/'
                    continue
                if line.find('/hdd') != -1:
                    myhdd = '/media/hdd/'
                    continue

            f.close()
        else:
            fileExists('/proc/mounts')
        if mycf:
            mycf
            self.list.append((_('CF card mounted in:        ') + mycf, mycf))
        else:
            mycf
        if myusb:
            myusb
            self.list.append((_('USB device mounted in:     ') + myusb, myusb))
        else:
            myusb
        if myusb2:
            myusb2
            self.list.append((_('USB 2 device mounted in:   ') + myusb2, myusb2))
        else:
            myusb2
        if myusb3:
            myusb3
            self.list.append((_('USB 3 device mounted in:   ') + myusb3, myusb3))
        else:
            myusb3
        if mysd:
            mysd
            self.list.append((_('SD card mounted in:         ') + mysd, mysd))
        else:
            mysd
        if myhdd:
            myhdd
            self.list.append((_('HDD mounted in:               ') + myhdd, myhdd))
        else:
            myhdd
        self['config'].setList(self.list)
        print len(self.list)
        if len(self.list) < 1:
            self['label2'].setText(_('Sorry no device found to store backup. Please check your media in EGAMI devices panel.'))
            self.deviceok = False

    def myclose(self):
        self.close()

    def saveMysets(self):
        if self.deviceok == True:
            mysel = self['config'].getCurrent()
            self.doFullBackup(mysel[1])
        else:
            self.session.open(MessageBox, _('Sorry, there is not any connected devices in your STB.\nPlease connect HDD or USB to full backup Your EGAMI Image!'), MessageBox.TYPE_INFO)

    def SearchUSBcanidate(self):
        for paths, subdirs, files in walk('/media'):
            for dir in subdirs:
                if not dir == 'hdd' and not dir == 'net':
                    for file in listdir('/media/' + dir):
                        if file.find('backupstick') > -1:
                            print 'USB-DEVICE found on: /media/%s' % dir
                            return '/media/' + dir

            break

        return 'XX'

    def yellow(self):
        if SystemInfo['HaveMultiBoot']:
            self.selection = self.selection + 1
            if self.selection == len(self.list):
                self.selection = 0
            self['key_yellow'].setText(_(self.list[self.selection]))
            if self.list[self.selection] == 'Recovery':
                cmdline = self.read_startup('/boot/STARTUP').split('=', 1)[1].split(' ', 1)[0]
            else:
                cmdline = self.read_startup('/boot/' + self.list[self.selection]).split('=', 1)[1].split(' ', 1)[0]
            cmdline = cmdline.lstrip('/dev/')
            self.MTDROOTFS = cmdline
            self.MTDKERNEL = cmdline[:-1] + str(int(cmdline[-1:]) - 1)
            print '[FULL BACKUP] Multiboot rootfs ', self.MTDROOTFS
            print '[FULL BACKUP] Multiboot kernel ', self.MTDKERNEL

    def read_startup(self, FILE):
        self.file = FILE
        with open(self.file, 'r') as myfile:
            data = myfile.read().replace('\n', '')
        myfile.close()
        return data

    def list_files(self, PATH):
        files = []
        if SystemInfo['HaveMultiBoot']:
            self.path = PATH
            for name in listdir(self.path):
                if path.isfile(path.join(self.path, name)):
                    cmdline = self.read_startup('/boot/' + name).split('=', 1)[1].split(' ', 1)[0]
                    if cmdline in Harddisk.getextdevices('ext4'):
                        files.append(name)

            files.append('Recovery')
        return files

    def doFullBackup(self, DIRECTORY):
        self.DIRECTORY = DIRECTORY
        self.TITLE = _('Full back-up on %s') % self.DIRECTORY
        self.START = time()
        self.DATE = strftime('%Y%m%d_%H%M', localtime(self.START))
        self.IMAGEVERSION = self.imageInfo()
        if 'ubi' in self.ROOTFSTYPE.split():
            self.MKFS = '/usr/sbin/mkfs.ubifs'
        elif 'tar.bz2' in self.ROOTFSTYPE.split() or SystemInfo['HaveMultiBoot']:
            self.MKFS = '/bin/tar'
            self.BZIP2 = '/usr/bin/bzip2'
        else:
            self.MKFS = '/usr/sbin/mkfs.jffs2'
        self.UBINIZE = '/usr/sbin/ubinize'
        self.NANDDUMP = '/usr/sbin/nanddump'
        self.WORKDIR = '%s/bi' % self.DIRECTORY
        self.TARGET = 'XX'
        if not path.exists(self.MKFS):
            text = '%s not found !!' % self.MKFS
            self.session.open(MessageBox, _(text), type=MessageBox.TYPE_ERROR)
            return
        elif not path.exists(self.NANDDUMP):
            text = '%s not found !!' % self.NANDDUMP
            self.session.open(MessageBox, _(text), type=MessageBox.TYPE_ERROR)
            return
        else:
            self.SHOWNAME = '%s %s' % (self.MACHINEBRAND, self.MODEL)
            self.MAINDESTOLD = '%s/%s' % (self.DIRECTORY, self.MODEL)
            self.MAINDEST = '%s/%s' % (self.DIRECTORY, self.IMAGEFOLDER)
            self.EXTRA = '%s/EGAMI_fullbackup_%s/%s/%s' % (self.DIRECTORY,
             self.MODEL,
             self.DATE,
             self.IMAGEFOLDER)
            self.EXTRAOLD = '%s/EGAMI_fullbackup_%s/%s/%s' % (self.DIRECTORY,
             self.MODEL,
             self.DATE,
             self.MODEL)
            self.message = "echo -e '\n"
            self.message += _('Back-up Tool for a %s\n' % self.SHOWNAME).upper()
            self.message += VERSION + '\n'
            self.message += '_________________________________________________\n\n'
            self.message += _('Please be patient, a backup will now be made,\n')
            if self.ROOTFSTYPE == 'ubi':
                self.message += _('because of the used filesystem the back-up\n')
                self.message += _('will take about 3-12 minutes for this system\n')
            elif SystemInfo['HaveMultiBoot'] and self.list[self.selection] == 'Recovery':
                self.message += _('because of the used filesystem the back-up\n')
                self.message += _('will take about 30 minutes for this system\n')
            elif 'tar.bz2' in self.ROOTFSTYPE.split() or SystemInfo['HaveMultiBoot']:
                self.message += _('because of the used filesystem the back-up\n')
                self.message += _('will take about 1-4 minutes for this system\n')
            else:
                self.message += _('this will take between 2 and 9 minutes\n')
            self.message += '\n_________________________________________________\n\n'
            self.message += "'"
            system('rm -rf %s' % self.WORKDIR)
            if not path.exists(self.WORKDIR):
                makedirs(self.WORKDIR)
            if not path.exists('/tmp/bi/root'):
                makedirs('/tmp/bi/root')
            system('sync')
            if SystemInfo['HaveMultiBoot']:
                system('mount /dev/%s /tmp/bi/root' % self.MTDROOTFS)
            else:
                system('mount --bind / /tmp/bi/root')
            if 'jffs2' in self.ROOTFSTYPE.split():
                cmd1 = '%s --root=/tmp/bi/root --faketime --output=%s/root.jffs2 %s' % (self.MKFS, self.WORKDIR, self.MKUBIFS_ARGS)
                cmd2 = None
                cmd3 = None
            elif 'tar.bz2' in self.ROOTFSTYPE.split() or SystemInfo['HaveMultiBoot']:
                cmd1 = '%s -cf %s/rootfs.tar -C /tmp/bi/root --exclude=/var/nmbd/* .' % (self.MKFS, self.WORKDIR)
                cmd2 = '%s %s/rootfs.tar' % (self.BZIP2, self.WORKDIR)
                cmd3 = None
            else:
                f = open('%s/ubinize.cfg' % self.WORKDIR, 'w')
                f.write('[ubifs]\n')
                f.write('mode=ubi\n')
                f.write('image=%s/root.ubi\n' % self.WORKDIR)
                f.write('vol_id=0\n')
                f.write('vol_type=dynamic\n')
                f.write('vol_name=rootfs\n')
                f.write('vol_flags=autoresize\n')
                f.close()
                ff = open('%s/root.ubi' % self.WORKDIR, 'w')
                ff.close()
                cmd1 = '%s -r /tmp/bi/root -o %s/root.ubi %s' % (self.MKFS, self.WORKDIR, self.MKUBIFS_ARGS)
                cmd2 = '%s -o %s/root.ubifs %s %s/ubinize.cfg' % (self.UBINIZE,
                 self.WORKDIR,
                 self.UBINIZE_ARGS,
                 self.WORKDIR)
                cmd3 = 'mv %s/root.ubifs %s/root.%s' % (self.WORKDIR, self.WORKDIR, self.ROOTFSTYPE)
            cmdlist = []
            cmdlist.append(self.message)
            cmdlist.append('echo "Create: root.%s\n"' % self.ROOTFSTYPE)
            cmdlist.append(cmd1)
            if cmd2:
                cmdlist.append(cmd2)
            if cmd3:
                cmdlist.append(cmd3)
            cmdlist.append('chmod 644 %s/root.%s' % (self.WORKDIR, self.ROOTFSTYPE))
            cmdlist.append('echo " "')
            cmdlist.append('echo "Create: kerneldump"')
            cmdlist.append('echo " "')
            if SystemInfo['HaveMultiBoot']:
                cmdlist.append('dd if=/dev/%s of=%s/kernel.bin' % (self.MTDKERNEL, self.WORKDIR))
            elif self.MTDKERNEL == 'mmcblk0p1':
                cmdlist.append('dd if=/dev/%s of=%s/kernel_auto.bin' % (self.MTDKERNEL, self.WORKDIR))
            else:
                cmdlist.append('nanddump -a -f %s/vmlinux.gz /dev/%s' % (self.WORKDIR, self.MTDKERNEL))
            cmdlist.append('echo " "')
            if HaveGZkernel:
                cmdlist.append('echo "Check: kerneldump"')
            cmdlist.append('sync')
            if SystemInfo['HaveMultiBoot'] and self.list[self.selection] == 'Recovery':
                GPT_OFFSET = 0
                GPT_SIZE = 1024
                BOOT_PARTITION_OFFSET = int(GPT_OFFSET) + int(GPT_SIZE)
                BOOT_PARTITION_SIZE = 3072
                KERNEL_PARTITION_OFFSET = int(BOOT_PARTITION_OFFSET) + int(BOOT_PARTITION_SIZE)
                KERNEL_PARTITION_SIZE = 8192
                ROOTFS_PARTITION_OFFSET = int(KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
                ROOTFS_PARTITION_SIZE = 1048576
                SECOND_KERNEL_PARTITION_OFFSET = int(ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
                SECOND_ROOTFS_PARTITION_OFFSET = int(SECOND_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
                THRID_KERNEL_PARTITION_OFFSET = int(SECOND_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
                THRID_ROOTFS_PARTITION_OFFSET = int(THRID_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
                FOURTH_KERNEL_PARTITION_OFFSET = int(THRID_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
                FOURTH_ROOTFS_PARTITION_OFFSET = int(FOURTH_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
                EMMC_IMAGE = '%s/disk.img' % self.WORKDIR
                EMMC_IMAGE_SIZE = 3817472
                IMAGE_ROOTFS_SIZE = 196608
                cmdlist.append('echo " "')
                cmdlist.append('echo "Create: Recovery Fullbackup disk.img"')
                cmdlist.append('echo " "')
                cmdlist.append('dd if=/dev/zero of=%s bs=1024 count=0 seek=%s' % (EMMC_IMAGE, EMMC_IMAGE_SIZE))
                cmdlist.append('parted -s %s mklabel gpt' % EMMC_IMAGE)
                PARTED_END_BOOT = int(BOOT_PARTITION_OFFSET) + int(BOOT_PARTITION_SIZE)
                cmdlist.append('parted -s %s unit KiB mkpart boot fat16 %s %s' % (EMMC_IMAGE, BOOT_PARTITION_OFFSET, PARTED_END_BOOT))
                PARTED_END_KERNEL1 = int(KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
                cmdlist.append('parted -s %s unit KiB mkpart kernel1 %s %s' % (EMMC_IMAGE, KERNEL_PARTITION_OFFSET, PARTED_END_KERNEL1))
                PARTED_END_ROOTFS1 = int(ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
                cmdlist.append('parted -s %s unit KiB mkpart rootfs1 ext2 %s %s' % (EMMC_IMAGE, ROOTFS_PARTITION_OFFSET, PARTED_END_ROOTFS1))
                PARTED_END_KERNEL2 = int(SECOND_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
                cmdlist.append('parted -s %s unit KiB mkpart kernel2 %s %s' % (EMMC_IMAGE, SECOND_KERNEL_PARTITION_OFFSET, PARTED_END_KERNEL2))
                PARTED_END_ROOTFS2 = int(SECOND_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
                cmdlist.append('parted -s %s unit KiB mkpart rootfs2 ext2 %s %s' % (EMMC_IMAGE, SECOND_ROOTFS_PARTITION_OFFSET, PARTED_END_ROOTFS2))
                PARTED_END_KERNEL3 = int(THRID_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
                cmdlist.append('parted -s %s unit KiB mkpart kernel3 %s %s' % (EMMC_IMAGE, THRID_KERNEL_PARTITION_OFFSET, PARTED_END_KERNEL3))
                PARTED_END_ROOTFS3 = int(THRID_ROOTFS_PARTITION_OFFSET) + int(ROOTFS_PARTITION_SIZE)
                cmdlist.append('parted -s %s unit KiB mkpart rootfs3 ext2 %s %s' % (EMMC_IMAGE, THRID_ROOTFS_PARTITION_OFFSET, PARTED_END_ROOTFS3))
                PARTED_END_KERNEL4 = int(FOURTH_KERNEL_PARTITION_OFFSET) + int(KERNEL_PARTITION_SIZE)
                cmdlist.append('parted -s %s unit KiB mkpart kernel4 %s %s' % (EMMC_IMAGE, FOURTH_KERNEL_PARTITION_OFFSET, PARTED_END_KERNEL4))
                PARTED_END_ROOTFS4 = int(EMMC_IMAGE_SIZE) - 1024
                cmdlist.append('parted -s %s unit KiB mkpart rootfs4 ext2 %s %s' % (EMMC_IMAGE, FOURTH_ROOTFS_PARTITION_OFFSET, PARTED_END_ROOTFS4))
                cmdlist.append('dd if=/dev/zero of=%s/boot.img bs=1024 count=%s' % (self.WORKDIR, BOOT_PARTITION_SIZE))
                cmdlist.append('mkfs.msdos -S 512 %s/boot.img' % self.WORKDIR)
                cmdlist.append('echo "boot emmcflash0.kernel1 \'root=/dev/mmcblk0p3 rw rootwait hd51_4.boxmode=1\'" > %s/STARTUP' % self.WORKDIR)
                cmdlist.append('echo "boot emmcflash0.kernel1 \'root=/dev/mmcblk0p3 rw rootwait hd51_4.boxmode=1\'" > %s/STARTUP_1' % self.WORKDIR)
                cmdlist.append('echo "boot emmcflash0.kernel2 \'root=/dev/mmcblk0p5 rw rootwait hd51_4.boxmode=1\'" > %s/STARTUP_2' % self.WORKDIR)
                cmdlist.append('echo "boot emmcflash0.kernel3 \'root=/dev/mmcblk0p7 rw rootwait hd51_4.boxmode=1\'" > %s/STARTUP_3' % self.WORKDIR)
                cmdlist.append('echo "boot emmcflash0.kernel4 \'root=/dev/mmcblk0p9 rw rootwait hd51_4.boxmode=1\'" > %s/STARTUP_4' % self.WORKDIR)
                cmdlist.append('mcopy -i %s/boot.img -v %s/STARTUP ::' % (self.WORKDIR, self.WORKDIR))
                cmdlist.append('mcopy -i %s/boot.img -v %s/STARTUP_1 ::' % (self.WORKDIR, self.WORKDIR))
                cmdlist.append('mcopy -i %s/boot.img -v %s/STARTUP_2 ::' % (self.WORKDIR, self.WORKDIR))
                cmdlist.append('mcopy -i %s/boot.img -v %s/STARTUP_3 ::' % (self.WORKDIR, self.WORKDIR))
                cmdlist.append('mcopy -i %s/boot.img -v %s/STARTUP_4 ::' % (self.WORKDIR, self.WORKDIR))
                cmdlist.append('dd conv=notrunc if=%s/boot.img of=%s bs=1024 seek=%s' % (self.WORKDIR, EMMC_IMAGE, BOOT_PARTITION_OFFSET))
                cmdlist.append('dd conv=notrunc if=/dev/%s of=%s bs=1024 seek=%s' % (self.MTDKERNEL, EMMC_IMAGE, KERNEL_PARTITION_OFFSET))
                cmdlist.append('dd if=/dev/%s of=%s bs=1024 seek=%s count=%s' % (self.MTDROOTFS,
                 EMMC_IMAGE,
                 ROOTFS_PARTITION_OFFSET,
                 IMAGE_ROOTFS_SIZE))
            self.session.open(Console, title=self.TITLE, cmdlist=cmdlist, finishedCallback=self.doFullBackupCB, closeOnSuccess=True)
            return

    def doFullBackupCB(self):
        if HaveGZkernel:
            ret = commands.getoutput(' gzip -d %s/vmlinux.gz -c > /tmp/vmlinux.bin' % self.WORKDIR)
            if ret:
                text = 'Kernel dump error\n'
                text += 'Please Flash your Kernel new and Backup again'
                system('rm -rf /tmp/vmlinux.bin')
                self.session.open(MessageBox, _(text), type=MessageBox.TYPE_ERROR)
                return
        cmdlist = []
        cmdlist.append(self.message)
        if HaveGZkernel:
            cmdlist.append('echo "Kernel dump OK"')
            cmdlist.append('rm -rf /tmp/vmlinux.bin')
        cmdlist.append('echo "_________________________________________________"')
        cmdlist.append('echo "Almost there... "')
        cmdlist.append('echo "Now building the USB-Image"')
        system('rm -rf %s' % self.MAINDEST)
        if not path.exists(self.MAINDEST):
            makedirs(self.MAINDEST)
        if not path.exists(self.EXTRA):
            makedirs(self.EXTRA)
        f = open('%s/imageversion' % self.MAINDEST, 'w')
        f.write(self.IMAGEVERSION)
        f.close()
        if self.ROOTFSBIN == 'rootfs.tar.bz2':
            system('mv %s/rootfs.tar.bz2 %s/rootfs.tar.bz2' % (self.WORKDIR, self.MAINDEST))
        else:
            system('mv %s/root.%s %s/%s' % (self.WORKDIR,
             self.ROOTFSTYPE,
             self.MAINDEST,
             self.ROOTFSBIN))
        if SystemInfo['HaveMultiBoot']:
            system('mv %s/kernel.bin %s/kernel.bin' % (self.WORKDIR, self.MAINDEST))
        elif self.KERNELBIN == 'kernel_auto.bin':
            system('mv %s/kernel_auto.bin %s/kernel_auto.bin' % (self.WORKDIR, self.MAINDEST))
        else:
            system('mv %s/vmlinux.gz %s/%s' % (self.WORKDIR, self.MAINDEST, self.KERNELBIN))
        if SystemInfo['HaveMultiBoot'] and self.list[self.selection] == 'Recovery':
            system('mv %s/disk.img %s/disk.img' % (self.WORKDIR, self.MAINDEST))
        elif self.MODEL in ('vusolo4k', 'vuduo2', 'vusolo2', 'vusolo', 'vuduo', 'vuultimo', 'vuuno'):
            cmdlist.append('echo "This file forces a reboot after the update." > %s/reboot.update' % self.MAINDEST)
        elif self.MODEL in ('vuzero', 'vusolose', 'xpeedlxpro'):
            cmdlist.append('echo "This file forces the update." > %s/force.update' % self.MAINDEST)
        else:
            cmdlist.append('echo "rename this file to "force" to force an update without confirmation" > %s/noforce' % self.MAINDEST)
        if self.MODEL in ('gbquad', 'gbquadplus', 'gb800ue', 'gb800ueplus', 'gbultraue', 'twinboxlcd', 'twinboxlcdci', 'singleboxlcd', 'sf208', 'sf228'):
            lcdwaitkey = '/usr/share/lcdwaitkey.bin'
            lcdwarning = '/usr/share/lcdwarning.bin'
            if path.exists(lcdwaitkey):
                system('cp %s %s/lcdwaitkey.bin' % (lcdwaitkey, self.MAINDEST))
            if path.exists(lcdwarning):
                system('cp %s %s/lcdwarning.bin' % (lcdwarning, self.MAINDEST))
        if self.MODEL == 'gb800solo':
            burnbat = '%s/EGAMI_fullbackup_%s/%s' % (self.DIRECTORY, self.MODEL, self.DATE)
            f = open('%s/burn.bat' % burnbat, 'w')
            f.write('flash -noheader usbdisk0:gigablue/solo/kernel.bin flash0.kernel\n')
            f.write('flash -noheader usbdisk0:gigablue/solo/rootfs.bin flash0.rootfs\n')
            f.write('setenv -p STARTUP "boot -z -elf flash0.kernel: ')
            f.write("'rootfstype=jffs2 bmem=106M@150M root=/dev/mtdblock6 rw '")
            f.write('"\n')
            f.close()
        cmdlist.append('cp -r %s/* %s/' % (self.MAINDEST, self.EXTRA))
        cmdlist.append('sync')
        file_found = True
        if not path.exists('%s/%s' % (self.MAINDEST, self.ROOTFSBIN)):
            print 'ROOTFS bin file not found'
            file_found = False
        if not path.exists('%s/%s' % (self.MAINDEST, self.KERNELBIN)):
            print 'KERNEL bin file not found'
            file_found = False
        if path.exists('%s/noforce' % self.MAINDEST):
            print 'NOFORCE bin file not found'
            file_found = False
        if SystemInfo['HaveMultiBoot'] and not self.list[self.selection] == 'Recovery':
            cmdlist.append('echo "_________________________________________________\n"')
            cmdlist.append('echo "Multiboot Image created on:" %s' % self.MAINDEST)
            cmdlist.append('echo "and there is made an extra copy on:"')
            cmdlist.append('echo %s' % self.EXTRA)
            cmdlist.append('echo "_________________________________________________\n"')
            cmdlist.append('echo " "')
            cmdlist.append('echo "\nPlease wait...almost ready! "')
            cmdlist.append('echo " "')
            cmdlist.append('echo "To restore the image:"')
            cmdlist.append('echo "Use OnlineFlash in SoftwareManager"')
        elif file_found:
            cmdlist.append('echo "_________________________________________________\n"')
            cmdlist.append('echo "USB Image created on:" %s' % self.MAINDEST)
            cmdlist.append('echo "and there is made an extra copy on:"')
            cmdlist.append('echo %s' % self.EXTRA)
            cmdlist.append('echo "_________________________________________________\n"')
            cmdlist.append('echo " "')
            cmdlist.append('echo "\nPlease wait...almost ready! "')
            cmdlist.append('echo " "')
            cmdlist.append('echo "To restore the image:"')
            cmdlist.append('echo "Please check the manual of the receiver"')
            cmdlist.append('echo "on how to restore the image"')
        else:
            cmdlist.append('echo "_________________________________________________\n"')
            cmdlist.append('echo "Image creation failed - "')
            cmdlist.append('echo "Probable causes could be"')
            cmdlist.append('echo "     wrong back-up destination "')
            cmdlist.append('echo "     no space left on back-up device"')
            cmdlist.append('echo "     no writing permission on back-up device"')
            cmdlist.append('echo " "')
        if self.DIRECTORY == '/media/hdd':
            self.TARGET = self.SearchUSBcanidate()
            print 'TARGET = %s' % self.TARGET
            if self.TARGET == 'XX':
                cmdlist.append('echo " "')
            else:
                cmdlist.append('echo "_________________________________________________\n"')
                cmdlist.append('echo " "')
                cmdlist.append('echo "There is a valid USB-flash drive detected in one "')
                cmdlist.append('echo "of the USB-ports, therefor an extra copy of the "')
                cmdlist.append('echo "back-up image will now be copied to that USB- "')
                cmdlist.append('echo "flash drive. "')
                cmdlist.append('echo "This only takes about 1 or 2 minutes"')
                cmdlist.append('echo " "')
                cmdlist.append('mkdir -p %s/%s' % (self.TARGET, self.IMAGEFOLDER))
                cmdlist.append('cp -r %s %s/' % (self.MAINDEST, self.TARGET))
                cmdlist.append('sync')
                cmdlist.append('echo "Backup finished and copied to your USB-flash drive"')
        cmdlist.append('umount /tmp/bi/root')
        cmdlist.append('rmdir /tmp/bi/root')
        cmdlist.append('rmdir /tmp/bi')
        cmdlist.append('rm -rf %s' % self.WORKDIR)
        cmdlist.append('sleep 5')
        END = time()
        DIFF = int(END - self.START)
        TIMELAP = str(datetime.timedelta(seconds=DIFF))
        cmdlist.append('echo " Time required for this process: %s"' % TIMELAP)
        self.session.open(Console, title=self.TITLE, cmdlist=cmdlist, closeOnSuccess=True)

    def imageInfo(self):
        AboutText = _('Full Image Backup ')
        AboutText += _('By EGAMI Image Team') + '\n'
        AboutText += _('Support at') + ' www.egami-image.com\n\n'
        AboutText += _('[Image Info]\n')
        AboutText += _('Model: %s %s\n') % (getMachineBrand(), getMachineName())
        AboutText += _('Backup Date: %s\n') % strftime('%Y-%m-%d', localtime(self.START))
        if path.exists('/proc/stb/info/chipset'):
            AboutText += _('Chipset: BCM%s') % about.getChipSetString().lower().replace('\n', '').replace('bcm', '') + '\n'
        AboutText += _('CPU: %s') % about.getCPUString() + '\n'
        AboutText += _('Cores: %s') % about.getCpuCoresString() + '\n'
        AboutText += _('Version: %s') % getImageVersion() + '\n'
        AboutText += _('Build: %s') % getImageBuild() + '\n'
        AboutText += _('Kernel: %s') % about.getKernelVersionString() + '\n'
        string = getDriverDate()
        year = string[0:4]
        month = string[4:6]
        day = string[6:8]
        driversdate = '-'.join((year, month, day))
        AboutText += _('Drivers:\t%s') % driversdate + '\n'
        AboutText += _('Last update:\t%s') % getEnigmaVersionString() + '\n\n'
        AboutText += _('[Enigma2 Settings]\n')
        AboutText += commands.getoutput('cat /etc/enigma2/settings')
        AboutText += _('\n\n[User - bouquets (TV)]\n')
        try:
            f = open('/etc/enigma2/bouquets.tv', 'r')
            lines = f.readlines()
            f.close()
            for line in lines:
                if line.startswith('#SERVICE:'):
                    bouqet = line.split()
                    if len(bouqet) > 3:
                        bouqet[3] = bouqet[3].replace('"', '')
                        f = open('/etc/enigma2/' + bouqet[3], 'r')
                        userbouqet = f.readline()
                        AboutText += userbouqet.replace('#NAME ', '')
                        f.close()

        except:
            AboutText += 'Error reading bouquets.tv'

        AboutText += _('\n[User - bouquets (RADIO)]\n')
        try:
            f = open('/etc/enigma2/bouquets.radio', 'r')
            lines = f.readlines()
            f.close()
            for line in lines:
                if line.startswith('#SERVICE:'):
                    bouqet = line.split()
                    if len(bouqet) > 3:
                        bouqet[3] = bouqet[3].replace('"', '')
                        f = open('/etc/enigma2/' + bouqet[3], 'r')
                        userbouqet = f.readline()
                        AboutText += userbouqet.replace('#NAME ', '')
                        f.close()

        except:
            AboutText += 'Error reading bouquets.radio'

        AboutText += _('\n[Installed Plugins]\n')
        AboutText += commands.getoutput('opkg list_installed | grep enigma2-plugin-')
        return AboutText
