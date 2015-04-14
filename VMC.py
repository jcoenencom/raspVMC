import binascii
import socket
import re

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

class VMC:

	global FFrame
	global escaped

	FFrame = re.compile(b'\x07\xf0([\x00-\xff]+)\x07\x0f')
	escaped = re.compile(b'\x07\x07')

#	def __init__(self, newframe):
#		if len(newframe) == 1 :
#			self.cmd = newframe
#			self.CFrame()		#create the frame from command code
#		else:
#			self.frame = newframe
#			self.cmd = newframe[1]
#			self.datalen = newframe[2]
#			self.ck = newframe[len(newframe)-1]
#			self.Checksum()		#verify the checksum
#			self.Payload()		#extract the payload
#			self.getvalue.get(self.cmd,self.default)(self)

	def __init__(self,*args):
		arg=list(args)		
		if len(args)==1:
			if len(arg[0]) == 1 :		#single single byte must be a no data command
				
                        	self.cmd = arg.pop(0)
                        	self.CFrame()           #create the frame from command code
                	else:				#more then a byte this is a frame
				newframe=arg[0]
	                        self.frame = escaped.sub(b'\x07',newframe)    #remove escaped 07
 				self.cmd = newframe[1]
                        	self.datalen = newframe[2]
          	                self.ck = newframe[len(newframe)-1]
                	        if self.Checksum():         #verify the checksum
                        		self.Payload()          #extract the payload when checksum OK
                   			self.getvalue.get(self.cmd,self.default)(self)
		elif  len(args)>1:			#more then one argument this is a command with data
			self.cmd = arg.pop(0)		#first argument is command byte
			self.datalen = len(arg)-1		#number of data byte is number of arguments
			self.CMFrame(*arg)		
	def clear(self):
		self.temperature.clear()
	def CFrame(self):
		self.ck = (173 + ord(self.cmd)) % 256
		self.frame=chr(0)+self.cmd+chr(0)+chr(self.ck)	#build a command frame NEED TO ESCAPE THE 07 !!!!
	def CMFrame(self,*arg):
		escaped = re.compile(b'\x07')
		sum = 173 + ord(self.cmd) + len(arg)
		frame = chr(0)+self.cmd+ chr(len(arg))
		for var in arg:
			sum+=ord(var)
			frame+=var
		self.ck=sum % 256
		frame += chr(self.ck)
		self.frame = frame
