from Tools.Profile import profile
profile('LOAD:ElementTree')
import xml.etree.cElementTree
import os
profile('LOAD:enigma_skin')
from enigma import eSize, ePoint, eRect, gFont, eWindow, eLabel, ePixmap, eWindowStyleManager, addFont, gRGB, eWindowStyleSkinned, getDesktop
from Components.config import ConfigSubsection, ConfigText, ConfigSlider, config, ConfigSelection, ConfigNothing
from Components.Sources.Source import ObsoleteSource
from Components.SystemInfo import SystemInfo
from Tools.Directories import resolveFilename, SCOPE_SKIN, SCOPE_SKIN_IMAGE, SCOPE_FONTS, SCOPE_ACTIVE_SKIN, SCOPE_ACTIVE_LCDSKIN, SCOPE_CURRENT_SKIN, SCOPE_CONFIG, fileExists
from Tools.Import import my_import
from Tools.LoadPixmap import LoadPixmap
from Components.RcModel import rc_model
from boxbranding import getBoxType
config.vfd = ConfigSubsection()
config.vfd.show = ConfigSelection([('skin_text.xml', _('Channel Name')), ('skin_text_clock.xml', _('Clock'))], 'skin_text.xml')
if not os.path.exists('/usr/share/enigma2/skin_text.xml'):
    config.vfd.show = ConfigNothing()
colorNames = {}
colorNamesInt = dict()
switchPixmap = dict()
cascadingStyleSheets = dict()
colorNamesHuman = {}
fonts = {'Body': ('Regular',
          18,
          22,
          16),
 'ChoiceList': ('Regular',
                20,
                24,
                18)}
parameters = {}
constant_widgets = {}
variables = {}
DEFAULT_SKIN = 'oDreamy-FHD/skin.xml'
DEFAULT_DISPLAY_SKIN = 'skin_display.xml'
isVTISkin = False

def dump(x, i = 0):
    print ' ' * i + str(x)
    try:
        for n in x.childNodes:
            dump(n, i + 1)

    except:
        None

    return


class SkinError(Exception):

    def __init__(self, message):
        self.msg = message

    def __str__(self):
        return "[Skin] {%s}: %s. Please contact the skin's author!" % (config.skin.primary_skin.value, self.msg)


class DisplaySkinError(Exception):

    def __init__(self, message):
        self.msg = message

    def __str__(self):
        return "[Skin] {%s}: %s. Please contact the skin's author!" % (config.skin.display_skin.value, self.msg)


dom_skins = []

def addSkin(name, scope = SCOPE_SKIN):
    global dom_skins
    if name is None or not len(name):
        print '[SKIN ERROR] attempt to add a skin without filename'
        return False
    else:
        filename = resolveFilename(scope, name)
        if fileExists(filename):
            mpath = os.path.dirname(filename) + '/'
            try:
                file = open(filename, 'r')
                dom_skins.append((mpath, xml.etree.cElementTree.parse(file).getroot()))
            except:
                print '[SKIN ERROR] error in %s' % filename
                return False

            return True
        return False


def get_modular_files(name, scope = SCOPE_SKIN):
    dirname = resolveFilename(scope, name + 'mySkin/')
    file_list = []
    if fileExists(dirname):
        skin_files = os.listdir(dirname)
        if len(skin_files):
            for f in skin_files:
                if f.startswith('skin_') and f.endswith('.xml'):
                    file_list.append('mySkin/' + f)

    file_list = sorted(file_list, key=str.lower)
    return file_list


def skin_user_skinname():
    name = 'skin_user_' + config.skin.primary_skin.value[:config.skin.primary_skin.value.rfind('/')] + '.xml'
    filename = resolveFilename(SCOPE_CONFIG, name)
    if fileExists(filename):
        return name
    else:
        return None


config.skin = ConfigSubsection()
config.skin.runningStep = ConfigSlider(default=4, increment=1, limits=(0, 9))
if not fileExists(resolveFilename(SCOPE_SKIN, DEFAULT_SKIN)):
    DEFAULT_SKIN = 'skin.xml'
config.skin.primary_skin = ConfigText(default=DEFAULT_SKIN)
config.skin.display_skin = ConfigText(default=DEFAULT_DISPLAY_SKIN)

def skinExists(skin = False):
    if not skin or not isinstance(skin, skin):
        skin = config.skin.primary_skin.value
    skin = resolveFilename(SCOPE_SKIN, skin)
    if not fileExists(skin):
        if fileExists(resolveFilename(SCOPE_SKIN, DEFAULT_SKIN)):
            config.skin.primary_skin.value = DEFAULT_SKIN
        else:
            config.skin.primary_skin.value = 'skin.xml'
        config.skin.primary_skin.save()


skinExists()
if SystemInfo['grautec']:
    DEFAULT_DISPLAY_SKIN = 'skin_display_grautec.xml'

def getSkinPath():
    primary_skin_path = config.skin.primary_skin.value.replace('skin.xml', '')
    if not primary_skin_path.endswith('/'):
        primary_skin_path = primary_skin_path + '/'
    return primary_skin_path


primary_skin_path = getSkinPath()
profile('LoadSkin')
res = None
name = skin_user_skinname()
if name:
    res = addSkin(name, SCOPE_CONFIG)
if not name or not res:
    addSkin('skin_user.xml', SCOPE_CONFIG)
addSkin('skin_box.xml')
addSkin('skin_second_infobar.xml')
display_skin_id = 1
if getBoxType().startswith('dm'):
    display_skin_id = 2
try:
    if not addSkin(os.path.join('display', config.skin.display_skin.value)):
        raise DisplaySkinError, '[Skin] display skin not found'
except Exception as err:
    print '[Skin]', err
    skin = DEFAULT_DISPLAY_SKIN
    if config.skin.display_skin.value == skin:
        skin = 'skin_display.xml'
    print '[Skin] defaulting to standard display skin...', skin
    config.skin.display_skin.value = skin
    skin = os.path.join('display', skin)
    addSkin(skin)
    del skin

try:
    if not addSkin(config.vfd.show.value):
        raise DisplaySkinError, '[Skin] display vfd skin not found'
except:
    addSkin('skin_text.xml')

addSkin('skin_subtitles.xml')
try:
    addSkin(primary_skin_path + 'skin_user_colors.xml', SCOPE_SKIN)
    print '[SKIN] loading user defined colors for skin', primary_skin_path + 'skin_user_colors.xml'
except (SkinError, IOError, AssertionError) as err:
    print '[SKIN] not loading user defined colors for skin'

try:
    addSkin(primary_skin_path + 'skin_user_header.xml', SCOPE_SKIN)
    print '[SKIN] loading user defined header file for skin', primary_skin_path + 'skin_user_header.xml'
