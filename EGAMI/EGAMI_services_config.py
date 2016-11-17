from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Screens.Console import Console
from Screens.LocationBox import *
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.Label import Label
from Components.config import *
from Components.ConfigList import *
from Tools.Directories import fileExists, resolveFilename, SCOPE_SKIN_IMAGE
import os
from EGAMI.EGAMI_tools import wyszukaj_re, wyszukaj_in, loadcfg

class EGHttpd(ConfigListScreen, Screen):
    skin = '\n\t<screen name="EGHttpd" position="center,center" size="570,350" title="EGAMI HTTPD Server Setup" >\n\t\t  <widget name="config" position="10,10" size="550,220" scrollbarMode="showOnDemand" />\n\t\t  <widget name="state" position="120,245" size="300,25" font="Regular;20" halign="center" noWrap="1" backgroundColor="red" foregroundColor="white" shadowOffset="-2,-2" shadowColor="black"  />\n\t\t  <ePixmap name="key_red_png" pixmap="skin_default/buttons/button_red.png" position="10,320" size="140,40" alphatest="on" />\n\t\t  <widget name="key_red" position="40,320" zPosition="1" size="200,40" font="Regular;20" halign="left" valign="top" backgroundColor="#9f1313" transparent="1" />\n\t\t  <ePixmap name="key_green_png" pixmap="skin_default/buttons/button_green.png" position="150,320" size="140,40" alphatest="on" />\n\t\t  <widget name="key_green" position="180,320" zPosition="1" size="200,40" font="Regular;20" halign="left" valign="top" backgroundColor="#9f1313" transparent="1" />\n\t\t  <ePixmap name="key_yellow_png" pixmap="skin_default/buttons/button_yellow.png" position="300,320" size="140,40" alphatest="on" />\n\t\t  <widget name="key_yellow" position="330,320" zPosition="1" size="140,40" font="Regular;20" halign="left" valign="top" backgroundColor="#a08500" transparent="1" />\n\t\t  <ePixmap name="key_blue_png" pixmap="skin_default/buttons/button_blue.png" position="450,320" size="140,40" alphatest="on" />\n\t\t  <widget name="key_blue" position="480,320" zPosition="1" size="140,40" font="Regular;20" halign="left" valign="top" backgroundColor="#a08500" transparent="1" />\n\t</screen>'

    def __init__(self, session, args = 0):
        Screen.__init__(self, session)
        session = None
        self.load_conf()
        self.httpau = ConfigSelection(default=self.def_httpau, choices=[('1', _('Yes')), ('0', _('No'))])
        self.httproot = ConfigText(default=self.def_httproot, fixed_size=False)
        self.httpport = ConfigText(default=self.def_httpport, fixed_size=False)
        self.httpconf = ConfigText(default=self.def_httpconf, fixed_size=False)
        self.createSetup()
        ConfigListScreen.__init__(self, self.list, session=session)
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions', 'CiSelectionActions'], {'cancel': self.cancel,
         'red': self.start_httpd,
         'green': self.cancel,
         'yellow': self.start,
         'blue': self.stop}, -2)
        self['key_red'] = Label(_('Save'))
        self['key_green'] = Label(_('Cancel'))
        self['key_yellow'] = Label(_('Start'))
        self['key_blue'] = Label(_('Stop'))
        self['state'] = Label()
        self.createInfo()
        return

    def createInfo(self):
        os.system('ps > /tmp/ps.tmp')
        zrodlo = open('/tmp/ps.tmp', 'r')
        szukana_fraza = 'httpd'
        if wyszukaj_in(zrodlo, szukana_fraza):
            self['state'].setText(_('Status: Httpd is running!'))
        else:
            self['state'].setText(_('Status: Httpd stopped!'))
        os.system('rm -rf /tmp/ps.tmp')
        zrodlo.seek(0)
        zrodlo.close()

    def createSetup(self):
        self.list = []
        self.list.append(getConfigListEntry(_('Autostart:'), self.httpau))
        self.list.append(getConfigListEntry(_('WWW Directory:'), self.httproot))
        self.list.append(getConfigListEntry(_('Port:'), self.httpport))
        self.list.append(getConfigListEntry(_('HTTPD Config File:'), self.httpconf))

    def load_conf(self):
        self.def_httpau = '0'
        self.def_httproot = '/usr/www'
        self.def_httpport = '8047'
        self.def_httpconf = '/var/etc/httpd.conf'
        if fileExists('/scripts/httpd_script.sh'):
            f = open('/scripts/httpd_script.sh', 'r')
            for line in f.readlines():
                line = line.strip()
                if line.find('HTTP_ON=') != -1:
                    self.def_httpau = line[8:9]
                elif line.find('HTTPROOT=') != -1:
                    self.def_httproot = line[9:]
                elif line.find('HTTPPORT=') != -1:
                    self.def_httpport = line[9:]
                elif line.find('HTTPCONF=') != -1:
                    self.def_httpconf = line[9:]

            f.close()

    def save_conf(self):
        zrodlo = open('/scripts/httpd_script.sh').readlines()
        cel = open('/scripts/httpd_script.sh', 'w')
        for s in zrodlo:
            cel.write(s.replace('HTTP_ON=' + self.def_httpau, 'HTTP_ON=' + self.httpau.value))

        cel.close()
        zrodlo = open('/scripts/httpd_script.sh').readlines()
        cel = open('/scripts/httpd_script.sh', 'w')
        for s in zrodlo:
            cel.write(s.replace(self.def_httproot, self.httproot.value))

        cel.close()
        zrodlo = open('/scripts/httpd_script.sh').readlines()
        cel = open('/scripts/httpd_script.sh', 'w')
        for s in zrodlo:
            cel.write(s.replace(self.def_httpport, self.httpport.value))

        cel.close()
        zrodlo = open('/scripts/httpd_script.sh').readlines()
        cel = open('/scripts/httpd_script.sh', 'w')
        for s in zrodlo:
            cel.write(s.replace(self.def_httpconf, self.httpconf.value))

        cel.close()

    def start(self):
        self.stop()
        self.save_conf()
        self['state'].setText(_('Status: httpd is starting...'))
        os.system('/scripts/httpd_script.sh start2')
        self.createInfo()

    def stop(self):
        self['state'].setText(_('Status: httpd is stopping...'))
        os.system('/scripts/httpd_script.sh stop;killall -9 httpd')
        self.createInfo()

    def start_httpd(self):
        self.save_conf()
        self.createInfo()
        self.load_conf()
        self.close(True)

    def cancel(self):
        self.close(False)


