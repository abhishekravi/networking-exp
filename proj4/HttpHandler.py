import sys
from urlparse import urlparse
from tcpHandler import TCPHandler

#http handler class
class HttpHandler:
	
	#constructor method 
  def __init__(self,main_url):
    self.hostname = urlparse(main_url).hostname
    self.path = urlparse(main_url).path
    self.req = "GET " + self.path + \
               " HTTP/1.1\n" + \
               "Host: " + self.hostname + \
               "\n\n"
  
	#method to get the socket
  def getSocket(self):
		tcp = TCPHandler(self.hostname)
		return tcp

	#method to send and recieve data
  def sendRecv(self):
		s = self.getSocket()
		recvBuff = ""
		sent = s.send(self.req)
		if sent:
			recvBuff = s.receive()
		else:
			print("connection failed")
		return recvBuff

#method to write the data to a file
def writeToFile(data,url):	
		name = getName(url)    
		f = open(name, "w")
		f.write(data)
		f.close

#method to get the file name
def getName(url):
  if url.endswith('/'):
    fil='index.html'
  else:
	  parts = url.split('/')
	  fil=parts[len(parts) - 1]
  return fil

#main method to execute the program
def http():
	#check if input is proper
	if(len(sys.argv) == 2):
		url = sys.argv[1]
		ht=HttpHandler(url)
		#send and receive the data
		data = ht.sendRecv()
		#terminate if http status code is not 200
		if getStatus(data) == '200':
			writeToFile(getContent(data), url)
		else:
			print("http error with status code:" + getStatus(data))
	else:
		print("expected input: [URL]")

#get the http status code from the response
def getStatus(data):
	return data[9:12]

#get the content to be written from the response
def getContent(data):
	return data[data.find("\n\r")+3:]

#call main method
http()

