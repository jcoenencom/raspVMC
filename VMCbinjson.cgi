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

sock.connect(server_address)

rcvd=VMC().getfanstatus(sock)
rcvd.getusage(sock)
rcvd.getalltemp(sock)
rcvd.getfanconfig(sock)
rcvd.getdevinfo(sock)
rcvd.getinputs(sock)
rcvd.getbypass(sock)


print "Status: 200 OK"
print "Content-Type: application/json"
print ""

print json.dumps(rcvd.objet,sort_keys=True,indent=4)

sys.stdout.flush()

sock.close()