except (SkinError, IOError, AssertionError) as err:
    print '[SKIN] not loading user defined header file for skin'

def load_modular_files():
    modular_files = get_modular_files(primary_skin_path, SCOPE_SKIN)
    if len(modular_files):
        for f in modular_files:
            try:
                addSkin(primary_skin_path + f, SCOPE_SKIN)
                print '[SKIN] loading modular skin file : ', primary_skin_path + f
            except (SkinError, IOError, AssertionError) as err:
                print '[SKIN] failed to load modular skin file : ', err


load_modular_files()
try:
    if not addSkin(config.skin.primary_skin.value):
        raise SkinError, 'primary skin not found'
except Exception as err:
    print 'SKIN ERROR:', err
    skin = DEFAULT_SKIN
    if config.skin.primary_skin.value == skin:
        skin = 'skin.xml'
    print 'defaulting to standard skin...', skin
    config.skin.primary_skin.value = skin
    addSkin(skin)
    del skin

addSkin('skin_default_egami.xml')
addSkin('skin_default.xml')
profile('LoadSkinDefaultDone')

def parseCoordinate(s, e, size = 0, font = None):
    global fonts
    s = s.strip()
    if s == 'center':
        if not size:
            val = 0
        else:
            val = (e - size) / 2
    else:
        if s == '*':
            return None
        if s[0] is 'e':
            val = e
            s = s[1:]
        elif s[0] is 'c':
            val = e / 2
            s = s[1:]
        else:
            val = 0
        if s:
            if s[-1] is '%':
                val += e * int(s[:-1]) / 100
            elif s[-1] is 'w':
                val += fonts[font][3] * int(s[:-1])
            elif s[-1] is 'h':
                val += fonts[font][2] * int(s[:-1])
            else:
                val += int(s)
    if val < 0:
        val = 0
    return val


def getParentSize(object, desktop):
    size = eSize()
    if object:
        parent = object.getParent()
        if parent and parent.size().isEmpty():
            parent = parent.getParent()
        if parent:
            size = parent.size()
        elif desktop:
            size = desktop.size()
    return size


def parseValuePair(s, scale, object = None, desktop = None, size = None):
    x, y = s.split(',')
    parentsize = eSize()
    if object and ('c' in x or 'c' in y or 'e' in x or 'e' in y or '%' in x or '%' in y):
        parentsize = getParentSize(object, desktop)
    xval = parseCoordinate(x, parentsize.width(), size and size.width() or 0)
    yval = parseCoordinate(y, parentsize.height(), size and size.height() or 0)
    return (xval * scale[0][0] / scale[0][1], yval * scale[1][0] / scale[1][1])


def parsePosition(s, scale, object = None, desktop = None, size = None):
    x, y = parseValuePair(s, scale, object, desktop, size)
    return ePoint(x, y)


def parseSize(s, scale, object = None, desktop = None):
    x, y = parseValuePair(s, scale, object, desktop)
    return eSize(x, y)


def parseFont(s, scale):
    try:
        f = fonts[s]
        name = f[0]
        size = f[1]
    except:
        name, size = s.split(';')

    return gFont(name, int(size) * scale[0][0] / scale[0][1])


def parseColor(s):
    if s[0] != '#':
        try:
            return colorNames[s]
        except:
            raise SkinError("[Skin] color '%s' must be #aarrggbb or valid named color" % s)

    return gRGB(int(s[1:], 16))


def parseColorInt(s):
    if s[0] != '#':
        try:
            return colorNamesInt[s]
        except:
            raise SkinError("color '%s' must be #aarrggbb or valid named color" % s)

    return int(s[1:], 16)


def getAttribFromCSS(style, name, value):
    for attrib in cascadingStyleSheets[style].keys():
        _value = cascadingStyleSheets[style][attrib]
        if attrib == name:
            return _value
        if attrib == 'css':
            value = getAttribFromCSS(_value, name, value)
            if value:
                return value

    return value


def getAttribScreen(attrib, name):
    value = attrib.get(name)
    if value:
        return value
    styles = attrib.get('css')
    if styles:
        styles = styles.split(',')
        for style in styles:
            style = style.strip()
            value = getAttribFromCSS(style, name, value)
            if value:
                return value

    return value


def collectAttributes(skinAttributes, node, context, skin_path_prefix = None, ignore = (), filenames = frozenset(('pixmap',
 'pointer',
 'seek_pointer',
 'backgroundPixmap',
 'selectionPixmap',
 'sliderPixmap',
 'scrollbarbackgroundPixmap'))):
    size = None
    pos = None
    font = None
    for attrib, value in node.items():
        if attrib not in ignore:
            if attrib in filenames:
                pngfile = resolveFilename(SCOPE_ACTIVE_SKIN, value, path_prefix=skin_path_prefix)
                if fileExists(resolveFilename(SCOPE_ACTIVE_LCDSKIN, value, path_prefix=skin_path_prefix)):
                    pngfile = resolveFilename(SCOPE_ACTIVE_LCDSKIN, value, path_prefix=skin_path_prefix)
                value = pngfile
            if attrib == 'size':
                size = value.encode('utf-8')
            elif attrib == 'position':
                pos = value.encode('utf-8')
            elif attrib == 'font':
                font = value.encode('utf-8')
                skinAttributes.append((attrib, font))
            else:
                skinAttributes.append((attrib, value.encode('utf-8')))

    if font is None:
        font = getAttribScreen(node.attrib, 'font')
    if size is None:
        size = getAttribScreen(node.attrib, 'size')
    if pos is None:
        pos = getAttribScreen(node.attrib, 'position')
    if font is not None:
        font = font.encode('utf-8')
        skinAttributes.append(('font', font))
    if size is not None:
        size = size.encode('utf-8')
    if pos is not None:
        pos, size = context.parse(pos, size, font)
        skinAttributes.append(('position', pos))
    if size is not None:
        skinAttributes.append(('size', size))
    return


def morphRcImagePath(value):
    if rc_model.rcIsDefault() is False:
            if value == '/usr/share/enigma2/skin_default/rc.png' or value == '/usr/share/enigma2/skin_default/rcold.png':
		    value = rc_model.getRcLocation() + 'rc.png'
	    elif value == '/usr/share/enigma2/skin_default/rc0.png' or value == '/usr/share/enigma2/skin_default/rc1.png' or value == '/usr/share/enigma2/skin_default/rc2.png':
		    value = rc_model.getRcLocation() + 'rc.png'
    return value


def loadPixmap(path, desktop):
    cached = False
    option = path.find('#')
    if option != -1:
        options = path[option + 1:].split(',')
        path = path[:option]
        cached = 'cached' in options
    ptr = LoadPixmap(morphRcImagePath(path), desktop, cached)
    if ptr is None:
        print '[SKIN] pixmap file %s not found!' % path
    return ptr


