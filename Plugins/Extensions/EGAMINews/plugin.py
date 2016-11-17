from Plugins.Plugin import PluginDescriptor
from Components.About import about
from Components.ActionMap import ActionMap
from Components.Console import Console
from Components.config import config, ConfigYesNo
from Components.GUIComponent import GUIComponent
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ScrollLabel import ScrollLabel
from Components.Sources.StaticText import StaticText
from Components.Sources.List import List
from Components.Ipkg import IpkgComponent
from Components.Sources.StaticText import StaticText
from Components.Slider import Slider
from Components.Network import iNetwork
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Ipkg import Ipkg
from Screens.Standby import TryQuitMainloop
from Tools.BoundFunction import boundFunction
from Tools.Directories import *
from Tools.LoadPixmap import LoadPixmap
from Tools.Notifications import AddNotificationWithCallback
from os import statvfs, remove, path as os_path
from enigma import eTimer
import xml.dom.minidom
from xml.dom.minidom import Node
from cPickle import dump, load
import urllib2
import socket
packagetmpfile = '/tmp/.package.tmp'
cache_file = '/tmp/.updatecache'
update_trigger = '/etc/do_update'
from boxbranding import getBoxType, getMachineBuild, getMachineBrand, getMachineName, getMachineProcModel

def menu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(_('EGAMI News'),
          main,
          'EGAMINews',
          1)]
    return []


#from enigma import eEGAMI
#Use Old Patch Fuuuuuuk EGAMI-TEAM
def main(session, **kwargs):
#   m = eEGAMI.getInstance().checkkernel()
    m = checkkernel()
    if m == 1:
        try:
            session.open(EGAMIMainNews)
        except:
            print '[EGAMINews] Plugin execution failed'

    else:
        session.open(MessageBox, _('Sorry: Wrong image in flash found. You have to install in flash EGAMI Image'), MessageBox.TYPE_INFO, 3)


def start_update_notification(reason, **kwargs):
    if config.usage.check_for_updates.value > 0 and kwargs.has_key('session'):
        session = kwargs['session']
        update_notification.setSession(session)
        update_notification.init_timer()


def Plugins(**kwargs):
    return [PluginDescriptor(name='EGAMINews', where=PluginDescriptor.WHERE_MENU, description=_('Latest news about EGAMI Images'), fnc=menu), PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=start_update_notification)]


def getHeader():
    imageversion = about.getImageVersionString()
    ret = 'EGAMI ' + imageversion + ' - '
    ret += '%s %s\n' % (getMachineBrand(), getMachineName())
    return ret


header = getHeader()

def write_cache(cache_data):
    if not os_path.isdir(os_path.dirname(cache_file)):
        try:
            mkdir(os_path.dirname(cache_file))
        except OSError:
            pass

    fd = open(cache_file, 'w')
    dump(cache_data, fd, -1)
    fd.close()


def load_cache():
    fd = open(cache_file)
    cache_data = load(fd)
    fd.close()
    return cache_data


def newsURL():
    news = 'http://egami-feed.com/plugins/egaminews.xml'
    return news


def skip_entry(entry):
    if entry.hasAttribute('require'):
        require = entry.getAttribute('require').split(',')
        if len(require) and getMachineBuild() not in require:
            return True
    return False


def parse_xml():
    list = []
    xml_ok = True
    news_url = newsURL()
    try:
        news = urllib2.urlopen(news_url, None, 5.0).read()
    except urllib2.HTTPError:
        return 2
    except urllib2.URLError:
        return 3
    except socket.timeout as e:
        return 4
    except:
        return 5

    try:
        xmldoc = xml.dom.minidom.parseString(news)
    except xml.parsers.expat.ExpatError:
        return 3

    news = None
    for node in xmldoc.getElementsByTagName('update'):
        if skip_entry(node):
            continue
        update_type = 'normal'
        if node.hasAttribute('type'):
            update_type = node.getAttribute('type')
        title = node.getElementsByTagName('title')
        update_title = title[0].firstChild.data
        update_list = node.getElementsByTagName('item')
        p_item_list = []
        for entry in update_list:
            if skip_entry(entry):
                continue
            my_item = None
            for update_item in entry.getElementsByTagName('itemtext'):
                if update_item.firstChild:
                    my_item = update_item.firstChild.data

            p_subitem_list = []
            for topic in entry.getElementsByTagName('description'):
                if topic.firstChild:
                    if skip_entry(topic):
                        continue
                    topic_description = topic.firstChild.data
                    p_subitem_list.append(topic_description)

            p_item_list.append((my_item, p_subitem_list))

        list.append((update_title, p_item_list, update_type))

    xmldoc.unlink()
    write_cache(list)
    list = None
    return 1


