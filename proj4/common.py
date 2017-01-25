import socket
import fcntl
import struct

adapter = 'eth0' #this holds the name of the network interface we are using to connect

#method to calculate checksum
def checksum(msg):
	if len(msg) % 2 == 1:  # this message is of odd length
		msg += struct.pack('B', 0) #padding so that its length becomes even
	s = 0
    # loop taking 2 characters at a time
	for i in range(0, len(msg), 2):
		w = ord(msg[i]) + (ord(msg[i + 1]) << 8)
		s += w
	s = (s >> 16) + (s & 0xffff)
	s += s >> 16
    # complement and mask to 4 byte short
	s = ~s & 0xffff
	return s

#method to get local ip address
def getLocalIP(ifname = adapter):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	addr = socket.inet_ntoa(fcntl.ioctl(
		sock.fileno(),
		0x8915,  # SIOCGIFADDR
		struct.pack('256s', ifname[:15])
		)[20:24])
	return addr
