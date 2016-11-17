from enigma import loadPNG, eSize, ePoint, eSlider, eTimer, RT_HALIGN_RIGHT, fontRenderClass, eConsoleAppContainer, getDesktop
from Screens.MessageBox import MessageBox
from Screens.PluginBrowser import *
from Screens.Screen import Screen
from Screens.PluginBrowser import PluginDownloadBrowser
from Components.GUIComponent import *
from Components.HTMLComponent import *
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Components.config import *
from Components.ConfigList import *
from Components.FileList import *
from Components.Sources.List import List
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap, MultiPixmap
from Components.PluginComponent import plugins
from Components.ScrollLabel import ScrollLabel
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_CURRENT_SKIN, fileExists
from Tools.LoadPixmap import LoadPixmap
from urllib2 import Request, urlopen, URLError, HTTPError
import os
import sys
import traceback
import StringIO
from xml.dom import EMPTY_NAMESPACE
import xml.dom.minidom
from EGAMI.EGAMI_tools import wyszukaj_re, getStbArch, catalogXmlUrl
fp = None

class BoundFunction:

    def __init__(self, fnc, *args):
        self.fnc = fnc
        self.args = args

    def __call__(self):
        self.fnc(*self.args)


def odinstalacyjnyPlik(ipkgResult, menuName):
    if not os.path.exists('/usr/uninstall/'):
        os.system('mkdir /usr/uninstall/')
    while 1:
        currentLine = ipkgResult.readline()
        if currentLine == '':
            break
        foundPacketNamePos = currentLine.find('Installing ')
        if foundPacketNamePos is not -1:
            name = currentLine[foundPacketNamePos + 11:]
            nextSpace = name.find(' (')
            name = name[:nextSpace]
            os.system('mkdir /usr/uninstall/' + name)
            fp = open('/usr/uninstall/' + name + '/' + name, 'w')
            fp.write(menuName)
            fp.close()
            return None

    return None

def EGAddonEntry(name, desc, author, version, size, info_txt, info_pic, menu_pic, function):
    res = [(name,
      function,
      info_txt,
      info_pic)]
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        width = 1280
        icons = 'iconsHD'
    else:
        width = 640
        icons = 'icons'
    if fileExists(resolveFilename(SCOPE_CURRENT_SKIN) + 'egami_icons/' + menu_pic + '.png'):
        png = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN) + 'egami_icons/' + menu_pic + '.png')
    else:
        png = LoadPixmap('/usr/lib/enigma2/python/EGAMI/' + icons + '/installer/' + menu_pic + '.png')
        if png is None:
            png = LoadPixmap('/usr/lib/enigma2/python/EGAMI/' + icons + '/addons/addon_download.png')
    if screenwidth and screenwidth == 1920:
        res.append(MultiContentEntryText(pos=(90, 6), size=(800, 40), font=0, text=name))
        if version != '':
            res.append(MultiContentEntryText(pos=(90, 38), size=(800, 35), font=1, flags=RT_HALIGN_LEFT, text=_('Info: ') + str(version)))
        (res.append(MultiContentEntryPixmapAlphaBlend(pos=(5, 5), size=(90, 90), png=png)),)
    else:
        res.append(MultiContentEntryText(pos=(60, 3), size=(400, 30), font=0, text=name))
        if version != '':
            res.append(MultiContentEntryText(pos=(60, 28), size=(800, 15), font=1, flags=RT_HALIGN_LEFT, text=_('Info: ') + str(version)))
        (res.append(MultiContentEntryPixmapAlphaBlend(pos=(5, 3), size=(45, 45), png=png)),)
    return res


def EGAddonMenuEntry(name, desc, function, pngname):
    res = [(name, function)]
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
        png = LoadPixmap('/usr/lib/enigma2/python/EGAMI/' + icons + '/installer/' + pngname + '.png')
        if png is None:
            png = LoadPixmap('/usr/lib/enigma2/python/EGAMI/' + icons + '/addons/addon_download.png')
    if screenwidth and screenwidth == 1920:
        res.append(MultiContentEntryText(pos=(95, 5), size=(800, 65), font=0, text=name))
        if desc != '':
            res.append(MultiContentEntryText(pos=(95, 40), size=(800, 55), font=1, text=desc))
        (res.append(MultiContentEntryPixmapAlphaBlend(pos=(5, 5), size=(90, 90), png=png)),)
    else:
        res.append(MultiContentEntryText(pos=(60, 5), size=(500, 30), font=0, text=name))
        if desc != '':
            res.append(MultiContentEntryText(pos=(60, 25), size=(500, 30), font=1, text=desc))
        (res.append(MultiContentEntryPixmapAlphaBlend(pos=(5, 5), size=(45, 45), png=png)),)
    return res


