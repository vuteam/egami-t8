import sys
import os
import struct
import shutil

def EgamiBootMainEx(source, target, installsettings, installplugins, installchannellist):
    egamihome = '/media/egamiboot'
    egamiroot = 'media/egamiboot'
    multihome = 'media/egamiboot'
    to = '/media/egamiboot/EgamiBootI/' + target
    cmd = 'rm -r %s > /dev/null 2<&1' % to
    rc = os.system(cmd)
    to = '/media/egamiboot/EgamiBootI/' + target
    cmd = 'mkdir %s > /dev/null 2<&1' % to
    rc = os.system(cmd)
    to = '/media/egamiboot/EgamiBootI/' + target
    cmd = 'chmod -R 0777 %s' % to
    rc = os.system(cmd)
    rc = EgamiBootExtract(source, target)
    cmd = 'mkdir -p %s/EgamiBootI/%s/media > /dev/null 2>&1' % (egamihome, target)
    rc = os.system(cmd)
    cmd = 'rm %s/EgamiBootI/%s/%s > /dev/null 2>&1' % (egamihome, target, egamiroot)
    rc = os.system(cmd)
    cmd = 'rmdir %s/EgamiBootI/%s/%s > /dev/null 2>&1' % (egamihome, target, egamiroot)
    rc = os.system(cmd)
    cmd = 'mkdir -p %s/EgamiBootI/%s/%s > /dev/null 2>&1' % (egamihome, target, egamiroot)
    rc = os.system(cmd)
    cmd = 'cp /etc/network/interfaces %s/EgamiBootI/%s/etc/network/interfaces > /dev/null 2>&1' % (egamihome, target)
    rc = os.system(cmd)
    cmd = 'cp /etc/wpa_supplicant.conf %s/EgamiBootI/%s/etc/wpa_supplicant.conf > /dev/null 2>&1' % (egamihome, target)
    rc = os.system(cmd)
    cmd = 'rm -rf %s/EgamiBootI/%s/usr/lib/enigma2/python/Plugins/Extensions/HbbTV' % (egamihome, target)
    rc = os.system(cmd)
    cmd = 'mkdir  %s/EgamiBootI/%s/usr/lib/enigma2/python/Plugins/Extensions/EGAMIBoot > /dev/null 2>&1' % (egamihome, target)
    rc = os.system(cmd)
    cmd = 'cp -r -p /usr/lib/enigma2/python/EGAMI/MiniEGAMIBoot/* %s/EgamiBootI/%s/usr/lib/enigma2/python/Plugins/Extensions/EGAMIBoot/ > /dev/null 2>&1' % (egamihome, target)
    rc = os.system(cmd)
    cmd = 'cp /usr/lib/enigma2/python/boxbranding.so %s/EgamiBootI/%s/usr/lib/enigma2/python/boxbranding.so > /dev/null 2>&1' % (egamihome, target)
    rc = os.system(cmd)
    cmd = 'cp /etc/hostname %s/EgamiBootI/%s/etc/hostname > /dev/null 2>&1' % (egamihome, target)
    rc = os.system(cmd)
    cmd = 'cp -a /usr/share/enigma2/rc_models/* %s/EgamiBootI/%s/usr/share/enigma2/rc_models/ > /dev/null 2>&1' % (egamihome, target)
    rc = os.system(cmd)
    cmd = 'cp -r -p /usr/lib/enigma2/python/Plugins/Extensions/CamdMenager %s/EgamiBootI/%s/usr/lib/enigma2/python/Plugins/Extensions > /dev/null 2>&1' % (egamihome, target)
    rc = os.system(cmd)
    cmd = 'cp -r -p /usr/lib/enigma2/python/Plugins/SystemPlugins/FanControl %s/EgamiBootI/%s/usr/lib/enigma2/python/Plugins/SystemPlugins > /dev/null 2>&1' % (egamihome, target)
    rc = os.system(cmd)
    cmd = 'cp -r -p /usr/share/enigma2/rc_models %s/EgamiBootI/%s/usr/share/enigma2 > /dev/null 2>&1' % (multihome, target)
    rc = os.system(cmd)
    if installsettings == 'True':
        cmd = 'mkdir -p %s/EgamiBootI/%s/etc/enigma2 > /dev/null 2>&1' % (egamihome, target)
        rc = os.system(cmd)
        cmd = 'cp -f /etc/enigma2/settings %s/EgamiBootI/%s/etc/enigma2' % (egamihome, target)
        rc = os.system(cmd)
        cmd = 'cp -f /etc/enigma2/*.xml %s/EgamiBootI/%s/etc/enigma2' % (egamihome, target)
        rc = os.system(cmd)
        cmd = 'cp -f /etc/tuxbox/* %s/EgamiBootI/%s/etc/tuxbox/' % (egamihome, target)
        rc = os.system(cmd)
        cmd = 'cp /etc/passwd %s/EgamiBootI/%s/etc/passwd > /dev/null 2>&1' % (egamihome, target)
        rc = os.system(cmd)
        cmd = 'cp /etc/resolv.conf %s/EgamiBootI/%s/etc/resolv.conf > /dev/null 2>&1' % (egamihome, target)
        rc = os.system(cmd)
    if installplugins == 'True':
        cmd = 'cp -af /usr/lib/enigma2/python/Plugins/Extensions/* %s/EgamiBootI/%s/usr/lib/enigma2/python/Plugins/Extensions/' % (egamihome, target)
        rc = os.system(cmd)
        cmd = 'cp -af /usr/lib/enigma2/python/Plugins/SystemPlugins/* %s/EgamiBootI/%s/usr/lib/enigma2/python/Plugins/SystemPlugins/' % (egamihome, target)
        rc = os.system(cmd)
    if installchannellist == 'True':
        cmd = 'mkdir -p %s/EgamiBootI/%s/etc/enigma2 > /dev/null 2>&1' % (egamihome, target)
        rc = os.system(cmd)
        cmd = 'cp -f /etc/enigma2/*.tv %s/EgamiBootI/%s/etc/enigma2/' % (egamihome, target)
        rc = os.system(cmd)
        cmd = 'cp -f /etc/enigma2/*.radio %s/EgamiBootI/%s/etc/enigma2/' % (egamihome, target)
        rc = os.system(cmd)
        cmd = 'cp -f /etc/enigma2/lamedb %s/EgamiBootI/%s/etc/enigma2/lamedb' % (egamihome, target)
        rc = os.system(cmd)
    cmd = 'mkdir -p %s/EgamiBootI/%s/media > /dev/null 2>&1' % (egamihome, target)
    rc = os.system(cmd)
    cmd = 'mkdir -p %s/EgamiBootI/%s/media/usb > /dev/null 2>&1' % (egamihome, target)
    rc = os.system(cmd)
    filename = egamihome + '/EgamiBootI/' + target + '/etc/fstab'
    filename2 = filename + '.tmp'
    out = open(filename2, 'w')
    f = open(filename, 'r')
    for line in f.readlines():
        if line.find('/dev/mtdblock2') != -1:
            line = '#' + line
        elif line.find('/dev/root') != -1:
            line = '#' + line
        out.write(line)

    f.close()
    out.close()
    os.rename(filename2, filename)
    tpmd = egamihome + '/EgamiBootI/' + target + '/etc/init.d/tpmd'
    if os.path.exists(tpmd):
        os.system('rm ' + tpmd)
    filename = egamihome + '/EgamiBootI/' + target + '/usr/lib/enigma2/python/Components/config.py'
    if os.path.exists(filename):
        filename2 = filename + '.tmp'
        out = open(filename2, 'w')
        f = open(filename, 'r')
        for line in f.readlines():
            if line.find('if file("/proc/stb/info/vumodel")') != -1:
                line = '#' + line
            elif line.find('rckeyboard_enable = True') != -1:
                line = '#' + line
            out.write(line)

        f.close()
        out.close()
        os.rename(filename2, filename)
    filename = egamihome + '/EgamiBootI/' + target + '/usr/lib/enigma2/python/Tools/HardwareInfoVu.py'
    if os.path.exists(filename):
        filename2 = filename + '.tmp'
        out = open(filename2, 'w')
        f = open(filename, 'r')
        for line in f.readlines():
            if line.find('print "hardware detection failed"') != -1:
                line = '\t\t    HardwareInfoVu.device_name ="duo"'
            out.write(line)

        f.close()
        out.close()
        os.rename(filename2, filename)
    filename = egamihome + '/EgamiBootI/' + target + '/etc/bhversion'
    if os.path.exists(filename):
        os.system('echo "BlackHole 2.1.4" > ' + filename)
    filename = egamihome + '/EgamiBootI/' + target + '/etc/init.d/volatile-media.sh'
    if os.path.exists(filename):
        cmd = 'rm ' + filename
        os.system(cmd)
    mypath = egamihome + '/EgamiBootI/' + target + '/usr/lib/opkg/info/'
    if not os.path.exists(mypath):
        mypath = egamihome + '/EgamiBootI/' + target + '/var/lib/opkg/info/'
    for fn in os.listdir(mypath):
        if fn.find('kernel-image') != -1 and fn.find('postinst') != -1:
            filename = mypath + fn
            filename2 = filename + '.tmp'
            out = open(filename2, 'w')
            f = open(filename, 'r')
            for line in f.readlines():
                if line.find('/boot') != -1:
                    line = line.replace('/boot', '/boot > /dev/null 2>\\&1; exit 0')
                out.write(line)

            if f.close():
                out.close()
                os.rename(filename2, filename)
                cmd = 'chmod -R 0755 %s' % filename
                rc = os.system(cmd)
        if fn.find('-bootlogo.postinst') != -1:
            filename = mypath + fn
            filename2 = filename + '.tmp'
            out = open(filename2, 'w')
            f = open(filename, 'r')
            for line in f.readlines():
                if line.find('/boot') != -1:
                    line = line.replace('/boot', '/boot > /dev/null 2>\\&1; exit 0')
                out.write(line)

            f.close()
            out.close()
            os.rename(filename2, filename)
            cmd = 'chmod -R 0755 %s' % filename
            rc = os.system(cmd)
        if fn.find('-bootlogo.postrm') != -1:
            filename = mypath + fn
            filename2 = filename + '.tmp'
            out = open(filename2, 'w')
            f = open(filename, 'r')
            for line in f.readlines():
                if line.find('/boot') != -1:
                    line = line.replace('/boot', '/boot > /dev/null 2>\\&1; exit 0')
                out.write(line)

            f.close()
            out.close()
            os.rename(filename2, filename)
            cmd = 'chmod -R 0755 %s' % filename
            rc = os.system(cmd)
        if fn.find('-bootlogo.preinst') != -1:
            filename = mypath + fn
            filename2 = filename + '.tmp'
            out = open(filename2, 'w')
            f = open(filename, 'r')
            for line in f.readlines():
                if line.find('/boot') != -1:
                    line = line.replace('/boot', '/boot > /dev/null 2>\\&1; exit 0')
                out.write(line)

            f.close()
            out.close()
            os.rename(filename2, filename)
            cmd = 'chmod -R 0755 %s' % filename
            rc = os.system(cmd)
        if fn.find('-bootlogo.prerm') != -1:
            filename = mypath + fn
            filename2 = filename + '.tmp'
            out = open(filename2, 'w')
            f = open(filename, 'r')
            for line in f.readlines():
                if line.find('/boot') != -1:
                    line = line.replace('/boot', '/boot > /dev/null 2>\\&1; exit 0')
                out.write(line)

            f.close()
            out.close()
            os.rename(filename2, filename)
            cmd = 'chmod -R 0755 %s' % filename
            rc = os.system(cmd)

    rc = EgamiBootRemoveUnpackDirs()
    filename = egamihome + '/EgamiBootI/.egamiboot'
    out = open('/media/egamiboot/EgamiBootI/.egamiboot', 'w')
    out.write(target)
    out.close()
    os.system('touch /tmp/.egamireboot')
    rc = os.system('sync')
    os.system('reboot')


