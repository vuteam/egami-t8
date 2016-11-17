from enigma import eListboxPythonMultiContent, gFont, getDesktop
from boxbranding import getMachineBrand, getMachineName, getBoxType
from Screens.MessageBox import MessageBox
from Screens.SmartConsole import SmartConsole
from Screens.NetworkSetup import *
from Screens.Setup import Setup
from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Screens.PluginBrowser import PluginDownloadBrowser
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from Components.Button import Button
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Harddisk import harddiskmanager
from Components.config import *
from Tools.Directories import fileExists, resolveFilename, SCOPE_CURRENT_SKIN
from Plugins.SystemPlugins.NetworkBrowser.NetworkBrowser import NetworkBrowser
from EGAMI.EGAMI_services_config import EGDropbearConfig
from EGAMI.EGAMI_tools import runBackCmd, unload_modules, wyszukaj_in, catalogXmlUrl
from EGAMI.EGAMI_addon_manager import EG_PrzegladaczAddonow, EG_Manual_installation, EGAddonRemove, EGConnectionAnimation
from os import system, listdir, symlink, unlink, readlink, path as os_path, stat, mkdir, popen, makedirs, access, rename, remove, W_OK, R_OK, F_OK, chmod, walk, getcwd, chdir
if os_path.exists('/usr/lib/enigma2/python/Plugins/SystemPlugins/EGAMIPluginSpeedUp'):
    from Plugins.SystemPlugins.EGAMIPluginSpeedUp.plugin import EGAMIPluginLoadScreen
    HAVE_EGAMISPEEDUP = True
else:
    HAVE_EGAMISPEEDUP = False

def EgamiMenuEntryComponent(name, description, long_description = None, pngname = 'default', width = 540):
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        width = 1280
        icons = 'iconsHD'
    else:
        width = 640
        icons = 'icons'
    if fileExists(resolveFilename(SCOPE_CURRENT_SKIN) + 'egami_icons/' + pngname + '.png'):
        png = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN) + 'egami_icons/' + pngname + '.png')
    else:
        png = LoadPixmap('/usr/lib/enigma2/python/EGAMI/' + icons + '/' + pngname + '.png')
        if png is None:
            png = LoadPixmap('/usr/lib/enigma2/python/EGAMI/' + icons + '/default.png')
    if screenwidth and screenwidth == 1920:
        return [(_(name), _(long_description)),
         MultiContentEntryText(pos=(100, 5), size=(width - 60, 40), font=0, text=_(name)),
         MultiContentEntryText(pos=(100, 40), size=(width - 60, 35), font=1, text=_(description)),
         MultiContentEntryPixmapAlphaBlend(pos=(10, 5), size=(90, 90), png=png)]
    else:
        return [(_(name), _(long_description)),
         MultiContentEntryText(pos=(70, 5), size=(width - 60, 25), font=0, text=_(name)),
         MultiContentEntryText(pos=(70, 26), size=(width - 60, 17), font=1, text=_(description)),
         MultiContentEntryPixmapAlphaBlend(pos=(10, 5), size=(45, 45), png=png)]
        return


def EgamiSeparatorEntryComponent(sep, width = 800):
    if fileExists('/usr/lib/enigma2/python/EGAMI/icons/div-h.png'):
        png = LoadPixmap('/usr/lib/enigma2/python/EGAMI/icons/div-h.png')
    else:
        png = LoadPixmap('/usr/share/enigma2/skin_default/div-h.png')
    return [sep, MultiContentEntryPixmapAlphaBlend(pos=(10, 24), size=(width, 2), png=png)]


