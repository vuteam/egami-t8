from re import compile as re_compile
from os import path as os_path, listdir
from Components.MenuList import MenuList
from Components.Harddisk import harddiskmanager
from Tools.Directories import SCOPE_CURRENT_SKIN, resolveFilename, fileExists
from enigma import RT_HALIGN_LEFT, eListboxPythonMultiContent, eServiceReference, eServiceCenter, gFont, getDesktop
from Tools.LoadPixmap import LoadPixmap
from os import listdir, remove, rename, system, path, symlink, chdir
from os.path import splitext
import re
import os
EXTENSIONS = {'m4a': 'music',
 'mp2': 'music',
 'mp3': 'music',
 'wav': 'music',
 'wma': 'music',
 'ogg': 'music',
 'flac': 'music',
 'dts': 'dts',
 'jpg': 'picture',
 'jpeg': 'picture',
 'png': 'picture',
 'bmp': 'picture',
 'ts': 'movie',
 'avi': 'movie',
 'divx': 'movie',
 'm4v': 'movie',
 'mpg': 'movie',
 'mpeg': 'movie',
 'mkv': 'movie',
 'mp4': 'movie',
 'mov': 'movie',
 'flv': 'movie',
 'm2ts': 'movie',
 'mts': 'movie',
 'wmv': 'movie',
 '3gp': 'movie',
 '3g2': 'movie',
 'txt': 'txt',
 'conf': 'txt',
 'cfg': 'txt',
 'srt': 'txt',
 'py': 'py',
 'sh': 'sh',
 'html': 'html',
 'xml': 'xml',
 'cfg': 'cfg',
 'lst': 'lst',
 'ipk': 'ipk',
 'zip': 'zip',
 'tar': 'tar',
 'tgz': 'tar',
 'gz': 'gz',
 'rar': 'rar'}

def getPNGByExt(name):
    screenwidth = getDesktop(0).size().width()
    basename, ext = splitext(name)
    if ext.startswith('.'):
        ext = ext[1:]
    if ext == 'gz':
        _, ex = splitext(basename)
        if ex == '.tar':
            ext = 'tgz'
    elif re.match('^r\\d+$', ext):
        ext = 'rar'
    imgpath = '/usr/lib/enigma2/python/Plugins/Extensions/FileCommander/images/'
    if screenwidth and screenwidth == 1920:
        imgpath = '/usr/lib/enigma2/python/Plugins/Extensions/FileCommander/imageshd/'
    if ext in EXTENSIONS:
        return LoadPixmap(cached=True, path=imgpath + EXTENSIONS[ext] + '.png')
    else:
        return LoadPixmap(cached=True, path=imgpath + 'file.png')


def FileEntryComponent(name, absolute = None, isDir = False, isLink = False):
    screenwidth = getDesktop(0).size().width()
    res = [(absolute, isDir, isLink)]
    imgpath = '/usr/lib/enigma2/python/Plugins/Extensions/FileCommander/images/'
    if screenwidth and screenwidth == 1920:
        imgpath = '/usr/lib/enigma2/python/Plugins/Extensions/FileCommander/imageshd/'
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         55,
         5,
         1175,
         50,
         0,
         RT_HALIGN_LEFT,
         name))
    else:
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         55,
         1,
         1175,
         35,
         0,
         RT_HALIGN_LEFT,
         name))
    if isDir and not isLink:
        png = LoadPixmap(cached=True, path=imgpath + 'directory.png')
    elif isLink:
        png = LoadPixmap(cached=True, path=imgpath + 'link.png')
    else:
        png = getPNGByExt(name)
    if png is not None:
        if screenwidth and screenwidth == 1920:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
             10,
             5,
             35,
             35,
             png))
        else:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
             10,
             4,
             20,
             20,
             png))
    return res


