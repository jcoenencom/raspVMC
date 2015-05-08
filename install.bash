#!/bin/bash

#install apache and socat

apt-get update
apt-get install apache2 socat

#cleanup libraries
rm /usr/lib/pymodules/python2.7/VMC.*
cp VMC.pyc /usr/lib/pymodules/python2.7/
cp VMC.py /usr/lib/pymodules/python2.7/

#server in /home/pi
cp server.py ..
chown pi ../server.py
chmod a+x ../server.py

#clients in /home/pi
cp client?.py ../
chown pi ../client?.py
chmod a+x ../client?.py


#html pages in /var/www
cp VMC?.html /var/www
chown pi /var/www/VMC?.html

#cgi's in  apache default dir
cp *.cgi /usr/lib/cgi-bin
chown pi /usr/lib/cgi-bin/VMC*.cgi
chmod a+x /usr/lib/cgi-bin/VMC*.cgi

#include libraries for json display in web pages
cp -r json* /var/www
chown -R pi /var/www/json*

#configuration file
if [ ! -d "/etc/VMC" ]; then 
    mkdir "/etc/VMC"
fi

cp VMC.ini /etc/VMC/