class EgamiMenuList(MenuList):

    def __init__(self, list, enableWrapAround = True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        screenwidth = getDesktop(0).size().width()
        if screenwidth and screenwidth == 1920:
            self.l.setFont(0, gFont('Regular', 32))
            self.l.setFont(1, gFont('Regular', 24))
            self.l.setItemHeight(80)
        else:
            self.l.setFont(0, gFont('Regular', 20))
            self.l.setFont(1, gFont('Regular', 14))
            self.l.setItemHeight(50)


class EgamiMainPanel(Screen):
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        skin = '\n\t\t\t<screen name="EgamiMainPanel" position="center,100" size="1280,920">\n\t\t\t\t<ePixmap position="40,870" size="100,40" zPosition="0" pixmap="buttons/red.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<ePixmap position="200,870" size="100,40" zPosition="0" pixmap="buttons/green.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<widget name="key_red" position="80,870" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="red" transparent="1" />\n\t\t\t\t<widget name="key_green" position="240,870" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="green" transparent="1" />\n\t\t\t\t<widget name="list" position="10,20" size="805,820" zPosition="2" scrollbarMode="showOnDemand" transparent="1"/>\n\t\t\t\t<eLabel position="825,30" size="2,800" backgroundColor="darkgrey" zPosition="3" />\n\t\t\t\t<widget name="description" position="880,445" size="370,410" zPosition="1" font="Regular;32" halign="center" backgroundColor="black" transparent="1" />  \n\t\t\t</screen> '
    else:
        skin = '\n\t\t\t<screen name="EgamiMainPanel" position="center,70" size="920,620">\n\t\t\t\t  <widget name="key_red" zPosition="4" position="50,590" size="140,40" halign="left" font="Regular;22" transparent="1" />\n\t\t\t\t  <widget name="key_green" zPosition="4" position="240,590" size="240,40" halign="left" font="Regular;22" transparent="1" />\n\t\t\t\t  <widget name="key_yellow" zPosition="4" position="400,590" size="140,40" halign="left" font="Regular;22" transparent="1" />\n\t\t\t\t  <widget name="key_blue" zPosition="4" position="580,590" size="140,40" halign="left" font="Regular;22" transparent="1"  />\n\t\t\t\t  <ePixmap pixmap="skin_default/buttons/button_red.png" position="20,590" size="140,40" alphatest="on" />\n\t\t\t\t  <ePixmap pixmap="skin_default/buttons/button_green.png" position="210,590" size="140,40" alphatest="on" />  \n\t\t\t\t  <widget name="list" position="10,20" size="535,550" zPosition="2" scrollbarMode="showOnDemand" transparent="1"/>\n\t\t\t\t  <eLabel position="540,30" size="2,500" backgroundColor="darkgrey" zPosition="3" />\n\t\t\t\t  <widget name="description" position="600,245" size="250,410" zPosition="1" font="Regular;22" halign="center" backgroundColor="black" transparent="1" />  \n\t\t\t</screen> '

    def __init__(self, session):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('EGAMI Panel'))
        self['key_red'] = Label(_('Exit'))
        self['key_green'] = Label(_('EGAMI Update'))
        self['key_yellow'] = Label()
        self['key_blue'] = Label()
        self['description'] = Label()
        self.menu = 0
        self.currentIndexMenu = 0
        self.list = []
        self['list'] = EgamiMenuList(self.list)
        self.selectedList = []
        self.onChangedEntry = []
        self['list'].onSelectionChanged.append(self.selectionChanged)
        self['actions'] = ActionMap(['SetupActions',
         'WizardActions',
         'MenuActions',
         'MoviePlayerActions'], {'ok': self.keyOk,
         'back': self.keyRed,
         'cancel': self.keyRed,
         'left': self.goLeft,
         'right': self.goRight,
         'up': self.goUp,
         'down': self.goDown}, -1)
        self['ColorActions'] = HelpableActionMap(self, 'ColorActions', {'red': self.keyRed,
         'green': self.keyGreen,
         'yellow': self.keyYellow})
        self.GenerateMenu()
        self.subMenu = False
        self.selectedList = self['list']
        self.selectionChanged()

    def selectionChanged(self):
        if self.selectedList == self['list']:
            item = self['list'].getCurrent()
            if item and not item[0] == 'separator':
                self['description'].setText(_(item[0][1]))

    def goLeft(self):
        self.selectedList.pageUp()

    def goRight(self):
        self.selectedList.pageDown()

    def goUp(self):
        self.selectedList.up()
        item = self['list'].getCurrent()
        if item[0] == 'separator':
            index = self['list'].getSelectedIndex()
            self['list'].moveToIndex(index - 1)

    def goDown(self):
        self.selectedList.down()
        item = self['list'].getCurrent()
        if item[0] == 'separator':
            index = self['list'].getSelectedIndex()
            self['list'].moveToIndex(index + 1)

    def keyRed(self):
        if self.subMenu == True:
            self.GenerateMenu()
        else:
            self.close()

    def keyGreen(self):
        try:
            from Plugins.Extensions.EGAMINews.plugin import EGAMIMainNews
            self.session.open(EGAMIMainNews)
        except:
            self.session.openWithCallback(self.runUpgrade, MessageBox, _('Do you want to update your EGAMI image?') + '\n' + _('\nAfter pressing OK, please wait!'))

    def keyYellow(self):
        pass

    def keyOk(self):
        item = self['list'].getCurrent()
        selected = item[0][0]
        if selected == _('EGAMI Cam Center'):
            self.currentIndexMenu = self['list'].getSelectedIndex()
            from EGAMI.EGAMI_Blue import EmuManager
            self.session.open(EmuManager)
        elif selected == _('EGAMI Buttons'):
            self.currentIndexMenu = self['list'].getSelectedIndex()
            from Screens.ButtonSetup import ButtonSetup
            self.session.open(ButtonSetup)
        elif selected == _('EGAMI User Scripts'):
            self.currentIndexMenu = self['list'].getSelectedIndex()
            self.session.open(EGScript)
        elif selected == _('EGAMI Devices Manager'):
            self.currentIndexMenu = self['list'].getSelectedIndex()
            from EGAMI.EGAMI_devices_menu import EGDeviceManager
            self.session.open(EGDeviceManager)
        elif selected == _('EGAMI Mounts Manager'):
            self.currentIndexMenu = self['list'].getSelectedIndex()
            self.session.open(EGNetBrowser)
        elif selected == _('EGAMI Services Manager'):
            self.currentIndexMenu = self['list'].getSelectedIndex()
            self.GenerateServicesMenu()
        elif selected == _('EGAMI Software Tools'):
            self.currentIndexMenu = self['list'].getSelectedIndex()
            self.GenerateSoftwareToolsMenu()
        elif selected == _('EGAMI Settings'):
            self.currentIndexMenu = self['list'].getSelectedIndex()
            self.GenerateSettingsMenu()
        elif selected == _('EGAMI System Info'):
            self.currentIndexMenu = self['list'].getSelectedIndex()
            self.GenerateInformationsMenu()
        elif selected == _('EGAMI System Speed Up'):
            self.session.open(EGAMIPluginLoadScreen)
        elif selected == _('Samba'):
            self.session.open(NetworkSamba)
        elif selected == _('Dropbear'):
            self.session.open(EGDropbearConfig)
        elif selected == _('NFS'):
            self.session.open(NetworkNfs)
        elif selected == _('FTP'):
            self.session.open(NetworkFtp)
        elif selected == _('AFP'):
            self.session.open(NetworkAfp)
        elif selected == _('OpenVPN'):
            self.session.open(NetworkOpenvpn)
        elif selected == _('MiniDLNA'):
            self.session.open(NetworkMiniDLNA)
        elif selected == _('Inadyn'):
            self.session.open(NetworkInadyn)
        elif selected == _('SABnzbd'):
            self.session.open(NetworkSABnzbd)
        elif selected == _('uShare'):
            self.session.open(NetworkuShare)
        elif selected == _('Telnet'):
            self.session.open(NetworkTelnet)
        elif selected == _('Animations Setup'):
            self.session.open(Setup, 'egamianimationsetup')
        elif selected == _('Infobar Setup'):
            from EGAMI.EGAMI_Green import EGInfoBarSetup
            self.session.open(EGInfoBarSetup)
        elif selected == _('Permanental Clock Setup'):
            from EGAMI.EGAMI_Green import EGClockSetup
            self.session.open(EGClockSetup)
        elif selected == _('Channel List Setup'):
            self.session.open(Setup, 'channelselection')
        elif selected == _('Recording Setup'):
            self.session.open(Setup, 'recording')
        elif selected == _('Subtitles Setup'):
            self.session.open(Setup, 'subtitlesetup')
        elif selected == _('Auto Language Setup'):
            self.session.open(Setup, 'autolanguagesetup')
        elif selected == _('Decoding Setup'):
            from EGAMI.EGAMI_Green import EGDecodingSetup
            self.session.open(EGDecodingSetup)
        elif selected == _('Update Setup'):
            from EGAMI.EGAMI_Green import EGUpdateSetup
            self.session.open(EGUpdateSetup)
        elif selected == _('Bootlogo Setup'):
            from EGAMI.EGAMI_Bootlogo import EgamiBootLogoSelector
            self.session.open(EgamiBootLogoSelector)
        elif selected == _('Kernel Modules Setup'):
            from EGAMI.EGAMI_Green import EGKernelModules
            self.session.open(EGKernelModules)
        elif selected == _('Show Enigma2 Config File'):
            self.session.open(EGEnigma2ConfigInfo)
        elif selected == _('Show Kernel Messages'):
            self.session.open(EGKernelInfo)
        elif selected == _('Show Process List'):
            self.session.open(EGProcessInfo)
        elif selected == _('Show Filesystem Mounts'):
            cmdlist = []
            cmdlist.append('mount')
            cmdlist.append("echo '%s'" % _('Press OK to close the window.'))
            self.session.open(SmartConsole, _('EGAMI - Show Filesystem Mounts'), cmdlist=cmdlist, progressmode=False)
        elif selected == _('Show Uptime'):
            msg = self.session.open(MessageBox, _('Current Time, Operating Time and Load Average :') + '\n\n' + self.ShowUptime(), MessageBox.TYPE_INFO)
            msg.setTitle(_('EGAMI - Uptime'))
        elif selected == _('Show Network Connections'):
            cmdlist = []
            cmdlist.append('who')
            cmdlist.append("echo '%s'" % _('Press OK to close the window.'))
            self.session.open(SmartConsole, _('EGAMI - Show all connected sockets from ip-stack'), cmdlist=cmdlist, progressmode=False)
        elif selected == _('Show Routing Table'):
            cmdlist = []
            cmdlist.append('ip addr; iwconfig; echo ------------------------------------------------; route -n; echo ================================================; cat /etc/resolv.conf')
            cmdlist.append("echo '%s'" % _('Press OK to close the window.'))
            self.session.open(SmartConsole, title=_('EGAMI show network configuration and routing table'), cmdlist=cmdlist, progressmode=False)
        elif selected == _('Show System Memory Info'):
            msg = self.session.open(MessageBox, _('Current Memory Usage :') + '\n\n' + self.ShowMemoryUsage(), MessageBox.TYPE_INFO)
            msg.setTitle(_('EGAMI - Memory Usage'))
        elif selected == _('Show Network Details'):
            cmdlist = []
            cmdlist.append('netstat -t -u')
            cmdlist.append("echo '%s'" % _('Press OK to close the window.'))
            self.session.open(SmartConsole, _('EGAMI - show network stats'), cmdlist=cmdlist, progressmode=False)
        elif selected == _('Show HDD Temperature'):
            if os_path.exists('/dev/sda') == True:
                msg = self.session.openWithCallback(self.hdparm, MessageBox, _("Hard-disk Manufacturer, Type and it's Temperature :") + '\n\n' + self.ScanHDD() + '\n\n' + _('Are you sure to set hdd in standby mode?'), MessageBox.TYPE_YESNO)
                msg.setTitle(_('HDD Temperature'))
            else:
                self.session.open(MessageBox, _('No internal Harddisk detected!!!! \n\nPlease install an internal Harddisk first to be in a position to check harddisk temperature.'), MessageBox.TYPE_INFO, timeout=5)
        elif selected == _('Show Stream Info'):
            self.session.open(EGStreamInfo)
        elif selected == _('EGAMI Personal Backup'):
            if self.checkMountedDevices():
                from EGAMI.EGAMI_backup_panel import EGAMIBackupPanel
                self.session.open(EGAMIBackupPanel)
            else:
                self.session.open(MessageBox, _('Please connect HDD or USB to backup/restore Your EGAMI Image!'), MessageBox.TYPE_INFO)
        elif selected == _('EGAMI Full Backup'):
            if self.checkMountedDevices():
                from EGAMI.EGAMI_backup_panel import EGFullBackup
                self.session.open(EGFullBackup)
            else:
                self.session.open(MessageBox, _('Please connect HDD or USB to full backup of Your EGAMI Image!'), MessageBox.TYPE_INFO)
        elif selected == _('Swap File Setup'):
            from EGAMI.EGAMI_devices_menu import EGAMISwap
            self.session.open(EGAMISwap)
        elif selected == _('Download EGAMI Addons'):
            staturl = catalogXmlUrl()
            downfile = '/tmp/.catalog.xml'
            if fileExists(downfile):
                remove(downfile)
            self.session.openWithCallback(self.EGConnectionCallback, EGConnectionAnimation, staturl, downfile)
        elif selected == _('Download Plugins'):
            self.session.open(PluginDownloadBrowser, 0)
        elif selected == _('User Server Addons'):
            if fileExists('/etc/user_addon.txt'):
                urlfile = file('/etc/user_addon.txt', 'r')
                linieurl = urlfile.read()
                urlfile.close()
                self.session.open(EG_PrzegladaczAddonow, linieurl)
            else:
                plik = 'There is no user_addon.txt file in /etc with server url!'
                self.session.open(MessageBox, _(plik), MessageBox.TYPE_INFO, timeout=5)
        elif selected == _('Install Tar.gz and IPK Addons'):
            self.session.open(EG_Manual_installation)
        elif selected == _('Remove Plugins'):
            self.session.open(PluginDownloadBrowser, 1)
        elif selected == _('Remove EGAMI addons'):
            self.session.open(EGAddonRemove)

    def GenerateMenu(self):
        self.subMenu = False
        self.setTitle(_('EGAMI Panel - Main Menu'))
        self.list = []
        self.list.append(EgamiMenuEntryComponent('EGAMI Cam Center', _('Start/stop/select soft-cam'), _('Start/stop/select your cam, You need to install first a softcam'), 'main/cam_center'))
        self.list.append(EgamiSeparatorEntryComponent('separator'))
        self.list.append(EgamiMenuEntryComponent('EGAMI Buttons', _('Change some keys functions'), _('You can setup here what buttons should do'), 'main/quickbutton'))
        self.list.append(EgamiMenuEntryComponent('EGAMI User Scripts', _('Run Your scripts from /usr/scripts'), _('It is running scripts from /usr/script'), 'main/user_script'))
        self.list.append(EgamiMenuEntryComponent('EGAMI Devices Manager', _('Manage Your devices like USB, HDD, DVD...'), _('Setup your connected devices'), 'main/dev_manager'))
        self.list.append(EgamiMenuEntryComponent('EGAMI Mounts Manager', _('Setup your mounts for network'), _('Setup your mounts for network'), 'main/mount_manager'))
        self.list.append(EgamiMenuEntryComponent('EGAMI Software Tools', _('Update/Backup/Restore your box'), _('Update/Backup your firmware, Backup/Restore settings'), 'main/sw_tools'))
        self.list.append(EgamiMenuEntryComponent('EGAMI Services Manager', _('Manage Inadyn, SSH, uShare, OpenVPN, NFS, DLNA'), _('Setup your network daemons'), 'main/services'))
        self.list.append(EgamiMenuEntryComponent('EGAMI Settings', _('Setup Your infobar, channel selections and others'), _('Setup Your infobar, channel selections and others'), 'main/settings'))
        self.list.append(EgamiMenuEntryComponent('EGAMI System Info', _('Shows informations about system and hardware'), _('Shows information about Memory, HW and SW'), 'main/sys_info'))
        if HAVE_EGAMISPEEDUP:
            self.list.append(EgamiMenuEntryComponent('EGAMI System Speed Up', _('Speed up system booting time'), _('Speed up system booting'), 'main/speed'))
        self['list'].l.setList(self.list)
        self['list'].moveToIndex(self.currentIndexMenu)

    def GenerateServicesMenu(self):
        self.subMenu = True
        self.setTitle(_('EGAMI Panel - Services Manager'))
        self.list = []
        self.list.append(EgamiMenuEntryComponent('Samba', _('Setup Samba'), _('Setup Samba'), 'services/samba'))
        self.list.append(EgamiMenuEntryComponent('Dropbear', _('Setup Dropbear SSH'), _('Setup Dropbear'), '/services/dropbear'))
        self.list.append(EgamiMenuEntryComponent('NFS', _('Setup NFS'), _('Setup NFS'), 'services/nfs'))
        self.list.append(EgamiMenuEntryComponent('FTP', _('Setup FTP'), _('Setup FTP'), 'services/ftp'))
        self.list.append(EgamiMenuEntryComponent('AFP', _('Setup AFP'), _('Setup AFP'), 'services/afp'))
        self.list.append(EgamiMenuEntryComponent('OpenVPN', _('Setup OpenVPN'), _('Setup OpenVPN'), 'services/openvpn'))
        self.list.append(EgamiMenuEntryComponent('MiniDLNA', _('Setup MiniDLNA'), _('Setup MiniDLNA'), 'services/minidlna'))
        self.list.append(EgamiMenuEntryComponent('Inadyn', _('Setup Inadyn'), _('Setup Inadyn'), 'services/inadyn'))
        self.list.append(EgamiMenuEntryComponent('uShare', _('Setup uShare'), _('Setup uShare'), 'services/ushare'))
        self.list.append(EgamiMenuEntryComponent('Telnet', _('Setup Telnet'), _('Setup Telnet'), 'services/telnet'))
        self['list'].l.setList(self.list)
        self['list'].moveToIndex(0)

    def GenerateSettingsMenu(self):
        self.subMenu = True
        self.setTitle(_('EGAMI Panel - Settings Manager'))
        self.list = []
        self.list.append(EgamiMenuEntryComponent('Animations Setup', _('Configure animations'), _('Setup fade, animations, switch, slider'), 'settings/infobar'))
        self.list.append(EgamiMenuEntryComponent('Infobar Setup', _('Configure infobar'), _('Setup infobar, weather and clock'), 'settings/infobar'))
        self.list.append(EgamiMenuEntryComponent('Permanental Clock Setup', _('Configure permanental clock'), _('Setup permanental clock'), 'settings/clock'))
        self.list.append(EgamiMenuEntryComponent('Recording Setup', _('Configure recordings'), _('Setup recording path, options and others'), 'settings/recording'))
        self.list.append(EgamiMenuEntryComponent('Subtitles Setup', _('Configure subtitles'), _('Setup subtitles color, font size and positions'), 'settings/subtitles'))
        self.list.append(EgamiMenuEntryComponent('Auto Language Setup', _('Configure audio lanaguage'), _('Setup auto-language speech'), 'settings/autolanguage'))
        self.list.append(EgamiMenuEntryComponent('Channel List Setup', _('Configure service list look and behaviour'), _('Setup picons, progress bar and others in channel selection'), 'settings/channellist'))
        self.list.append(EgamiMenuEntryComponent('Decoding Setup', _('Configure zap messages'), _('Setup zap errors and CI messages'), 'settings/decoding'))
        self.list.append(EgamiMenuEntryComponent('Update Setup', _('Configure updates parameters'), _('Setup updates setup'), 'settings/update'))
        self.list.append(EgamiMenuEntryComponent('Swap File Setup', _('Setup Swapfile'), _('Create swap file partition'), 'main/dev_manager'))
        self.list.append(EgamiMenuEntryComponent('Bootlogo Setup', _('Choose Your favorite bootlogo'), _('Setup bootlogo'), 'settings/bootlogo'))
        self.list.append(EgamiMenuEntryComponent('Kernel Modules Setup', _('Enable or disable kernel modules'), _('Setup kernel modules'), 'informations/info'))
        self['list'].l.setList(self.list)
        self['list'].moveToIndex(0)

    def GenerateInformationsMenu(self):
        self.subMenu = True
        self.setTitle(_('EGAMI Panel - System Informations'))
        self.list = []
        self.list.append(EgamiMenuEntryComponent('Show Enigma2 Config File', _('Show information about GUI config file'), _('Informations about current enigma2 register'), 'informations/info'))
        self.list.append(EgamiMenuEntryComponent('Show Process List', _('Show running processes'), _('Send signals to processes'), 'informations/info'))
        self.list.append(EgamiMenuEntryComponent('Show Kernel Messages', _('Show information about kernel'), _('Show kernel informations'), 'informations/info'))
        self.list.append(EgamiMenuEntryComponent('Show Filesystem Mounts', _('Show active mounts'), _('The list of current mounted things'), 'informations/info'))
        self.list.append(EgamiMenuEntryComponent('Show Uptime', _('Show operating system uptime'), _('How long does Your STB is running ?'), 'informations/info'))
        self.list.append(EgamiMenuEntryComponent('Show Routing Table', _('Show network configuration and routing table'), _('Routing table and network configuration'), 'informations/info'))
        self.list.append(EgamiMenuEntryComponent('Show Network Connections', _('Show all connected sockets from ip-stack'), _('All incomming and outgoing connections'), 'informations/info'))
        self.list.append(EgamiMenuEntryComponent('Show System Memory Info', _('Show whole system memory usage'), _('System memory usage'), 'informations/info'))
        self.list.append(EgamiMenuEntryComponent('Show Network Details', _('Shows assigned ip-adresses, routingtable and nameserver'), _('Shows assigned ip-adresses, routingtable and nameserver'), 'informations/info'))
        self.list.append(EgamiMenuEntryComponent('Show HDD Temperature', _('Shows current HDD temperature'), _('Shows current HDD temperature in C and F'), 'informations/info'))
        self.list.append(EgamiMenuEntryComponent('Show Stream Info', _('Shows advanced informations about stream'), _('PAT/PMT/NIT and more informations about stream'), 'informations/info'))
        self['list'].l.setList(self.list)
        self['list'].moveToIndex(0)

    def GenerateSoftwareToolsMenu(self):
        self.subMenu = True
        self.setTitle(_('EGAMI Panel - Software Tools'))
        self.list = []
        self.list.append(EgamiMenuEntryComponent('EGAMI Personal Backup', _('Create Your settings and plugins backup'), _('Make backup of plugins, skins, settings, cams and restore it after fresh image installation'), ''))
        self.list.append(EgamiMenuEntryComponent('EGAMI Full Backup', _('Create flashable image backup'), _('Make full image backup which allows to flash other boxes'), ''))
        self.list.append(EgamiSeparatorEntryComponent('separator'))
        self.list.append(EgamiMenuEntryComponent('Download EGAMI Addons', _('Download from feed IPTV, SoftCams'), _('Collection of nice IPTV plugins, bootlogos and softcams'), ''))
        self.list.append(EgamiMenuEntryComponent('Download Plugins', _('Download from feeds skins, extensions, picons'), _('Collection of plugins/skins/picons/channel lists'), ''))
        self.list.append(EgamiSeparatorEntryComponent('separator'))
        self.list.append(EgamiMenuEntryComponent('User Server Addons', _('Download feeds from Your own server'), _('Use Your onw server for feed downloads'), ''))
        self.list.append(EgamiMenuEntryComponent('Install Tar.gz and IPK Addons', _('Install manually packages from /tmp'), _('You can install here tar.gz/tar.bz2/ipk/zip packages'), ''))
        self.list.append(EgamiSeparatorEntryComponent('separator'))
        self.list.append(EgamiMenuEntryComponent('Remove Plugins', _('Remove installed plugins'), _('You can remove here extensions which you want'), ''))
        self.list.append(EgamiMenuEntryComponent('Remove EGAMI addons', _('Remove softcams or iptv plugins'), _('You remove softcams and iptv plugins here'), ''))
        self['list'].l.setList(self.list)
        self['list'].moveToIndex(0)

    def EGConnectionCallback(self):
        downfile = '/tmp/.catalog.xml'
        if fileExists(downfile):
            self.session.open(EG_PrzegladaczAddonow, '/tmp/.catalog.xml')
        else:
            nobox = self.session.open(MessageBox, _('Sorry, Connection Failed'), MessageBox.TYPE_INFO)

    def runUpgrade(self, result):
        if result:
            from Plugins.SystemPlugins.SoftwareManager.plugin import UpdatePlugin
            self.session.open(UpdatePlugin, '/usr/lib/enigma2/python/Plugins/SystemPlugins/SoftwareManager')

    def hdparm(self, result):
        if result is None or result is False:
            pass
        else:
            for hdd in harddiskmanager.HDDList():
                device_path = hdd[1].getDeviceDir()
                cmd = 'hdparm -qy ' + str(device_path)
                system(cmd)

            return
        return

    def ScanHDD(self):
        ret = ''
        try:
            for hdd in harddiskmanager.HDDList():
                device_path = hdd[1].getDeviceDir()
                device_model = hdd[1].model()
                device_size = hdd[1].capacity()
                device_temp = popen('hddtemp -q ' + str(device_path) + ' | cut -d":" -f3').readline()
                ret += '%s (%s, %s) : %s\n' % (device_path,
                 device_model,
                 device_size,
                 device_temp)

            return ret
        except:
            return _('No Harddisk or Harddisk with S.M.A.R.T capabilites detected')

    def ShowUptime(self):
        try:
            ret = ''
            out_line = popen('uptime').readline()
            ret = ret + _('At') + out_line + '\n'
            return ret
            out_line.close()
        except:
            return _('Could not grep Uptime Information from busybox')

    def ShowMemoryUsage(self):
        try:
            ret = ''
            out_lines = []
            out_lines = popen('free').readlines()
            for lidx in range(len(out_lines) - 1):
                ret = ret + out_lines[lidx] + '\n'

            return ret
            out_lines.close()
        except:
            return _('Could not grep Memory Usage information from busybox')

    def checkMountedDevices(self):
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
            return False
        else:
            return True