class EGAMIMainNews(Screen):
    skin = '\n\t    <screen name="EGAMIMainNews" position="center,center" size="750,550" title="EGAMI News" >\n\t\t    <widget name="header" position="10,10" size="730,60" font="Regular;24" halign="center" />\n\t\t    <widget source="menu" render="Listbox" position="10,90" size="730,400" scrollbarMode="showOnDemand" transparent="1">\n\t\t\t    <convert type="TemplatedMultiContent" transparent="0">\n\t\t\t\t    {"template": [\n\t\t\t\t\t\t    MultiContentEntryPixmapAlphaBlend(pos = (0, 0), size = (48, 48), png = 2), # index 4 is the status pixmap\n\t\t\t\t\t\t    MultiContentEntryText(pos = (52, 2), size = (720, 44), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1),\n\t\t\t\t\t    ],\n\t\t\t\t    "fonts": [gFont("Regular", 24),gFont("Regular", 16)],\n\t\t\t\t    "itemHeight": 50\n\t\t\t\t    }\n\t\t\t    </convert>\n\t\t    </widget>\n\t\t    <ePixmap pixmap="skin_default/buttons/button_red.png" position="35,507" size="25,25" alphatest="on" />\n\t\t    <ePixmap pixmap="skin_default/buttons/button_green.png" position="195,507" size="25,25" alphatest="on" />\n\t\t    <ePixmap pixmap="skin_default/buttons/button_yellow.png" position="355,507" size="25,25" alphatest="on" />\n\t\t    <ePixmap pixmap="skin_default/buttons/button_blue.png" position="515,507" size="25,25" alphatest="on" />\n\t\t    <widget source="key_red" render="Label" position="62,495" zPosition="1" size="130,50" font="Regular;20" halign="left" valign="center" />\n\t\t    <widget source="key_green" render="Label" position="222,495" zPosition="1" size="130,50" font="Regular;20" halign="left" valign="center" />\n\t\t    <widget source="key_yellow" render="Label" position="382,495" zPosition="1" size="130,50" font="Regular;20" halign="left" valign="center" />\n\t\t    <widget source="key_blue" render="Label" position="542,495" zPosition="1" size="130,50" font="Regular;20" halign="left" valign="center" />\n\t    </screen>'

    def __init__(self, session, args = 0):
        Screen.__init__(self, session)
        self.session = session
        self.title = _('News about EGAMI')
        try:
            self['title'] = StaticText(self.title)
        except:
            pass

        self.png_normal = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'Extensions/EGAMINews/images/update_normal.png'))
        self.png_info = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'Extensions/EGAMINews/images/update_info.png'))
        self.png_urgent = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'Extensions/EGAMINews/images/update_urgent.png'))
        self.list = [('loading', _('Please wait ...'), self.png_info)]
        self['menu'] = List(self.list)
        self['status'] = Label()
        self['header'] = Label(header)
        self['key_red'] = StaticText(_('Exit'))
        self['key_green'] = StaticText(_('Update'))
        self['key_blue'] = StaticText(_('Show updates'))
        self['key_yellow'] = StaticText(_('Changelog'))
        self['key_info'] = StaticText()
        self['shortcuts'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.runMenuEntry,
         'cancel': self.keyCancel,
         'green': self.greenKey,
         'red': self.keyCancel,
         'yellow': self.yellowKey,
         'blue': self.blueKey}, -2)
        self.onLayoutFinish.append(self.setMenu)

    def greenKey(self):
        self.session.open(UpdateEGAMI)

    def yellowKey(self):
        self.runMenuEntry(show_upgradable=False)

    def blueKey(self):
        self.runMenuEntry(show_upgradable=True)

    def setMenu(self):
        self.delayTimer = eTimer()
        self.delayTimer.start(100, True)
        self.delayTimer.callback.append(self.createMenu)

    def createMenu(self):
        self.list = []
        res = parse_xml()
        if res == 1:
            list = load_cache()
            for item in list:
                update_type = str(item[2])
                png = self.png_normal
                if update_type == 'urgent':
                    png = self.png_urgent
                elif update_type == 'info':
                    png = self.png_info
                self.list.append((item, str(item[0]), png))

            list = None
        elif res == 2:
            message = _('It seems that your Internet connection is not ok, please check it')
        elif res == 3:
            message = _('The news file can not be analyzed, please be patient and try again later')
        elif res == 4:
            message = _('Timeout with connection to server, please be patient and try again later')
        elif res == 5:
            message = _('The news file can not be reach from server, seems server has problems')
        self['menu'].updateList(self.list)
        if res > 1:
            self.session.open(MessageBox, message, MessageBox.TYPE_ERROR, timeout=30)
        return

    def runMenuEntry(self, show_upgradable = False):
        idx = self['menu'].getIndex()
        if idx or len(self.list):
            self.session.openWithCallback(self.setMenuIndex, EGAMIUpdateInfo, idx, show_upgradable)

    def setMenuIndex(self, idx = 0):
        self['menu'].setIndex(idx)

    def keyCancel(self):
        self.list = None
        for f in (packagetmpfile, cache_file):
            if fileExists(f):
                remove(f)

        self.close()
        return


