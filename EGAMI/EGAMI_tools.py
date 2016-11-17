from boxbranding import getMachineBuild, getBoxType
from Screens.TaskView import JobView
from Components.About import about
from Components.Task import Task, Job, job_manager, Condition
from Components.config import config, configfile
from Tools.Directories import fileExists
from Tools.Downloader import downloadWithProgress
from enigma import eConsoleAppContainer
import re, string
import os
from socket import *
import socket

def catalogXmlUrl():
    if getBoxType() in ('vusolose', 'vuzero', 'vuuno', 'vusolo', 'vusolo2', 'vuultimo', 'vuduo', 'vuduo2'):
        url = 'http://sodo13.zz.mu/plugins/catalog_enigma2_new.xml'
    else:
        url = 'http://enigma-spark.com/egami/catalog_enigma2.xml'
    return url

def getStbArch():
    if about.getChipSetString() in ('7366', '7376', '5272s', '7252', '7251', '7251S', '7252', '7252S'):
        return 'armv7ahf'
    elif about.getChipSetString() in 'pnx8493':
        return 'armv7a-vfp'
    elif about.getChipSetString() in ('meson-6', 'meson-64'):
        return 'cortexa9hf'
    elif about.getChipSetString() in ('7162', '7111'):
        return 'sh40'
    else:
        return 'mipsel'

def checkkernel():
    mycheck = 0
    if not fileExists('/media/usb'):
        os.system('mkdir /media/usb')
    if getMachineBuild().startswith('h'):
        return 1
    if getMachineBuild() in ('7000s', '7100s', '7400s', 'g300', 'hd2400', 'vusolo4k', 'wetekplay'):
        return 1
    if os.path.isfile('/proc/stb/info/vumodel') and os.path.isfile('/proc/stb/info/version'):
        if open('/proc/stb/info/vumodel').read().startswith('uno') or open('/proc/stb/info/vumodel').read().strip() == 'duo' or open('/proc/stb/info/vumodel').read().startswith('solo') or open('/proc/stb/info/vumodel').read().startswith('ultimo') or open('/proc/stb/info/vumodel').read().startswith('solo2') or open('/proc/stb/info/vumodel').read().startswith('duo2'):
            if about.getKernelVersionString() == '3.13.5' or about.getKernelVersionString() == '3.9.6':
                mycheck = 1
    else:
        mycheck = 0
    return mycheck


def readEmuName():
    try:
        defaultcam = '/usr/emu_scripts/Ncam_Ci.sh'
        if fileExists('/etc/EGCamConf'):
            f = open('/etc/EGCamConf', 'r')
            for line in f.readlines():
                parts = line.strip().split('|')
                if parts[0] == 'deldefault':
                    defaultcam = parts[1]

            f.close()
    except:
        defaultcam = 'Common Interface'

    return defaultcam


def readEmuNameOld():
    try:
        fp = open('/etc/egami/emuname', 'r')
        emuLine = fp.readline()
        fp.close()
        emuLine = emuLine.strip('\n')
        return emuLine
    except:
        return 'Common Interface'


def readEcmFile():
    try:
        ecmfile = file('/tmp/ecm.info', 'r')
        ecmfile_r = ecmfile.read()
        ecmfile.close()
        return ecmfile_r
    except:
        return 'ECM Info not aviable!'


def sendCmdtoEGEmuD(cmd):
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect('/tmp/egami.socket')
        print '[EG-EMU MANAGER] communicate with socket'
        s.send(cmd)
        s.close()
    except socket.error:
        print '[EG-EMU MANAGER] could not communicate with socket, lets try to start emud'
        cmd = '/bin/emud'
        runBackCmd(cmd)
        if s is not None:
            s.close()

    return

def runBackCmd(cmd):
    eConsoleAppContainer().execute(cmd)


def getRealName(string):
    if string.startswith(' '):
        while string.startswith(' '):
            string = string[1:]

    return string


def hex_str2dec(str):
    ret = 0
    try:
        ret = int(re.sub('0x', '', str), 16)
    except:
        pass

    return ret


def norm_hex(str):
    return '%04x' % hex_str2dec(str)


def loadcfg(plik, fraza, dlugosc):
    wartosc = '0'
    if fileExists(plik):
        f = open(plik, 'r')
        for line in f.readlines():
            line = line.strip()
            if line.find(fraza) != -1:
                wartosc = line[dlugosc:]

        f.close()
    return wartosc


def loadbool(plik, fraza, dlugosc):
    wartosc = '0'
    if fileExists(plik):
        f = open(plik, 'r')
        for line in f.readlines():
            line = line.strip()
            if line.find(fraza) != -1:
                wartosc = line[dlugosc:]

        f.close()
    if wartosc == '1':
        return True
    else:
        return False


def unload_modules(name):
    try:
        from sys import modules
        del modules[name]
    except:
        pass


def wyszukaj_in(zrodlo, szukana_fraza):
    wyrazenie = string.strip(szukana_fraza)
    for linia in zrodlo.xreadlines():
        if wyrazenie in linia:
            return True

    return False


def wyszukaj_re(szukana_fraza):
    wyrazenie = re.compile(string.strip(szukana_fraza), re.IGNORECASE)
    zrodlo = open('/usr/share/enigma2/' + config.skin.primary_skin.value, 'r')
    for linia in zrodlo.xreadlines():
        if re.search(wyrazenie, linia) != None:
            return True

    zrodlo.close()
    return False


class FileDownloadJob(Job):

    def __init__(self, url, filename, file):
        Job.__init__(self, _('Downloading %s' % file))
        FileDownloadTask(self, url, filename)


class DownloaderPostcondition(Condition):

    def check(self, task):
        return task.returncode == 0

    def getErrorMessage(self, task):
        return self.error_message


class FileDownloadTask(Task):

    def __init__(self, job, url, path):
        Task.__init__(self, job, _('Downloading'))
        self.postconditions.append(DownloaderPostcondition())
        self.job = job
        self.url = url
        self.path = path
        self.error_message = ''
        self.last_recvbytes = 0
        self.error_message = None
        self.download = None
        self.aborted = False
        return

    def run(self, callback):
        self.callback = callback
        self.download = downloadWithProgress(self.url, self.path)
        self.download.addProgress(self.download_progress)
        self.download.start().addCallback(self.download_finished).addErrback(self.download_failed)
        print '[FileDownloadTask] downloading', self.url, 'to', self.path

    def abort(self):
        print '[FileDownloadTask] aborting', self.url
        if self.download:
            self.download.stop()
        self.aborted = True

    def download_progress(self, recvbytes, totalbytes):
        if recvbytes - self.last_recvbytes > 10000:
            self.progress = int(100 * (float(recvbytes) / float(totalbytes)))
            self.name = _('Downloading') + ' ' + '%d of %d kBytes' % (recvbytes / 1024, totalbytes / 1024)
            self.last_recvbytes = recvbytes

    def download_failed(self, failure_instance = None, error_message = ''):
        self.error_message = error_message
        if error_message == '' and failure_instance is not None:
            self.error_message = failure_instance.getErrorMessage()
        Task.processFinished(self, 1)
        return

    def download_finished(self, string = ''):
        if self.aborted:
            self.finish(aborted=True)
        else:
            Task.processFinished(self, 0)