class EGProcessInfo(Screen):
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        skin = '\n\t\t\t<screen name="EGProcessInfo" position="center,center" size="970,750" >\n\t\t\t\t<widget name="menu" itemHeight="50" font="Regular;28"  position="10,10" size="950,680" scrollbarMode="showOnDemand" transparent="1" />\n\t\t\t\t<widget name="key_red" position="50,720" zPosition="2" size="200,30" font="Regular;28" valign="top" halign="left" transparent="1"/>\n\t\t\t\t<ePixmap position="20,720" zPosition="1" size="200,40" pixmap="buttons/red.png" transparent="1" alphatest="on" />\n\t\t\t\t<widget name="key_green" position="310,720" zPosition="2" size="200,30" font="Regular;28" valign="top" halign="left" transparent="1"/>\n\t\t\t\t<ePixmap position="280,720" zPosition="1" size="200,40" pixmap="buttons/green.png" transparent="1" alphatest="on" />\n\t\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen name="EGProcessInfo" position="center,center" size="670,550" >\n\t\t\t\t<widget name="menu" position="10,10" size="650,480" scrollbarMode="showOnDemand" transparent="1" />\n\t\t\t\t<widget name="key_red" position="50,520" zPosition="2" size="200,20" font="Regular;20" valign="top" halign="left" transparent="1"/>\n\t\t\t\t<ePixmap position="20,520" zPosition="1" size="200,40" pixmap="skin_default/buttons/button_red.png" transparent="1" alphatest="on" />\n\t\t\t\t<widget name="key_green" position="310,520" zPosition="2" size="200,20" font="Regular;20" valign="top" halign="left" transparent="1"/>\n\t\t\t\t<ePixmap position="280,520" zPosition="1" size="200,40" pixmap="skin_default/buttons/button_green.png" transparent="1" alphatest="on" />\n\t\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('EGAMI Process Informations'))
        self.list = []
        self['menu'] = MenuList(self.list)
        self['key_red'] = Button(_('Send Signal'))
        self['key_green'] = Button(_('Show details'))
        self.onLayoutFinish.append(self.fillList)
        self['actions'] = ActionMap(['EGActions'], {'ok': self.KeyOk,
         'red': self.KeyRed,
         'green': self.KeyGreen,
         'exit': self.Exit}, -1)

    def fillList(self):
        count = 0
        for line in popen('ps -A', 'r').readlines():
            count += 1
            x = line.strip().split()
            try:
                pro_str = str(x[0]) + '\t' + x[1] + '\t' + str(x[3]) + '\t' + str(x[4])
            except:
                pro_str = str(x[0]) + '\t' + x[1] + '\t\t' + str(x[3])

            self.list.append(pro_str)

        self['menu'].setList(self.list)
        self['menu'].moveToIndex(1)

    def fillList2(self):
        self['menu'].setList(self.list)
        self['menu'].moveToIndex(1)

    def KeyOk(self):
        self.showDetails()

    def KeyGreen(self):
        self.showDetails()

    def KeyRed(self):
        val = self['menu'].l.getCurrentSelection()
        val = val.strip().split()
        if val:
            menu = []
            menu.append(('SIGHUP', 0))
            menu.append(('SIGINT', 0))
            menu.append(('SIGQUIT', 0))
            menu.append(('SIGTRAP', 0))
            menu.append(('SIGABRT', 0))
            menu.append(('SIGKILL', 0))
            menu.append(('SIGUSR1', 0))
            menu.append(('SIGALRM', 0))
            menu.append(('SIGTERM', 0))
            menu.append(('SIGCONT', 0))
            menu.append(('SIGSTOP', 0))
            self.session.openWithCallback(self.menuCallback, ChoiceBox, list=menu, title=_('send signal to this process...') + '\n' + val[2])

    def menuCallback(self, val):
        if val != None:
            val_2 = self['menu'].l.getCurrentSelection()
            val_2 = val_2.strip().split()
            cmd = 'killall -' + val[0] + ' ' + val_2[2]
            runBackCmd(cmd)
            system('ps > /tmp/.ps')
            self.fillList()
            self.fillList2()
        return

    def showDetails(self):
        val = self['menu'].l.getCurrentSelection()
        val = val.strip().split()
        if val:
            cmd = 'cat /proc/' + str(val[0]) + '/status'
            cmdlist = []
            cmdlist.append(cmd)
            cmdlist.append("echo '%s'" % _('Press OK to close the window.'))
            self.session.open(SmartConsole, _('Details'), cmdlist=cmdlist, progressmode=False)

    def Exit(self):
        self.close()