class EGAMIUpdateInfo(Screen):
    skin = '\n\t\t    <screen name="EGAMIUpdateInfo" position="center,center" size="750,550" title="EGAMI News" >\n\t\t    <widget name="header" position="10,10" size="740,60" font="Regular;24" halign="center" />\n\t\t    <widget name="update" position="10,90" size="740,400" font="Regular;20" halign="left" />\n\t\t    <ePixmap pixmap="skin_default/buttons/button_red.png" position="35,507" size="25,25" alphatest="on" />\n\t\t    <ePixmap pixmap="skin_default/buttons/button_green.png" position="195,507" size="25,25" alphatest="on" />\n\t\t    <ePixmap pixmap="skin_default/buttons/button_yellow.png" position="355,507" size="25,25" alphatest="on" />\n\t\t    <ePixmap pixmap="skin_default/buttons/button_blue.png" position="515,507" size="25,25" alphatest="on" />\n\t\t    <widget source="key_red" render="Label" position="62,495" zPosition="1" size="130,50" font="Regular;20" halign="left" valign="center" />\n\t\t    <widget source="key_green" render="Label" position="222,495" zPosition="1" size="130,50" font="Regular;20" halign="left" valign="center" />\n\t\t    <widget source="key_yellow" render="Label" position="382,495" zPosition="1" size="130,50" font="Regular;20" halign="left" valign="center" />\n\t\t    <widget source="key_blue" render="Label" position="542,495" zPosition="1" size="130,50" font="Regular;20" halign="left" valign="center" />\n\t    </screen>'

    def __init__(self, session, idx = 0, show_upgradable = False):
        self.session = session
        Screen.__init__(self, session)
        self.title = _('News about EGAMI')
        try:
            self['title'] = StaticText(self.title)
        except:
            pass

        self.list = load_cache()
        self.idx = idx
        self.infotxt = self.list[self.idx]
        self['update'] = ScrollLabel(self.getNews())
        self['header'] = Label(self.getHeaderWithDate())
        self['key_red'] = StaticText(_('Close'))
        self['key_green'] = StaticText(_('Update'))
        self['key_yellow'] = StaticText(_('Changelog'))
        self['key_blue'] = StaticText(_('Show updates'))
        self['actions'] = ActionMap(['ColorActions', 'SetupActions', 'EventViewActions'], {'red': self.closeNews,
         'green': self.greenPressed,
         'yellow': self.yellowPressed,
         'blue': self.bluePressed,
         'cancel': self.closeNews,
         'nextEvent': self.prevUpdate,
         'prevEvent': self.nextUpdate,
         'pageUp': self.pageUp,
         'pageDown': self.pageDown}, -1)
        if show_upgradable:
            self.bluePressed()

    def getText(self, what):
        self.what = what
        if self.what == 'news':
            ret = self.getNews()
        elif self.what == 'updates':
            ret = self.getUpdates()
        elif self.what == 'header':
            ret = self.getHeaderWithDate()
        return ret

    def bluePressed(self):
        try:
            self['title'].setText(_('Upgradable Packages'))
        except Exception as e:
            pass

        self['update'].setText(_('Please wait ...'))
        self.getUpdates()

    def yellowPressed(self):
        try:
            self['title'].setText(_('News about EGAMI'))
        except Exception as e:
            pass

        self['update'].setText(self.getText('news'))

    def pageUp(self):
        self['update'].pageUp()

    def pageDown(self):
        self['update'].pageDown()

    def nextUpdate(self):
        if self.idx + 1 < len(self.list):
            self.idx += 1
            self.updateText()

    def prevUpdate(self):
        if self.idx != 0:
            self.idx += -1
            self.updateText()

    def updateText(self):
        self.infotxt = self.list[self.idx]
        self['update'].setText(self.getNews())
        self['header'].setText(self.getHeaderWithDate())

    def greenPressed(self):
        self.session.open(UpdateEGAMI)

    def closeNews(self):
        self.list = None
        self.close(self.idx)
        return

    def getNews(self):
        ret = ''
        if len(self.infotxt[1]):
            for item in self.infotxt[1]:
                ret += '* ' + str(item[0]) + '\n'
                if len(item[1]):
                    for desc in item[1]:
                        ret += '    - ' + str(desc) + '\n'

                    ret += '\n'

        return ret

    def getHeaderWithDate(self):
        ret = header + self.infotxt[0]
        return str(ret)

    def getUpdates(self):
        if not fileExists(packagetmpfile):
            self.Console = Console()
            cmd = 'opkg update'
            self.Console.ePopen(cmd, self.opkg_update_finished)
        else:
            self.opkg_upgrade_finished(result=None, retval=0)
        return

    def opkg_update_finished(self, result, retval, extra_args = None):
        if not self.Console:
            self.Console = Console()
        cmd = 'opkg list-upgradable > %s' % packagetmpfile
        self.Console.ePopen(cmd, self.opkg_upgrade_finished)

    def opkg_upgrade_finished(self, result, retval, extra_args = None):
        if fileExists(packagetmpfile):
            f = open(packagetmpfile, 'r')
            updates = f.readlines()
            f.close()
            txt = ''
            for line in updates:
                line = line.split(' - ')
                if len(line) >= 3:
                    packagename = line[0].strip()
                    oldversion = line[1].strip()
                    newversion = line[2].strip()
                    if not packagename == '':
                        txt += _('\nPackage : %s \nold version : %s \nnew version : %s\n') % (packagename, oldversion, newversion)

            checkempty = len(txt)
            if checkempty == 0:
                txt = _('\nYour System is up to date')
            else:
                config.usage.update_available.value = True
        else:
            txt = _('It seems that your Internet connection is not ok, please check it')
        self['update'].setText(txt)


