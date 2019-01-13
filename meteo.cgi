#!/usr/bin/python
import json
import socket
import httplib

#web =httplib.HTTPConnection('localhost',8083)
#web =httplib.HTTPSConnection('jpco:jpc0@localhost:8083')
#web.request("GET","/fhem?cmd=jsonlist2%20TX3&XHR=1")
#resp=web.getresponse()
#io=StringIO(resp.read())

# exemple use the temperture measured on a TX3 sensor and read by fhem instance
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_address = ('127.0.0.1', 7072)
#sock.connect(server_address)
#sock.send('JsonList TX3\n')
#io=sock.recv(1024)
#TX3=json.loads(io)


print "Content-Type: text/plain"
print
# print "-" in case no sensor is implemented
print "-"

#print TX3['ResultSet']['Results']['READINGS']['temperature']['VAL']