class EGKernelInfo(Screen):
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        skin = '\n\t\t\t<screen name="EGKernelInfo" position="center,center" size="970,750" >\n\t\t\t\t<widget name="menu" itemHeight="50" font="Regular;28" position="10,10" size="950,730" scrollbarMode="showOnDemand" transparent="1" />\n\t\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen name="EGKernelInfo" position="center,center" size="770,550" >\n\t\t\t\t<widget name="menu" position="10,10" size="750,530" scrollbarMode="showOnDemand" transparent="1" />\n\t\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('EGAMI Kernel Informations'))
        self.list = []
        self['menu'] = MenuList(self.list)
        self.onLayoutFinish.append(self.fillList)
        self['actions'] = ActionMap(['EGActions'], {'exit': self.Exit}, -1)

    def fillList(self):
        count = 0
        for x in popen('dmesg', 'r').readlines():
            count += 1
            self.list.append(x)

        self['menu'].l.setList(self.list)
        self['menu'].moveToIndex(count - 1)

    def Exit(self):
        self.close()


class EGEnigma2ConfigInfo(Screen):
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        skin = '<screen name="EGEnigma2ConfigInfo" position="center,center" size="970,750" title="EGAMI Kernel Informations" >\n\t\t\t\t<widget name="menu" itemHeight="50" font="Regular;28" position="10,10" size="950,730" scrollbarMode="showOnDemand" transparent="1" />\n\t\t\t</screen>'
    else:
        skin = '<screen name="EGEnigma2ConfigInfo" position="center,center" size="770,550" title="EGAMI Enigma2 Config" >\n\t\t\t\t<widget name="menu" position="10,10" size="750,530" scrollbarMode="showOnDemand" transparent="1" />\n\t\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.fillList()
        self['menu'] = MenuList(self.list)
        self.onLayoutFinish.append(self.fillList2)
        self['actions'] = ActionMap(['EGActions'], {'exit': self.Exit}, -1)

    def fillList(self):
        self.list = []
        f = open('/etc/enigma2/settings', 'r')
        for line in f.readlines():
            x = line.strip()
            pro_str = str(x)
            self.list.append(pro_str)

        f.close()

    def fillList2(self):
        self['menu'].setList(self.list)
        self['menu'].moveToIndex(0)

    def Exit(self):
        self.close()


