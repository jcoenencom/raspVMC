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

TTYs=glob.glob('/dev/tty????')

i=0

for dev in TTYs:
        print i,': ',dev
        i+=1

VDEV=i
while (VDEV>=i):
        VDEV=input("Select the device connecting the VMC to the raspberry pi:")

print 'ConfoSense connected on device ',TTYs[VDEV]

config.add_section('VMC')
config.set('VMC','device',TTYs[VDEV])

i=0

for dev in TTYs:
	if (i!=VDEV):
		print i,': ',dev
		i+=1

CDEV=i
while (CDEV>=i):
	CDEV=input("Select the device connecting the ConfoSense to the raspberry pi:")

print 'ConfoSense connected on device ',TTYs[CDEV]


config.add_section('ConfoSense')
config.set('ConfoSense', 'Ctty', TTYs[CDEV])

# Writing our configuration file to 'example.cfg'
with open('VMC.ini.new', 'wb') as configfile:
    config.write(configfile)
