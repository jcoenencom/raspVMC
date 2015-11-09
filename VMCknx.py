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

def getFromDict(dataDict, mapList):    
    for k in mapList: dataDict = dataDict[k]
    return dataDict

# Set a given data in a dictionary with position provided as a list
def setInDict(dataDict, mapList, value): 
    for k in mapList[:-1]: dataDict = dataDict[k]
    dataDict[mapList[-1]] = value

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
   retval=[high,low]

   return (retval);

def encode_dpt7 (state): # 2byte unsigned int
   high = "%x" % (state >> 8)
   low = "%x"% (state & 0xff)
   retval=[high,low]
   return (retval);

def encode_dpt1(state):  # 1 bit status (0 or 1)
	retval = [str(state)]
	return retval;

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
# get all paramters from the VMC
	rcvd=VMC().getAll(sock)
#        print json.dumps(rcvd.objet,sort_keys=True,indent=4)
# get the list of options in section knx
	items=config.options('knx')
	for item in items:
		gadtype= config.get('knx',item)
		if (item != 'gateway'):
			mapList = item.split('-',5)
			value=getFromDict(rcvd.objet,mapList)
			(gad,type) = gadtype.split(',',1)
			retval = eval('encode_'+type+'('+str(value)+')')
			command = (["/usr/local/bin/groupwrite", 'ip:'+config.get('knx','gateway'),gad]+retval )
			result = subprocess.check_output(command)
			print time.strftime('%d/%m/%y %H:%M:%S',time.localtime()),':',"setting ",mapList," Value ",value, command, result
	sys.stdout.flush()
	i +=1
	time.sleep(timer)
sock.close()

