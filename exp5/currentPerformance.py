import SocketServer
import commands
import socket
import time

#homeIP = '129.10.117.186'
serverPort = 60025
#method to get latency using scamper
def getLatency(ip):
	try:
		cmd = "scamper -c 'ping -c 1' -i " + ip + "|grep time="
		op = commands.getoutput(cmd)
		strs = op.split(' ')
		timeString = strs[len(strs) - 2].split('=')
		time = timeString[len(timeString)-1]
	except Exception:
		time = "na"
	return time

#method to find time taken to connect to the server
def timeToConnect(ip):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	startTime=time.time()
	try:
		s.connect((ip,22))
		endTime=time.time()
		ttc=str((endTime-startTime)*1000)
	except socket.error, err:
		print (err)
		ttc = "na"    
	finally:
		s.close()
	return ttc

#server handler method
class ServerHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		ip = self.request.recv(1024)
		latency = getLatency(ip)
		ttc = timeToConnect(ip)
		self.request.sendall(str(latency) + " " + str(ttc))

#server socket is created here
def	run():
	server = SocketServer.TCPServer(("", serverPort), ServerHandler)
	server.serve_forever()

run()
