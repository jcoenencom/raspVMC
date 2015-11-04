#!/usr/bin/python

import select
import socket
import sys
import Queue
import ConfigParser
import serial
import string
import binascii
import re
from signal import *
import os
import subprocess
import syslog
import time
from stat import *

global server
global config
global debugL
global dgbsocket
global Ctrlconn
global DBGCLIENT
global DBGCONFIG
global DBGFRAME
global DBGFile
global dbgfd
global DBG
global outputs
global inputs

def debug(level,*args):
	
	if level <= int(debugL):
		print time.strftime('%d/%m/%y %H:%M:%S',time.localtime()),':',
		for arg in args:
			print arg,
		print
		sys.stdout.flush()
def signal_handler(signum,frame):
        syslog.syslog('Signal %s received Aborting Server, clearing Socket'%(str(signum)))
	syslog.syslog(str(sys.exc_info()))
	while inputs:
		instance=inputs.pop()
		mode=os.fstat(instance.fileno()).st_mode
		if S_ISSOCK(mode) and instance <> server:
			syslog.syslog('Closing IP socket on client '+str(instance.getpeername()))
		elif instance == server:		
			syslog.syslog('Closing server socket')
			server.close()
		else:
			syslog.syslog('Closing device connection ')
			instance.close()
        sys.exit(0)

def reply(tosend):
# verify that we should expect a reponse from the VMC
# len = 8 for normal request data from VMC
# cmd = 9c when the command is RS232 mode
# other commands from the standard protocol do not expect a reply (eg seet speed)
# on the contrary the Comfosense sends normal protocol frame eg temp reaquest with 1 data byte (always null ?)
# which complicates the detected fo reply
# the solution is to have a list and see if tosend[3] is in the list

#	replied=['\x67','\x69','\xa1','\x03','\x0b','\x0d','\x0f','\x11','\x13','\x97','\x9b','\x9d','\xc9','\xcd','\xd1','\xd5','\xd9','\xdd','\xdf','\xe1','\xe5','\xe9','\xeb','\x33','\x35','\x37','\x39'] 
	replied=['\x99','\x9f','\xcb','\xcf','\xd3','\xd7','\xdb','\xed']
#	temp = (len(tosend)==8) or (tosend[3] == b'\x9b')
	temp = tosend[3] not in replied
	debug(DBGFRAME,'Command code: ',binascii.hexlify(tosend[3]), " reply is ",temp)
	return (temp)


def response(Sport):
#read a response frame from the VMC and send it back
           bread = Sport.read(256);
           #print >>sys.stderr, 'Read %s Bytes', sys.getsizeof(bread)
           debug(DBGFRAME,'received from VMC ',binascii.hexlify(bread))
           #frames = pdata.findall(bread)
	   frame = re.search(b'(\x07\xf0.{3}(?:[^\x07]|(?:\x07\x07))*\x07\x0f)',bread,flags=re.S)
           if frame:       # we have frames
                   debug(DBGFRAME,len(frame.group()), 'frames received from VMC only one is expected from theread ')
                   #for frame in frames:
                   # need to be check for consistency of the sender, if it does not exist drop the frame
                   debug(DBGFRAME, "frame received from VMC stored in client queue ", binascii.hexlify(frame.group(1)))
		   Sport.write(binascii.a2b_hex('07f3'))   #send an ACK back to the VMC
		   return(frame.group(1))
	   else:
			debug(DBGFRAME,"No frame detected in ", binascii.hexlify(bread))
			return(None)
           Ready = True     #next client request can be processed

#initialize Globals

DBGCONFIG=2
DBGCLIENT=3
DBGFRAME=8

# define the signal handler (interrupts)

signals = {
        SIGABRT: 'SIGABRT',
        SIGALRM: 'SIGALRM',
        SIGBUS: 'SIGBUS',
        SIGCHLD: 'SIGCHLD',
        SIGCONT: 'SIGCONT',
        SIGFPE: 'SIGFPE',
        SIGHUP: 'SIGHUP',
        SIGILL: 'SIGILL',
        SIGINT: 'SIGINT',
        SIGPIPE: 'SIGPIPE',
        SIGPOLL: 'SIGPOLL',
        SIGPROF: 'SIGPROF',
        SIGQUIT: 'SIGQUIT',
        SIGSEGV: 'SIGSEGV',
        SIGSYS: 'SIGSYS',
        SIGTERM: 'SIGTERM',
        SIGTRAP: 'SIGTRAP',
        SIGTSTP: 'SIGTSTP',
        SIGTTIN: 'SIGTTIN',
        SIGTTOU: 'SIGTTOU',
        SIGURG: 'SIGURG',
        SIGUSR1: 'SIGUSR1',
        SIGUSR2: 'SIGUSR2',
        SIGVTALRM: 'SIGVTALRM',
        SIGXCPU: 'SIGXCPU',
        SIGXFSZ: 'SIGXFSZ',
        }

