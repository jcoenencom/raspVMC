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
	timer = 1
elif len(sys.argv) == 1:
	howmany=1
	timer=1
i=0
while i < howmany:
	print 'requesting data ',i
	rcvd=VMC().gettemp(sock)
	rcvd.getfanstatus(sock)
	rcvd.getusage(sock)
	rcvd.getalltemp(sock)
	rcvd.getconfig(sock)
	rcvd.getfanconfig(sock)
	rcvd.getvalve(sock)
	rcvd.getdevinfo(sock)
	rcvd.getinputs(sock)
	rcvd.getbypass(sock)
	os.system("clear")
        print json.dumps(rcvd.objet,sort_keys=True,indent=4)
	sys.stdout.flush()
	i +=1
	time.sleep(timer)
print 'closing socket'
sock.close()