#escape.sub(b'\x07\x07',frame)      #finally replacee all 07 by 0707


	def HEXFrame(self):
		return(binascii.hexlify(self.frame))

	def FullFrame(self):
		FFR = b'\x07\xf0'+self.frame+b'\x07\x0f'
		return (FFR)

	def Checksum(self):
		sum=173			#start from 173
		for c in self.frame:
			sum+= ord(c)	# sumup all bytes
		sum -= ord(c)		#remove checksum from calculation
		checksum = chr(sum % 256)
		if checksum != self.ck:
			print 'Bad checksum, in frame ', binascii.hexlify(self.frame), ord(self.ck),'Calculated ', ord(checksum) 
			return -1
		else:
			return checksum

	def Payload(self):
		RFrame = re.compile(b'(.{4})(.{2})(.+)(.{2})')
		result = RFrame.search(binascii.hexlify(self.frame))
		self.payload=binascii.a2b_hex(result.group(3))
		return (self.payload)	

	def tempa(self):
                keys = ['Tairneuf', 'Tsoufflage', 'Trepris','Textrait']
                for i in range (0,4):
                        key=keys[i]
                        self.temperature[key]=float((ord(self.payload[i])/2)-20)
		self.objet['data']['temperature']=self.temperature
		return self.temperature
	def tempb(self):
		keys = ['Tconfort','Tairneuf', 'Tsoufflage', 'Trepris','Textrait']
		mode = ['absent','present']
		for i in range (0,5):
	                key=keys[i]
	                self.temperature[key]=float((ord(self.payload[i])/2)-20)
		ttemp = ord(self.payload[5])
		self.temperature['capteur']['Tairneuf'] = mode[ttemp&1]
		self.temperature['capteur']['Tsoufflage'] = mode[(ttemp&2)/2]
		self.temperature['capteur']['Trepris'] = mode[(ttemp&4)/4]
		self.temperature['capteur']['Textrait'] = mode[(ttemp&8)/8]
		self.temperature['capteur']['TEnthalpie'] = mode[(ttemp&16)/16]
		self.temperature['capteur']['Tapppoint'] = mode[(ttemp&32)/32]
		self.temperature['capteur']['Thotte'] = mode[(ttemp&64)/64]
		self.temperature['capteur']['Tenthaplie'] = float((ord(self.payload[6])/2)-20)
		self.temperature['capteur']['Tappoint'] = float((ord(self.payload[7])/2)-20)
		self.temperature['capteur']['Thotte'] = float((ord(self.payload[8])/2)-20)

		self.objet['data']['temperature']=self.temperature
		return(self.temperature)
	def firmware(self):
		self.objet['device']={'firmware':str(ord(self.payload[0]))+'.'+str(ord(self.payload[1])),'name':self.payload[3:]}
	def Rfanstatus(self):
		self.fanstatus['soufflagepourcent']=ord(self.payload[0])
		self.fanstatus['extraitpourcent']=ord(self.payload[1])
		self.fanstatus['soufflagerpm']=1875000/(ord(self.payload[2])*256+ord(self.payload[3]))
		self.fanstatus['extraitrpm']=1875000/(ord(self.payload[4])*256+ord(self.payload[5]))
		self.objet['data']['ventilateurs']=self.fanstatus
		return self.fanstatus
	def Gusage(self):
		self.usage['filtres']=ord(self.payload[15])*256+ord(self.payload[16])
		self.usage['vitesse1']=ord(self.payload[3])*256*256+ord(self.payload[4])*256+ord(self.payload[5])
		self.usage['vitesse2']=ord(self.payload[6])*256*256+ord(self.payload[7])*256+ord(self.payload[8])
		self.usage['absent']=ord(self.payload[0])*256*256+ord(self.payload[1])*256+ord(self.payload[2])
		self.usage['prechauffe']=ord(self.payload[11])*256+ord(self.payload[12])
		self.usage['antigel']=ord(self.payload[9])*256+ord(self.payload[10])
		self.usage['bypass']=ord(self.payload[13])*256+ord(self.payload[14])
		self.usage['vitesse3']=ord(self.payload[17])*256+ord(self.payload[18])
		self.objet['data']['usage']=self.usage
		return self.usage
	def Gbypass(self):
		mode=['hiver','ete']
		self.bypass['facteur']=ord(self.payload[2])
		self.bypass['periode']=ord(self.payload[3])
		self.bypass['correction']=ord(self.payload[4])
		self.bypass['mode']=mode[ord(self.payload[3])]
		self.objet['data']['bypass']=self.bypass
		return self.bypass
	def GConfig(self):
		type=['droit','gauche','undef']
		pres=['absent','present','non reglemente']
		taille=['petite','large','undef']
		status=['actif','-']
		self.config['prechauffage']=pres[ord(self.payload[0])]
		self.config['bypass']=pres[ord(self.payload[1])]
		self.config['type']=type[ord(self.payload[2])]
		self.config['taille']=taille[ord(self.payload[3])]
		self.config['enthalpie']=pres[ord(self.payload[9])]
		self.config['confofond']=pres[ord(self.payload[10])]
		temp=ord(self.payload[6])
		self.config['actif']['P10']=status[temp&1]
		self.config['actif']['P11']=status[(temp&2)/2]
		self.config['actif']['P12']=status[(temp&4)/4]
		self.config['actif']['P13']=status[(temp&8)/8]
		self.config['actif']['P14']=status[(temp&16)/16]
		self.config['actif']['P15']=status[(temp&32)/32]
		self.config['actif']['P16']=status[(temp&64)/64]
		self.config['actif']['P17']=status[(temp&128)/128]
		temp=ord(self.payload[7])
		self.config['actif']['P18']=status[temp&1]
		self.config['actif']['P19']=status[(temp&2)/2]
		temp=ord(self.payload[8])
		self.config['actif']['P90']=status[temp&1]
		self.config['actif']['P91']=status[(temp&2)/2]
		self.config['actif']['P92']=status[(temp&4)/4]
		self.config['actif']['P93']=status[(temp&8)/8]
		self.config['actif']['P94']=status[(temp&16)/16]
		self.config['actif']['P95']=status[(temp&32)/32]
		self.config['actif']['P96']=status[(temp&64)/64]
		self.objet['config']=self.config
	def Rfansettings(self):
		self.fansettings['extraction']['absent']=ord(self.payload[0])
		self.fansettings['extraction']['vitesse1']=ord(self.payload[1])
		self.fansettings['extraction']['vitesse2']=ord(self.payload[2])
		self.fansettings['extraction']['vitesse3']=ord(self.payload[10])
		self.fansettings['extraction']['actuel']=ord(self.payload[6])
                self.fansettings['admission']['absent']=ord(self.payload[3])
                self.fansettings['admission']['vitesse1']=ord(self.payload[4])
                self.fansettings['admission']['vitesse2']=ord(self.payload[5])
                self.fansettings['admission']['vitesse3']=ord(self.payload[11])
                self.fansettings['admission']['actuel']=ord(self.payload[7])
		self.fansettings['vitesse']=ord(self.payload[8])
		self.fansettings['extractionetat']=ord(self.payload[9])
		self.objet['config']['ventilateurs']=self.fansettings
	def Rvalvestat(self):
		etat = ['Ouvert','Ferme''Inconnu']
		self.valvesetat['bypass']=ord(self.payload[0])
		self.valvesetat['prechauff']=etat[ord(self.payload[1])]
		self.valvesetat['courantmoteurbypass']=ord(self.payload[2])
		self.valvesetat['courantmoteurprechauf']=ord(self.payload[3])
		self.objet['data']['valvesetat'] = self.valvesetat
	def Retatswitches(self):
		mode = ['OFF','ON']
		self.etatswitches['L1']=mode[ord(self.payload[0])&1]
		self.etatswitches['L2']=mode[(ord(self.payload[0])&2)/2]
		self.etatswitches['SDB']=mode[ord(self.payload[1]) & 1 ]
		self.etatswitches['hotte']=mode[ (ord(self.payload[1])&2)/2]
		self.etatswitches['SDBluxe']=mode[ (ord(self.payload[1])&16)/16]
		self.objet['data']['etatswitches']=self.etatswitches
	def GRSmode(self):
		mode=['No Connection','PC only','CCEASE only','PC Master','PC logmode']