for num in signals:
        signal(num, signal_handler)



#signal.signal(signal.SIGILL,  signal_handler)

#read config file

config = ConfigParser.RawConfigParser()
config.read('/etc/VMC/VMC.ini')


# get debug level set to 0 if not defined
try:
        debugL = config.get('debug','level')

except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
        debugL=0


try:
	DBGFile = config.get('debug','log')
	dbgfd=open(DBGFile,'a')
	sys.stdout = dbgfd

except:
	DBGFile = "stdout"
	dbgfd=sys.stdout
	print "problem with log"


#open the serial port attached to the VMC

serialport = config.get('VMC','device')

Sport = serial.Serial(port = serialport, baudrate = 9600, timeout = 0.25)


#define protocol regular expression

pack = re.compile('\x07\xf3') #ack
pdata = re.compile(b'(\x07\xf0.{3}(?:[^\x07]|(?:\x07\x07))*\x07\x0f)')  #generic data frame

CCmsg = ""    # message buffer for CCease

# Create a TCP/IP socket
# get server information from configuration
try:
	config.get('server','port')
	Port = int(string.replace(config.get('server','port'),'"',''))
except:
	Port = 10000
try:
	config.get('server','bind')
	bind = string.replace(config.get('server','bind'),'"','')
except:
	bind = ''


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server_address = (bind, Port)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(server_address)
server.listen(5)

syslog.syslog('Starting NEW VMC server on device'+serialport+', Debug to:'+DBGFile+', running on IP address:'+str(server_address))

# Create a TCP/IP socket
# get server information from configuration
try:
        config.get('ConfoSense','port')
        CCPort = int(string.replace(config.get('ConfoSense','port'),'"',''))
except:
        CCPort = 10001

try:
	config.get('control','port')
	CTRLPORT = int(string.replace(config.get('Control','port'),'"',''))
except:
	CTRLPORT = 10002


CCserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CCserver.setblocking(0)
CCserver_address = (bind, CCPort)
CCserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
CCserver.bind(CCserver_address)
syslog.syslog('Starting VMC server for ConfoSense on IP address:'+str(CCserver_address)+' port '+str(CCPort))

# Listen for incoming connections

CCserver.listen(1)

#control port
CCTRL = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CCTRL.setblocking(0)
CCTRL_address = (bind, CTRLPORT)
CCTRL.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
CCTRL.bind(CCTRL_address)
syslog.syslog('Starting VMC server for Control on IP address:'+str(CCTRL_address)+' port '+str(CTRLPORT))

CCTRL.listen(1)

Ctrlconn = None
CCconn = None

dbgsocket = None


#take care of socat process

try:
        PTY = config.get('socat','pty')
	SERVER=config.get('client','server')
	PORT=config.get('server','port')
	SOCAT=['socat','PTY,mode=666,link='+PTY,'TCP-CONNECT:'+SERVER+':'+PORT]
	for arg in SOCAT:
		debug(DBGCONFIG,arg)
	PID = subprocess.Popen(SOCAT).pid
	syslog.syslog('socat started on '+str(PTY)+', PID:'+str(PID))
except:
        bind = ''
	e = sys.exc_info()[0]
        print "error: %s" % e

	syslog.syslog('VMCserver cannot start socat (maybe not configured)')


# Sockets from which we expect to read
inputs = [ server ]

inputs.append(CCserver)
inputs.append(CCTRL)


#append serial socket

portno = socket.fromfd(Sport.fileno(),socket.AF_INET,socket.SOCK_STREAM)

inputs.append(portno)

# Sockets to which we expect to write
outputs = [ ]
outputs.append(portno)
clients = []

#normally outputs.append(Sport.fileno()) to be able to write to serial


# Outgoing message queues (socket:Queue)
message_queues = {}
messages = Queue.Queue()
sender = Queue.Queue()
Ready = True

while inputs:

