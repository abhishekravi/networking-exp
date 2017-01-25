import os 
variants=['Reno','SACK']
queueing=['RED', 'DropTail']
command_to_run_tcl="/course/cs4700f12/ns-allinone-2.35/bin/ns"

def runSimulations():
  ops = []
  for varnt in variants:
    for queue in queueing:
       command=command_to_run_tcl+" "+"experiment3.tcl"+" "+varnt+" "+queue
       os.system(command)
       expType = varnt+"_"+queue
       ops.append(readFile(expType))
  writeToOutput(ops)


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
  def __init__(self,variant,tcpTh,cbrTh,tcpL,cbrL):
    self.variant = variant
    self.tcpTh = tcpTh
    self.cbrTh = cbrTh
    self.tcpL = tcpL
    self.cbrL = cbrL

#method to read the trace file
def readFile(expType):
  f=open("output.tr","r")
  lines = []
  traces= []
  op = Output(expType,[],[],[],[])
  count=0
  startTime = 0
  lines = f.read().split('\n')
  f.close()
  for i in range(len(lines)):
    #filtering out empty lines
    if(lines[i] != ""):
      trace = Trace(lines[i])
      traces.append(trace)
  th = calculateThroughput(traces,op)
  latency = calculateLatency(traces,op)
  return op

def writeToOutput(ops):
  for i in range(len(ops)):
    f= open(ops[i].variant+".csv","w")
    for j in range(len(ops[i].tcpTh)):
      s=""
      s+=ops[i].variant
      s+=","
      s+=str(ops[i].tcpTh[j])
      s+=","
      s+=str(ops[i].cbrTh[j])
      s+=","
      s+=str(ops[i].tcpL[j])
      s+=","
      s+=str(ops[i].cbrL[j])
      s+="\n"
      f.write(s)
    f.close()

  
      
#method to calculate throughput in kbps
def calculateThroughput(traces,op):
  size = traces[0].size
  interval = 10
  intEndTime = 10
  startTime = traces[0].time
  endTime = 0
  numOfPackets = 0
  cbrSize = 0
  tcpSize = 0
  tcp = []
  cbr = []
  for i in range(len(traces)):
    if(traces[i].time > intEndTime or i == (len(traces)-1)):
       tcp.append(((8 * tcpSize) / interval)/1000)
       cbr.append(((8 * cbrSize) / interval)/1000)
       cbrSize = 0
       tcpSize = 0
       intEndTime += interval
    if(traces[i].event == "r" and traces[i].srcAddr =="0.0" and traces[i].destAddr =="3.0"):
      tcpSize += traces[i].size
    if(traces[i].event == "r" and traces[i].srcAddr =="4.0" and traces[i].destAddr =="5.0"):
      cbrSize += traces[i].size
  op.tcpTh = tcp
  op.cbrTh = cbr
  
  return op

#method to calculate latency
def calculateLatency(traces,op):
  intEndTime = 10
  interval = 10
  tcp = []
  cbr = []
  tcpStartTimes = {}
  cbrStartTimes = {}
  tcpEndTimes = {}
  cbrEndTimes = {}
  seqs = []
  for i in range(len(traces)):
    if(traces[i].time > intEndTime or i == (len(traces)-1)):
      totalTime = 0
      numOfPacks = 0
      for key in tcpStartTimes.viewkeys():
        if(key in tcpEndTimes.viewkeys()):
          seqs.append(key)
      for s in seqs:
        totalTime += tcpEndTimes.get(s) - tcpStartTimes.get(s)
        numOfPacks += 1
      if(numOfPacks == 0):
        tcp.append(0)
      else:
        tcp.append((totalTime/numOfPacks)*1000)
      
      seqs = []
      totalTime = 0
      numOfPacks = 0
      for key in cbrStartTimes.viewkeys():
        if(key in cbrEndTimes.viewkeys()):
          seqs.append(key)
      for s in seqs:
        totalTime += cbrEndTimes.get(s) - cbrStartTimes.get(s)
        numOfPacks += 1
      if(numOfPacks == 0):
        cbr.append(0)
      else:
        cbr.append((totalTime/numOfPacks)*1000)
      intEndTime += interval
      tcpStartTimes = {}
      cbrStartTimes = {}
      tcpEndTimes = {}
      cbrEndTimes = {}
      seqs = []
  
    if(traces[i].event == "+" and traces[i].flowid == "1" and traces[i].sendNode == "0"):
      tcpStartTimes.update({traces[i].seqNum : traces[i].time})
    if(traces[i].event == "r" and traces[i].flowid == "1" and traces[i].recNode == "0"):
      tcpEndTimes.update({traces[i].seqNum : traces[i].time})
    if(traces[i].event == "+" and traces[i].flowid == "2" and traces[i].sendNode == "4"):
      cbrStartTimes.update({traces[i].seqNum : traces[i].time})
    if(traces[i].event == "r" and traces[i].flowid == "2" and traces[i].recNode == "4"):
      cbrEndTimes.update({traces[i].seqNum : traces[i].time})
  op.tcpL = tcp
  op.cbrL = cbr
  return op

runSimulations()