class EGListaAddonow(MenuList, HTMLComponent, GUIComponent):

    def __init__(self, list, enableWrapAround = False):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.list = list
        self.l.setList(list)
        screenwidth = getDesktop(0).size().width()
        if screenwidth and screenwidth == 1920:
            self.l.setFont(0, gFont('Regular', 32))
            self.l.setFont(1, gFont('Regular', 24))
            self.l.setItemHeight(100)
        else:
            self.l.setFont(0, gFont('Regular', 20))
            self.l.setFont(1, gFont('Regular', 14))
            self.l.setItemHeight(50)
        self.onSelectionChanged = []
        self.enableWrapAround = enableWrapAround
        GUI_WIDGET = eListbox

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        instance.selectionChanged.get().append(self.selectionChanged)
        if self.enableWrapAround:
            self.instance.setWrapAround(True)

    def selectionChanged(self):
        for f in self.onSelectionChanged:
            f()


class EGScrollLabel(ScrollLabel):

    def resizeAndSet(self, newText, height):
        s = self.instance.size()
        textSize = (s.width(), s.height())
        textSize = (textSize[0], textSize[1] - height)
        self.instance.resize(eSize(*textSize))
        p = self.instance.position()
        pos = (p.x(), p.y() + height)
        self.instance.move(ePoint(pos[0], pos[1]))
        self.long_text.resize(eSize(*textSize))
        self.long_text.move(ePoint(pos[0], pos[1]))
        s = self.long_text.size()
        lineheight = fontRenderClass.getInstance().getLineHeight(self.long_text.getFont())
        lines = int(s.height() / lineheight)
        self.pageHeight = int(lines * lineheight)
        self.instance.resize(eSize(s.width(), self.pageHeight + int(lineheight / 6)))
        self.scrollbar.move(ePoint(s.width() - 20, 0))
        self.scrollbar.resize(eSize(20, self.pageHeight + int(lineheight / 6)))
        self.scrollbar.setOrientation(eSlider.orVertical)
        self.scrollbar.setRange(0, 100)
        self.scrollbar.setBorderWidth(1)
        self.long_text.move(ePoint(0, 0))
        self.long_text.resize(eSize(s.width() - 30, self.pageHeight * 16))
        self.setText(newText)


class EGAddonInfo(Screen):
    skin = '\n\t\t<screen name="EGAddonInfo" position="center,center" size="820,550" title="EGAMI Addon Informations">\n\t\t\t<widget name="image" position="10,10" size="800,420" alphatest="on" />\n\t\t\t<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,385" size="800,4"/>\n\t\t\t<widget name="text" position="10,400" size="800,160" font="Regular;20" />\n\t\t</screen>'

    def __init__(self, session, textFile, picFile):
        Screen.__init__(self, session)
        self['text'] = EGScrollLabel('No info found...')
        self['image'] = Pixmap()
        self['image'].hide()
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.cancel,
         'back': self.cancel,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown}, -1)
        self.infoFile = textFile
        self.imageFile = picFile
        self.onLayoutFinish.append(self.downloadInfo)

    def cancel(self):
        self.close()

    def downloadInfo(self):
        os.system('rm /tmp/AddonInfo.txt')
        if not self.infoFile.endswith('/'):
            os.system('wget -q ' + self.infoFile + ' -O /tmp/AddonInfo.txt')
        if fileExists('/tmp/AddonInfo.txt'):
            infoFile = open('/tmp/AddonInfo.txt', 'r')
            theText = infoFile.read()
            infoFile.close()
            os.system('rm /tmp/AddonInfo.txt')
            self['text'].setText(theText)
        else:
            self['text'].setText(_('No further information available.'))
        try:
            self.imageFile, width, height = self.imageFile.split('|')
        except:
            width = 48
            height = 48

        width = int(width)
        height = int(height)
        os.system('rm /tmp/AddonInfo.png')
        if not self.imageFile.endswith('/'):
            os.system('wget -q ' + self.imageFile + ' -O /tmp/AddonInfo.png')
        if fileExists('/tmp/AddonInfo.png'):
            self['image'].instance.setPixmapFromFile('/tmp/AddonInfo.png')
            pixSize = (width, height)
            self['image'].show()
            os.system('rm /tmp/AddonInfo.png')


