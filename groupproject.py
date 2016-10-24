#botnet server POC
#uses web requests to direct botnet

#not sure how low level libraries we need to use

from multiprocessing import Process, Queue, Manager
import SocketServer
import ssl
from socket import * #want lower level than built-in tcp servers
import sys
import logging


PORT = ('localhost', 4443)

NUMBEROFTHREADS = 4 #will probably create new threads on demand rather than use poollike
NUMBEROFWORKERS = NUMBEROFTHREADS - 1


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
    
def main():
    logging.info("Starting main")
    #create worker threads and send them to workerfunction
    manager = Manager()

    #create managed lists passed on to worker threads
    commandqueue = manager.list()
    finishedqueuelist = [manager.list() for _ in range(NUMBEROFWORKERS)]   
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
    logging.basicConfig(level=logging.DEBUG)
    main()
    logging.info("Shutting down")