#		self.RSmode = mode[int(math.log(ord(self.payload[0]), 2))]
		self.objet['config']['RS232Mode']=mode[ord(self.payload[0])]

	def erreurs(self):
		for i in range (0,17):
			self.erreurcodes[i+1]=binascii.hexlify(self.payload[i])
		self.objet['data']['erreurs']=self.erreurcodes




	def default(self,dummy):
		print "processing for frame ", binascii.hexlify(self.cmd), "not yet impelemented"

	def gettemp(self,socket):
		self.cmd = b'\x0f'
                self.CFrame()
		socket.sendall(self.FullFrame())
		data = socket.recv(64)
		if len(data) >0:
			result = FFrame.match(data)
			self.frame = result.group(1)
                        self.cmd = self.frame[1]
                        self.datalen = self.frame[2]
                        self.ck = self.frame[len(self.frame)-1]
			if self.Checksum():         #verify the checksum
				self.Payload()          #extract the payload when checksum OK
				self.getvalue.get(self.cmd,self.default)(self)
			
		return(self) 

        def getusage(self,socket):
                self.cmd = b'\xdd'
                self.CFrame()
                socket.sendall(self.FullFrame())
                data = socket.recv(64)
                if len(data) >0:
                        result = FFrame.match(data)
                        self.frame = result.group(1)
                        self.cmd = self.frame[1]
                        self.datalen = self.frame[2]
                        self.ck = self.frame[len(self.frame)-1]
                        if self.Checksum():         #verify the checksum
                                self.Payload()          #extract the payload when checksum OK
                                self.getvalue.get(self.cmd,self.default)(self)

                return(self)

        def getfanstatus(self,socket):
                self.cmd = b'\x0b'
                self.CFrame()
                socket.sendall(self.FullFrame())
                data = socket.recv(64)
                if len(data) >0:
                        result = FFrame.match(data)
                        self.frame = result.group(1)
                        self.cmd = self.frame[1]
                        self.datalen = self.frame[2]
                        self.ck = self.frame[len(self.frame)-1]
                        if self.Checksum():         #verify the checksum
                                self.Payload()          #extract the payload when checksum OK
                                self.getvalue.get(self.cmd,self.default)(self)

                return(self)

        def getalltemp(self,socket):
                self.cmd = b'\xd1'
                self.CFrame()
                socket.sendall(self.FullFrame())
                data = socket.recv(64)
                if len(data) >0:
                        result = FFrame.match(data)
                        if result:
				self.frame = result.group(1)
                        	self.cmd = self.frame[1]
                        	self.datalen = self.frame[2]
                        	self.ck = self.frame[len(self.frame)-1]
                        	if self.Checksum():         #verify the checksum
                                	self.Payload()          #extract the payload when checksum OK
                                	self.getvalue.get(self.cmd,self.default)(self)

                return(self)


        def getconfig(self,socket):
                self.cmd = b'\xd5'
                self.CFrame()
                socket.sendall(self.FullFrame())
                data = socket.recv(64)
                if len(data) >0:
                        result = FFrame.match(data)
                        self.frame = result.group(1)
                        self.cmd = self.frame[1]
                        self.datalen = self.frame[2]
                        self.ck = self.frame[len(self.frame)-1]
                        if self.Checksum():         #verify the checksum
                                self.Payload()          #extract the payload when checksum OK
                                self.getvalue.get(self.cmd,self.default)(self)

                return(self)

        def getfanconfig(self,socket):
                self.cmd = b'\xcd'
                self.CFrame()
                socket.sendall(self.FullFrame())
                data = socket.recv(64)
                if len(data) >0:
                        result = FFrame.match(data)
                        self.frame = result.group(1)
                        self.cmd = self.frame[1]
                        self.datalen = self.frame[2]
                        self.ck = self.frame[len(self.frame)-1]
                        if self.Checksum():         #verify the checksum
                                self.Payload()          #extract the payload when checksum OK
                                self.getvalue.get(self.cmd,self.default)(self)

                return(self)

        def getvalve(self,socket):
                self.cmd = b'\x0d'
                self.CFrame()
                socket.sendall(self.FullFrame())
                data = socket.recv(64)
                if len(data) >0:
                        result = FFrame.match(data)
                        self.frame = result.group(1)
                        self.cmd = self.frame[1]
                        self.datalen = self.frame[2]
                        self.ck = self.frame[len(self.frame)-1]
                        if self.Checksum():         #verify the checksum
                                self.Payload()          #extract the payload when checksum OK
                                self.getvalue.get(self.cmd,self.default)(self)
                return(self)

        def getdevinfo(self,socket):
                self.cmd = b'\x69'
                self.CFrame()
                socket.sendall(self.FullFrame())
                data = socket.recv(64)
                if len(data) >0:
                        result = FFrame.match(data)
                        self.frame = result.group(1)
                        self.cmd = self.frame[1]
                        self.datalen = self.frame[2]
                        self.ck = self.frame[len(self.frame)-1]
                        if self.Checksum():         #verify the checksum
                                self.Payload()          #extract the payload when checksum OK
                                self.getvalue.get(self.cmd,self.default)(self)

                return(self)

        def getinputs(self,socket):
                self.cmd = b'\x03'
                self.CFrame()
                socket.sendall(self.FullFrame())
                data = socket.recv(64)
                if len(data) >0:
                        result = FFrame.match(data)
                        self.frame = result.group(1)
                        self.cmd = self.frame[1]
                        self.datalen = self.frame[2]
                        self.ck = self.frame[len(self.frame)-1]
                        if self.Checksum():         #verify the checksum
                                self.Payload()          #extract the payload when checksum OK
                                self.getvalue.get(self.cmd,self.default)(self)

                return(self)
        def getbypass(self,socket):
                self.cmd = b'\xdf'
                self.CFrame()
                socket.sendall(self.FullFrame())
                data = socket.recv(64)
                if len(data) >0:
                        result = FFrame.match(data)
                        self.frame = result.group(1)
                        self.cmd = self.frame[1]
                        self.datalen = self.frame[2]
                        self.ck = self.frame[len(self.frame)-1]
                        if self.Checksum():         #verify the checksum
                                self.Payload()          #extract the payload when checksum OK
                                self.getvalue.get(self.cmd,self.default)(self)

                return(self)

	temperature=AutoVivification()
	erreurcodes={}
	fanstatus={}
	usage={}
	bypass={}
	config=AutoVivification()
	valvesetat={}
	etatswitches={}
	fansettings=AutoVivification()
	objet=AutoVivification()
	getvalue = {b'\x10':tempa,b'\xd2':tempb,b'\x68':firmware, b'\x6a':firmware,b'\x0c':Rfanstatus, b'\xde':Gusage, b'\xe0':Gbypass, b'\xd6':GConfig, b'\xce':Rfansettings, b'\68':firmware, b'\x0e':Rvalvestat, b'\x9c':GRSmode, b'\x04':Retatswitches, b'\xda':erreurs}
