from socket import *
from struct import *
from ipHandler import *
from random import randint
import common
import time


#re-transmit time in seconds
RT = 60
#timeout in seconds
TIMEOUT = 60

# class to hold tcp header data
class TCPHeader:
  
  def __init__(self):
    self.tcp_s_port=0                 #sender port
    self.tcp_d_port=80								#destination port
    self.tcp_seq_num=0								#seq number
    self.tcp_ack_num=0								#ack number
    self.tcp_doffset=5								#data offset
    self.tcp_flag_fin=0								#fin flag
    self.tcp_flag_syn=0								#syn flag
    self.tcp_flag_rest=0							#rest flag
    self.tcp_flag_psh=0								#push flag
    self.tcp_flag_ack=0								#ack flag
    self.tcp_flag_urg=0								#urgent flag
    self.tcp_window_size=htons(65535)	#window size
    self.tcp_checksum=0								#checksum
    self.tcp_urg_ptr=0								#urgent priority

#TCP handler class
class TCPHandler:
	
	#Constructor method for tcp handler  
	def __init__(self,host):
		self.iph = IpHandler(host) 								#ip layer handling object
		self.host = host 													#host to connect to 
		self.destPort = 80 												# destination port
		self.sendPort = randint(1024, 65530) 			#generates random port each time prigram is run
		self.destIP = socket.gethostbyname(host) 	# get ip to which packet has to be sent to
		self.srcIP = common.getLocalIP() 					# local ip address
		self.sequence = randint(0,66536) 					#current sequence
		self.expectedSeq = 0											#exprected sequence from server
		self.expectedAck = 0											#expected ack from server
		self.ack = 0															#current ack
		self.prevRequest = ""											#prev request
		self.cwnd= 1															#congestion window

	#method to send TCP packet
	def send(self,data):
		#performing 3 way handshake to establish connection
		success =	self.negotiateConn()
		if success:
			#sending http request
			request = self.createNewPacket(False,False,False,data)
			self.iph.createOutgoing(request,self.destIP)
			self.sequence += len(data)
			self.expectedAck = self.sequence
			self.prevRequest = request
			#receiving ack for request sent
			raw = self.receiveRaw()
			hdr = self.getHeader(raw)
			if hdr.tcp_ack_num == self.expectedAck:
				ret = True
		else:
			ret = False
		return ret


	#method to send ack
	def sendAck(self):
		request = self.createNewPacket(False,True,False,"")
		if(self.cwnd < 1000):
			self.cwnd +=1
		self.iph.createOutgoing(request,self.destIP)

	#method to send fin
	def sendFin(self):
		request = self.createNewPacket(False,False,True,"")
		self.iph.createOutgoing(request,self.destIP)

	#method to perform 3 way handshake with server
	def negotiateConn(self):
		st = round(time.time())		
		#creating syn
		request = self.createNewPacket(True,False,False,"")
		self.iph.createOutgoing(request,self.destIP)
		#get syn/ack
		raw_data = self.receiveRaw()
		tcpHdr = self.getHeader(raw_data)
		connected= False
		while True:
			if (self.sequence + 1) == tcpHdr.tcp_ack_num:
				connected = True				
				self.cwnd+=1
				break
			if (round(time.time()) - st) >= TIMEOUT:
				self.cwnd=1
				break
			self.iph.createOutgoing(request,self.destIP)
			raw_data = self.receiveRaw()
			tcpHdr = self.getHeader(raw_data)
		if connected:
			self.ack = tcpHdr.tcp_seq_num + 1
			self.sequence += 1
			#sending ack for syn/ack
			self.sendAck()
			self.expectedSeq = self.ack
		return connected
	
	#create a tcp packet
	def createNewPacket(self,synf,ackf,fin,payload):
		hdr = TCPHeader()		
		hdr.tcp_s_port = self.sendPort
		hdr.tcp_d_port = self.destPort
		hdr.tcp_seq_num = self.sequence
		hdr.tcp_ack_num = self.ack
		hdr.tcp_flag_ack = 1
		#for syc packet
		if synf:
			hdr.tcp_flag_syn = 1
			hdr.tcp_flag_ack = 0
			hdr.tcp_seq_num = self.sequence

		#for ack packet
		if fin:
			hdr.tcp_flag_fin = 1
	
		tcp_off_rest= (hdr.tcp_doffset << 4) + 0
		tcp_flags = hdr.tcp_flag_fin + \
                (hdr.tcp_flag_syn << 1) + \
                 (hdr.tcp_flag_rest << 2) + \
                 (hdr.tcp_flag_psh <<3) + \
                 (hdr.tcp_flag_ack << 4) + \
                 (hdr.tcp_flag_urg << 5)
		tcp_hdr = pack('!HHLLBBHHH', hdr.tcp_s_port, hdr.tcp_d_port, hdr.tcp_seq_num, hdr.tcp_ack_num, tcp_off_rest, tcp_flags,  
                    hdr.tcp_window_size, 
                    hdr.tcp_checksum,
                    hdr.tcp_urg_ptr)
		
		#pseudo header part		
		so_addr = socket.inet_aton(self.destIP)
		des_addr = socket.inet_aton(self.srcIP)
		placeholder = 0
		prot = socket.IPPROTO_TCP
		tcp_len = len(tcp_hdr) + len(payload)
		pse_header=pack('!4s4sBBH', so_addr, des_addr, placeholder, prot, tcp_len)
		#calculate the checksum		
		hdr.tcp_checksum = common.checksum(pse_header + tcp_hdr + payload)
		#construct the header with checksum
		tcp_header=pack('!HHLLBBH' , hdr.tcp_s_port,hdr.tcp_d_port,hdr.tcp_seq_num,hdr.tcp_ack_num, tcp_off_rest,      
                      tcp_flags,hdr.tcp_window_size) + \
                      pack('H',hdr.tcp_checksum) + \
                      pack('!H',hdr.tcp_urg_ptr)
		#return the constructed tcp packet
		self.expectedAck = self.sequence + len(payload)
		return tcp_header + payload

	#receive raw pakcet
	def receiveRaw(self):
		raw = 	self.iph.processRecvd()	
		return raw
		
	#method to receive data
	def receive(self):
		st = round(time.time())
		payload = ""
		while True:		
			rawData = self.receiveRaw()
			hdr = self.getHeader(rawData)
			#drop packet if wrong port			
			if hdr.tcp_d_port != self.sendPort:
				continue
			#check if packet is valid by checking checksum and expected sequence
			if self.validPacket(hdr,rawData,st):
				dataSize=(hdr.tcp_doffset) * 4 			
				payload += rawData[dataSize:]
				self.ack += len(rawData[dataSize:])
				self.expectedSeq = self.ack
				self.sendAck()
			else:
				#when we haven't gotten the expected packet or checksum is not valid
				self.sendAck()
				continue
			#server communication completed
			if(hdr.tcp_flag_fin == 1):
				self.sequence += 1
				self.ack += 1
				self.sendAck()
				self.sendFin()
				break
		return payload

	#method to validate checksum and check the seqnum
	def validPacket(self,hdr,rawData,st):
		chkvalid = self.validateChecksum(hdr,rawData)
		seqvalid = self.checkSequence(hdr,st)
		return chkvalid and seqvalid
	
	#check expected sequence num
	def checkSequence(self,hdr,st):
		if self.expectedSeq == hdr.tcp_seq_num:
			return True
		else:		
			#retransmit packet if proper ack not received		
			self.cwnd = 1			
			if((round(time.time()) - st) >= RT):
				self.iph.createOutgoing(self.prevRequest,self.destIP)
		return False

			
	#method to validate checksum
	def validateChecksum(self,hdr,rawData):
		valid = False		
		pseudoHeader = pack('!4s4sBBH',
                                    socket.inet_aton(self.srcIP),
                                    socket.inet_aton(self.destIP),
                                    0,
                                    socket.IPPROTO_TCP,  
                                    len(rawData))
		valid = common.checksum(pseudoHeader + rawData) == 0
		return valid

	#method to deconstruct a TCP packet
	def getHeader(self,packt):
		tcpHead = TCPHeader()
		tcpVals = unpack('!HHLLBBH' , packt[0:16])
		tcpHead.tcp_s_port = tcpVals[0]
		tcpHead.tcp_d_port = tcpVals[1]
		tcpHead.tcp_seq_num = tcpVals[2]
		tcpHead.tcp_ack_num = tcpVals[3]
		tcp_off_rest = tcpVals[4]
		tcp_flags = tcpVals[5]
	
		tcpHead.tcp_doffset=tcp_off_rest >> 4
		
		tcpHead.tcp_flag_fin=tcp_flags & 0x01
		tcpHead.tcp_flag_syn=(tcp_flags & 0x02) >> 1
		tcpHead.tcp_flag_rest=(tcp_flags & 0x03) >> 2
		tcpHead.tcp_flag_psh=(tcp_flags & 0x04) >> 3
		tcpHead.tcp_flag_ack=(tcp_flags & 0x05) >> 4
		tcpHead.tcp_flag_urg=(tcp_flags & 0x06) >> 5
		return tcpHead