class EGScript(Screen):
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        skin = '\n\t\t\t<screen name="EGScript" position="center,center" size="960,605" >\n\t\t\t\t<widget name="list" itemHeight="50" font="Regular;28" position="10,10" size="940,580" scrollbarMode="showOnDemand" transparent="1" />\n\t\t\t\t<widget name="statuslab" position="10,540" size="940,50" font="Regular;26" valign="center" noWrap="1" backgroundColor="#333f3f3f" foregroundColor="#FFC000" shadowOffset="-2,-2" shadowColor="black" />\n\t\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen name="EGScript" position="center,center" size="560,405" >\n\t\t\t\t<widget name="list" position="10,10" size="540,280" scrollbarMode="showOnDemand" transparent="1" />\n\t\t\t\t<widget name="statuslab" position="10,370" size="540,30" font="Regular;16" valign="center" noWrap="1" backgroundColor="#333f3f3f" foregroundColor="#FFC000" shadowOffset="-2,-2" shadowColor="black" />\n\t\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('EGAMI Script Tool'))
        self['statuslab'] = Label(_('N/A'))
        self['key_red'] = Label(_('Run'))
        self.mlist = []
        self.populateSL()
        self['list'] = MenuList(self.mlist)
        self['list'].onSelectionChanged.append(self.schanged)
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.mygo,
         'ok': self.mygo,
         'back': self.close})
        self.onLayoutFinish.append(self.refr_sel)

    def refr_sel(self):
        self['list'].moveToIndex(1)
        self['list'].moveToIndex(0)

    def populateSL(self):
        self.scriptdesc = {}
        myscripts = listdir('/usr/scripts')
        for fil in myscripts:
            if fil.find('_smartscript.sh') != -1:
                fil2 = fil[:-15]
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
        mysel2 = '/usr/scripts/' + mysel + '_smartscript.sh'
        mytitle = 'EGScript Tool: ' + mysel
        cmdlist = []
        cmdlist.append(mysel2)
        cmdlist.append("echo '%s'" % _('Press OK to close the window.'))
        self.session.open(SmartConsole, title=mytitle, cmdlist=cmdlist, progressmode=False)