pngcache = []

def cachemenu():
    global pngcache
    pixmaplist = []
    for path, skin in dom_skins:
        for x in skin.findall('screen'):
            if x.attrib.get('name') == 'menu_mainmenu':
                print x.attrib.get('name')
                for s in x.findall('ePixmap'):
                    if s.attrib.get('pixmap', '') is not '':
                        pixmaplist.append(s.attrib.get('pixmap', ''))

                for s in x.findall('widget'):
                    if s.attrib.get('pixmap', '') is not '':
                        pixmaplist.append(s.attrib.get('pixmap', ''))

    desktop = getDesktop(0)
    for s in pixmaplist:
        value = '/usr/share/enigma2/' + s
        ptr = loadPixmap(value, desktop)
        pngcache.append((value, ptr))


try:
    if config.skin.primary_skin.value == 'oDreamy-FHD/skin.xml' or config.skin.primary_skin.value == DEFAULT_SKIN:
        cachemenu()
except:
    print '[SKIN] fail cache main menu'

class AttributeParser():

    def __init__(self, guiObject, desktop, scale = ((1, 1), (1, 1))):
        self.guiObject = guiObject
        self.desktop = desktop
        self.scaleTuple = scale

    def applyOne(self, attrib, value):
        try:
            getattr(self, attrib)(value)
        except AttributeError:
            print SkinError('[SKIN] Attribute not implemented:"%s" value:"%s"' % (attrib, value))
        except SkinError as ex:
            print '\x1b[91m[SKIN] Error:', ex,
            print '\x1b[0m'
        except:
            print SkinError('[Skin] attribute "%s" with wrong (or unknown) value "%s"' % (attrib, value))

    def applyAll(self, attrs):
        firstattrs = []
        secondattrs = []
        for attrib, value in attrs:
            try:
                getattr(self, attrib)(value)
            except AttributeError:
                print SkinError('[SKIN] Attribute not implemented:"%s" value:"%s"' % (attrib, value))
            except SkinError as ex:
                print '\x1b[91m[Skin] Error:', ex,
                print '\x1b[0m'
            except:
                print SkinError('[Skin] attribute "%s" with wrong (or unknown) value "%s"' % (attrib, value))

            if attrib.lower() == 'font':
                secondattrs.append((0, attrib, value))
            if attrib.lower() == 'size':
                secondattrs.append((1, attrib, value))
            elif attrib.lower() == 'position':
                secondattrs.append((2, attrib, value))
            elif attrib.lower() == 'itemheight':
                secondattrs.append((3, attrib, value))
            elif attrib.lower() == 'itemwidth':
                secondattrs.append((4, attrib, value))
            elif attrib.lower() == 'cursorsize':
                secondattrs.append((5, attrib, value))
            elif attrib.lower() == 'orientation':
                secondattrs.append((6, attrib, value))
            elif attrib.lower() == 'runningstep':
                secondattrs.append((7, attrib, value))
            else:
                firstattrs.append((attrib, value))

        if len(secondattrs) > 0:
            secondattrs.sort(key=lambda x: x[0])
            attrs = firstattrs + [ (attrib, value) for x, attrib, value in secondattrs ]
        for attrib, value in attrs:
            self.applyOne(attrib, value)

    def conditional(self, value):
        pass

    def position(self, value):
        if isinstance(value, tuple):
            self.guiObject.move(ePoint(*value))
        else:
            self.guiObject.move(parsePosition(value, self.scaleTuple, self.guiObject, self.desktop, self.guiObject.csize()))

    def size(self, value):
        if isinstance(value, tuple):
            self.guiObject.resize(eSize(*value))
        else:
            self.guiObject.resize(parseSize(value, self.scaleTuple, self.guiObject, self.desktop))

    def animationPaused(self, value):
        pass

    def NoAnimationAfter(self, value):
        pass

    def Animation(self, value):
        self.guiObject.setAnimationMode({'disable': 0,
         'off': 0,
         'offshow': 16,
         'offhide': 1,
         'onshow': 1,
         'onhide': 16,
         'disable_onshow': 16,
         'disable_onhide': 1}[value])

    def animationMode(self, value):
        self.guiObject.setAnimationMode({'disable': 0,
         'off': 0,
         'offshow': 16,
         'offhide': 1,
         'onshow': 1,
         'onhide': 16}[value])

    def title(self, value):
        global isVTISkin
        if value[:3].lower() == 'vti':
            isVTISkin = True
        self.guiObject.setTitle(_(value))

    def text(self, value):
        self.guiObject.setText(_(value))

    def font(self, value):
        self.guiObject.setFont(parseFont(value, self.scaleTuple))

    def secondfont(self, value):
        self.guiObject.setSecondFont(parseFont(value, self.scaleTuple))

    def zPosition(self, value):
        self.guiObject.setZPosition(int(value))

    def itemHeight(self, value):
        self.guiObject.setItemHeight(int(value))

    def pixmap(self, value):
        ptr = None
        for cvalue, cptr in pngcache:
            if cvalue == value:
                ptr = cptr

        if ptr is None:
            if not fileExists(value):
                ptr = loadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, value), self.desktop)
            else:
                ptr = loadPixmap(value, self.desktop)
        self.guiObject.setPixmap(ptr)
        return

    def backgroundPixmap(self, value):
        ptr = None
        for cvalue, cptr in pngcache:
            if cvalue == value:
                ptr = cptr

        if ptr is None:
            if not fileExists(value):
                ptr = loadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, value), self.desktop)
            else:
                ptr = loadPixmap(value, self.desktop)
        self.guiObject.setBackgroundPicture(ptr)
        return

    def selectionPixmap(self, value):
        ptr = None
        for cvalue, cptr in pngcache:
            if cvalue == value:
                ptr = cptr

        if ptr is None:
            if not fileExists(value):
                ptr = loadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, value), self.desktop)
            else:
                ptr = loadPixmap(value, self.desktop)
        self.guiObject.setSelectionPicture(ptr)
        return

    def sliderPixmap(self, value):
        ptr = None
        for cvalue, cptr in pngcache:
            if cvalue == value:
                ptr = cptr

        if ptr is None:
            if not fileExists(value):
                ptr = loadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, value), self.desktop)
            else:
                ptr = loadPixmap(value, self.desktop)
        self.guiObject.setSliderPicture(ptr)
        return

    def scrollbarbackgroundPixmap(self, value):
        ptr = None
        for cvalue, cptr in pngcache:
            if cvalue == value:
                ptr = cptr

        if ptr is None:
            if not fileExists(value):
                ptr = loadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, value), self.desktop)
            else:
                ptr = loadPixmap(value, self.desktop)
        self.guiObject.setScrollbarBackgroundPicture(ptr)
        return

    def sliderBackground(self, value):
        self.guiObject.setPixmap(loadPixmap(value, self.desktop), self.guiObject.SliderBackground)

    def sliderForeground(self, value):
        self.guiObject.setPixmap(loadPixmap(value, self.desktop), self.guiObject.SliderForeground)

    def sliderPointer(self, value):
        self.guiObject.setPixmap(loadPixmap(value, self.desktop), self.guiObject.SliderPointer)

    def tipTop(self, value):
        self.guiObject.setPixmap(loadPixmap(value, self.desktop), self.guiObject.TipTop)

    def tipBottom(self, value):
        self.guiObject.setPixmap(loadPixmap(value, self.desktop), self.guiObject.TipBottom)

    def tipLeft(self, value):
        self.guiObject.setPixmap(loadPixmap(value, self.desktop), self.guiObject.TipLeft)

    def tipReight(self, value):
        self.guiObject.setPixmap(loadPixmap(value, self.desktop), self.guiObject.TipReight)

    def scrollbarSliderPicture(self, value):
        ptr = None
        for cvalue, cptr in pngcache:
            if cvalue == value:
                ptr = cptr

        if ptr is None:
            if not fileExists(value):
                ptr = loadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, value), self.desktop)
            else:
                ptr = loadPixmap(value, self.desktop)
        self.guiObject.setScrollbarSliderPicture(ptr)
        return

    def scrollbarBackgroundPicture(self, value):
        ptr = None
        for cvalue, cptr in pngcache:
            if cvalue == value:
                ptr = cptr

        if ptr is None:
            if not fileExists(value):
                ptr = loadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, value), self.desktop)
            else:
                ptr = loadPixmap(value, self.desktop)
        self.guiObject.setScrollbarBackgroundPicture(ptr)
        return

    def alphatest(self, value):
        self.guiObject.setAlphatest({'on': 1,
         'off': 0,
         'blend': 2}[value])

    def scale(self, value):
        self.guiObject.setScale(1)

    def orientation(self, value):
        try:
            self.guiObject.setOrientation(*{'orVertical': (self.guiObject.orVertical, False),
             'orTopToBottom': (self.guiObject.orVertical, False),
             'orBottomToTop': (self.guiObject.orVertical, True),
             'orHorizontal': (self.guiObject.orHorizontal, False),
             'orLeftToRight': (self.guiObject.orHorizontal, False),
             'orRightToLeft': (self.guiObject.orHorizontal, True)}[value])
        except KeyError:
            print "[Skin] Orientation must be either Vertical or Horizontal!, not %s. Please contact the skin's author!" % value

    def valign(self, value):
        try:
            self.guiObject.setVAlign({'top': self.guiObject.alignTop,
             'center': self.guiObject.alignCenter,
             'bottom': self.guiObject.alignBottom}[value])
        except KeyError:
            print "[Skin] Valign must be either top, center or bottom!, not %s. Please contact the skin's author!" % value

    def halign(self, value):
        try:
            self.guiObject.setHAlign({'left': self.guiObject.alignLeft,
             'center': self.guiObject.alignCenter,
             'right': self.guiObject.alignRight,
             'block': self.guiObject.alignBlock}[value])
        except KeyError:
            print "[Skin] Halign must be either left, center, right or block!, not %s. Please contact the skin's author!" % value

    def textOffset(self, value):
        if value in variables:
            value = variables[value]
        x, y = value.split(',')
        self.guiObject.setTextOffset(ePoint(int(x) * self.scaleTuple[0][0] / self.scaleTuple[0][1], int(y) * self.scaleTuple[1][0] / self.scaleTuple[1][1]))
        if isVTISkin:
            self.guiObject.setUseVTIWorkaround()

    def flags(self, value):
        if value in variables:
            value = variables[value]
        flags = value.split(',')
        for f in flags:
            try:
                fv = eWindow.__dict__[f]
                self.guiObject.setFlag(fv)
            except KeyError:
                print '[Skin] illegal flag %s!' % f

    def backgroundColor(self, value):
        self.guiObject.setBackgroundColor(parseColor(value))

    def backgroundColorSelected(self, value):
        self.guiObject.setBackgroundColorSelected(parseColor(value))

    def foregroundColor(self, value):
        self.guiObject.setForegroundColor(parseColor(value))

    def foregroundColorSelected(self, value):
        self.guiObject.setForegroundColorSelected(parseColor(value))

    def foregroundNotCrypted(self, value):
        self.guiObject.setForegroundColor(parseColor(value))

    def backgroundNotCrypted(self, value):
        self.guiObject.setBackgroundColor(parseColor(value))

    def foregroundCrypted(self, value):
        self.guiObject.setForegroundColor(parseColor(value))

    def backgroundCrypted(self, value):
        self.guiObject.setBackgroundColor(parseColor(value))

    def foregroundEncrypted(self, value):
        self.guiObject.setForegroundColor(parseColor(value))

    def backgroundEncrypted(self, value):
        self.guiObject.setBackgroundColor(parseColor(value))

    def shadowColor(self, value):
        self.guiObject.setShadowColor(parseColor(value))

    def selectionDisabled(self, value):
        self.guiObject.setSelectionEnable(0)

    def transparent(self, value):
        self.guiObject.setTransparent(int(value))

    def borderColor(self, value):
        self.guiObject.setBorderColor(parseColor(value))

    def borderWidth(self, value):
        self.guiObject.setBorderWidth(int(value))

    def scrollbarSliderBorderWidth(self, value):
        self.guiObject.setScrollbarSliderBorderWidth(int(value))

    def scrollbarWidth(self, value):
        self.guiObject.setScrollbarWidth(int(value))

    def scrollbarSliderBorderColor(self, value):
        self.guiObject.setSliderBorderColor(parseColor(value))

    def scrollbarSliderForegroundColor(self, value):
        self.guiObject.setSliderForegroundColor(parseColor(value))

    def scrollbarMode(self, value):
        self.guiObject.setScrollbarMode(getattr(self.guiObject, value))

    def enableWrapAround(self, value):
        self.guiObject.setWrapAround(True)

    def itemHeight(self, value):
        self.guiObject.setItemHeight(int(value))

    def pointer(self, value):
        name, pos = value.split(':')
        pos = parsePosition(pos, self.scaleTuple)
        ptr = loadPixmap(name, self.desktop)
        self.guiObject.setPointer(0, ptr, pos)

    def seek_pointer(self, value):
        name, pos = value.split(':')
        pos = parsePosition(pos, self.scaleTuple)
        ptr = loadPixmap(name, self.desktop)
        self.guiObject.setPointer(1, ptr, pos)

    def shadowOffset(self, value):
        self.guiObject.setShadowOffset(parsePosition(value, self.scaleTuple))

    def noWrap(self, value):
        self.guiObject.setNoWrap(1)

    def linelength(self, value):
        pass

    def css(self, value):
        styles = value.split(',')
        for style in styles:
            style = style.strip()
            for _attrib in cascadingStyleSheets[style].keys():
                _value = cascadingStyleSheets[style][_attrib]
                self.applyOne(_attrib, _value)

    def sliderLength(self, value):
        pass

    def sliderLengthTip(self, value):
        self.guiObject.setLengthTip(int(value))

    def noWrap(self, value):
        self.guiObject.setNoWrap(1)

    def runningLine(self, value):
        self.guiObject.setRunningLine(int(value))

    def runningList(self, value):
        self.guiObject.setRunningList(int(value))

    def runningCursor(self, value):
        self.guiObject.setRunningCursor(int(value))

    def runningStep(self, value):
        if value[0].lower() == 'x':
            if self.guiObject.getOrientation() == self.guiObject.orHorizontal:
                autoval = self.guiObject.getItemWidth() / (1 + config.skin.runningStep.value)
                print '[Skin] set runningstep: %s->%d H(%dx%d)' % (value,
                 autoval,
                 self.guiObject.getItemWidth(),
                 self.guiObject.getItemHeight())
            else:
                autoval = self.guiObject.getItemHeight() / (1 + config.skin.runningStep.value)
                print '[Skin] set runningstep: %s->%d V(%dx%d)' % (value,
                 autoval,
                 self.guiObject.getItemWidth(),
                 self.guiObject.getItemHeight())
            value = autoval if autoval != 0 else value[1:]
        self.guiObject.setRunningStep(int(value))

    def enableMultilist(self, value):
        self.guiObject.setMultiList(True)

    def id(self, value):
        pass