class EG_InternetAddons(Screen):
    ALLOW_SUSPEND = True
    STATE_IDLE = 0
    STATE_DOWNLOAD = 1
    STATE_INSTALL = 2
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        skin = '\n\t\t\t<screen name="EG_InternetAddons" position="center,center" size="920,850" >\n\t\t\t\t<widget name="status" position="10,10" size="900,30" font="Regular;30" valign="center" halign="center"/>\n\t\t\t\t<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,45" size="900,4"/>\n\t\t\t\t<widget name="menu" position="10,80" size="900,650" scrollbarMode="showOnDemand"/>\n\t\t\t\t<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,760" size="900,4"/>\n\t\t\t\t<ePixmap position="40,790" size="100,40" zPosition="0" pixmap="buttons/red.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<ePixmap position="240,790" size="100,40" zPosition="0" pixmap="buttons/green.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<widget name="key_red" position="80,790" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="red" transparent="1" />\n\t\t\t\t<widget name="key_green" position="280,790" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="green" transparent="1" />\n\t\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen name="EG_InternetAddons" position="center,center" size="620,550" title="EGAMI Management Addons - Internet Addons" >\n\t\t\t\t<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,45" size="800,4"/>\n\t\t\t\t<widget name="menu" position="10,60" size="610,420" scrollbarMode="showOnDemand"/>\n\t\t\t\t<widget name="status" position="30,10" size="400,25" font="Regular;21" valign="center" halign="center"/>\n\t\t\t\t<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,485" size="800,4"/>\n\t\t\t\t<ePixmap position="30,509" zPosition="0" size="35,25" pixmap="skin_default/buttons/button_red.png" transparent="1" alphatest="on" />\n\t\t\t\t<widget name="key_red" position="65,509" size="200,25" font="Regular;18"/>\n\t\t\t\t<ePixmap position="430,509" zPosition="0" size="35,25" pixmap="skin_default/buttons/button_blue.png" transparent="1" alphatest="on" />\n\t\t\t\t<widget name="key_blue" position="470,509" size="200,25" font="Regular;20" />\n\t\t\t</screen>'

    def __init__(self, session, parent, childNode, url):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('EGAMI On Line Addons Installation'))
        menuList = []
        self.multi = False
        self.url = url
        try:
            header = parent.getAttribute('text').encode('UTF-8')
            menuType = parent.getAttribute('type').encode('UTF-8')
            if menuType == 'multi':
                self.multi = True
            else:
                self.multi = False
            menuList = self.buildMenuTree(childNode)
        except:
            tracefp = StringIO.StringIO()
            traceback.print_exc(file=tracefp)
            message = tracefp.getvalue()

        if self.multi:
            self['menu'] = EGListaAddonow(menuList)
        else:
            self['menu'] = MenuList(menuList)
        self['actions'] = ActionMap(['ColorActions', 'OkCancelActions', 'MovieSelectionActions'], {'ok': self.nacisniecieOK,
         'red': self.nacisniecieOK,
         'cancel': self.closeNonRecursive,
         'exit': self.closeRecursive,
         'green': self.showAddonInfo})
        self['status'] = Label(_('Please, choose addon to install:'))
        self['key_red'] = Label(_('Download'))
        self['key_green'] = Label(_('Preview'))
        self.state = self.STATE_IDLE
        self.StateTimer = eTimer()
        self.StateTimer.stop()
        self.StateTimer.timeout.get().append(self.uruchomInstalator)

    def uruchomInstalator(self):
        if self.state == self.STATE_DOWNLOAD:
            self.state = self.STATE_IDLE
            self.fileUrl = 'http://egami-feed.com/plugins/' + self.saved_url
            print self.fileUrl
            if os.path.exists('/tmp/Addon.ipk'):
                os.system('rm /tmp/Addon.ipk')
            if self.fileUrl.endswith('.tgz') or self.fileUrl.endswith('.tar.gz') or self.fileUrl.endswith('.tar.bz2'):
                os.system('wget -q ' + self.fileUrl + ' -O /tmp/Addon.tgz')
            else:
                os.system('wget -q ' + self.fileUrl + ' -O /tmp/Addon.ipk')
            message = str(_('Do You want to install') + ' ' + self.saved_item_name + '?')
            if os.path.exists('/tmp/Addon.ipk'):
                installBox = self.session.openWithCallback(self.instalujIPK, MessageBox, _(message), MessageBox.TYPE_YESNO)
                installBox.setTitle(_('IPK Installation...'))
            elif os.path.exists('/tmp/Addon.tgz'):
                installBox = self.session.openWithCallback(self.instalujTGZ, MessageBox, _(message), MessageBox.TYPE_YESNO)
                installBox.setTitle(_('EGAMI Package Installation...'))
            else:
                errorBox = self.session.open(MessageBox, _('Failed to download an Addon...'), MessageBox.TYPE_ERROR)
                errorBox.setTitle(_('Failed...'))
            return None
        else:
            if self.state == self.STATE_INSTALL:
                if os.path.exists('/tmp/Addon.ipk'):
                    os.system('opkg -force-overwrite install /tmp/Addon.ipk ; rm /tmp/Addon.ipk')
                    self['status'].setText(_('Addon installed sucessfully !'))
                    self.state = self.STATE_IDLE
                    self.StateTimer.stop()
                    return None
                if os.path.exists('/tmp/Addon.tgz'):
                    resultFile = os.popen('cd /; tar -xz -f /tmp/Addon.tgz ; rm /tmp/Addon.tgz;rm /usr/sbin/nab_e2_restart.sh; chmod 755 /tmp/egami_e2_installer.sh; /2tmp/egami_e2_installer.sh; rm /tmp/egami_e2_installer.sh')
                    if fileExists('/tmp/restartgui'):
                        infoBox = self.session.openWithCallback(self.rebootGUI, MessageBox, _('Addon installed sucessfully !\nTo get it on plugin list, You need to reload GUI. Would You like to do it right now ?'), MessageBox.TYPE_YESNO)
                    else:
                        infoBox = self.session.open(MessageBox, _('Addon installed sucessfully !'), MessageBox.TYPE_INFO, 5)
                    infoBox.setTitle(_('Success...'))
                    self['status'].setText(_('Addon installed sucessfully !'))
                    self.state = self.STATE_IDLE
                    self.StateTimer.stop()
            elif self.state == self.STATE_IDLE:
                self['status'].setText(_('Please, choose an addon to install:'))
                self.StateTimer.stop()
                return None
            return None

    def rebootGUI(self, yesno):
        if yesno:
            os.system('killall -9 enigma2')
        else:
            self['status'].setText(_('Remember to reload enigma2 !'))

    def pobierzIPK(self, item, url, size_str):
        self.saved_item_name = item
        self.saved_url = url
        self.state = self.STATE_DOWNLOAD
        self['status'].setText(_('Downloading an addon... Please wait...'))
        self.StateTimer.start(200, True)

    def instalujIPK(self, yesno):
        if yesno:
            self.state = self.STATE_INSTALL
            self['status'].setText(_('Installing an addon... Please wait...'))
            self.StateTimer.start(200, True)
        else:
            infoBox = self.session.open(MessageBox, _('Installation aborted !'), MessageBox.TYPE_INFO)
            self.state = self.STATE_IDLE
            return None
        return None

    def instalujTGZ(self, yesno):
        if yesno:
            self.state = self.STATE_INSTALL
            self['status'].setText(_('Installing an addon... Please wait...'))
            self.StateTimer.start(200, True)
        else:
            infoBox = self.session.open(MessageBox, _('Installation aborted !'), MessageBox.TYPE_INFO)
            self.state = self.STATE_IDLE
            return None
        return None

    def nacisniecieOK(self):
        try:
            if self.multi:
                selection = self['menu'].getCurrent()
                selection[0][1]()
            else:
                selection = self['menu'].l.getCurrentSelection()
                selection[1]()
        except:
            tracefp = StringIO.StringIO()
            traceback.print_exc(file=tracefp)
            message = tracefp.getvalue()

    def zamknijMenu(self, *res):
        if len(res) and res[0]:
            plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
            self.close(True)

    def showAddonInfo(self):
        try:
            if self.multi:
                selection = self['menu'].getCurrent()
                info_txt = selection[0][2]
                info_pic = selection[0][3]
            else:
                selection = self['menu'].l.getCurrentSelection()
                info_txt = selection[2]
                info_pic = selection[3]
        except:
            info_txt = ''
            info_pic = ''

        if selection:
            info_txt = str(info_txt)
            info_pic = str(info_pic)
            self.root_url = 'http://egami-feed.com/plugins/'
            infoBox = self.session.open(EGAddonInfo, str(self.root_url + info_txt), str(self.root_url + info_pic))
            if self.multi:
                selection = self['menu'].getCurrent()
                infoBox.setTitle(_(selection[0][0]))
            else:
                selection = self['menu'].l.getCurrentSelection()
                infoBox.setTitle(_(selection[0]))

    def noweMenu(self, destList, node):
        menuTitle = node.getAttribute('text').encode('UTF-8')
        menuDesc = node.getAttribute('desc').encode('UTF-8')
        menuIcon = node.getAttribute('menu_pic').encode('UTF-8')
        info_arch = node.getAttribute('arch').encode('UTF-8')
        if info_arch == '':
            info_arch = 'all'
        a = BoundFunction(self.session.openWithCallback, self.zamknijMenu, EG_InternetAddons, node, node.childNodes, self.url)
        if info_arch in (getStbArch(), 'all'):
            if self.multi:
                destList.append(EGAddonMenuEntry(menuTitle, menuDesc, a, menuIcon))
            else:
                destList.append((menuTitle, a))

    def addItem(self, destList, node):
        item_text = node.getAttribute('text').encode('UTF-8')
        item_url = node.getAttribute('url').encode('UTF-8')
        item_desc = node.getAttribute('desc').encode('UTF-8')
        item_author = node.getAttribute('author').encode('UTF-8')
        item_version = node.getAttribute('version').encode('UTF-8')
        item_size = node.getAttribute('size').encode('UTF-8')
        info_txt = node.getAttribute('info_txt').encode('UTF-8')
        info_pic = node.getAttribute('info_pic').encode('UTF-8')
        menu_pic = node.getAttribute('menu_pic').encode('UTF-8')
        info_arch = node.getAttribute('arch').encode('UTF-8')
        if info_arch == '':
            info_arch = 'all'
        a = BoundFunction(self.pobierzIPK, item_text, item_url, item_size)
        if info_arch in (getStbArch(), 'all'):
            if self.multi:
                destList.append(EGAddonEntry(item_text, item_desc, item_author, item_version, item_size, info_txt, info_pic, menu_pic, a))
            else:
                destList.append((item_text,
                 a,
                 info_txt,
                 info_pic))

    def buildMenuTree(self, childNode):
        list = []
        for x in childNode:
            if x.nodeType != xml.dom.minidom.Element.nodeType:
                pass
            elif x.tagName == 'item':
                self.addItem(list, x)
            elif x.tagName == 'menu':
                self.noweMenu(list, x)

        return list

    def closeNonRecursive(self):
        plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
        downfile = '/tmp/.catalog.xml'
        if fileExists(downfile):
            os.remove(downfile)
        self.close(False)

    def closeRecursive(self):
        plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
        downfile = '/tmp/.catalog.xml'
        if fileExists(downfile):
            os.remove(downfile)
        self.close(True)