class FileList(MenuList):

    def __init__(self, directory, showDirectories = True, showFiles = True, showMountpoints = True, matchingPattern = None, useServiceRef = False, inhibitDirs = False, inhibitMounts = False, isTop = False, enableWrapAround = False, additionalExtensions = None):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.additional_extensions = additionalExtensions
        self.mountpoints = []
        self.current_directory = None
        self.current_mountpoint = None
        self.useServiceRef = useServiceRef
        self.showDirectories = showDirectories
        self.showMountpoints = showMountpoints
        self.showFiles = showFiles
        self.isTop = isTop
        self.matchingPattern = matchingPattern
        self.inhibitDirs = inhibitDirs or []
        self.inhibitMounts = inhibitMounts or []
        self.refreshMountpoints()
        self.changeDir(directory)
        screenwidth = getDesktop(0).size().width()
        if screenwidth and screenwidth == 1920:
            self.l.setFont(0, gFont('Regular', 28))
            self.l.setItemHeight(50)
        else:
            self.l.setFont(0, gFont('Regular', 20))
            self.l.setItemHeight(25)
        self.serviceHandler = eServiceCenter.getInstance()
        return

    def refreshMountpoints(self):
        self.mountpoints = [ os_path.join(p.mountpoint, '') for p in harddiskmanager.getMountedPartitions() ]
        self.mountpoints.sort(reverse=True)

    def getMountpoint(self, file):
        file = os_path.join(os_path.realpath(file), '')
        for m in self.mountpoints:
            if file.startswith(m):
                return m

        return False

    def getMountpointLink(self, file):
        if os_path.realpath(file) == file:
            return self.getMountpoint(file)
        else:
            if file[-1] == '/':
                file = file[:-1]
            mp = self.getMountpoint(file)
            last = file
            file = os_path.dirname(file)
            while last != '/' and mp == self.getMountpoint(file):
                last = file
                file = os_path.dirname(file)

            return os_path.join(last, '')

    def getSelection(self):
        if self.l.getCurrentSelection() is None:
            return
        else:
            return self.l.getCurrentSelection()[0]

    def getCurrentEvent(self):
        l = self.l.getCurrentSelection()
        if not l or l[0][1]:
            return None
        else:
            return self.serviceHandler.info(l[0][0]).getEvent(l[0][0])
            return None

    def getFileList(self):
        return self.list

    def inParentDirs(self, dir, parents):
        dir = os_path.realpath(dir)
        for p in parents:
            if dir.startswith(p):
                return True

        return False

    def changeDir(self, directory, select = None):
        self.list = []
        if self.current_directory is None:
            if directory and self.showMountpoints:
                self.current_mountpoint = self.getMountpointLink(directory)
            else:
                self.current_mountpoint = None
        self.current_directory = directory
        directories = []
        files = []
        if directory is None and self.showMountpoints:
            for p in harddiskmanager.getMountedPartitions():
                path = os_path.join(p.mountpoint, '')
                if path not in self.inhibitMounts and not self.inParentDirs(path, self.inhibitDirs):
                    self.list.append(FileEntryComponent(name=p.description, absolute=path, isDir=True, isLink=False))

            files = []
            directories = []
        elif directory is None:
            files = []
            directories = []
        elif self.useServiceRef:
            root = eServiceReference('2:0:1:0:0:0:0:0:0:0:' + directory)
            if self.additional_extensions:
                root.setName(self.additional_extensions)
            serviceHandler = eServiceCenter.getInstance()
            list = serviceHandler.list(root)
            while 1:
                s = list.getNext()
                if not s.valid():
                    del list
                    break
                if s.flags & s.mustDescent:
                    directories.append(s.getPath())
                else:
                    files.append(s)

            directories.sort()
            files.sort()
        elif fileExists(directory):
            try:
                files = listdir(directory)
            except:
                files = []

            files.sort()
            tmpfiles = files[:]
            for x in tmpfiles:
                if os_path.isdir(directory + x):
                    directories.append(directory + x + '/')
                    files.remove(x)

        if directory is not None and self.showDirectories and not self.isTop:
            if directory == self.current_mountpoint and self.showMountpoints:
                self.list.append(FileEntryComponent(name='<' + _('List of Storage Devices') + '>', absolute=None, isDir=True, isLink=False))
            elif directory != '/' and not (self.inhibitMounts and self.getMountpoint(directory) in self.inhibitMounts):
                self.list.append(FileEntryComponent(name='<' + _('Parent Directory') + '>', absolute='/'.join(directory.split('/')[:-2]) + '/', isDir=True, isLink=False))
        if self.showDirectories:
            for x in directories:
                if not (self.inhibitMounts and self.getMountpoint(x) in self.inhibitMounts) and not self.inParentDirs(x, self.inhibitDirs):
                    name = x.split('/')[-2]
                    testname = x[:-1]
                    if os_path.islink(testname):
                        self.list.append(FileEntryComponent(name=name, absolute=x, isDir=True, isLink=True))
                    else:
                        self.list.append(FileEntryComponent(name=name, absolute=x, isDir=True, isLink=False))

        if self.showFiles:
            for x in files:
                if self.useServiceRef:
                    path = x.getPath()
                    name = path.split('/')[-1]
                else:
                    path = directory + x
                    name = x
                if self.matchingPattern is None or re_compile(self.matchingPattern).search(path):
                    self.list.append(FileEntryComponent(name=name, absolute=x, isDir=False, isLink=False))

        if self.showMountpoints and len(self.list) == 0:
            self.list.append(FileEntryComponent(name=_('nothing connected'), absolute=None, isDir=False, isLink=False))
        self.l.setList(self.list)
        if select is not None:
            i = 0
            self.moveToIndex(0)
            for x in self.list:
                p = x[0][0]
                if isinstance(p, eServiceReference):
                    p = p.getPath()
                if p == select:
                    self.moveToIndex(i)
                i += 1 

    def getCurrentDirectory(self):
        return self.current_directory

    def canDescent(self):
        if self.getSelection() is None:
            return False
        else:
            return self.getSelection()[1]

    def descent(self):
        if self.getSelection() is None:
            return
        else:
            self.changeDir(self.getSelection()[0], select=self.current_directory)
            return

    def getFilename(self):
        if self.getSelection() is None:
            return
        else:
            x = self.getSelection()[0]
            if isinstance(x, eServiceReference):
                x = x.getPath()
            return x

    def getServiceRef(self):
        if self.getSelection() is None:
            return
        else:
            x = self.getSelection()[0]
            if isinstance(x, eServiceReference):
                return x
            return

    def execBegin(self):
        harddiskmanager.on_partition_list_change.append(self.partitionListChanged)

    def execEnd(self):
        harddiskmanager.on_partition_list_change.remove(self.partitionListChanged)

    def refresh(self):
        self.changeDir(self.current_directory, self.getFilename())

    def partitionListChanged(self, action, device):
        self.refreshMountpoints()
        if self.current_directory is None:
            self.refresh()
        return

    def getSelectionID(self):
        idx = self.l.getCurrentSelectionIndex()
        return idx