def applySingleAttribute(guiObject, desktop, attrib, value, scale = ((1, 1), (1, 1))):
    AttributeParser(guiObject, desktop, scale).applyOne(attrib, value)


def applyAllAttributes(guiObject, desktop, attributes, scale):
    AttributeParser(guiObject, desktop, scale).applyAll(attributes)


def loadSingleSkinData(desktop, skin, path_prefix):
    for c in skin.findall('output'):
        id = c.attrib.get('id')
        if id:
            id = int(id)
        else:
            id = 0
        if id == 0:
            for res in c.findall('resolution'):
                get_attr = res.attrib.get
                xres = get_attr('xres')
                if xres:
                    xres = int(xres)
                else:
                    xres = 720
                yres = get_attr('yres')
                if yres:
                    yres = int(yres)
                else:
                    yres = 576
                bpp = get_attr('bpp')
                if bpp:
                    bpp = int(bpp)
                else:
                    bpp = 32
                from enigma import gMainDC
                gMainDC.getInstance().setResolution(xres, yres)
                desktop.resize(eSize(xres, yres))
                if bpp != 32:
                    pass

    for skininclude in skin.findall('include'):
        filename = skininclude.attrib.get('filename')
        if filename:
            skinfile = resolveFilename(SCOPE_ACTIVE_SKIN, filename, path_prefix=path_prefix)
            if not fileExists(skinfile):
                skinfile = resolveFilename(SCOPE_SKIN_IMAGE, filename, path_prefix=path_prefix)
            if fileExists(skinfile):
                print '[Skin] loading include:', skinfile
                loadSkin(skinfile)

    for c in skin.findall('switchpixmap'):
        for pixmap in c.findall('pixmap'):
            get_attr = pixmap.attrib.get
            name = get_attr('name')
            if not name:
                raise SkinError('[Skin] switchpixmap needs name attribute')
            filename = get_attr('filename')
            if not filename:
                raise SkinError('[Skin] switchpixmap needs filename attribute')
            resolved_png = resolveFilename(SCOPE_ACTIVE_SKIN, filename, path_prefix=path_prefix)
            if fileExists(resolved_png):
                switchPixmap[name] = resolved_png
            else:
                raise SkinError('[Skin] switchpixmap pixmap filename="%s" (%s) not found' % (filename, resolved_png))

    for c in skin.findall('cascadingstylesheets'):
        stylename = c.attrib.get('name')
        cascadingStyleSheets[stylename] = dict()
        for pixmap in c.findall('css'):
            get_attr = pixmap.attrib.get
            name = get_attr('name')
            if not name:
                raise SkinError('[Skin] cascadingstylesheets needs name attribute')
            value = get_attr('value')
            if not filename:
                raise SkinError('[Skin] cascadingstylesheets needs value attribute')
            if name in ('pixmap', 'pointer', 'seek_pointer', 'backgroundPixmap', 'selectionPixmap', 'sstartPixmap', 'sbodyPixmap', 'sendPixmap', 'sballPixmap', 'sbackgroundPixmap', 'sliderBackground', 'sliderForeground', 'sliderPointer', 'tipTop', 'tipBottom', 'tipLeft', 'tipReight'):
                value = resolveFilename(SCOPE_ACTIVE_SKIN, value, path_prefix=path_prefix)
            cascadingStyleSheets[stylename][name] = value.encode('utf-8')

    for c in skin.findall('colors'):
        for color in c.findall('color'):
            get_attr = color.attrib.get
            name = get_attr('name')
            color = get_attr('value')
            if name and color:
                colorNames[name] = parseColor(color)
                if color[0] != '#':
                    for key in colorNames:
                        if key == color:
                            colorNamesHuman[name] = colorNamesHuman[key]
                            break

                else:
                    humancolor = color[1:]
                    if len(humancolor) >= 6:
                        colorNamesHuman[name] = int(humancolor, 16)
            else:
                print '[Skin] need color and name, got %s %s' % (name, color)

    for c in skin.findall('fonts'):
        for font in c.findall('font'):
            get_attr = font.attrib.get
            filename = get_attr('filename', '<NONAME>')
            name = get_attr('name', 'Regular')
            scale = get_attr('scale')
            if scale:
                scale = int(scale)
            else:
                scale = 100
            is_replacement = get_attr('replacement') and True or False
            render = get_attr('render')
            if render:
                render = int(render)
            else:
                render = 0
            resolved_font = resolveFilename(SCOPE_FONTS, filename, path_prefix=path_prefix)
            if not fileExists(resolved_font):
                resolved_font = resolveFilename(SCOPE_ACTIVE_SKIN, filename)
                if fileExists(resolveFilename(SCOPE_CURRENT_SKIN, filename)):
                    resolved_font = resolveFilename(SCOPE_CURRENT_SKIN, filename)
                elif fileExists(resolveFilename(SCOPE_ACTIVE_LCDSKIN, filename)):
                    resolved_font = resolveFilename(SCOPE_ACTIVE_LCDSKIN, filename)
            addFont(resolved_font, name, scale, is_replacement, render)

        for alias in c.findall('alias'):
            get = alias.attrib.get
            try:
                name = get('name')
                font = get('font')
                size = int(get('size'))
                height = int(get('height', size))
                width = int(get('width', size))
                fonts[name] = (font,
                 size,
                 height,
                 width)
            except Exception as ex:
                print '[Skin] bad font alias', ex

    for c in skin.findall('parameters'):
        for parameter in c.findall('parameter'):
            get = parameter.attrib.get
            try:
                name = get('name')
                value = get('value')
                if name.find('Font') != -1:
                    font = value.split(';')
                    if isinstance(font, list) and len(font) == 2:
                        parameters[name] = (str(font[0]), int(font[1]))
                else:
                    parameters[name] = map(int, value.split(','))
            except Exception as ex:
                print '[SKIN] bad parameter', ex

    for c in skin.findall('constant-widgets'):
        for constant_widget in c.findall('constant-widget'):
            get = constant_widget.attrib.get
            name = get('name')
            if name:
                constant_widgets[name] = constant_widget

    for c in skin.findall('variables'):
        for parameter in c.findall('variable'):
            get = parameter.attrib.get
            name = get('name')
            value = get('value')
            x, y = value.split(',')
            if value and name:
                variables[name] = str(x) + ',' + str(y)

    for c in skin.findall('subtitles'):
        from enigma import eSubtitleWidget
        scale = ((1, 1), (1, 1))
        for substyle in c.findall('sub'):
            get_attr = substyle.attrib.get
            font = parseFont(get_attr('font'), scale)
            col = get_attr('foregroundColor')
            if col:
                foregroundColor = parseColor(col)
                haveColor = 1
            else:
                foregroundColor = gRGB(16777215)
                haveColor = 0
            col = get_attr('borderColor')
            if col:
                borderColor = parseColor(col)
            else:
                borderColor = gRGB(0)
            borderwidth = get_attr('borderWidth')
            if borderwidth is None:
                borderWidth = 3
            else:
                borderWidth = int(borderwidth)
            face = eSubtitleWidget.__dict__[get_attr('name')]
            eSubtitleWidget.setFontStyle(face, font, haveColor, foregroundColor, borderColor, borderWidth)

    for windowstyle in skin.findall('windowstyle'):
        style = eWindowStyleSkinned()
        style_id = windowstyle.attrib.get('id')
        if style_id:
            style_id = int(style_id)
        else:
            style_id = 0
        font = gFont('Regular', 20)
        offset = eSize(20, 5)
        for title in windowstyle.findall('title'):
            get_attr = title.attrib.get
            offset = parseSize(get_attr('offset'), ((1, 1), (1, 1)))
            font = parseFont(get_attr('font'), ((1, 1), (1, 1)))

        style.setTitleFont(font)
        style.setTitleOffset(offset)
        for borderset in windowstyle.findall('borderset'):
            bsName = str(borderset.attrib.get('name'))
            for pixmap in borderset.findall('pixmap'):
                get_attr = pixmap.attrib.get
                bpName = get_attr('pos')
                filename = get_attr('filename')
                if filename and bpName:
                    pngfile = resolveFilename(SCOPE_ACTIVE_SKIN, filename, path_prefix=path_prefix)
                    if fileExists(resolveFilename(SCOPE_SKIN_IMAGE, filename, path_prefix=path_prefix)):
                        pngfile = resolveFilename(SCOPE_SKIN_IMAGE, filename, path_prefix=path_prefix)
                    png = loadPixmap(pngfile, desktop)
                    style.setPixmap(eWindowStyleSkinned.__dict__[bsName], eWindowStyleSkinned.__dict__[bpName], png)

        for color in windowstyle.findall('color'):
            get_attr = color.attrib.get
            colorType = get_attr('name')
            color = parseColor(get_attr('color'))
            try:
                style.setColor(eWindowStyleSkinned.__dict__['col' + colorType], color)
            except:
                raise SkinError('Unknown color %s' % colorType)

        x = eWindowStyleManager.getInstance()
        x.setStyle(style_id, style)

    for margin in skin.findall('margin'):
        style_id = margin.attrib.get('id')
        if style_id:
            style_id = int(style_id)
        else:
            style_id = 0
        r = eRect(0, 0, 0, 0)
        v = margin.attrib.get('left')
        if v:
            r.setLeft(int(v))
        v = margin.attrib.get('top')
        if v:
            r.setTop(int(v))
        v = margin.attrib.get('right')
        if v:
            r.setRight(int(v))
        v = margin.attrib.get('bottom')
        if v:
            r.setBottom(int(v))
        getDesktop(style_id).setMargins(r)

    return