class EGDjMountConfigRoot(LocationBox):
    skin = '\n\t\t<screen name="EGDjMountConfigRoot" position="center,center" size="540,460" >\n\t\t\t<widget name="text" position="0,2" size="540,22" font="Regular;22" />\n\t\t\t<widget name="target" position="0,23" size="540,22" valign="center" font="Regular;22" />\n\t\t\t<widget name="filelist" position="0,55" zPosition="1" size="540,210" scrollbarMode="showOnDemand" selectionDisabled="1" />\n\t\t\t<widget name="red" position="0,415" zPosition="1" size="135,40" pixmap="skin_default/buttons/button_red.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_red" position="0,415" zPosition="2" size="135,40" halign="center" valign="center" font="Regular;22" transparent="1" shadowColor="black" shadowOffset="-1,-1" />\t\n\t\t\t<widget name="green" position="135,415" zPosition="1" size="135,40" pixmap="skin_default/buttons/button_green.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_green" position="135,415" zPosition="2" size="135,40" halign="center" valign="center" font="Regular;22" transparent="1" shadowColor="black" shadowOffset="-1,-1" />\n\t\t</screen>'

    def __init__(self, session):
        inhibitDirs = ['/bin',
         '/boot',
         '/dev',
         '/etc',
         '/lib',
         '/proc',
         '/sbin',
         '/sys',
         '/usr',
         '/var']
        log = loadcfg('/scripts/djmount_script.sh', 'UPNPROOT=', 9)
        LocationBox.__init__(self, session, text=_('Where would You like to have an UPnP root directory?'), currDir=log, bookmarks=None, autoAdd=True, editDir=False, inhibitDirs=[], minFree=None)
        return

    def cancel(self):
        LocationBox.cancel(self)

    def selectConfirmed(self, ret):
        if ret:
            log = loadcfg('/scripts/djmount_script.sh', 'UPNPROOT=', 9)
            new_root = self.getPreferredFolder()
            zrodlo = open('/scripts/djmount_script.sh').readlines()
            cel = open('/scripts/djmount_script.sh', 'w')
            for s in zrodlo:
                cel.write(s.replace(log, new_root))

            cel.close()
            LocationBox.selectConfirmed(self, ret)