#   Wait for at least one of the sockets to be ready for processing
#   print >>sys.stderr, '\nwaiting for the next event'
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    # Handle inputs
    # this need to be handling the case where only an ack is received from the VMC
    for s in readable:
        if s is server:
            # A "readable" server socket is ready to accept a connection
            connection, client_address = s.accept()
            debug(DBGCLIENT,'new client connection from', client_address)
            connection.setblocking(0)
            inputs.append(connection)
	    clients.append(connection)
	elif s is CCserver:
	    # A CCease connection is established
	    connection, client_address = s.accept()
	    debug(DBGCLIENT,'New connection for CCEASE/COMFOSENSE from ', client_address)
	    connection.setblocking(0)
	    inputs.append(connection)
	    CCconn=connection
	elif s is CCTRL:
	# control connection established
	    connection, client_address = s.accept()
	    debug(DBGCLIENT,'New connection for Server control from ', client_address)
            connection.setblocking(0)
            inputs.append(connection)
            Ctrlconn=connection
	elif s is Ctrlconn:
        # a message is recevied from the control link
		CComd=s.recv(128)		
        	if CComd:
                	debug(DBGCONFIG,"Request for control command ",CComd," from ", s.getpeername())
            	# return message queue size
			if CComd[0:4]=='help':
				s.send(" available commands: help, size, debug lvl, moni, moff, quit, exit, abort \n")
			elif CComd[0:4]=='size':
				one = str(messages.qsize())
        	            	s.send("There are "+one+" messages in the queue\n")
			elif CComd[0:5]=='debug':
				debugL = int(CComd[6])
				debug(DBGCONFIG,'Change Debug level to ',debugL,' immediate')
			elif ((CComd[0:4]=='quit') or (CComd[0:4]=='exit')):
				debug(DBGCONFIG,'closing', s.getpeername(), 'after user request')
				if s in outputs:
					outputs.remove(s)
				inputs.remove(s)
				sys.stdout=dbgfd                  #make sure stdout goes back to log file before closing socket
				s.close()
				del s
				Ctrlconn = None
			elif CComd[0:4]=='moni':
				debug(DBGCONFIG,'monitoring turned on')
				sys.stdout=Ctrlconn.makefile('w')
				dgbsocket=s
			elif CComd[0:4]=='moff':
				debug(DBGCONFIG,'monitoring turned off')
				sys.stdout=dbgfd
				dbgsocket=None
			elif CComd[0:5]=='abort':
                                debug(DBGCONFIG,'terminate server after user request')
                                if s in outputs:
                                        outputs.remove(s)
                                inputs.remove(s)
				dbgsocket=None
                                s.close()
                                del s
                                exit()

        	else:
	                # Interpret empty result as closed connection
	                debug(DBGCLIENT,'closing', client_address, 'after reading no data')
        	        # Stop listening for input on the connection
	                if s in outputs:
	                    outputs.remove(s)
	                inputs.remove(s)
	                s.close()
	                del s   #finally remove the socket
	elif s is CCconn:
        # received a request from CCEASE
	# incomming characters must be buffered and buffer is checked for frame 
                CComd=s.recv(128)
		if CComd:
			CCmsg += CComd
			frame = re.search(b'(\x07\xf0.{3}(?:[^\x07]|(?:\x07\x07))*\x07\x0f)',CCmsg)
			# debug(DBGCLIENT,"CCEase RX:", binascii.hexlify(CComd), "Buffer :",binascii.hexlify(CCmsg))
			if frame:
				debug(DBGFRAME,"ConfoSense Request for    ",binascii.hexlify(frame.group(1))," from ", s.getpeername())
				messages.put((s,frame.group(1)))
				CCmsg = ""
                else:
                        # Interpret empty result as closed connection
                        debug(DBGCLIENT,'closing', client_address, 'after reading no data')
                        # Stop listening for input on the connection
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        s.close()
                        del s   #finally remove the socket
			CCconn = None
        else:
	    if s in clients:
	            data = s.recv(1024)
        	    if data:
#			print binascii.hexlify(data)
			frame = pdata.match(data)    #extract the frame from the received data (filter out ACK)
			if frame:
        	        # A readable client socket has data
		                debug(DBGFRAME,'received',binascii.hexlify(data),s.getpeername()," from client",s.getpeername()," retained is ",binascii.hexlify(frame.group(1)))
				messages.put((s,frame.group(1)))  #store in send queue, client and frame
        	    else:
               	 # Interpret empty result as closed connection
               		debug(DBGCLIENT,'closing', client_address, 'after reading no data')
                	# Stop listening for input on the connection
                	inputs.remove(s)
                	s.close()
                	# Remove message queue
			del s   #finally remove the socket
	    else:
		del s
    # Handle outputs
    for s in writable:
	if s is portno:
	    if not messages.empty():
		(client,tosend) = messages.get()
		debug(DBGFRAME,"Processing msg from queue ", client.getpeername())
		debug(DBGFRAME,'Sending frame ',binascii.hexlify(tosend),' to VMC', "from Client ", client.getpeername())
	    	Nbytes=Sport.write(tosend)    #send next message in queue
		if reply(tosend):
			debug(DBGFRAME,"expecting a reply")
			next_msg = response(Sport)
			if ( next_msg is not None):
				debug (DBGFRAME,'sending ',binascii.hexlify(next_msg)," to ",client.getpeername())
				client.send(next_msg)
		else:
			debug(DBGFRAME,"not expecting a reply")
    for s in exceptional:
        	debug( DBGCLIENT,'handling exceptional condition for', s.getpeername())
        # Stop listening for input on the connection
        	inputs.remove(s)
        	if s in outputs:
        	    outputs.remove(s)
        	s.close()
	
        	# Remove message queue
        	del message_queues[s]
