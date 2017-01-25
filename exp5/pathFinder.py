import socket
from urllib2 import *
import json
from math import sin, cos, sqrt, atan2, radians
import os.path

#dictionary of replicas with their geographical coordinates
replicas = {'52.0.73.113':[39.044,-77.488],'52.16.219.28':[53.333,-6.249],'52.11.8.29':[45.84,-119.701],'52.8.12.101':[37.339,-121.895],'52.28.48.84':[50.117,8.683],'52.68.12.77':[35.685,139.751],'52.74.143.5':[1.293,103.856],'52.64.63.125':[-33.867,151.208],'54.94.214.108':[-23.548,-46.637]}

GEOLINK = 'http://freegeoip.net/json/'

#port at which the performance readers should be running
serverPort = 60025

#class to hold performance data
class PerformanceData:
	def __init__(self, ip,latency,connectTime,dist):
		self.ip = ip
		self.latency = latency
		self.connectTime = connectTime
		self.distance = dist
		self.slat = 0
		self.slong = 0

#Path finder class
class PathFinder:
	def __init__(self):	
	# dictionary of client ip and the replica they should choose
		self.pathFrequency = {}
		self.paths={}
		self.initializePaths()

	#method to get the best replica
	def getBestPath(self,ip):
		data = getLocation(ip)
		self.slat = data['latitude']
		self.slong = data['longitude']
		bestpath = ""		
		if ip in self.paths:
			bestpath = self.getFromCache(ip)
		else:
			bestpath = self.getFromServers(ip)
		return bestpath

	
	#returns the best path from the cache	
	def getFromCache(self,ip):
		path = self.paths[ip]
		#if this client ip has been requested 50 times, then refresh the path next time by pinging the servers
		if(self.pathFrequency[ip] >= 50):
			self.paths.pop(ip)
			self.pathFrequency.pop(ip)
			self.updatePathsFile()
		else:
			self.pathFrequency[ip] = self.pathFrequency[ip] + 1
		return path

	#retruns the best path after pinging the servers
	def getFromServers(self,ip):
		performances = []
		#get performance data for all replica servers
		for r in replicas:
			performances.append(self.getPerformance(r,ip))
		#sort based on latency, connection time and geographical distance
		performances = sorted(performances, key=lambda perf: (perf.latency,perf.connectTime, perf.distance))
		bestPath = 	performances[0].ip
		self.paths[ip] = bestPath
		self.pathFrequency[ip] = 1
		self.updatePathsFile()
		return bestPath

	#update the paths file
	def updatePathsFile(self):
		f = open("paths.txt", "w")
		for p in self.paths:
			data = p + " " + self.paths[p] + "\n"
			f.write(data)
	
	#method to ping the performance program at servers to get their network performance info
	def getPerformance(self,host,ip):
		data = PerformanceData(host,'nil','nil','nil')
		#return path if already cached		
		try:
			s = socket.socket()         # Create a socket object
			s.connect((host, serverPort))
			s.send(ip)
			resp = s.recv(1024)
			info = resp.split(' ')
			try:
				data.latency = float(info[0])
				data.connectTime = float(info[1])
				data.distance = self.calculateDist(replicas[host][0],replicas[host][1])
			except ValueError:
				data.latency = 99999
				data.connectTime = 99999
				data.distance = self.calculateDist(replicas[host][0],replicas[host][1])
		except socket.error, err:
			print (err)
		finally:
			s.close()
		return data	

	#this method calculates the distance between two geographical coordinates in km
	def calculateDist(self, lat, lon):
		R = 6371; #in km
		dLat = radians(lat-self.slat)
		dLon = radians(lon-self.slong)
		lat1 = radians(self.slat)
		lat2 = radians(lat)
		a = sin(dLat/2) * sin(dLat/2) + sin(dLon/2) * sin(dLon/2) * cos(lat1) * cos(lat2)
		c = 2 * atan2(sqrt(a), sqrt(1-a))
		d = R * c
		return d
	
	#method to initialize paths already stored
	def initializePaths(self):
		if(os.path.exists("paths.txt")):
			f = open("paths.txt","r")
			while True:
				line = f.readline()
				if not line:
					break
				data = line.split(' ')
				self.paths[data[0]] = data[1].rstrip('\n')
				self.pathFrequency[data[0]] = 0
				
	
#this method gets the location of any given ip
def getLocation(ip):
	try:
		res=urlopen(GEOLINK + ip).read()
		loc=json.loads(res)
		return loc
	except:
		print("Error finding location")

