#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
from VMC import VMC
import binascii
import re
import sys
import ConfigParser
import socket
import string
import time
import signal, os


class LOG:

# offset current line offset
# line_offset array with all line offset
# file = file handler
# lines = number of line in file

        def __init__(self,logfile):

		self.file = open(logfile,"rb")

		self.line_offset = []
		offset = 0
		self.lines=0
		for line in self.file:
			self.line_offset.append(offset)
    			offset += len(line)
			self.lines+=1
		self.file.seek(0)
		self.offset=0

	def readf(self):
		self.file.seek(self.line_offset[self.offset])
		line = self.file.readline()
		self.offset += 1
		if self.offset >= self.lines:
			self.offset=0		#rollover
		return line

	def readb(self):
		self.offset += -1
		if self.offset <0:
			self.offset=self.lines-1	# rollover
		self.file.seek(self.line_offset[self.offset])
		line = self.file.readline()
		return line
	def readpageup(self,lines):
		self.offset += lines
		if self.offset > self.lines:
			self.offset=self.lines
		self.file.seek(self.line_offset[self.offset])
		line = self.file.readline()
		return line
	def readpagedown(self,lines):
		self.offset -= lines
		if self.offset < 0:
			self.offset=0
		self.file.seek(self.line_offset[self.offset])
		line = self.file.readline()
		return line



def handler(signum, frame):
	print 'Signal handler called with signal', signum
	exit()

def resize(signum, frame):

	y, x = screen.getmaxyx()
	screen.clear()
	curses.resizeterm(y, x)
	screen.refresh()

def scan(dictionary, screen, row, col):
	tab = 25
	icol = col
	for key, value in dictionary.iteritems():
		if isinstance(value, dict):
			screen.move(row,icol)
			screen.clrtobot()
			screen.move(row,icol)
			screen.addstr(row,icol,str(key).ljust(32))
#			row+=1
			icol +=15
			row = scan(value, screen, row, icol)
			icol -=15
		else:
			screen.move(row+5,0)
			screen.clrtobot()
			screen.refresh()
			screen.addstr(row,icol,str(key).ljust(tab))
			try:
				screen.addstr(row,icol+tab,str(value).ljust(32))
			except  TypeError:
				screen.nodelay(0)
				event = screen.getch()
			row+=1
	screen.refresh()
	return row


pos={}

pos['Tairneuf']=4,0
pos['Tconfort']=3,10
pos['Textrait']=4,15
pos['Trepris']=5,15
pos['Tsoufflage']=5,0


signal.signal(signal.SIGALRM, handler)
signal.signal(signal.SIGWINCH,resize)


HFrame = re.compile('07f0([0-9a-f]+)070f')
RFrame = re.compile('sending .+')

realtime = False

config = ConfigParser.RawConfigParser()
config.read('/etc/VMC/VMC.ini')


if len(sys.argv)>=2:
	if sys.argv[1] == "RT":
		# Create a TCP/IP socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# Connect the socket to the port where the server is listening
		server_address = (string.replace(config.get('client','server'),'"',''),  int(string.replace(config.get('server','port'),'"','')))
		sock.connect(server_address)
		realtime = True
		if len(sys.argv) >2:
			args = sys.argv[2:]
		else:
			args=("FULL")

	elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
		print "\t"+sys.argv[0]+" -h --help : this information"
		print "\t"+sys.argv[0]+" logfile name : process the log file"
		print "\t"+sys.argv[0]+" no arguments process the log file specified in /etc/VMC/VMC.ini"
		print "\t"+sys.argv[0]+" RT : realtime, connects the server as specified in /etc/VMC/VMC.ini"
		print "\t+++++++++++++++++++++++++++++++++++++\nkeys usage"
		print "\t's': Step mode (stop), 'g' Run mode (go)"
		print "\t't' top, 'b' bottom, go to first or last line of log file"
		print "\t'f' forward, 'r' reverse read direction"
		print "\t'q' clean exit, if utility aborts use command tset or reset to reset terminal"
		print "\tarrow up/down go one line up/down in file, or get next reading in realtime"
		print "\tpage up/down go 40 log lines up/down"
		print "\tany key other than 'q', 's', 'g' will get a next reading in real time"
		print "\tRT additional parameters can be FULL TEMP FAN VALVES USAGE CONFIG INPUTS"
		exit()
	else:
	        logfile=str(sys.argv[1])
		file = LOG(logfile)
		line = file.readf()
		realtime=False
elif len(sys.argv) <= 1:
        logfile=config.get('DEBUG','log')
	file = LOG(logfile)
	line = file.readf()
	realtime=False