dom_screens = {}

def loadSkin(name, scope = SCOPE_SKIN):
    global display_skin_id
    global dom_screens
    filename = resolveFilename(scope, name)
    if fileExists(filename):
        path = os.path.dirname(filename) + '/'
        file = open(filename, 'r')
        for elem in xml.etree.cElementTree.parse(file).getroot():
            if elem.tag == 'screen':
                name = elem.attrib.get('name', None)
                if name:
                    sid = elem.attrib.get('id', None)
                    if sid and sid != display_skin_id:
                        elem.clear()
                        continue
                    if name in dom_screens:
                        dom_screens[name][0].clear()
                    dom_screens[name] = (elem, path)
                else:
                    elem.clear()
            else:
                elem.clear()

        file.close()
    return


def loadSkinData(desktop):
    global dom_skins
    skins = dom_skins[:]
    skins.reverse()
    for path, dom_skin in skins:
        loadSingleSkinData(desktop, dom_skin, path)
        for elem in dom_skin:
            if elem.tag == 'screen':
                name = elem.attrib.get('name', None)
                if name:
                    sid = elem.attrib.get('id', None)
                    if sid and sid != display_skin_id:
                        elem.clear()
                        continue
                    if name in dom_screens:
                        dom_screens[name][0].clear()
                    dom_screens[name] = (elem, path)
                else:
                    elem.clear()
            else:
                elem.clear()

    del dom_skins
    return


