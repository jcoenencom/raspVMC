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
import signal
import os
import subprocess
import syslog
from stat import *

global server
global config
global debugL

global DBGCLIENT
global DBGCONFIG
global DBGFRAME
global DBGFile
global DBG
global outputs
global inputs


def debug(level,*args):
	
	if level <= int(debugL):
		for arg in args:
			print arg,
		print
		sys.stdout.flush()


def signal_handler(signal,frame):
        syslog.syslog('Signal (SIGINT/SIGKILL) received Aborting Server, clearing Socket')
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
# verify that we expect a reponse from the VMC
# len = 8 for normal request data from VMC
# cmd = 9c when the command is RS232 mode

	temp = (len(tosend)==8) or (tosend[3] == b'\x9b')
	return (temp)


#initialize Globals

DBGCONFIG=2
DBGCLIENT=3
DBGFRAME=8

# define the signal handler (interrupts)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
#signal.signal(signal.SIGILL,  signal_handler)

#read config file

config = ConfigParser.RawConfigParser()
config.read('/etc/VMC/VMC.ini')


# get debug level set to 0 if not defined
try:
        debugL = config.get('DEBUG','level')

except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
        debugL=0


try:
	DBGFile = config.get('DEBUG','log')
	sys.stdout = open(DBGFile,'a')

except:
	DBGFile = "stdout"
	print "problem with log"

print DBGFile

#open the serial port attached to the VMC

serialport = string.replace(config.get('VMC','device'),'"','')

Sport = serial.Serial(port = serialport, baudrate = 9600, timeout = 0.05)


#define protocol regular expression

pack = re.compile('\x07\xf3') #ack
pdata = re.compile(b'(\x07\xf0.{3}(?:[^\x07]|(?:\x07\x07))*\x07\x0f)')  #generic data frame



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

syslog.syslog('Starting VMC server on device'+serialport+', Debug to:'+DBGFile+', running on IP address:'+str(server_address))


# Listen for incoming connections
server.listen(5)


#take care of socat process

try:
        PTY = string.replace(config.get('socat','PTY'),'"','')
	SERVER=string.replace(config.get('client','server'),'"','')
	PORT=string.replace(config.get('server','port'),'"','')
	SOCAT=['socat','PTY,mode=666,link='+PTY,'TCP-CONNECT:'+SERVER+':'+PORT]
	for arg in SOCAT:
		debug(DBGCONFIG,arg)
	PID = subprocess.Popen(SOCAT).pid
	syslog.syslog('socat started on '+str(PTY)+', PID:'+str(PID))
except:
        bind = ''
	e = sys.exc_info()[0]
        print "error: %s" % e

	syslog.syslog('VMCserver cannot start socat '+str(SOCAT))


# Sockets from which we expect to read
inputs = [ server ]


#append serial socket

portno = socket.fromfd(Sport.fileno(),socket.AF_INET,socket.SOCK_STREAM)

inputs.append(portno)

# Sockets to which we expect to write
outputs = [ ]
outputs.append(portno)


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
        if s is portno:
           bread = Sport.read(256);
           #print >>sys.stderr, 'Read %s Bytes', sys.getsizeof(bread)
	   debug(DBGFRAME,'received from VMC ',binascii.hexlify(bread))
           frames = pdata.findall(bread)
	   if len(frames)>0:       # we have frames 
		   sending = sender.get()
		   debug(DBGFRAME,len(frames), 'frame received from VMConly one expected from read ')
		   for frame in frames:
			# need to be check for consistency of the sender, if it does not exist drop the frame
			   debug(DBGFRAME, "frame received from VMC stored in client queue ", binascii.hexlify(frame))
			   if sending :
				message_queues[sending].put(frame)
			   else:
				debug( DBGCLIENT,'client is dead (socket is not in list) drop the frame')
	   Sport.write(binascii.a2b_hex('07f3'))   #send an ACK back to the VMC
	   Ready = True     #next client request can be processed
        elif s is server:
            # A "readable" server socket is ready to accept a connection
            connection, client_address = s.accept()
            debug(DBGCLIENT,'new client connection from', client_address)
            connection.setblocking(0)
            inputs.append(connection)

            # Give the connection a queue for data we want to send
            message_queues[connection] = Queue.Queue()
        else:
            data = s.recv(1024)
            if data:
#		print binascii.hexlify(data)
		frame = pdata.match(data)    #extract the frame from the received data (filter out ACK)
		if frame:
                # A readable client socket has data
	                debug(DBGFRAME,'received',binascii.hexlify(data),s.getpeername()," from client",s.getpeername()," retained is ",binascii.hexlify(frame.group(1)))
			messages.put(frame.group(1))  #store in send queue
			if reply(frame.group(1)):	# store only the command frames
				sender.put(s)			    #store sender in sender queue if we expect a reply
	                # Add output channel for response
	                if s not in outputs:
	                    outputs.append(s)
		#send to serial
            else:
                # Interpret empty result as closed connection
                debug(DBGCLIENT,'closing', client_address, 'after reading no data')
                # Stop listening for input on the connection
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()
                # Remove message queue
                del message_queues[s]
		del s   #finally remove the socket
    # Handle outputs
    for s in writable:
	if s is portno:
	    if not messages.empty() and Ready:
		tosend = messages.get()
	    	if reply(tosend):		#this is a single byte command must get an answer
			Ready = False	
		debug(DBGFRAME,'Sending frame ',binascii.hexlify(tosend),' to VMC')
	    	Nbytes=Sport.write(tosend)    #send next message in queue
	elif s in outputs:
	        if not message_queues[s].empty():
		    next_msg=message_queues[s].get_nowait()
        	    # s is ready for writing, write back the queued received message
        	    debug (DBGFRAME,'sending ',binascii.hexlify(next_msg)," to ",s.getpeername())
        	    s.send(next_msg)

