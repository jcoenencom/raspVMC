#!/usr/bin/python

import ConfigParser
import glob

config = ConfigParser.RawConfigParser()

# When adding sections or items, add them in the reverse order of
# how you want them to be displayed in the actual file.
# In addition, please note that using RawConfigParser's and the raw
# mode of ConfigParser's respective set functions, you can assign
# non-string values to keys internally, but will receive an error
# when attempting to write to a file or when you get it in non-raw
# mode. SafeConfigParser does not allow such assignments to take place.


yesno=['Y', 'N']

TTYs=glob.glob('/dev/tty????')

i=0

for dev in TTYs:
        print i,': ',dev
        i+=1

VDEV=i
while (VDEV>=i):
        VDEV=input("Select the device connecting the VMC to the raspberry pi: ")

print 'ConfoSense connected on device ',TTYs[VDEV]

config.add_section('VMC')
config.set('VMC','device',TTYs[VDEV])

i=0

for dev in TTYs:
	if (i!=VDEV):
		print i,': ',dev
		i+=1
print i,': Do not use Confosense'
CDEV=i+1
while (CDEV>i):
	CDEV=input("Select the device connecting the ConfoSense to the raspberry pi: ")

if (CDEV != i):
	print 'ConfoSense connected on device ',TTYs[CDEV]
	config.add_section('ConfoSense')
	config.set('ConfoSense', 'Ctty', TTYs[CDEV])

bind=raw_input("server bind address (nothing for all): ")
port=raw_input("server port number (default 10000): ")

if (port is ''):
	port=10000

config.add_section("server")
config.set('server', 'bind', bind)
config.set('server','port',port)

ctrlport=raw_input("enter port number for telnet remote control (def=10002):")
if (ctrlport is ''):
	ctrlport='10002'
config.add_section('control')
config.set('control','port',ctrlport)


server=raw_input("server address for clients (blank for this machine : ")
if (server is ''):
	server = '127.0.0.1'

config.add_section("client")
config.set('client', 'server', server)




socat='*'
while (socat not in yesno):
        socat=raw_input("Use socat to define virtual port (fhem client) (Y/N): ")
if (socat is 'Y'):
	virtty=raw_input("Enter the Virtual port filename (def. /tmp/ttyVMC): ")
	if (virtty is ''):
		virtty='/tmp/ttyVMC'
	config.add_section('socat')
	config.set('socat','PTY',virtty)


logfile=raw_input("log file name (def=/var/log/VMClog.log): ")

if (logfile is ''):
	logfile='/var/log/VMClog.log'

level=raw_input("debug level (2=config, 3=client, 8=frames, def=3): ")

if (level is ''):
	level='3'
config.add_section('debug')
config.set('debug','log',logfile)
config.set('debug','level',level)

mysql='*'

while (mysql not in yesno):
	mysql=raw_input("Use mysql database to store data sample (Y/N): ")

if (mysql is 'Y'):
	host=raw_input("Mysql server address: ")
	username=raw_input("User name:")
	password=raw_input("Password: ")
	DB=raw_input("Data base name: ")
	config.add_section("mysql")
	config.set('mysql', 'host', host)
	config.set('mysql', 'user', username)
	config.set('mysql', 'password',password)
	config.set('mysql', 'DB',DB)


with open('VMC.ini.new', 'wb') as configfile:
    config.write(configfile)
