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
print "Content-Type: text/html\r\n\r\n"
#print "Content-Length: %d" % (len(body))
#print ""
#print body

print '<body>'

form = cgi.FieldStorage()

speed = form.getvalue('speed')

config = ConfigParser.RawConfigParser()
config.read('/etc/VMC/VMC.ini')


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (string.replace(config.get('client','server'),'"',''),  int(string.replace(config.get('server','port'),'"','')))
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

fspeed=VMC(b'\x99',chr(1+int(speed)))
#print binascii.hexlify(fspeed.FullFrame())
try:
        sock.sendall(fspeed.FullFrame())
#	print binascii.hexlify(fspeed.FullFrame())
finally:
    print 'setting speed to ', speed
    sock.close()