class EGDjMountConfig(ConfigListScreen, Screen):
    skin = '\n\t\t<screen name="EGDjMountConfig" position="center,center" size="570,350" title="EGAMI DjMount Setup" >\n\t\t\t      <widget name="config" position="10,10" size="550,200" scrollbarMode="showOnDemand" />\n\t\t\t      <widget name="state" position="120,240" size="300,25" font="Regular;20" halign="center" noWrap="1" backgroundColor="red" foregroundColor="white" shadowOffset="-2,-2" shadowColor="black"  />\n\t\t\t      <ePixmap name="key_red_png" pixmap="skin_default/buttons/button_red.png" position="10,320" size="140,40" alphatest="on" />\n\t\t\t      <widget name="key_red" position="40,320" zPosition="1" size="200,40" font="Regular;20" halign="left" valign="top" backgroundColor="#9f1313" transparent="1" />\n\t\t\t      <ePixmap name="key_green_png" pixmap="skin_default/buttons/button_green.png" position="150,320" size="140,40" alphatest="on" />\n\t\t\t      <widget name="key_green" position="180,320" zPosition="1" size="200,40" font="Regular;20" halign="left" valign="top" backgroundColor="#9f1313" transparent="1" />\n\t\t\t      <ePixmap name="key_yellow_png" pixmap="skin_default/buttons/button_yellow.png" position="300,320" size="140,40" alphatest="on" />\n\t\t\t      <widget name="key_yellow" position="330,320" zPosition="1" size="140,40" font="Regular;20" halign="left" valign="top" backgroundColor="#a08500" transparent="1" />\n\t\t\t      <ePixmap name="key_blue_png" pixmap="skin_default/buttons/button_blue.png" position="450,320" size="140,40" alphatest="on" />\n\t\t\t      <widget name="key_blue" position="480,320" zPosition="1" size="140,40" font="Regular;20" halign="left" valign="top" backgroundColor="#a08500" transparent="1" />\n\t\t      </screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        session = None
        self.load_conf()
        self.au = ConfigSelection(default=self.def_au, choices=[('1', _('Yes')), ('0', _('No'))])
        self.dir_root = ConfigText(default=self.def_dir_root)
        self.createSetup()
        ConfigListScreen.__init__(self, self.list, session=session)
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions', 'CiSelectionActions'], {'cancel': self.cancel,
         'red': self.start_djmount,
         'green': self.cancel,
         'yellow': self.start,
         'blue': self.stop}, -2)
        self['key_red'] = Label(_('Save'))
        self['key_green'] = Label(_('Cancel'))
        self['key_yellow'] = Label(_('Start'))
        self['key_blue'] = Label(_('Stop'))
        self['state'] = Label()
        self.createInfo()
        return

    def createSetup(self):
        self.list = []
        self.list.append(getConfigListEntry(_('Autostart:'), self.au))
        self.list.append(getConfigListEntry(_('DjMount UPnP root directory:'), self.dir_root))

    def createInfo(self):
        os.system('ps > /tmp/djmount.tmp')
        zrodlo = open('/tmp/djmount.tmp', 'r')
        szukana_fraza = '/usr/bin/djmount'
        if wyszukaj_in(zrodlo, szukana_fraza):
            self['state'].setText(_('Status: DjMount is running!'))
        else:
            self['state'].setText(_('Status: DjMount stopped!'))
        os.system('rm -rf /tmp/djmount.tmp')
        zrodlo.seek(0)
        zrodlo.close()

    def start(self):
        self.stop()
        self.save_conf()
        self['state'].setText(_('Status: djmount is starting...'))
        os.system('/scripts/djmount_script.sh start2')
        self.createInfo()

    def stop(self):
        self['state'].setText(_('Status: djmount is stopping...'))
        os.system('/scripts/djmount_script.sh stop;killall -9 djmount')
        self.createInfo()

    def cancel(self):
        self.close(False)

    def load_conf(self):
        self.def_au = '0'
        self.def_dir_root = '/media/hdd'
        if fileExists('/scripts/djmount_script.sh'):
            f = open('/scripts/djmount_script.sh', 'r')
            for line in f.readlines():
                line = line.strip()
                if line.find('UPNP_ON=') != -1:
                    self.def_au = line[8:9]

            f.close()
        self.def_dir_root = loadcfg('/scripts/djmount_script.sh', 'UPNPROOT=', 9)

    def save_conf(self):
        zrodlo = open('/scripts/djmount_script.sh').readlines()
        cel = open('/scripts/djmount_script.sh', 'w')
        for s in zrodlo:
            cel.write(s.replace('UPNP_ON=' + self.def_au, 'UPNP_ON=' + self.au.value))

        cel.close()

    def start_djmount(self):
        self.save_conf()
        self.createInfo()
        self.load_conf()
        self.close(True)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.handleKeysLeftAndRight()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.handleKeysLeftAndRight()

    def handleKeysLeftAndRight(self):
        sel = self['config'].getCurrent()[1]
        if sel == self.dir_root:
            self.session.open(EGDjMountConfigRoot)
            self.close()


