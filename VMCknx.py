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
import subprocess
import ConfigParser
from VMC import VMC

def encode_dpt9 (state): # 2byte signed float

   sign = 0x8000 if (state <0) else 0
   exp  = 0
   mant = 0

   mant = int(state * 100.0)
   while (abs(mant) > 2047):
        mant /= 2
        exp += 1

   data = sign | (exp << 11) | (mant & 0x07ff)

   high = "%x" % (data >> 8)
   low = "%x"% (data & 0xff)

   return high, low;




config = ConfigParser.RawConfigParser()
config.optionxform=str
config.read('/etc/VMC/VMC.ini')


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (string.replace(config.get('client','server'),'"',''),  int(string.replace(config.get('server','port'),'"','')))
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
#        print json.dumps(rcvd.objet,sort_keys=True,indent=4)
# get the list of options in section knx
	items=config.options('knx')
	for item in items:
		gadtype= config.get('knx',item)
		if (item != 'gateway'):
			(gad,type) = gadtype.split(',',1)
			(a,b)= eval('encode_'+type+'('+str(rcvd.objet['data']['temperature'][item])+')')
			command = (["/usr/local/bin/groupwrite", 'ip:'+config.get('knx','gateway'),gad,a,b] )
			result = subprocess.check_output(command)
			print command, result
	sys.stdout.flush()
	i +=1
	time.sleep(timer)
sock.close()