class EGStreamInfo(Screen):
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        skin = '<screen name="EGStreamInfo" position="center,center" size="970,750" >\n\t\t\t\t<widget name="menu" itemHeight="50" font="Regular;28" position="10,10" size="950,730" scrollbarMode="showOnDemand" transparent="1" />\n\t\t\t</screen>'
    else:
        skin = '<screen name="EGStreamInfo" position="center,center" size="380,310" >\n\t\t\t\t<widget name="menu" position="10,10" size="360,280" scrollbarMode="showOnDemand" transparent="1" />\n\t\t\t</screen>'

    def __init__(self, session, args = 0):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('EGAMI Kernel Informations'))
        self.menu = args
        list = []
        list.append((_('PAT Info'), '1'))
        list.append((_('CAT Info'), '2'))
        list.append((_('NIT Info'), '3'))
        list.append((_('EIT/TOT/TDT Info'), '5'))
        list.append((_('ECM Info'), '7'))
        list.append((_('DVB Snoop Help'), '8'))
        self['menu'] = MenuList(list)
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.go,
         'back': self.close}, -1)

    def go(self):
        returnValue = self['menu'].l.getCurrentSelection()[1]
        if returnValue is not None:
            if returnValue is '1':
                cmdlist = []
                cmdlist.append('/usr/bin/dvbsnoop -n 1 -hideproginfo 0x0000')
                cmdlist.append("echo '%s'" % _('Press OK to close the window.'))
                self.session.open(SmartConsole, _('Stream advanced info - PAT'), cmdlist=cmdlist, progressmode=False)
            elif returnValue is '2':
                cmdlist = []
                cmdlist.append('/usr/bin/dvbsnoop -n 1 -hideproginfo 0x0001')
                cmdlist.append("echo '%s'" % _('Press OK to close the window.'))
                self.session.open(SmartConsole, _('Stream advanced info - CAT'), cmdlist=cmdlist, progressmode=False)
            elif returnValue is '3':
                cmdlist = []
                cmdlist.append('/usr/bin/dvbsnoop -n 1 -hideproginfo 0x0010')
                cmdlist.append("echo '%s'" % _('Press OK to close the window.'))
                self.session.open(SmartConsole, _('Stream advanced info - NIT'), cmdlist=cmdlist, progressmode=False)
            elif returnValue is '4':
                cmdlist = []
                cmdlist.append('/usr/bin/dvbsnoop -n 1 -hideproginfo 0x0011')
                cmdlist.append("echo '%s'" % _('Press OK to close the window.'))
                self.session.open(SmartConsole, _('Stream advanced info - SDT/BAT'), cmdlist=cmdlist, progressmode=False)
            elif returnValue is '5':
                cmdlist = []
                cmdlist.append('/usr/bin/dvbsnoop -n 1 -hideproginfo 0x0012')
                cmdlist.append("echo '%s'" % _('Press OK to close the window.'))
                self.session.open(SmartConsole, _('Stream advanced info - EIT/TOT/TDT'), cmdlist=cmdlist, progressmode=False)
            elif returnValue is '6':
                cmdlist = []
                cmdlist.append('/usr/bin/dvbsnoop -if /tmp/pmt.tmp -hideproginfo')
                cmdlist.append("echo '%s'" % _('Press OK to close the window.'))
                self.session.open(SmartConsole, _('Stream advanced info - PMT'), cmdlist=cmdlist, progressmode=False)
            elif returnValue is '7':
                cmdlist = []
                cmdlist.append('cat /tmp/ecm.info')
                cmdlist.append("echo '%s'" % _('Press OK to close the window.'))
                self.session.open(SmartConsole, _('Stream advanced info - ECM'), cmdlist=cmdlist, progressmode=False)
            elif returnValue is '8':
                cmdlist = []
                cmdlist.append('/usr/bin/dvbsnoop -help')
                cmdlist.append("echo '%s'" % _('Press OK to close the window.'))
                self.session.open(SmartConsole, _('Stream advanced info - Help'), cmdlist=cmdlist, progressmode=False)
        return