class EGSyslogDConfig(ConfigListScreen, Screen):
    skin = '\n\t\t    <screen name="EGSyslogDConfig" position="center,center" size="570,450" title="EGAMI Syslogd and Klogd Setup" >\n\t\t\t      <widget name="config" position="10,10" size="550,330" scrollbarMode="showOnDemand" />\n\t\t\t      <widget name="state" position="100,360" size="370,25" font="Regular;20" halign="center" noWrap="1" backgroundColor="red" foregroundColor="white" shadowOffset="-2,-2" shadowColor="black"  />\n\t\t\t      <ePixmap name="key_red_png" pixmap="skin_default/buttons/button_red.png" position="10,420" size="140,40" alphatest="on" />\n\t\t\t      <widget name="key_red" position="40,420" zPosition="1" size="200,40" font="Regular;20" halign="left" valign="top" backgroundColor="#9f1313" transparent="1" />\n\t\t\t      <ePixmap name="key_green_png" pixmap="skin_default/buttons/button_green.png" position="150,420" size="140,40" alphatest="on" />\n\t\t\t      <widget name="key_green" position="180,420" zPosition="1" size="200,40" font="Regular;20" halign="left" valign="top" backgroundColor="#9f1313" transparent="1" />\n\t\t\t      <ePixmap name="key_yellow_png" pixmap="skin_default/buttons/button_yellow.png" position="300,420" size="140,40" alphatest="on" />\n\t\t\t      <widget name="key_yellow" position="330,420" zPosition="1" size="140,40" font="Regular;20" halign="left" valign="top" backgroundColor="#a08500" transparent="1" />\n\t\t\t      <ePixmap name="key_blue_png" pixmap="skin_default/buttons/button_blue.png" position="450,420" size="140,40" alphatest="on" />\n\t\t\t      <widget name="key_blue" position="480,420" zPosition="1" size="140,40" font="Regular;20" halign="left" valign="top" backgroundColor="#a08500" transparent="1" />\n\t\t    </screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        session = None
        self.load_conf()
        self.au = ConfigSelection(default=self.def_enigma_debug, choices=[('1', _('Yes')), ('0', _('No'))])
        self.enigma_debug = ConfigSelection(default=self.def_enigma_debug, choices=[('1', _('Yes')), ('0', _('No'))])
        self.kernel_debug = ConfigSelection(default=self.def_kernel_debug, choices=[('1', _('Yes')), ('0', _('No'))])
        self.buffer_size = ConfigNumber(default=self.def_buffer_size)
        self.set_idx = ConfigSelection(default=self.def_set_idx, choices=[('1', _('Yes')), ('0', _('No'))])
        self.inter_min = ConfigNumber(default=self.def_inter_min)
        self.red_size = ConfigSelection(default=self.def_red_size, choices=[('1', _('Yes')), ('0', _('No'))])
        self.log_file_name = ConfigText(default=self.def_log_file_name, fixed_size=False)
        self.rem_log = ConfigSelection(default=self.def_rem_log, choices=[('1', _('Yes')), ('0', _('No'))])
        self.rem_host = ConfigText(default=self.def_rem_host)
        self.rem_port = ConfigNumber(default=self.def_rem_port)
        self.createSetup()
        ConfigListScreen.__init__(self, self.list, session=session)
        self.rem_log.addNotifier(self.typeChange)
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions', 'CiSelectionActions'], {'cancel': self.cancel,
         'red': self.start_syslogd,
         'green': self.cancel,
         'yellow': self.start,
         'blue': self.stop}, -2)
        self['key_red'] = Label(_('Save'))
        self['key_green'] = Label(_('Cancel'))
        self['key_yellow'] = Label(_('Start'))
        self['key_blue'] = Label(_('Stop'))
        self['state'] = Label()
        self.createInfo()
        return

    def createInfo(self):
        os.system('ps > /tmp/syslogd.tmp')
        zrodlo = open('/tmp/syslogd.tmp', 'r')
        szukana_fraza = '/sbin/klogd'
        if wyszukaj_in(zrodlo, szukana_fraza):
            self['state'].setText(_('Status: syslogd and klogd are running!'))
        else:
            self['state'].setText(_('Status: syslogd and klogd stopped!'))
        os.system('rm -rf /tmp/syslogd.tmp')
        zrodlo.seek(0)
        zrodlo.close()

    def typeChange(self, value):
        self.createSetup()
        self['config'].l.setList(self.list)

    def createSetup(self):
        self.list = []
        self.list.append(getConfigListEntry(_('Autostart:'), self.au))
        self.list.append(getConfigListEntry(_('Enigma-Debug:'), self.enigma_debug))
        self.list.append(getConfigListEntry(_('Kernel-Debug:'), self.kernel_debug))
        self.list.append(getConfigListEntry(_('Buffer size [kB]:'), self.buffer_size))
        self.list.append(getConfigListEntry(_('Set index mark:'), self.set_idx))
        self.list.append(getConfigListEntry(_('Interval in min:'), self.inter_min))
        self.list.append(getConfigListEntry(_('Reduce size logging:'), self.red_size))
        self.list.append(getConfigListEntry(_('Log file name:'), self.log_file_name))
        self.list.append(getConfigListEntry(_('Remote logging:'), self.rem_log))
        if self.rem_log.value == '1':
            self.list.append(getConfigListEntry(_('\tRemote host:'), self.rem_host))
            self.list.append(getConfigListEntry(_('\tRemote port:'), self.rem_port))

    def load_conf(self):
        self.def_enigma_debug = '0'
        self.def_kernel_debug = '0'
        self.def_buffer_size = 16
        self.def_set_idx = '1'
        self.def_inter_min = 20
        self.def_red_size = '0'
        self.def_log_file_name = '/var/log/messages'
        self.def_rem_log = '0'
        self.def_rem_host = '192.168.0.1'
        self.def_rem_port = 514
        if fileExists('/scripts/syslogd_script.sh'):
            f = open('/scripts/syslogd_script.sh', 'r')
            for line in f.readlines():
                line = line.strip()
                if line.find('SYSLOGD_ON=') != -1:
                    self.def_enigma_debug = line[11:]
                elif line.find('KLOGD_ON=') != -1:
                    self.def_kernel_debug = line[9:]
                elif line.find('BUFFERSIZE=') != -1:
                    self.def_buffer_size = line[11:]
                elif line.find('MARKINT=') != -1:
                    self.def_inter_min = line[8:]
                elif line.find('REDUCE=') != -1:
                    self.def_red_size = line[7:]
                elif line.find('LOGFILE=') != -1:
                    self.def_log_file_name = line[8:]
                elif line.find('REMOTE=') != -1:
                    self.def_rem_log = line[7:]
                elif line.find('REMOTE_HOST=') != -1:
                    self.def_rem_host = line[12:]
                elif line.find('REMOTE_PORT=') != -1:
                    self.def_rem_port = line[12:]

            f.close()

    def save_conf(self):
        zrodlo = open('/scripts/syslogd_script.sh').readlines()
        cel = open('/scripts/syslogd_script.sh', 'w')
        for s in zrodlo:
            cel.write(s.replace('SYSLOGD_ON=' + self.def_enigma_debug, 'SYSLOGD_ON=' + self.enigma_debug.value))

        cel.close()
        zrodlo = open('/scripts/syslogd_script.sh').readlines()
        cel = open('/scripts/syslogd_script.sh', 'w')
        for s in zrodlo:
            cel.write(s.replace('KLOGD_ON=' + self.def_kernel_debug, 'KLOGD_ON=' + self.kernel_debug.value))

        cel.close()
        zrodlo = open('/scripts/syslogd_script.sh').readlines()
        cel = open('/scripts/syslogd_script.sh', 'w')
        for s in zrodlo:
            cel.write(s.replace(self.def_buffer_size, str(self.buffer_size.value)))

        cel.close()
        zrodlo = open('/scripts/syslogd_script.sh').readlines()
        cel = open('/scripts/syslogd_script.sh', 'w')
        for s in zrodlo:
            cel.write(s.replace(self.def_inter_min, str(self.inter_min.value)))

        cel.close()
        zrodlo = open('/scripts/syslogd_script.sh').readlines()
        cel = open('/scripts/syslogd_script.sh', 'w')
        for s in zrodlo:
            cel.write(s.replace('REDUCE=' + self.def_red_size, 'REDUCE=' + self.red_size.value))

        cel.close()
        zrodlo = open('/scripts/syslogd_script.sh').readlines()
        cel = open('/scripts/syslogd_script.sh', 'w')
        for s in zrodlo:
            cel.write(s.replace(self.def_log_file_name, self.log_file_name.value))

        cel.close()
        zrodlo = open('/scripts/syslogd_script.sh').readlines()
        cel = open('/scripts/syslogd_script.sh', 'w')
        for s in zrodlo:
            cel.write(s.replace('REMOTE=' + self.def_rem_log, 'REMOTE=' + self.rem_log.value))

        cel.close()
        zrodlo = open('/scripts/syslogd_script.sh').readlines()
        cel = open('/scripts/syslogd_script.sh', 'w')
        for s in zrodlo:
            cel.write(s.replace(self.def_rem_host, self.rem_host.value))

        cel.close()
        zrodlo = open('/scripts/syslogd_script.sh').readlines()
        cel = open('/scripts/syslogd_script.sh', 'w')
        for s in zrodlo:
            cel.write(s.replace(self.def_rem_port, str(self.rem_port.value)))

        cel.close()

    def start(self):
        self.stop()
        self.save_conf()
        self['state'].setText(_('Status: syslogd is starting...'))
        os.system('/scripts/syslogd_script.sh start2')
        self.createInfo()

    def stop(self):
        self['state'].setText(_('Status: syslogd is stopping...'))
        os.system('/scripts/syslogd_script.sh stop;killall -9 syslogd klogd')
        self.createInfo()

    def start_syslogd(self):
        self.save_conf()
        self.close(True)

    def cancel(self):
        self.close(False)