class EG_PrzegladaczAddonow(EG_InternetAddons):

    def getMenuFile(self, url):
        inputUrl = url
        xmlFile = os.popen('cat /tmp/.catalog.xml').read()
        mdom = xml.dom.minidom.parseString(xmlFile)
        return mdom

    def __init__(self, session, url):
        try:
            self.root_url = url
            mdom = self.getMenuFile(self.root_url)
            node = mdom.childNodes[0]
            child = mdom.childNodes[0].childNodes
            EG_InternetAddons.__init__(self, session, mdom.childNodes[0], mdom.childNodes[0].childNodes, url)
        except:
            tracefp = StringIO.StringIO()
            traceback.print_exc(file=tracefp)
            message = tracefp.getvalue()
            EG_InternetAddons.__init__(self, session, None, None, None)

        return


class EGAddonRemove(Screen):
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        skin = '\n\t\t\t<screen name="EGAddonRemove" position="center,center" size="920,850" >\n\t\t\t\t<widget name="status" position="10,10" size="900,30" font="Regular;30" valign="center" halign="center"/>\n\t\t\t\t<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,45" size="900,4"/>\n\t\t\t\t<widget name="remove" itemHeight="50" font="Regular;28" position="10,80" size="900,750" scrollbarMode="showOnDemand"/>\n\t\t\t\t<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,760" size="900,4"/>\n\t\t\t\t<ePixmap position="40,790" size="100,40" zPosition="0" pixmap="buttons/red.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<widget name="key_red" position="80,790" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="red" transparent="1" />\n\t\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen name="EGAddonRemove" position="center,center" size="620,550" title="EGAMI Management Addons - Remove Addon" >\n\t\t\t\t<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,45" size="800,4"/>\n\t\t\t\t<widget name="remove" position="10,60" size="610,420" scrollbarMode="showOnDemand"/>\n\t\t\t\t<widget name="status" position="30,10" size="400,25" font="Regular;21" valign="center" halign="center"/>\n\t\t\t\t<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,485" size="800,4"/>\n\t\t\t\t<ePixmap position="30,509" zPosition="0" size="35,25" pixmap="skin_default/buttons/button_red.png" transparent="1" alphatest="on" />\n\t\t\t\t<widget name="key_red" position="65,509" size="200,25" font="Regular;18"/>\n\t\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('EGAMI Remove Addon'))
        self['status'] = Label(_('Please, choose addon to remove:'))
        self['key_red'] = Label(_('Remove'))
        self.mlist = []
        self['remove'] = MenuList(self.mlist)
        self['actions'] = ActionMap(['ColorActions', 'WizardActions', 'DirectionActions'], {'ok': self.askRemoveIPK,
         'red': self.askRemoveIPK,
         'back': self.closeAndReload}, -1)
        self.populateSL()

    def refr_sel(self):
        self['remove'].moveToIndex(1)
        self['remove'].moveToIndex(0)

    def closeAndReload(self):
        plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
        self.close()

    def populateSL(self):
        self.mlist = []
        myscripts = os.listdir('/usr/uninstall')
        for fil in myscripts:
            if fil.endswith('.del') and fil.startswith('Remove'):
                fil2 = fil[6:-4]
                self.mlist.append(fil2)
            elif fil.endswith('.del') and not fil.startswith('Remove'):
                fil2 = fil[0:-4]
                self.mlist.append(fil2)

        self['remove'].setList(self.mlist)

    def askRemoveIPK(self):
        try:
            ipkName = self['remove'].getCurrent()
            removeBox = self.session.openWithCallback(self.removeIPK, MessageBox, _('Do really want to remove ' + ipkName + '?'), MessageBox.TYPE_YESNO)
            removeBox.setTitle(_('Package Removing...'))
            return None
        except:
            return None

        return None

    def removeIPK(self, yesno):
        if yesno:
            mysel = self['remove'].getCurrent()
            mysel2 = '/usr/uninstall/' + mysel + '.del'
            if fileExists(mysel2):
                os.system('chmod 777 ' + mysel2)
                os.system(mysel2)
            else:
                mysel2 = '/usr/uninstall/Remove' + mysel + '.del'
                os.system('chmod 777 ' + mysel2)
                os.system(mysel2)
            infoBox = self.session.open(MessageBox, _('Addon removed!'), MessageBox.TYPE_INFO)
            infoBox.setTitle(_('Remove Package'))
            plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
            self.populateSL()
        else:
            infoBox = self.session.open(MessageBox, _('Addon NOT removed!'), MessageBox.TYPE_INFO)
            infoBox.setTitle(_('Remove Package'))