def MultiFileSelectEntryComponent(name, absolute = None, isDir = False, isLink = False, selected = False):
    screenwidth = getDesktop(0).size().width()
    imgpath = '/usr/lib/enigma2/python/Plugins/Extensions/FileCommander/images/'
    if screenwidth and screenwidth == 1920:
        imgpath = '/usr/lib/enigma2/python/Plugins/Extensions/FileCommander/imageshd/'
    res = [(absolute,
      isDir,
      isLink,
      selected,
      name)]
    res.append((eListboxPythonMultiContent.TYPE_TEXT,
     55,
     1,
     1175,
     25,
     0,
     RT_HALIGN_LEFT,
     name))
    if isDir and not isLink:
        png = LoadPixmap(cached=True, path=imgpath + 'directory.png')
    elif isLink:
        png = LoadPixmap(cached=True, path=imgpath + 'link.png')
    else:
        png = getPNGByExt(name)
    if png is not None:
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST,
         30,
         4,
         20,
         20,
         png))
    if not name.startswith('<'):
        if selected is False:
            icon = LoadPixmap(cached=True, path=imgpath + 'lock_off.png')
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST,
             4,
             0,
             25,
             25,
             icon))
        else:
            icon = LoadPixmap(cached=True, path=imgpath + 'lock_on.png')
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST,
             4,
             0,
             25,
             25,
             icon))
    return res