class additionalWidget():

    def __init__(self):
        pass


class SizeTuple(tuple):

    def split(self, *args):
        return (str(self[0]), str(self[1]))

    def strip(self, *args):
        return '%s,%s' % self

    def __str__(self):
        return '%s,%s' % self


class SkinContext():

    def __init__(self, parent = None, pos = None, size = None, font = None):
        if parent is not None:
            if pos is not None:
                pos, size = parent.parse(pos, size, font)
                self.x, self.y = pos
                self.w, self.h = size
            else:
                self.x = None
                self.y = None
                self.w = None
                self.h = None
        return

    def __str__(self):
        return 'Context (%s,%s)+(%s,%s) ' % (self.x,
         self.y,
         self.w,
         self.h)

    def parse(self, pos, size, font):
        if size in variables:
            size = variables[size]
        if pos == 'fill':
            pos = (self.x, self.y)
            size = (self.w, self.h)
            self.w = 0
            self.h = 0
        else:
            w, h = size.split(',')
            w = parseCoordinate(w, self.w, 0, font)
            h = parseCoordinate(h, self.h, 0, font)
            if pos == 'bottom':
                pos = (self.x, self.y + self.h - h)
                size = (self.w, h)
                self.h -= h
            elif pos == 'top':
                pos = (self.x, self.y)
                size = (self.w, h)
                self.h -= h
                self.y += h
            elif pos == 'left':
                pos = (self.x, self.y)
                size = (w, self.h)
                self.x += w
                self.w -= w
            elif pos == 'right':
                pos = (self.x + self.w - w, self.y)
                size = (w, self.h)
                self.w -= w
            else:
                if pos in variables:
                    pos = variables[pos]
                size = (w, h)
                pos = pos.split(',')
                pos = (self.x + parseCoordinate(pos[0], self.w, size[0], font), self.y + parseCoordinate(pos[1], self.h, size[1], font))
        return (SizeTuple(pos), SizeTuple(size))