class EG_Manual_installation(Screen):
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        skin = '\n\t\t\t<screen name="EG_Manual_installation" position="center,center" size="920,850" >\n\t\t\t\t<widget name="status" position="10,10" size="900,30" font="Regular;30" valign="center" halign="center"/>\n\t\t\t\t<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,45" size="900,4"/>\n\t\t\t\t<widget name="listaaddonow" itemHeight="50" font="Regular;28" position="10,80" size="900,750" scrollbarMode="showOnDemand"/>\n\t\t\t\t<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,760" size="900,4"/>\n\t\t\t\t<ePixmap position="40,790" size="100,40" zPosition="0" pixmap="buttons/red.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<widget name="key_red" position="80,790" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="red" transparent="1" />\n\t\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen name="EG_Manual_installation" position="center,center" size="620,550" title="EGAMI Management Addons - Manual Install" >\n\t\t\t\t<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,45" size="800,4"/>\n\t\t\t\t<widget name="listaaddonow" position="10,60" size="610,420" scrollbarMode="showOnDemand"/>\n\t\t\t\t<widget name="status" position="30,10" size="400,25" font="Regular;21" valign="center" halign="center"/>\n\t\t\t\t<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,485" size="800,4"/>\n\t\t\t\t<ePixmap position="30,509" zPosition="0" size="35,25" pixmap="skin_default/buttons/button_red.png" transparent="1" alphatest="on" />\n\t\t\t\t<widget name="key_red" position="65,509" size="200,25" font="Regular;18"/>\n\t\t\t</screen>'

    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('EGAMI Manual Installation Addon'))
        self['listaaddonow'] = FileList('/tmp/', showDirectories=False, showFiles=True, matchingPattern='(?i)^.*\\.(ipk|tar.gz|tar.bz2)', isTop=False)
        self.addony = self['listaaddonow']
        self['status'] = Label(_('Please, choose addon to install:'))
        self['key_red'] = Label(_('Install'))
        self['actions'] = ActionMap(['ColorActions', 'WizardActions', 'DirectionActions'], {'ok': self.start,
         'red': self.start,
         'back': self.closeAndReload}, -1)

    def start(self):
        self.installItem = self['listaaddonow'].getFilename()
        try:
            if self['listaaddonow'].canDescent():
                self['listaaddonow'].descent()
            else:
                message = str('Install ' + self.installItem + '?')
                if self.installItem.endswith('.ipk'):
                    installBox = self.session.openWithCallback(self.installIPK, MessageBox, _(message), MessageBox.TYPE_YESNO)
                    installBox.setTitle(_('Install IPK'))
                elif self.installItem.endswith('tar.gz'):
                    installBox = self.session.openWithCallback(self.installTarGz, MessageBox, _(message), MessageBox.TYPE_YESNO)
                    installBox.setTitle(_('Install Tar-ball'))
                elif self.installItem.endswith('tar.bz2'):
                    installBox = self.session.openWithCallback(self.installTarBz2, MessageBox, _(message), MessageBox.TYPE_YESNO)
                    installBox.setTitle(_('Install Tar-ball'))
        except:
            print 'no file to install'

    def installIPK(self, yesno):
        if yesno:
            os.system('opkg -force-overwrite install /tmp/' + self.installItem)
            resultFile = os.popen('opkg -force-overwrite install /tmp/' + self.installItem)
            odinstalacyjnyPlik(resultFile, self.installItem)
            infoBox = self.session.open(MessageBox, _('Addon installed!'), MessageBox.TYPE_INFO)
            infoBox.setTitle(_('Addon installed sucessfully!'))
            os.system('rm -rf /tmp/*.ipk')
        else:
            infoBox = self.session.open(MessageBox, _('Addon NOT installed!'), MessageBox.TYPE_INFO)
            infoBox.setTitle(_('Addon is not compatiable!'))
            os.system('rm -rf /tmp/*.ipk')

    def installTarGz(self, yesno):
        if yesno:
            resultFile = os.popen('cd /; tar -xz -f /tmp/' + self.installItem + ';chmod 755 /tmp/egami_e2_installer.sh; /tmp/egami_e2_installer.sh; rm /tmp/egami_e2_installer.sh')
            infoBox = self.session.open(MessageBox, _('Package installed!'), MessageBox.TYPE_INFO)
            infoBox.setTitle(_('Addon installed sucessfully!'))
        else:
            infoBox = self.session.open(MessageBox, _('Package NOT installed!'), MessageBox.TYPE_INFO)
            infoBox.setTitle(_('Addon is not compatiable!'))

    def installTarBz2(self, yesno):
        if yesno:
            resultFile = os.popen('cd /; tar -xj -f /tmp/' + self.installItem + ';;chmod 755 /tmp/egami_e2_installer.sh; /tmp/egami_e2_installer.sh; rm /tmp/egami_e2_installer.sh')
            infoBox = self.session.open(MessageBox, _('Package installed!'), MessageBox.TYPE_INFO)
            infoBox.setTitle(_('Addon installed sucessfully!'))
        else:
            infoBox = self.session.open(MessageBox, _('Package NOT installed!'), MessageBox.TYPE_INFO)
            infoBox.setTitle(_('Addon is not compatiable!'))

    def closeAndReload(self):
        plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
        self.close()


