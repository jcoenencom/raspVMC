#!/bin/bash
cp VMC.py /usr/lib/pymodules/python2.7/VMC.py
cp server.py ..
chown pi ../server.py
chmod a+x ../server.py

cp client?.py ../
chown pi ../client?.py
chmod a+x ../client?.py

cp VMC?.html /var/www
chown pi /var/www/VMC?.html

cp *.cgi /usr/lib/cgi-bin
chown pi /usr/lib/cgi-bin/VMC*.cgi
chmod a+x /usr/lib/cgi-bin/VMC*.cgi

cp -r json* /var/www
chown -R pi /var/www/json*


