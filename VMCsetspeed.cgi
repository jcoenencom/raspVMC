#!/usr/bin/python

import socket
import sys
import time
import binascii
import re
import math
import time
import string
import ConfigParser
import json
from VMC import VMC
import cgi, cgitb

print "Status: 200 OK"
print "Content-Type: application/json"
print ""

form = cgi.FieldStorage()

speed = form.getvalue('speed')

config = ConfigParser.RawConfigParser()
config.read('/etc/VMC/VMC.ini')


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (string.replace(config.get('client','server'),'"',''),  int(string.replace(config.get('server','port'),'"','')))
sock.connect(server_address)

vitesse=['Absent','low','mid','high']

if int(speed) in range(0,4):

#	print 'setting Speed to ',vitesse[int(speed)]

	rcvd=VMC().setspeed(sock,int(speed))
	print json.dumps(rcvd.objet,sort_keys=True,indent=4)
	sys.stdout.flush()
else:
	print "invalid speed value: ", speed, " must be in range [0..3]"
socket.close()
