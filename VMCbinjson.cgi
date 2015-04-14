#!/usr/bin/python

import socket
import sys
import time
import binascii
import re
import math
import time
import json
import string
import ConfigParser
from VMC import VMC
import cgi


def sample(sock):
#b'\x69'
	commands = [ b'\x69',b'\x0b',b'\x0f', b'\xd1', b'\xdd', b'\xdf', b'\xd5', b'\xcd', b'\x0d', b'\x03' ]
	ttime=0
	ntime=0
	RFrame = re.compile(b'\x07\x0f0(.{4})(.{2})(.+)\x07\x0f')
	FFrame = re.compile(b'\x07\xf0([\x00-\xff]*)\x07\x0f')	
	try:

    # Send data
		for cmd in commands:
			start = time.time()
#        print 'sending command:', binascii.hexlify(cmd),' ',
			frame = VMC(cmd)
	        	sock.sendall(frame.FullFrame())
#        time.sleep(1)

    # Look for the response
			amount_received = 0
    
		       	data = sock.recv(64)
			if len(data) >0:
				result = FFrame.match(data)
				hexframe = result.group(1)
#				print 'result of findall received ',len(data),' findall ', result, binascii.hexlify(hexframe)
				elapsed = time.time()-start
#		print 'measured time ',elapsed,' sec '
				ttime += elapsed
				ntime+=1
				rcvd = VMC(hexframe)
#    		print json.dumps(rcvd.objet,sort_keys=True,indent=4)	
#		else:
#			print 'received empty message from server'

	        avgtime = ttime/ntime
#	        print 'Average command timing ', avgtime, 'total time ', ttime, ' for ', ntime, 'commands'
	        print json.dumps(rcvd.objet,sort_keys=True,indent=4)
	except:
		e = sys.exc_info()[0]
#		print "error: %s" % e
		exit()


config = ConfigParser.RawConfigParser()
config.read('/etc/VMC/VMC.ini')


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (string.replace(config.get('client','server'),'"',''),  int(string.replace(config.get('server','port'),'"','')))
sock.connect(server_address)


print "Content-Type: application/json"

print "Status: 200 OK"
print "Content-Type: application/json"
#print "Content-Length: %d" % (len(body))
print ""


sample(sock)

sock.close()