class MultiFileSelectList(FileList):

    def __init__(self, preselectedFiles, directory, showMountpoints = False, matchingPattern = None, showDirectories = True, showFiles = True, useServiceRef = False, inhibitDirs = False, inhibitMounts = False, isTop = False, enableWrapAround = False, additionalExtensions = None):
        self.selectedFiles = preselectedFiles
        if self.selectedFiles is None:
            self.selectedFiles = []
        FileList.__init__(self, directory, showMountpoints=showMountpoints, matchingPattern=matchingPattern, showDirectories=showDirectories, showFiles=showFiles, useServiceRef=useServiceRef, inhibitDirs=inhibitDirs, inhibitMounts=inhibitMounts, isTop=isTop, enableWrapAround=enableWrapAround, additionalExtensions=additionalExtensions)
        self.changeDir(directory)
        screenwidth = getDesktop(0).size().width()
        if screenwidth and screenwidth == 1920:
            self.l.setFont(0, gFont('Regular', 28))
            self.l.setItemHeight(50)
        else:
            self.l.setFont(0, gFont('Regular', 20))
            self.l.setItemHeight(25)
        self.onSelectionChanged = []
        return

    def selectionChanged(self):
        for f in self.onSelectionChanged:
            f()

    def changeSelectionState(self):
        idx = self.l.getCurrentSelectionIndex()
        count = 0
        newList = []
        for x in self.list:
            if idx == count:
                if x[0][4].startswith('<'):
                    newList.append(x)
                else:
                    if x[0][1] is True:
                        realPathname = x[0][0]
                    else:
                        realPathname = self.current_directory + x[0][0]
                    if x[0][3] is True:
                        SelectState = False
                        for entry in self.selectedFiles:
                            if entry == realPathname:
                                self.selectedFiles.remove(entry)

                    else:
                        SelectState = True
                        alreadyinList = False
                        for entry in self.selectedFiles:
                            if entry == realPathname:
                                alreadyinList = True

                        if not alreadyinList:
                            self.selectedFiles.append(realPathname)
                    newList.append(MultiFileSelectEntryComponent(name=x[0][4], absolute=x[0][0], isDir=x[0][1], isLink=x[0][2], selected=SelectState))
            else:
                newList.append(x)
            count += 1

        self.list = newList
        self.l.setList(self.list)

    def getSelectedList(self):
        return self.selectedFiles

    def changeDir(self, directory, select = None):
        self.list = []
        if self.current_directory is None:
            if directory and self.showMountpoints:
                self.current_mountpoint = self.getMountpointLink(directory)
            else:
                self.current_mountpoint = None
        self.current_directory = directory
        directories = []
        files = []
        if directory is None and self.showMountpoints:
            for p in harddiskmanager.getMountedPartitions():
                path = os_path.join(p.mountpoint, '')
                if path not in self.inhibitMounts and not self.inParentDirs(path, self.inhibitDirs):
                    self.list.append(MultiFileSelectEntryComponent(name=p.description, absolute=path, isDir=True))

            files = []
            directories = []
        elif directory is None:
            files = []
            directories = []
        elif self.useServiceRef:
            root = eServiceReference('2:0:1:0:0:0:0:0:0:0:' + directory)
            if self.additional_extensions:
                root.setName(self.additional_extensions)
            serviceHandler = eServiceCenter.getInstance()
            list = serviceHandler.list(root)
            while 1:
                s = list.getNext()
                if not s.valid():
                    del list
                    break
                if s.flags & s.mustDescent:
                    directories.append(s.getPath())
                else:
                    files.append(s)

            directories.sort()
            files.sort()
        elif fileExists(directory):
            try:
                files = listdir(directory)
            except:
                files = []

            files.sort()
            tmpfiles = files[:]
            for x in tmpfiles:
                if os_path.isdir(directory + x):
                    directories.append(directory + x + '/')
                    files.remove(x)

        if directory is not None and self.showDirectories and not self.isTop:
            if directory == self.current_mountpoint and self.showMountpoints:
                self.list.append(MultiFileSelectEntryComponent(name='<' + _('List of Storage Devices') + '>', absolute=None, isDir=True))
            elif directory != '/' and not (self.inhibitMounts and self.getMountpoint(directory) in self.inhibitMounts):
                self.list.append(MultiFileSelectEntryComponent(name='<' + _('Parent Directory') + '>', absolute='/'.join(directory.split('/')[:-2]) + '/', isDir=True))
        if self.showDirectories:
            for x in directories:
                if not (self.inhibitMounts and self.getMountpoint(x) in self.inhibitMounts) and not self.inParentDirs(x, self.inhibitDirs):
                    name = x.split('/')[-2]
                    alreadySelected = False
                    testname = x[:-1]
                    if os_path.islink(testname):
                        my_isLink = True
                    else:
                        my_isLink = False
                    for entry in self.selectedFiles:
                        if entry == x:
                            alreadySelected = True

                    if alreadySelected:
                        self.list.append(MultiFileSelectEntryComponent(name=name, absolute=x, isDir=True, isLink=my_isLink, selected=True))
                    else:
                        self.list.append(MultiFileSelectEntryComponent(name=name, absolute=x, isDir=True, isLink=my_isLink, selected=False))

        if self.showFiles:
            for x in files:
                if self.useServiceRef:
                    path = x.getPath()
                    name = path.split('/')[-1]
                else:
                    path = directory + x
                    name = x
                if self.matchingPattern is None or re_compile(self.matchingPattern).search(path):
                    alreadySelected = False
                    for entry in self.selectedFiles:
                        if os_path.basename(entry) == x:
                            alreadySelected = True

                    if alreadySelected:
                        self.list.append(MultiFileSelectEntryComponent(name=name, absolute=x, isDir=False, selected=True))
                    else:
                        self.list.append(MultiFileSelectEntryComponent(name=name, absolute=x, isDir=False, selected=False))

        self.l.setList(self.list)
        if select is not None:
            i = 0
            self.moveToIndex(0)
            for x in self.list:
                p = x[0][0]
                if isinstance(p, eServiceReference):
                    p = p.getPath()
                if p == select:
                    self.moveToIndex(i)
                i += 1