class UpdateEGAMI(Screen):
    skin = '<screen name="UpdateEGAMI" position="center,center" size="550,300" title="Software update" >\n\t\t<widget name="activityslider" position="0,0" size="550,5"  />\n\t\t<widget name="slider" position="0,150" size="550,30"  />\n\t\t<widget source="package" render="Label" position="10,30" size="540,20" font="Regular;18" halign="center" valign="center" backgroundColor="#25062748" transparent="1" />\n\t\t<widget source="status" render="Label" position="10,180" size="540,100" font="Regular;20" halign="center" valign="center" backgroundColor="#25062748" transparent="1" />\n\t\t</screen>'

    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        self.sliderPackages = {'ceryon-dvb-modules': 1,
         'broadmedia-dvb-modules': 2,
         'ini-dvb-modules': 3,
         'enigma2': 4,
         'egami-version-info': 5}
        self.slider = Slider(0, 4)
        self['slider'] = self.slider
        self.activityslider = Slider(0, 100)
        self['activityslider'] = self.activityslider
        self.status = StaticText(_('Please wait...'))
        self['status'] = self.status
        self.package = StaticText(_('Verifying your internet connection...'))
        self['package'] = self.package
        self.oktext = _('Press OK on your remote control to continue.')
        self.packages = 0
        self.error = 0
        self.processed_packages = []
        self.activity = 0
        self.activityTimer = eTimer()
        self.activityTimer.callback.append(self.doActivityTimer)
        self.ipkg = IpkgComponent()
        self.ipkg.addCallback(self.ipkgCallback)
        self.updating = False
        self['actions'] = ActionMap(['WizardActions'], {'ok': self.exit,
         'back': self.exit}, -1)
        self['actions'].csel = self
        self['actions'].setEnabled(False)
        iNetwork.checkNetworkState(self.checkNetworkCB)
        self.onClose.append(self.cleanup)

    def startUpgrade(self):
        update_options = ' '
        if config.usage.use_force_overwrite.value:
            update_options += '--force-overwrite '
        if config.usage.use_package_conffile.value:
            update_options += '--force-maintainer '
        f = open(update_trigger, 'w+')
        f.write(update_options)
        f.close()
        config.usage.update_available.value = False
        self.ipkg.startCmd(IpkgComponent.CMD_UPDATE)

    def cleanup(self):
        iNetwork.stopPingConsole()

    def getFreeSpace(self, mountpoint):
        if mountpoint:
            stat_info = statvfs(mountpoint)
            free_flash_space = stat_info.f_bfree * stat_info.f_bsize
            return free_flash_space

    def checkFreeSpace(self):
        free_flash_space = self.getFreeSpace('/')
        if free_flash_space > 19000000:
            self.startUpgrade()
        else:
            human_free_space = free_flash_space / 1048576
            msg = _('There are only %d MB free FLASH space available\nInstalling or updating software can cause serious software problems !\nContinue installing/updating software (at your own risk) ?') % human_free_space
            self.session.openWithCallback(self.cbSpaceCheck, MessageBox, msg, MessageBox.TYPE_YESNO, default=False)

    def cbSpaceCheck(self, result):
        if not result:
            self.close()
        else:
            self.startUpgrade()

    def checkNetworkCB(self, data):
        if data is not None:
            if data <= 2:
                self.updating = True
                self.activityTimer.start(100, False)
                self.package.setText(_('Package list update'))
                self.status.setText(_('Upgrading Your ') + ' %s %s ' % (getMachineBrand(), getMachineName()) + _('Please wait'))
                self.checkFreeSpace()
            else:
                self.package.setText(_('Your network is not working. Please try again.'))
                self.status.setText(self.oktext)
        return

    def doActivityTimer(self):
        self.activity += 1
        if self.activity == 100:
            self.activity = 0
        self.activityslider.setValue(self.activity)

    def ipkgCallback(self, event, param):
        if event == IpkgComponent.EVENT_DOWNLOAD:
            self.status.setText(_('Downloading'))
        elif event == IpkgComponent.EVENT_UPGRADE:
            if self.sliderPackages.has_key(param):
                self.slider.setValue(self.sliderPackages[param])
            self.package.setText(param)
            self.status.setText(_('Upgrading'))
            if param not in self.processed_packages:
                self.processed_packages.append(param)
                self.packages += 1
        elif event == IpkgComponent.EVENT_INSTALL:
            self.package.setText(param)
            self.status.setText(_('Installing'))
            if param not in self.processed_packages:
                self.processed_packages.append(param)
                self.packages += 1
        elif event == IpkgComponent.EVENT_REMOVE:
            self.package.setText(param)
            self.status.setText(_('Removing'))
            if param not in self.processed_packages:
                self.processed_packages.append(param)
                self.packages += 1
        elif event == IpkgComponent.EVENT_CONFIGURING:
            self.package.setText(param)
            self.status.setText(_('Configuring'))
        elif event == IpkgComponent.EVENT_MODIFIED:
            self.ipkg.write('Y')
        elif event == IpkgComponent.EVENT_ERROR:
            self['actions'].setEnabled(True)
        elif event == IpkgComponent.EVENT_DONE:
            if self.updating:
                self.updating = False
                if config.usage.use_package_conffile.value == True:
                    upgrade_args = {'use_maintainer': True,
                     'test_only': False}
                else:
                    upgrade_args = {'use_maintainer': False,
                     'test_only': False}
                if config.usage.use_force_overwrite.value:
                    upgrade_args['force_overwrite'] = True
                else:
                    upgrade_args['force_overwrite'] = False
                self.ipkg.startCmd(IpkgComponent.CMD_UPGRADE, args=upgrade_args)
            elif self.error == 0:
                self.slider.setValue(4)
                self.activityTimer.stop()
                self.activityslider.setValue(0)
                self.package.setText(_('Done - Installed or upgraded %d packages') % self.packages)
                self.status.setText(self.oktext)
                self['actions'].setEnabled(True)
            else:
                self.activityTimer.stop()
                self.activityslider.setValue(0)
                error = _('your %s %s might be unusable now. Please consult the manual for further assistance before rebooting your STB.') % (getMachineBrand(), getMachineName())
                if self.packages == 0:
                    error = _('No packages were upgraded yet. So you can check your network and try again.')
                if self.updating:
                    error = _("Your %s %s isn't connected to the internet properly. Please check it and try again.") % (getMachineBrand(), getMachineName())
                self.status.setText(_('Error') + ' - ' + error)
                self['actions'].setEnabled(True)

    def modificationCallback(self, res):
        self.ipkg.write(res and 'N' or 'Y')

    def exit(self):
        if not self.ipkg.isRunning():
            if self.packages == 0 and os_path.exists(update_trigger):
                remove(update_trigger)
            if self.packages != 0 and self.error == 0:
                f = open('/etc/do_update', 'w+').close()
                self.session.openWithCallback(self.exitAnswer, MessageBox, _('Upgrade finished.') + ' ' + _('Do you want to reboot your %s %s ?') % (getMachineBrand(), getMachineName()))
            else:
                self.close()
        elif not self.updating:
            self.close()

    def exitAnswer(self, result):
        if result is not None and result:
            self.session.open(TryQuitMainloop, 2)
        self.close()
        return