class SkinContextStack(SkinContext):

    def parse(self, pos, size, font):
        if pos == 'fill':
            pos = (self.x, self.y)
            size = (self.w, self.h)
        else:
            w, h = size.split(',')
            w = parseCoordinate(w, self.w, 0, font)
            h = parseCoordinate(h, self.h, 0, font)
            if pos == 'bottom':
                pos = (self.x, self.y + self.h - h)
                size = (self.w, h)
            elif pos == 'top':
                pos = (self.x, self.y)
                size = (self.w, h)
            elif pos == 'left':
                pos = (self.x, self.y)
                size = (w, self.h)
            elif pos == 'right':
                pos = (self.x + self.w - w, self.y)
                size = (w, self.h)
            else:
                if pos in variables:
                    pos = variables[pos]
                size = (w, h)
                pos = pos.split(',')
                pos = (self.x + parseCoordinate(pos[0], self.w, size[0], font), self.y + parseCoordinate(pos[1], self.h, size[1], font))
        return (SizeTuple(pos), SizeTuple(size))


def readSkin(screen, skin, names, desktop):
    if not isinstance(names, list):
        names = [names]
    for n in names:
        myscreen, path = dom_screens.get(n, (None, None))
        if myscreen is not None:
            name = n
            break
    else:
        name = "<embedded-in-'%s'>" % screen.__class__.__name__

    if myscreen is None:
        myscreen = getattr(screen, 'parsedSkin', None)
    if myscreen is None and getattr(screen, 'skin', None):
        skin = screen.skin
        print '[Skin] Parsing embedded skin', name
        if isinstance(skin, tuple):
            for s in skin:
                candidate = xml.etree.cElementTree.fromstring(s)
                if candidate.tag == 'screen':
                    sid = candidate.attrib.get('id', None)
                    if not sid or int(sid) == display_skin_id:
                        myscreen = candidate
                        break
            else:
                print '[Skin] Hey, no suitable screen!'

        else:
            myscreen = xml.etree.cElementTree.fromstring(skin)
        if myscreen:
            screen.parsedSkin = myscreen
    if myscreen is None:
        print '[Skin] No skin to read...'
        myscreen = screen.parsedSkin = xml.etree.cElementTree.fromstring('<screen></screen>')
    screen.skinAttributes = []
    skin_path_prefix = getattr(screen, 'skin_path', path)
    context = SkinContextStack()
    s = desktop.bounds()
    context.x = s.left()
    context.y = s.top()
    context.w = s.width()
    context.h = s.height()
    del s
    collectAttributes(screen.skinAttributes, myscreen, context, skin_path_prefix, ignore=('name',))
    context = SkinContext(context, myscreen.attrib.get('position'), myscreen.attrib.get('size'))
    screen.additionalWidgets = []
    screen.renderer = []
    visited_components = set()

    def process_constant_widget(constant_widget, context):
        get_attr = constant_widget.attrib.get
        wname = get_attr('name')
        if wname:
            try:
                cwvalue = constant_widgets[wname]
            except KeyError:
                if config.crash.skin_error_crash.value:
                    raise SkinError("[SKIN] ERROR - given constant-widget: '%s' not found in skin" % wname)
                else:
                    print "\x1b[91m[SKIN] ERROR - given constant-widget: '%s' not found in skin\x1b[0m" % wname
                    return

        if cwvalue:
            for x in cwvalue:
                myscreen.append(x)

        try:
            myscreen.remove(constant_widget)
        except ValueError:
            pass

    def process_none(widget, context):
        pass

    def process_widget(widget, context):
        get_attr = widget.attrib.get
        wname = get_attr('name')
        wsource = get_attr('source')
        if wname is None and wsource is None:
            print '[Skin] widget has no name and no source!'
            return
        else:
            if wname and wsource is None:
                visited_components.add(wname)
                try:
                    attributes = screen[wname].skinAttributes = []
                except:
                    raise SkinError("[Skin] component with name '" + wname + "' was not found in skin of screen '" + name + "'!")

                collectAttributes(attributes, widget, context, skin_path_prefix, ignore=('name',))
            elif wsource:
                while True:
                    scr = screen
                    path = wsource.split('.')
                    while len(path) > 1:
                        scr = screen.getRelatedScreen(path[0])
                        if scr is None:
                            raise SkinError("[Skin] specified related screen '" + wsource + "' was not found in screen '" + name + "'!")
                        path = path[1:]

                    source = scr.get(path[0])
                    if isinstance(source, ObsoleteSource):
                        print "[Skin] WARNING: SKIN '%s' USES OBSOLETE SOURCE '%s', USE '%s' INSTEAD!" % (name, wsource, source.new_source)
                        print '[Skin] OBSOLETE SOURCE WILL BE REMOVED %s, PLEASE UPDATE!' % source.removal_date
                        if source.description:
                            print source.description
                        wsource = source.new_source
                    else:
                        break

                if source is None:
                    if config.crash.skin_error_crash.value:
                        raise SkinError("source '" + wsource + "' was not found in screen '" + name + "'!")
                    else:
                        print "\x1b[91m[Skin] Error: Source '" + wsource + "' was not found in screen '" + name + "'!"
                wrender = get_attr('render')
                if not wrender:
                    raise SkinError("[Skin] you must define a renderer with render= for source '%s'" % wsource)
                sub_source_list = []
                for converter in widget.findall('convert'):
                    ctype = converter.get('type')
                    try:
                        parms = converter.text.strip()
                    except:
                        parms = ''

                    converter_class = my_import('.'.join(('Components', 'Converter', ctype))).__dict__.get(ctype)
                    sub_source = converter.get('source')
                    if sub_source is None:
                        c = None
                        for i in source.downstream_elements:
                            if isinstance(i, converter_class) and i.converter_arguments == parms:
                                c = i

                        if c is None:
                            c = converter_class(parms)
                            if len(sub_source_list) == 0:
                                c.connect(source)
                            else:
                                for source in sub_source_list:
                                    c.connect(source)

                                sub_source_list = []
                        source = c
                    else:
                        wsource = sub_source
                        while True:
                            scr = screen
                            path = wsource.split('.')
                            while len(path) > 1:
                                scr = screen.getRelatedScreen(path[0])
                                if scr is None:
                                    raise SkinError("[Skin] specified related screen '" + wsource + "' was not found in screen '" + name + "'!")
                                path = path[1:]

                            ssource = scr.get(path[0])
                            if isinstance(ssource, ObsoleteSource):
                                print "[Skin] WARNING: SKIN '%s' USES OBSOLETE SOURCE '%s', USE '%s' INSTEAD!" % (name, wsource, ssource.new_source)
                                print 'OBSOLETE SOURCE WILL BE REMOVED %s, PLEASE UPDATE!' % ssource.removal_date
                                if ssource.description:
                                    print ssource.description
                                wsource = ssource.new_source
                            else:
                                break

                        c = None
                        for i in ssource.downstream_elements:
                            if isinstance(i, converter_class) and i.converter_arguments == parms:
                                c = i

                        if c is None:
                            c = converter_class(parms)
                            c.connect(ssource)
                        sub_source_list.append(c)

                try:
                    renderer_class = my_import('.'.join(('Components', 'Renderer', wrender))).__dict__.get(wrender)
                except ImportError:
                    if config.crash.skin_error_crash.value:
                        raise SkinError("[Skin] Error: Renderer '%s' not found" % wrender)
                    else:
                        print "\x1b[91m[Skin] Error: Renderer '%s' not found\x1b[0m" % wrender
                        return

                renderer = renderer_class()
                renderer.connect(source)
                renderer.name = wname
                attributes = renderer.skinAttributes = []
                collectAttributes(attributes, widget, context, skin_path_prefix, ignore=('render', 'source', 'name'))
                screen.renderer.append(renderer)
            return
            return

    def process_applet(widget, context):
        try:
            codeText = widget.text.strip()
            widgetType = widget.attrib.get('type')
            code = compile(codeText, 'skin applet', 'exec')
        except Exception as ex:
            raise SkinError('[Skin] applet failed to compile: ' + str(ex))

        if widgetType == 'onLayoutFinish':
            screen.onLayoutFinish.append(code)
        elif widgetType == 'onShow':
            screen.onShowCode.append(code)
        elif widgetType == 'onHide':
            screen.onHideCode.append(code)
        else:
            raise SkinError("[Skin] applet type '%s' unknown!" % widgetType)

    def process_elabel(widget, context):
        w = additionalWidget()
        w.widget = eLabel
        w.skinAttributes = []
        collectAttributes(w.skinAttributes, widget, context, skin_path_prefix, ignore=('name',))
        screen.additionalWidgets.append(w)

    def process_epixmap(widget, context):
        w = additionalWidget()
        w.widget = ePixmap
        w.skinAttributes = []
        collectAttributes(w.skinAttributes, widget, context, skin_path_prefix, ignore=('name',))
        screen.additionalWidgets.append(w)