class EGPcscdConfig(ConfigListScreen, Screen):
    skin = '\n\t\t      <screen name="EGPcscdConfig" position="center,center" size="570,350" title="EGAMI Pcscd Setup" >\n\t\t\t      <widget name="config" position="10,10" size="550,200" scrollbarMode="showOnDemand" />\n\t\t\t      <widget name="state" position="120,240" size="300,25" font="Regular;20" halign="center" noWrap="1" backgroundColor="red" foregroundColor="white" shadowOffset="-2,-2" shadowColor="black"  />\n\t\t\t      <ePixmap name="key_red_png" pixmap="skin_default/buttons/button_red.png" position="10,320" size="140,40" alphatest="on" />\n\t\t\t      <widget name="key_red" position="40,320" zPosition="1" size="200,40" font="Regular;20" halign="left" valign="top" backgroundColor="#9f1313" transparent="1" />\n\t\t\t      <ePixmap name="key_green_png" pixmap="skin_default/buttons/button_green.png" position="150,320" size="140,40" alphatest="on" />\n\t\t\t      <widget name="key_green" position="180,320" zPosition="1" size="200,40" font="Regular;20" halign="left" valign="top" backgroundColor="#9f1313" transparent="1" />\n\t\t\t      <ePixmap name="key_yellow_png" pixmap="skin_default/buttons/button_yellow.png" position="300,320" size="140,40" alphatest="on" />\n\t\t\t      <widget name="key_yellow" position="330,320" zPosition="1" size="140,40" font="Regular;20" halign="left" valign="top" backgroundColor="#a08500" transparent="1" />\n\t\t\t      <ePixmap name="key_blue_png" pixmap="skin_default/buttons/button_blue.png" position="450,320" size="140,40" alphatest="on" />\n\t\t\t      <widget name="key_blue" position="480,320" zPosition="1" size="140,40" font="Regular;20" halign="left" valign="top" backgroundColor="#a08500" transparent="1" />\n\t\t      </screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        session = None
        self.load_conf()
        self.au = ConfigSelection(default=self.def_au, choices=[('1', _('Yes')), ('0', _('No'))])
        self.createSetup()
        ConfigListScreen.__init__(self, self.list, session=session)
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions', 'CiSelectionActions'], {'cancel': self.cancel,
         'red': self.start_samba,
         'green': self.cancel,
         'yellow': self.start,
         'blue': self.stop}, -2)
        self['key_red'] = Label(_('Save'))
        self['key_green'] = Label(_('Cancel'))
        self['key_yellow'] = Label(_('Start'))
        self['key_blue'] = Label(_('Stop'))
        self['state'] = Label()
        self.createInfo()
        return

    def createSetup(self):
        self.list = []
        self.list.append(getConfigListEntry(_('Autostart:'), self.au))

    def createInfo(self):
        os.system('ps > /tmp/pcscd.tmp')
        zrodlo = open('/tmp/pcscd.tmp', 'r')
        szukana_fraza = '/usr/sbin/pcscd'
        if wyszukaj_in(zrodlo, szukana_fraza):
            self['state'].setText(_('Status: Pcscd is running!'))
        else:
            self['state'].setText(_('Status: Pcscd stopped!'))
        os.system('rm -rf /tmp/pcscd.tmp')
        zrodlo.seek(0)
        zrodlo.close()

    def start(self):
        self.stop()
        self.save_conf()
        self['state'].setText(_('Status: pcscd is starting...'))
        os.system('/scripts/pcscd_script.sh start2')
        self.createInfo()

    def stop(self):
        self['state'].setText(_('Status: pcscd is stopping...'))
        os.system('/scripts/pcscd_script.sh stop;killall -9 pcscd')
        self.createInfo()

    def cancel(self):
        self.close(False)

    def load_conf(self):
        self.def_au = '0'
        if fileExists('/scripts/pcscd_script.sh'):
            f = open('/scripts/pcscd_script.sh', 'r')
            for line in f.readlines():
                line = line.strip()
                if line.find('PCSCD_ON=') != -1:
                    self.def_au = line[9:10]

            f.close()

    def save_conf(self):
        zrodlo = open('/scripts/pcscd_script.sh').readlines()
        cel = open('/scripts/pcscd_script.sh', 'w')
        for s in zrodlo:
            cel.write(s.replace('PCSCD_ON=' + self.def_au, 'PCSCD_ON=' + self.au.value))

        cel.close()

    def start_samba(self):
        self.save_conf()
        self.createInfo()
        self.load_conf()
        self.close(True)


