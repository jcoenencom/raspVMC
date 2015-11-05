#!/usr/bin/python

import socket
import sys
import time
import binascii
import re
import math
import time
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
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
#print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

fspeed=VMC(b'\xdb',chr(0),chr(0),chr(0),chr(1))
#print binascii.hexlify(fspeed.FullFrame())
try:
        sock.sendall(fspeed.FullFrame())
#	print binascii.hexlify(fspeed.FullFrame())
finally:
    print 'Filter active timer reset', speed
    sock.close()