class EGNetBrowser(Screen):
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        skin = '\n\t\t\t<screen name="EGNetBrowser" position="center,center" size="800,520" >\n\t\t\t\t<widget source="list" render="Listbox" itemHeight="50" font="Regular;28" position="10,10" size="780,460" scrollbarMode="showOnDemand" transparent="1" >\n\t\t\t\t\t<convert type="StringList" />\n\t\t\t\t</widget>\n\t\t\t\t<ePixmap position="40,470" size="100,40" zPosition="0" pixmap="buttons/red.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<ePixmap position="200,470" size="100,40" zPosition="0" pixmap="buttons/green.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<widget name="key_red" position="80,470" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="red" transparent="1" />\n\t\t\t\t<widget name="key_green" position="240,470" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="green" transparent="1" />\n\t\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen name="EGNetBrowser" position="center,center" size="800,520" >\n\t\t\t\t<widget source="list" render="Listbox" position="10,10" size="780,460" scrollbarMode="showOnDemand" transparent="1" >\n\t\t\t\t\t<convert type="StringList" />\n\t\t\t\t</widget>\n\t\t\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="200,480" size="140,40" alphatest="on" />\n\t\t\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="440,480" size="140,40" alphatest="on" />\n\t\t\t\t<widget name="key_red" position="200,480" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t\t\t<widget name="key_green" position="440,480" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('Select Network Interface'))
        self['key_red'] = Label(_('Exit'))
        self['key_green'] = Label(_('Select'))
        self.list = []
        self['list'] = List(self.list)
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.selectInte,
         'back': self.close,
         'green': self.selectInte,
         'red': self.close})
        self.list = []
        self.adapters = [ (iNetwork.getFriendlyAdapterName(x), x) for x in iNetwork.getAdapterList() ]
        for x in self.adapters:
            res = (x[0], x[1])
            self.list.append(res)

        self['list'].list = self.list

    def selectInte(self):
        mysel = self['list'].getCurrent()
        if mysel:
            inter = mysel[1]
            self.session.open(NetworkBrowser, inter, '/usr/lib/enigma2/python/Plugins/SystemPlugins/NetworkBrowser')
