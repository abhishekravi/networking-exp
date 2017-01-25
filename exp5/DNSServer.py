import socket
import sys
import struct
from pathFinder import PathFinder

#DNS pack class contains all info needed to process and resolve queries
class DNSPack:
	#constructor class
	def __init__(self):
		#header
		self.id = 0
		self.flags = 0
		self.quesCount = 0
		self.ansRCount = 0
		self.nameServerCount = 0
		self.addRCount = 0
		#body
		self.query = ""
		self.qname = ""
		self.qtype = 0
		self.qclass = 0
		self.rawQuery = ""
	
	# this method converts the raw data into data the program can process
	def getData(self,raw):
		#header in first 12 bytes		
		header = raw[ :12 ]
		[self.id,
		self.flags,
		self.quesCount,
		self.ansRCount,
		self.nameServerCount,
		self.addRCount] = struct.unpack('>HHHHHH', header)
		payload = raw[ 12:]
		#extract data from last 4 bytes		
		[self.qtype, self.qclass] = struct.unpack('>HH', payload[-4:])
		self.rawQuery = rawQuestData = payload[:-4]
		index = 0
		acc = []
		#this part extracts the query from the raw data
		while True:
			currSize = ord(rawQuestData[index])
			if currSize == 0:
				break
			index += 1
			acc.append(rawQuestData[index:index + currSize])
			index += currSize
		self.qname = '.'.join(acc)
		
	#method which builds an answer to the query
	def resolveAddress(self,srcIP,pathfinder):
		ip = self.getIP(srcIP,pathfinder)
		self.ansRCount = 1
		self.flags = 0x8180
		header = struct.pack('>HHHHHH', self.id, self.flags,
                             self.quesCount, self.ansRCount,
                             self.nameServerCount, self.addRCount)
		query = self.rawQuery + struct.pack('>HH', self.qtype, self.qclass)
		ansName = 0xC00C
		ansType = 0x0001
		ansClass = 0x0001
		ttl = 60  # time to live
		len = 4
		ans = struct.pack( '>HHHLH4s', ansName, ansType, ansClass,
                          ttl, len, socket.inet_aton(ip));
		return header + query + ans

	#actual ip resolution happens here
	def getIP(self,srcIP,pathfinder):
		#logic to best replica delegated to pathFinder program
		return pathfinder.getBestPath(srcIP)

#server socket is created here
def	createServer(port,name):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(("", port))
	pathfinder = PathFinder()
	print "waiting on port:", port
	#keep running continuously	
	while True:
		data, addr = s.recvfrom(4096)
		dnsPack = DNSPack()
		dnsPack.getData(data)
		if(dnsPack.getIP != ""):
			s.sendto(dnsPack.resolveAddress(addr[0],pathfinder),addr)

#method to check the inputs
def checkInput(args):
	if(len(args) != 5):
		print("Invalid arguments. expected: -p <port> -n <name>")
		sys.exit()

#main method to run the program
def run():
	checkInput(sys.argv)
	port = sys.argv[2]
	name = sys.argv[4]
	print (port)
	print(name)
	createServer(int(port),name)

run()