#    def process_ecursor(widget, context):
#        w = additionalWidget()
#        w.widget = eCursor
#        w.skinAttributes = []
#        collectAttributes(w.skinAttributes, widget, context, skin_path_prefix, ignore=('name',))
#        screen.additionalWidgets.append(w)

#    def process_eframe(widget, context):
#        w = additionalWidget()
#        w.widget = eFrame
#        w.skinAttributes = []
#        collectAttributes(w.skinAttributes, widget, context, skin_path_prefix, ignore=('name',))
#        screen.additionalWidgets.append(w)

#    def process_ebar(widget, context):
#        w = additionalWidget()
#        w.widget = eBar
#        w.skinAttributes = []
#        collectAttributes(w.skinAttributes, widget, context, skin_path_prefix, ignore=('name',))
#        screen.additionalWidgets.append(w)

    def process_screen(widget, context):

        def process(w):
            conditional = w.attrib.get('conditional')
            if conditional and not [ i for i in conditional.split(',') if i in screen.keys() ]:
                return
            p = processors.get(w.tag, process_none)
            try:
                p(w, context)
            except SkinError as e:
                print "[SKIN] SKIN ERROR in screen '%s' widget '%s':" % (name, w.tag), e

        cw = widget.findall('constant-widget')
        if cw:
            for w in cw:
                process(w)

            for w in myscreen.findall('widget'):
                process(w)

        for w in widget.getchildren():
            if cw and w.tag in ('constant-widget', 'widget'):
                continue
            process(w)

    def process_panel(widget, context):
        n = widget.attrib.get('name')
        if n:
            try:
                s = dom_screens.get(n, None)
                if s is None:
                    print "[SKIN] Unable to find screen '%s' referred in screen '%s'" % (n, name)
                    return
            except KeyError:
                print "[SKIN] Unable to find screen '%s' referred in screen '%s'" % (n, name)
            else:
                process_screen(s[0], context)

        layout = widget.attrib.get('layout')
        if layout == 'stack':
            cc = SkinContextStack
        else:
            cc = SkinContext
        try:
            c = cc(context, widget.attrib.get('position'), widget.attrib.get('size'), widget.attrib.get('font'))
        except Exception as ex:
            raise SkinError('Failed to create skincontext (%s,%s,%s) in %s: %s' % (widget.attrib.get('position'),
             widget.attrib.get('size'),
             widget.attrib.get('font'),
             context,
             ex))

        process_screen(widget, c)
        return

    processors = {None: process_none,
     'constant-widget': process_constant_widget,
     'widget': process_widget,
     'applet': process_applet,
     'eLabel': process_elabel,
     'ePixmap': process_epixmap,
#     'eCursor': process_ecursor,
#     'eFrame': process_eframe,
#     'eBar': process_ebar,
     'panel': process_panel}
    try:
        print '[SKIN] processing screen %s:' % name
        context.x = 0
        context.y = 0
        process_screen(myscreen, context)
    except Exception as e:
        print '[SKIN] SKIN ERROR in %s:' % name, e

    from Components.GUIComponent import GUIComponent
    nonvisited_components = [ x for x in set(screen.keys()) - visited_components if isinstance(x, GUIComponent) ]
    screen = None
    visited_components = None
    return


def parseAvailableSkinColor(color):
    if color in colorNamesHuman:
        return colorNamesHuman[color]
    else:
        print 'color %s ist not available at used skin' % color
        return None
