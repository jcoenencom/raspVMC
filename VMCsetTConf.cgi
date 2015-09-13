#!/usr/bin/python

import socket
import sys
import string
import ConfigParser
import json
from VMC import VMC
import cgi, cgitb

print "Status: 200 OK"
print "Content-Type: application/json"
print ""

form = cgi.FieldStorage()

tconf = form.getvalue('tconf')

config = ConfigParser.RawConfigParser()
config.read('/etc/VMC/VMC.ini')


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (string.replace(config.get('client','server'),'"',''),  int(string.replace(config.get('server','port'),'"','')))
sock.connect(server_address)

#vitesse=['Absent','low','mid','high']

if int(tconf) in range(0,30):

#	print 'setting Speed to ',vitesse[int(speed)]

	rcvd=VMC().setTconfort(sock,int(tconf))
	print json.dumps(rcvd.objet,sort_keys=True,indent=4)
	sys.stdout.flush()
else:
	print "invalid temperature value: ", tconf, " must be in range [0..30]"
socket.close()