class UpdateNotification:

    def setSession(self, session):
        self.session = session

    def show_NewsCenter(self, res = None):
        if config.usage.check_for_updates.value > 0:
            intervall = config.usage.check_for_updates.value * 1000 * 3600
            self.update_timer.start(intervall, True)
        if res:
            f = open(packagetmpfile, 'w+')
            f.write(self.upgradable_packages)
            f.close
            self.session.open(EGAMIMainNews)

    def check_updates(self):
        import pygeoip
        import json
        try:
            gi = pygeoip.GeoIP('/usr/lib/python2.7/pygeoip/GeoIP.dat')
            if getMachineProcModel() in ('ini-1000am', 'ini-2000am', 'ini-8000am'):
                address_ip = json.load(urlopen('http://httpbin.org/ip'))['origin']
                country_code = gi.country_code_by_addr(address_ip)
                if country_code in 'PL':
                    pass
        except:
            pass

        self.Console = Console()
        cmd = 'opkg update'
        self.Console.ePopen(cmd, self.opkg_update_finished)

    def opkg_update_finished(self, result, retval, extra_args = None):
        if not self.Console:
            self.Console = Console()
        cmd = 'opkg list-upgradable'
        self.Console.ePopen(cmd, self.opkg_upgrade_finished)

    def opkg_upgrade_finished(self, result, retval, extra_args = None):
        is_update = False
        if len(result):
            check_result = result.split('\n', 10)
            if len(check_result):
                for line in check_result:
                    line = line.split(' - ')
                    if len(line) >= 3:
                        is_update = True
                        break

        if is_update:
            self.upgradable_packages = result
            config.usage.update_available.value = True
            if config.usage.show_notification_for_updates.value:
                message = _('There are updates available.\nDo you want to open Software Update menu ?')
                AddNotificationWithCallback(boundFunction(self.show_NewsCenter), MessageBox, message, timeout=0)
            else:
                self.show_NewsCenter(res=None)
        else:
            config.usage.update_available.value = False
            if config.usage.check_for_updates.value > 0:
                intervall = config.usage.check_for_updates.value * 1000 * 3600
                self.update_timer.start(intervall, True)
        return

    def init_timer(self):
        self.update_timer = eTimer()
        self.update_timer.callback.append(self.check_updates)
        self.update_timer.start(120000, True)


update_notification = UpdateNotification()