class EGDropbearConfig(ConfigListScreen, Screen):
    skin = '\n\t\t<screen name="EGDropbearConfig" position="center,center" size="570,350" title="EGAMI Dropbear Setup" >\n\t\t\t<widget name="config" position="10,10" size="550,200" scrollbarMode="showOnDemand" />\n\t\t\t<widget name="state" position="120,240" size="300,25" font="Regular;20" halign="center" noWrap="1" backgroundColor="red" foregroundColor="white" shadowOffset="-2,-2" shadowColor="black"  />\n\t\t\t<ePixmap name="key_red_png" pixmap="skin_default/buttons/button_red.png" position="10,320" size="140,40" alphatest="on" />\n\t\t\t<widget name="key_red" position="40,320" zPosition="1" size="200,40" font="Regular;20" halign="left" valign="top" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<ePixmap name="key_green_png" pixmap="skin_default/buttons/button_green.png" position="150,320" size="140,40" alphatest="on" />\n\t\t\t<widget name="key_green" position="180,320" zPosition="1" size="200,40" font="Regular;20" halign="left" valign="top" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<ePixmap name="key_yellow_png" pixmap="skin_default/buttons/button_yellow.png" position="300,320" size="140,40" alphatest="on" />\n\t\t\t<widget name="key_yellow" position="330,320" zPosition="1" size="140,40" font="Regular;20" halign="left" valign="top" backgroundColor="#a08500" transparent="1" />\n\t\t\t<ePixmap name="key_blue_png" pixmap="skin_default/buttons/button_blue.png" position="450,320" size="140,40" alphatest="on" />\n\t\t\t<widget name="key_blue" position="480,320" zPosition="1" size="140,40" font="Regular;20" halign="left" valign="top" backgroundColor="#a08500" transparent="1" />\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        session = None
        self.load_conf()
        self.au = ConfigSelection(default=self.def_au, choices=[('0', _('Yes')), ('1', _('No'))])
        self.createSetup()
        ConfigListScreen.__init__(self, self.list, session=session)
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions', 'CiSelectionActions'], {'cancel': self.cancel,
         'red': self.start_samba,
         'green': self.cancel,
         'yellow': self.start,
         'blue': self.stop}, -2)
        self['key_red'] = Label(_('Save'))
        self['key_green'] = Label(_('Cancel'))
        self['key_yellow'] = Label(_('Start'))
        self['key_blue'] = Label(_('Stop'))
        self['state'] = Label()
        self.createInfo()
        return

    def createSetup(self):
        self.list = []
        self.list.append(getConfigListEntry(_('Autostart:'), self.au))

    def createInfo(self):
        os.system('ps > /tmp/drop.tmp')
        zrodlo = open('/tmp/drop.tmp', 'r')
        szukana_fraza = '/usr/sbin/dropbear'
        if wyszukaj_in(zrodlo, szukana_fraza):
            self['state'].setText(_('Status: DropBear is running!'))
        else:
            self['state'].setText(_('Status: DropBear stopped!'))
        os.system('rm -rf /tmp/drop.tmp')
        zrodlo.seek(0)
        zrodlo.close()

    def start(self):
        zrodlo = open('/etc/init.d/dropbear').readlines()
        cel = open('/etc/init.d/dropbear', 'w')
        for s in zrodlo:
            cel.write(s.replace('NO_START=' + self.def_au, 'NO_START=0'))

        cel.close()
        self.stop()
        self.save_conf()
        self['state'].setText(_('Status: dropbear is starting...'))
        os.system('/etc/init.d/dropbear start')
        self.createInfo()

    def stop(self):
        self['state'].setText(_('Status: dropbear is stopping...'))
        os.system('/etc/init.d/dropbear stop;killall -9 dropbear')
        self.createInfo()

    def cancel(self):
        self.close(False)

    def load_conf(self):
        self.def_au = '0'
        if fileExists('/etc/init.d/dropbear'):
            f = open('/etc/init.d/dropbear', 'r')
            for line in f.readlines():
                line = line.strip()
                if line.find('NO_START=') != -1:
                    self.def_au = line[9:10]

            f.close()

    def save_conf(self):
        zrodlo = open('/etc/init.d/dropbear').readlines()
        cel = open('/etc/init.d/dropbear', 'w')
        for s in zrodlo:
            cel.write(s.replace('NO_START=' + self.def_au, 'NO_START=' + self.au.value))

        cel.close()

    def start_samba(self):
        self.save_conf()
        self.createInfo()
        self.load_conf()
        self.close(True)