scr = curses.initscr()
global screen
screen = curses.newwin(86,100,0,0)

curses.start_color()
curses.init_pair(1,curses.COLOR_RED,curses.COLOR_YELLOW)
curses.init_pair(2,curses.COLOR_BLUE,curses.COLOR_GREEN)
curses.init_pair(3,curses.COLOR_RED,curses.COLOR_WHITE)
curses.noecho()
curses.curs_set(0)
screen.keypad(1)
if realtime:
	screen.addstr(0,0,"VMC realtime analyzer",curses.A_REVERSE)
else:
	screen.addstr(0,0,"VMC log analyzer, log file:"+logfile+" of "+str(file.lines)+" lines",curses.A_REVERSE)

screen.nodelay(0)


pagelen=40
reversecol=65
lineno=80
direction=1
dir={ 1:"forward", -1:"reverse" }

while True:
   if not realtime :
	screen.addstr(0,reversecol,dir[direction],curses.A_REVERSE)
        event = screen.getch()
        if event == ord("q"):
                        curses.endwin()
                        break
        elif event == ord("s"):
                        screen.nodelay(0)
        elif event == ord("g"):
                        screen.nodelay(1)
        elif event == ord("r"):
                        direction=-1
                        screen.addstr(0,reversecol,"reverse",curses.A_REVERSE)
        elif event == ord("f"):
                        screen.addstr(0,reversecol,"forward",curses.A_REVERSE)
                        direction=1
        elif event == 259:
                        #up arrow
                        line = file.readf()
        elif event == 258:
                        #down arrow
                        line = file.readb()
	elif event == 339:
			# page up
			line = file.readpageup(pagelen)
	elif event == 338:
			# page down
			line = file.readpagedown(pagelen)
	elif event == ord("t"):
			file.offset=file.lines-2
			line = file.readf()
	elif event == ord("b"):
			file.offset=0
			line = file.readf()
        else:
#                     screen.addstr(0,reversecol+10,str(event).ljust(5),curses.A_REVERSE)
                     event = 0
                     if direction == 1:
			line = file.readf()
		     else:
			line = file.readb()
	screen.addstr(0,lineno,"line #:"+str(file.offset).ljust(5),curses.A_REVERSE)
	result = HFrame.search(line)
	test = RFrame.search(line)
	temps = line[0:17]
	if result:
		hexframe = binascii.a2b_hex(result.group(1))
# check frame type if normal frame process it else just display command
		if (ord(hexframe[1])%2 != 1):
# line "sending to client" 
        	   if test:
			row=5
			col=0
			try:
				rcvd = VMC(hexframe)
			except IndexError:
#	IndexError detected in VMC class display frame and stop
				screen.addstr(3,0, "received at:"+temps+":"+result.group(1).ljust(64),curses.color_pair(3))
				screen.nodelay(0)
			screen.addstr(2,0,"Client frame:"+temps+":"+result.group(1).ljust(64),curses.color_pair(2))
			scan(rcvd.objet,screen,row,col)
			rcvd.clear()
# command frame just display command		         
		elif (ord(hexframe[1])%2 == 1):		
			hexframe = binascii.a2b_hex(result.group(1))
			command = binascii.hexlify(hexframe[1])
			screen.addstr(1,0,"Command frame: "+command.ljust(10)+" "+temps,curses.color_pair(1))

   else:
#realtime
	rcvd=VMC()
	screen.addstr(1,0,str(args)) 
	if "FULL" in args:
		rcvd.getAll(sock)
	if "TEMP" in args:
		rcvd.getalltemp(sock)
	if "FAN" in args:
		rcvd.getfanstatus(sock)
	if "BYPASS" in args:
		rcvd.getbypass(sock)
	if "INPUTS" in args:
		rcvd.getinputs(sock)
	if "VALVES" in args:
		rcvd.getvalve(sock)
	if "USAGE" in args:
		rcvd.getusage(sock)
	if "CONFIG" in args:
		rcvd.getconfig(sock)
		rcvd.getfanconfig(sock)
		rcvd.getdevinfo(sock)
		
	
	ms=time.time()
 	screen.addstr(2,0, "getting VMC info at "+time.strftime("%d/%m/%y %H:%M:%S.")+str(int(100*(ms - int(ms)))),curses.color_pair(1))
        scan(rcvd.objet,screen,5,0)
        rcvd.clear()
	event = screen.getch()
        if event == ord("q"):
                        curses.endwin()
                        break
        elif event == ord("s"):
                        screen.nodelay(0)
        elif event == ord("g"):
                        screen.nodelay(1)

