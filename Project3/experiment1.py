import os
variants=['Tahoe','Reno','NewReno','Vegas']
timings=[['1.0' ,'1.0'], ['5.0','1.0'],['1.0','5.0']]
command_to_run_tcl="/course/cs4700f12/ns-allinone-2.35/bin/ns"

def runSimulations():
  op = []
  for varnts in variants:
    for rate in range(1,10):
      ops = []  
      for times in timings:
            command=command_to_run_tcl+" "+"experiment1.tcl"+" "+varnts+" "+str(rate)+" "+times[0]+" "+times[1]
            os.system(command)
            expType = varnts+"_"+str(rate)+"_"+times[0]+"_"+times[1]+":"
            ops.append(readFile(varnts,rate,float(times[1])))
      getAverage(ops,op)
  writeToOutput(op)

def getAverage(temp,main):
  main.append(AvgOutput(temp[0].var,temp[0].rate,calcAvg(temp,"t"),calcAvg(temp,"d"),calcAvg(temp,"l")))

def calcAvg(temp,val):
  if(val == "t"):
    return (temp[0].th + temp[1].th + temp[2].th)/3
  if(val == "d"):
    return (temp[0].dr + temp[1].dr + temp[2].dr)/3
  if(val == "l"):
    return (temp[0].l + temp[1].l + temp[2].l)/3

    

#Trace class to hold trace data
class Trace:
  def __init__(self, line):
    traces = line.split(" ")
    self.event = traces[0]
    self.time = float(traces[1])
    self.sendNode = traces[2]
    self.recNode = traces[3]
    self.packType = traces[4]
    self.size = float(traces[5])
    self.flags = traces[6]
    self.flowid = traces[7]
    self.srcAddr = traces[8]
    self.destAddr = traces[9]
    self.seqNum = int(traces[10])
    self.packId = traces[11]

#class to hold the processed output values
class Output:
  def __init__(self,variant,throughput,droprate,latency):
    self.variant = variant
    self.throughput = throughput
    self.droprate = droprate
    self.latency = latency

class AvgOutput:
  def __init__(self,var,rate,th,dr,l):
    self.var = var
    self.rate = rate
    self.th = th
    self.dr = dr
    self.l = l

#method to read the trace file
def readFile(var,rate,time):
  f=open("output.tr","r")
  lines = []
  traces= []
  count=0
  startTime = 0
  lines = f.read().split('\n')
  f.close()
  for i in range(len(lines)):
    #filtering out empty lines and cbr data
    if(lines[i] != "" and lines[i].split(" ")[7] == "1"):
      trace = Trace(lines[i])
      traces.append(trace)
  th = calculateThroughput(traces,time)
  droprate = calculateDroprate(traces)

  #perform sort on the object list so that all seq numbers are grouped together
  traces = sorted(traces, key=lambda trace: (trace.seqNum ,trace.time))
  latency = calculateLatency(traces)
  return AvgOutput(var,rate,th,droprate,latency)

def writeToOutput(ops):
  f = open("exp1_output.csv", "w")
  for i in range(len(ops)):
    s=""
    s+=ops[i].var
    s+=","
    s+=str(ops[i].rate)
    s+=","
    s+=str(ops[i].th)
    s+=","
    s+=str(ops[i].dr)
    s+=","
    s+=str(ops[i].l)
    s+="\n"
    f.write(s)
  f.close()
  f = open("exp1_output_th.csv", "w")
  for i in range(len(ops)):
    s=""
    s+=ops[i].var
    s+=","
    s+=str(ops[i].rate)
    s+=","
    s+=str(ops[i].th)
    s+="\n"
    f.write(s)
  f.close
  f = open("exp1_output_dr.csv", "w")
  for i in range(len(ops)):
    s=""
    s+=ops[i].var
    s+=","
    s+=str(ops[i].rate)
    s+=","
    s+=str(ops[i].dr)
    s+="\n"
    f.write(s)
  f.close
  f = open("exp1_output_l.csv", "w")
  for i in range(len(ops)):
    s=""
    s+=ops[i].var
    s+=","
    s+=str(ops[i].rate)
    s+=","
    s+=str(ops[i].l)
    s+="\n"
    f.write(s)
  f.close


  
      
#method to calculate throughput in kbps
def calculateThroughput(traces,time):
  size = 0
  startTime = 50
  for i in range(len(traces)):
    if(traces[i].event == "+" and traces[i].sendNode=="0"):
	if(traces[i].time < startTime):
    		startTime = traces[i].time
    if(traces[i].event == "r" and traces[i].srcAddr =="0.0" and traces[i].destAddr =="3.0"):
      size += traces[i].size * 8
      endTime = traces[i].time
  return ( size  /(endTime - startTime))/1000

#method to calculate droprate
def calculateDroprate(traces):
  totalSent = 0
  totalRec = 0
  totalDrop = 0
  dropRate = 0
  for i in range(len(traces)):
    if(traces[i].event == "+" and traces[i].sendNode=="0"):
      totalSent += 1
    if(traces[i].event == "d"):
      totalDrop += 1
  dropRate = float(totalDrop)/float(totalSent)
  return dropRate

#method to calculate latency
def calculateLatency(traces):
  totalTime = 0
  numOfPacks = 0
  numOfPackRec = 0
  start = 0
  packId = ""
  for i in range(len(traces)):
    if(traces[i].event == "+" and traces[i].sendNode=="0"):
      start = traces[i].time
    if(traces[i].event == "r" and traces[i].recNode=="0"):
      if((traces[i].time - start) > 0):
        totalTime += traces[i].time - start
        numOfPacks +=1
  return float(totalTime/numOfPacks) * 1000

runSimulations()