def EgamiBootRemoveUnpackDirs():
    os.chdir('/media/egamiboot/EgamiBootUpload')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/venton-hdx'):
        shutil.rmtree('venton-hdx')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/hde'):
        shutil.rmtree('hde')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/hdx'):
        shutil.rmtree('hdx')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/hdp'):
        shutil.rmtree('hdp')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/miraclebox'):
        shutil.rmtree('miraclebox')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/atemio'):
        shutil.rmtree('atemio')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/xpeedlx'):
        shutil.rmtree('xpeedlx')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/xpeedlx3'):
        shutil.rmtree('xpeedlx3')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/bwidowx'):
        shutil.rmtree('bwidowx')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/bwidowx2'):
        shutil.rmtree('bwidowx2')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/beyonwiz'):
        shutil.rmtree('beyonwiz')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/vuplus'):
        shutil.rmtree('vuplus')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/sf3038'):
        shutil.rmtree('sf3038')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/et10000'):
        shutil.rmtree('et10000')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/et9x00'):
        shutil.rmtree('et9x00')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/et8000'):
        shutil.rmtree('et8000')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/et7x00'):
        shutil.rmtree('et7x00')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/et6x00'):
        shutil.rmtree('et6x00')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/et5x00'):
        shutil.rmtree('et5x00')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/et4x00'):
        shutil.rmtree('et4x00')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/gigablue'):
        shutil.rmtree('gigablue')
    if os.path.exists('/media/egamiboot/EgamiBootUpload/hd2400'):
        shutil.rmtree('hd2400')


