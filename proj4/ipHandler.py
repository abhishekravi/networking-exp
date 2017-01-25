import socket
import struct
import common
import sys

#class to handle ip layer operations
class IpHandler:

	#constructor where the raw socket is created	
	def __init__(self,host):
		try:
			self.sendSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
			self.recvSocket= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
			self.host = host
		except socket.error , msg:
			print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
			sys.exit()

	#method to create the ip header
	def getIPHeader(self, ip_id, ip_frag_off, ip_saddr, ip_daddr):
		return struct.pack( '!BBHHHBBH4s4s',	# the ! in the pack format string is for network byte order (big-endian)
		(4 << 4) + 5,	 					#ihl		
		0, 						 					#typeofservice		
		0, 					   					# kernel will fill the correct total length
		ip_id,			   					#Id of this packet
		ip_frag_off,						#fragment offset
		255,										#time to live
		socket.IPPROTO_TCP,			#protocol
		0,								    	# kernel will fill the correct checksum
		socket.inet_aton(ip_saddr),	  				  	#source address
		socket.inet_aton(ip_daddr))								#dest address
	
	#method to process received packets
	def processRecvd(self):
		raw_packet = ""		
		while True:
			raw_packet = self.recvSocket.recv(65535)
			if (self.checkPacket(raw_packet)):
				break;
		payload = raw_packet[20:]
		return payload

	#check if the ip addresses are proper and validate checksum
	def checkPacket(self,response):
		ret = False		
		ip_header = response[0:20]
		iph = struct.unpack('!BBHHHBBH4s4s' , ip_header)
		s_addr = socket.inet_ntoa(iph[8]);
		d_addr = socket.inet_ntoa(iph[9]);
		if (d_addr == common.getLocalIP() and s_addr == socket.gethostbyname(self.host)):
			ret = True and 	common.checksum(ip_header) == 0
		return ret

	#method to create outgoing packet and send it through
	def createOutgoing(self, payload, dest):
		ip_header = self.getIPHeader(23434, 16384, common.getLocalIP(), dest)
		packet = ip_header + payload
		self.sendSocket.sendto(packet,(dest, 80))

