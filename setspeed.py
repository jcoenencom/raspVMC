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

if len(sys.argv) == 2:
	speed=int(sys.argv[1])
else:
	speed=1

print 'setting Speed to ',speed

rcvd=VMC().setspeed(sock,int(speed))
print json.dumps(rcvd.objet,sort_keys=True,indent=4)
sys.stdout.flush()
print 'closing socket'
sock.close()

