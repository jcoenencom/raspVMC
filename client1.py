#!/usr/bin/python

import socket
import sys
import time
import binascii
import string
import re
import math
import time
import json
import os
import ConfigParser
from VMC import VMC



def sample(sock):

	commands = [ b'\x0b',b'\x67', b'\x69',b'\x0f', b'\xd1', b'\xdd', b'\xdf', b'\xd5', b'\xcd', b'\xd9' ]
	ttime=0
	ntime=0
	RFrame = re.compile(b'(.{4})(.{2})(.+)')
	FFrame = re.compile(b'\x07\xf0([\x00-\xff]+)\x07\x0f')	
	try:

    # Send data
		for cmd in commands:
			start = time.time()
			frame = VMC(cmd)
			print 'sending command:', binascii.hexlify(cmd),' ',binascii.hexlify(frame.frame),
	        	sock.sendall(frame.FullFrame())
#        time.sleep(1)

    # Look for the response
			amount_received = 0
    
		       	data = sock.recv(64)
			print "received ",len(data),binascii.hexlify(data),
			if len(data) >0:
                                result = FFrame.search(data)
				print "match result: ", result
				if result:
	                                hexframe = result.group(1)
#				print 'result of findall received ',len(data),' findall ', binascii.hexlify(hexframe)
				elapsed = time.time()-start
#		print 'measured time ',elapsed,' sec '
				ttime += elapsed
				ntime+=1
				rcvd = VMC(hexframe)
#		    		print json.dumps(rcvd.objet,sort_keys=True,indent=4)	
#		else:
#			print 'received empty message from server'

	        avgtime = ttime/ntime
		os.system("clear")
	        print 'Average command timing ', avgtime, 'total time ', ttime, ' for ', ntime, 'commands'
	        print json.dumps(rcvd.objet,sort_keys=True,indent=4)
	finally:
		e = sys.exc_info()[0]
#		print "error: %s" % e
#		exit()


config = ConfigParser.RawConfigParser()
config.read('/etc/VMC/VMC.ini')


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (string.replace(config.get('client','server'),'"',''),  int(string.replace(config.get('server','port'),'"','')))
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)
howmany=1
timer=1


if len(sys.argv)==3:
	print 'two args'
	howmany=int(sys.argv[1])
	timer=float(sys.argv[2])
elif len(sys.argv) == 2:
	howmany=int(sys.argv[1])
	timer = 0.5
elif len(sys.argv) == 1:
	howmany=1
	timer=0.5
i=0
while i < howmany:
	print 'requesting data'
        sample(sock)
	time.sleep(timer)
	i +=1
print 'closing socket'
sock.close()