def EgamiBootExtract(source, target):
    if os.path.exists('/media/egamiboot/ubi') is False:
        rc = os.system('mkdir /media/egamiboot/ubi')
    sourcefile = '/media/egamiboot/EgamiBootUpload/%s.zip' % source
    sourcefileNFI = '/media/egamiboot/EgamiBootUpload/%s.nfi' % source
    if os.path.exists(sourcefileNFI) is True:
        cmd = '/usr/lib/enigma2/python/Plugins/Extensions/EGAMIBoot/bin/nfidump ' + sourcefileNFI + ' /media/egamiboot/EgamiBootI/' + target
        rc = os.system(cmd)
        cmd = 'rm -rf ' + sourcefileNFI
        rc = os.system(cmd)
    elif os.path.exists(sourcefile) is True:
        os.chdir('/media/egamiboot/EgamiBootUpload')
        print '[EGAMIBoot] Extracknig ZIP image file'
        rc = os.system('unzip ' + sourcefile)
        rc = os.system('rm -rf ' + sourcefile)
        if os.path.exists('/media/egamiboot/EgamiBootUpload/venton-hdx'):
            os.chdir('venton-hdx')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/hde'):
            os.chdir('hde')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/hdx'):
            os.chdir('hdx')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/hdp'):
            os.chdir('hdp')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/miraclebox'):
            os.chdir('miraclebox')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/miraclebox/mini'):
                os.chdir('mini')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/miraclebox/miniplus'):
                os.chdir('miniplus')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/miraclebox/minihybrid'):
                os.chdir('minihybrid')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/miraclebox/twin'):
                os.chdir('twin')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/miraclebox/ultra'):
                os.chdir('ultra')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/miraclebox/micro'):
                os.chdir('micro')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/miraclebox/twinplus'):
                os.chdir('twinplus')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/miraclebox/mbmicro'):
                os.chdir('mbmicro')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/sf3038'):
            os.chdir('sf3038')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/atemio'):
            os.chdir('atemio')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/atemio/5x00'):
                os.chdir('5x00')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/atemio/6000'):
                os.chdir('6000')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/atemio/6100'):
                os.chdir('6100')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/atemio/6200'):
                os.chdir('6200')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/atemio/8x00'):
                os.chdir('8x00')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/xpeedlx'):
            os.chdir('xpeedlx')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/xpeedlx3'):
            os.chdir('xpeedlx3')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/bwidowx'):
            os.chdir('bwidowx')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/bwidowx2'):
            os.chdir('bwidowx2')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/beyonwiz'):
            os.chdir('beyonwiz')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/beyonwiz/hdx'):
                os.chdir('hdx')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/beyonwiz/hdp'):
                os.chdir('hdp')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/beyonwiz/hde2'):
                os.chdir('hde2')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/vuplus'):
            os.chdir('vuplus')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/vuplus/duo'):
                os.chdir('duo')
                os.system('mv root_cfe_auto.jffs2 rootfs.bin')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/vuplus/solo'):
                os.chdir('solo')
                os.system('mv -f root_cfe_auto.jffs2 rootfs.bin')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/vuplus/solose'):
                os.chdir('solose')
                os.system('mv -f root_cfe_auto.jffs2 rootfs.bin')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/vuplus/ultimo'):
                os.chdir('ultimo')
                os.system('mv -f root_cfe_auto.jffs2 rootfs.bin')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/vuplus/uno'):
                os.chdir('uno')
                os.system('mv -f root_cfe_auto.jffs2 rootfs.bin')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/vuplus/solo2'):
                os.chdir('solo2')
                os.system('mv -f root_cfe_auto.bin rootfs.bin')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/vuplus/duo2'):
                os.chdir('duo2')
                os.system('mv -f root_cfe_auto.bin rootfs.bin')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/vuplus/zero'):
                os.chdir('zero')
                os.system('mv -f root_cfe_auto.bin rootfs.bin')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/vuplus/solo4k'):
                os.chdir('solo4k')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/et10000'):
            os.chdir('et10000')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/et9x00'):
            os.chdir('et9x00')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/et8500'):
            os.chdir('et8500')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/et8000'):
            os.chdir('et8000')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/et7x00'):
            os.chdir('et7x00')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/et6x00'):
            os.chdir('et6x00')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/et5x00'):
            os.chdir('et5x00')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/et4x00'):
            os.chdir('et4x00')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/gigablue'):
            os.chdir('gigablue')
            if os.path.exists('/media/egamiboot/EgamiBootUpload/gigablue/quad'):
                os.chdir('quad')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/hd2400'):
            os.chdir('hd2400')
        if os.path.exists('/media/egamiboot/EgamiBootUpload/vuplus/solo4k/rootfs.tar.bz2'):
            cmd = 'tar -jxf rootfs.tar.bz2 -C /media/egamiboot/EgamiBootI/' + target
            rc = os.system(cmd)
        else:
            print '[EGAMIBoot] Extracting UBIFS image and moving extracted image to our target'
            cmd = 'chmod 777 /usr/lib/enigma2/python/Plugins/Extensions/EGAMIBoot/ubi_reader/ubi_extract_files.pyo'
            rc = os.system(cmd)
            cmd = 'python /usr/lib/enigma2/python/Plugins/Extensions/EGAMIBoot/ubi_reader/ubi_extract_files.pyo rootfs.bin -o /media/egamiboot/ubi'
            rc = os.system(cmd)
            os.chdir('/home/root')
            cmd = 'cp -r -p /media/egamiboot/ubi/rootfs/* /media/egamiboot/EgamiBootI/' + target
            rc = os.system(cmd)
            cmd = 'chmod -R +x /media/egamiboot/EgamiBootI/' + target
            rc = os.system(cmd)
            cmd = 'rm -rf /media/egamiboot/ubi'
            rc = os.system(cmd)
    else:
        return 0
    return 1
