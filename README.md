# raspVMC
Software suite to interface a ventilation system (Zehnder, storkair) with external entities, multiples clients are handled
A server module interfaces with the ventilation unit via an SR232 (serial) connection
Clients connect to the server either via TCP/IP connection or via a virtual serial device provided by a socat instance (the later being use by clients such as FHEM, see www.fhem.de, Device comfoair)
The intend is to make it also available for hardware devices (Comfosense, CCEASE) connecting via another serial port.
A library is provided that takes care of the protocol.
The server and clients are written in Python.
Example clients are provided, command line client.py outputs a json structure with data read from the ventilation unit, VMCmysql.py reads a set of data and writes them to a mysql database, a set of web pages and associated cgi clients provide web access to the ventilation unit.


INSTALLATION

Download the code from Github

unzip it and run install.bash from the directory

The installation will install the following things

updates the libraries
install python-serial moddule
apache2 & php: the web server that will serve the ventilation pages
socat : serial connector, used to connect ConfSense unit and FHEM driver
FHEM: perl written domotica program (www.fhem.de), a VMC instance is provided (see on http:raspberry:8083/fhem?room=VMC)
      The software provides graphical display of periodically read temperatures and fans speed, it uses its own driver

A line is inserted in inittab to restart the program in case of crash

At the end of the install process "init q" is issued to fire up the server

stderr is redirected to /var/log/VMCerr.log (crash log)

Configuration file /etc/VMC/VMC.ini

Sections:

[VMC] defines the serial device where is attached the VMC

[mysql] defines the mysql (if used) information

[server]
bind => address responding to client (empty means all addresses)
port => port where clients connect, (sometime 10000 is used be web admin tool)

[client]
server => defines the address of the server for the clients, this is used by clients running on raspberry not running the server.

[socat]
PTY defines a virtual port to be used by FHEM

[CCEASE]
tty defines the serial device to which is attached the CCEASE/Confosense
port define the server port for the CCEASE connexion

[debug]
level defines the debug level
log defines the log file

[knx] definition of the knx interface
gateway eibd or eibnetmux gateway
followed by a list of variables from the json exemple
Tconfort=9/5/0,dpt9     use the json's Tconfort, write to bus GAD 9/5/0 using dpt9 encoding (temperature) 