def EgamiAddonMenuEntryComponent(name, description, long_description = None, pngname = 'default', width = 540):
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
         MultiContentEntryText(pos=(100, 5), size=(width - 60, 45), font=0, text=_(name)),
         MultiContentEntryText(pos=(100, 40), size=(width - 60, 32), font=1, text=_(description)),
         MultiContentEntryPixmapAlphaTest(pos=(10, 5), size=(90, 90), png=png)]
    else:
        return [(_(name), _(long_description)),
         MultiContentEntryText(pos=(70, 5), size=(width - 60, 25), font=0, text=_(name)),
         MultiContentEntryText(pos=(70, 26), size=(width - 60, 17), font=1, text=_(description)),
         MultiContentEntryPixmapAlphaTest(pos=(10, 5), size=(45, 45), png=png)]
        return


def EgamiAddonSeparatorEntryComponent(sep, width = 500):
    png = LoadPixmap('/usr/lib/enigma2/python/EGAMI/icons/div-h.png')
    if png is None:
        png = LoadPixmap('/usr/share/enigma2//usr/lib/enigma2/python/EGAMI/icons/egami_icons/div-h.png')
    return [sep, MultiContentEntryPixmapAlphaTest(pos=(10, 24), size=(width, 2), png=png)]


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


class EGAddonMenu(Screen):
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        skin = '\n\t\t\t<screen name="EGAddonMenu" position="center,center" size="920,850" >\n\t\t\t\t<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,45" size="900,4"/>\n\t\t\t\t<widget name="list" position="10,60" size="900,750" scrollbarMode="showOnDemand"/>\n\t\t\t\t<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,760" size="900,4"/>\n\t\t\t\t<ePixmap position="40,790" size="100,40" zPosition="0" pixmap="buttons/red.png" transparent="1" alphatest="blend"/>\n\t\t\t\t<widget name="key_red" position="80,790" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="red" transparent="1" />\n\t\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen name="EGAddonMenu" position="center,center" size="620,550" >\n\t\t\t\t<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,45" size="800,4"/>\n\t\t\t\t<widget name="list" position="10,60" size="610,420" scrollbarMode="showOnDemand"/>\n\t\t\t\t<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,485" size="800,4"/>\n\t\t\t\t<ePixmap position="30,509" zPosition="0" size="35,25" pixmap="skin_default/buttons/button_red.png" transparent="1" alphatest="on" />\n\t\t\t\t<widget name="key_red" position="65,509" size="200,25" font="Regular;18"/>\n\t\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['key_red'] = Label(_('Exit'))
        self.list = []
        self['list'] = EgamiMenuList(self.list)
        self.selectedList = []
        self.onChangedEntry = []
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
        self.updateList()
        self.selectedList = self['list']

    def keyRed(self):
        self.close()

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

    def keyOk(self):
        item = self['list'].getCurrent()
        selected = item[0][0]
        if selected == _('Download EGAMI Addons'):
            staturl = catalogXmlUrl()
            downfile = '/tmp/.catalog.xml'
            if fileExists(downfile):
                os.remove(downfile)
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

    def EGConnectionCallback(self):
        downfile = '/tmp/.catalog.xml'
        if fileExists(downfile):
            self.session.open(EG_PrzegladaczAddonow, '/tmp/.catalog.xml')
        else:
            nobox = self.session.open(MessageBox, _('Sorry, Connection Failed'), MessageBox.TYPE_INFO)

    def noYet(self):
        nobox = self.session.open(MessageBox, _('Function Not Yet Available'), MessageBox.TYPE_INFO)
        nobox.setTitle(_('Info'))

    def runUpgrade(self, result):
        if result:
            from Plugins.SystemPlugins.SoftwareManager.plugin import UpdatePlugin
            self.session.open(UpdatePlugin, '/usr/lib/enigma2/python/Plugins/SystemPlugins/SoftwareManager')

    def updateList(self):
        self.setTitle(_('EGAMI Addons Panel'))
        self.list = []
        self.list.append(EgamiAddonMenuEntryComponent('Download EGAMI Addons', _('Download from feed IPTV, SoftCams'), _('Collection of nice IPTV plugins, bootlogos and softcams'), 'addons/addon_download'))
        self.list.append(EgamiAddonMenuEntryComponent('Download Plugins', _('Download from feeds skins, extensions, picons'), _('Collection of plugins/skins/picons/channel lists'), 'addons/addon_download'))
        self.list.append(EgamiAddonSeparatorEntryComponent('separator'))
        self.list.append(EgamiAddonMenuEntryComponent('User Server Addons', _('Download feeds from Your own server'), _('Use Your onw server for feed downloads'), 'addons/addon_cvs'))
        self.list.append(EgamiAddonMenuEntryComponent('Install Tar.gz and IPK Addons', _('Install manually packages from /tmp'), _('You can install here tar.gz/tar.bz2/ipk/zip packages'), 'addons/addon_manual'))
        self.list.append(EgamiAddonSeparatorEntryComponent('separator'))
        self.list.append(EgamiAddonMenuEntryComponent('Remove Plugins', _('Remove installed plugins'), _('You can remove here extensions which you want'), 'addons/addon_remove'))
        self.list.append(EgamiAddonMenuEntryComponent('Remove EGAMI addons', _('Remove softcams or iptv plugins'), _('You remove softcams and iptv plugins here'), 'addons/addon_remove'))
        self['list'].l.setList(self.list)


