import os
import platform
import cPickle
import urllib2
import time

def execute():
    fqn = os.uname()[1]
    machine = platform.machine()
    OS = os.name + " " + platform.system() + " " + platform.release()
    try:
        ip = urllib2.urlopen('http://ip.42.pl/raw').read()
    except:
        ip = ''
    t = time.strftime('%c')
    info = [fqn, OS, machine, ip, t]
    return info