class EGConnectionAnimation(Screen):
    skin = '<screen position="390,100" size="484,220" title="EGAMI" flags="wfNoBorder">\n\t\t\t<widget name="connect" position="0,0" size="484,250" zPosition="-1" pixmaps="/usr/lib/enigma2/python/EGAMI/icons/egami_icons/connection_1.png,/usr/lib/enigma2/python/EGAMI/icons/egami_icons/connection_2.png,/usr/lib/enigma2/python/EGAMI/icons/egami_icons/connection_3.png,/usr/lib/enigma2/python/EGAMI/icons/egami_icons/connection_4.png,/usr/lib/enigma2/python/EGAMI/icons/egami_icons/connection_5.png" transparent="1" />\n\t\t\t<widget name="lab1" position="10,180" halign="center" size="460,60" zPosition="1" font="Regular;20" valign="top" transparent="1" />\n\t\t  </screen>'

    def __init__(self, session, myurl, downfile):
        Screen.__init__(self, session)
        self['connect'] = MultiPixmap()
        self['connect'].setPixmapNum(0)
        self['lab1'] = Label(_('Wait please connection in progress ...'))
        self.myurl = myurl
        self.downfile = downfile
        self.activityTimer = eTimer()
        if self.downfile == 'N/A':
            self.activityTimer.timeout.get().append(self.updatepixWget)
        else:
            self.activityTimer.timeout.get().append(self.updatepix)
        self.onShow.append(self.startShow)
        self.onClose.append(self.delTimer)

    def startShow(self):
        self.curpix = 0
        self.count = 0
        self.activityTimer.start(300)

    def updatepixWget(self):
        self.activityTimer.stop()
        if self.curpix > 3:
            self.curpix = 0
        if self.count > 8:
            self.curpix = 4
            self['lab1'].setText(_('Wait please, download in progress...'))
        self['connect'].setPixmapNum(self.curpix)
        if self.count == 10:
            rc = system(self.myurl)
        if self.count == 11:
            self.close()
        self.activityTimer.start(120)
        self.curpix += 1
        self.count += 1

    def updatepix(self):
        self.activityTimer.stop()
        if self.curpix > 3:
            self.curpix = 0
        if self.count > 8:
            self.curpix = 4
            req = Request(self.myurl)
            try:
                response = urlopen(req)
                self['lab1'].setText(_('Connection Established'))
                html = response.read()
                out = open(self.downfile, 'w')
                out.write(html)
                out.close()
            except:
                e = None
                self['lab1'].setText(_('Connect can not be established'))
                self.close()

        self['connect'].setPixmapNum(self.curpix)
        if self.count == 10:
            self.close()
        self.activityTimer.start(120)
        self.curpix += 1
        self.count += 1
        return

    def delTimer(self):
        del self.activityTimer
