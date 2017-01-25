import os 
variants=[['Reno','Reno'],['NewReno','Reno'],['Vegas','Vegas'],['NewReno','Vegas']]
timings=[['1.0','1.0'],['1.0','10.0'],['10.0','1.0']]
command_to_run_tcl="/course/cs4700f12/ns-allinone-2.35/bin/ns"

def runSimulations():
  ops = []
  for varnts in variants:
    for rate in range(1,10):
        for times in timings:
            op = []
            command=command_to_run_tcl+" "+"experiment2.tcl"+" "+varnts[0]+" "+varnts[1]+" "+str(rate)+" "+times[0]+" "+times[1]
            os.system(command)
            expType = varnts[0]+"_"+varnts[1]+"_"+str(rate)+"_"+times[0]+"_"+times[1]+":"
            op.append(readFile(expType, times[0],times[1],AvgOutput(varnts[0],varnts[1],rate,0,0,0,0,0,0)))
        ops.append(getAverage(op))
  writeToOutput(ops)

def getAverage(op):
  ret = AvgOutput(op[0].var1,op[0].var2,op[0].rate,0,0,0,0,0,0)
  temp1 = 0
  temp2 = 0
  for o in op:
    temp1 += o.th1
    temp2 += o.th2
  ret.th1 = temp1 / len(op)
  ret.th2 = temp2 / len(op)
  temp1 = 0
  temp2 = 0
  for o in op:
    temp1 += o.dr1
    temp2 += o.dr2
  ret.dr1 = temp1 / len(op)
  ret.dr2 = temp2 / len(op)
  temp1 = 0
  temp2 = 0
  for o in op:
    temp1 += o.l1
    temp2 += o.l2
  ret.l1 = temp1 / len(op)
  ret.l2 = temp2 / len(op)
  return ret

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
  def __init__(self,var1,var2,rate,th1,dr1,l1,th2,dr2,l2):
    self.var1 = var1
    self.var2 = var2
    self.rate = rate
    self.th1 = th1
    self.dr1 = dr1
    self.l1 = l1
    self.th2 = th2
    self.dr2 = dr2
    self.l2 = l2


#method to read the trace file
def readFile(expType,time1,time2,op):
  f=open("output.tr","r")
  lines = []
  traces= []
  count=0
  startTime = 0
  lines = f.read().split('\n')
  f.close()
  for i in range(len(lines)):
    #filtering out empty lines and cbr data
    if(lines[i] != "" and (lines[i].split(" ")[7] == "1" or lines[i].split(" ")[7] == "2")):
      trace = Trace(lines[i])
      traces.append(trace)
  calculateThroughput(traces,time1,time2,op)
  droprate = calculateDroprate(traces,op)
  traces = sorted(traces, key=lambda trace: (trace.flowid,trace.seqNum ,trace.time))
  latency = calculateLatency(traces,op)
  return op

def writeToOutput(ops):
  f = open("exp2_output", "w")
  for i in range(len(ops)):
    s=""
    s+=ops[i].var1
    s+=","
    s+=ops[i].var2
    s+=","
    s+=str(ops[i].rate)
    s+=","
    s+=str(ops[i].th1)
    s+=","
    s+=str(ops[i].th2)
    s+=","
    s+=str(ops[i].dr1)
    s+=","
    s+=str(ops[i].dr2)
    s+=","
    s+=str(ops[i].l1)
    s+=","
    s+=str(ops[i].l2)
    s+="\n"
    f.write(s)
  f.close()
  f = open("exp2_output_th", "w")
  for i in range(len(ops)):
    s=""
    s+=ops[i].var1
    s+=","
    s+=ops[i].var2
    s+=","
    s+=str(ops[i].rate)
    s+=","
    s+=str(ops[i].th1)
    s+=","
    s+=str(ops[i].th2)
    s+="\n"
    f.write(s)
  f.close()
  f = open("exp2_output_dr", "w")
  for i in range(len(ops)):
    s=""
    s+=ops[i].var1
    s+=","
    s+=ops[i].var2
    s+=","
    s+=str(ops[i].rate)
    s+=","
    s+=str(ops[i].dr1)
    s+=","
    s+=str(ops[i].dr2)
    s+="\n"
    f.write(s)
  f.close()
  f = open("exp2_output_l", "w")
  for i in range(len(ops)):
    s=""
    s+=ops[i].var1
    s+=","
    s+=ops[i].var2
    s+=","
    s+=str(ops[i].rate)
    s+=","
    s+=str(ops[i].l1)
    s+=","
    s+=str(ops[i].l2)
    s+="\n"
    f.write(s)
  f.close()


  
      
#method to calculate throughput in kbps
def calculateThroughput(traces,time1,time2,ops):
  size1 = 0
  size2 = 0
  startTime1 = 50
  startTime2 = 50
  endTime1 = 0
  endTime2 = 0

  for i in range(len(traces)):
    if(traces[i].flowid == "1"):
      if(traces[i].event == "+" and traces[i].sendNode=="0"):
	if(traces[i].time < startTime1):
          startTime1 = traces[i].time
      if(traces[i].event == "r" and traces[i].srcAddr =="0.0" and traces[i].destAddr =="3.0"):
        size1 += traces[i].size * 8
        endTime1 = traces[i].time
    if(traces[i].flowid == "2"):
      if(traces[i].event == "+" and traces[i].sendNode=="4"):
	if(traces[i].time < startTime2):
          startTime2 = traces[i].time
      if(traces[i].event == "r" and traces[i].srcAddr =="4.0" and traces[i].destAddr =="5.0"):
        size2 += traces[i].size * 8
        endTime2 = traces[i].time
  ops.th1 = (size1  /(endTime1 - startTime1))/ 1000
  ops.th2 = (size2  /(endTime2 - startTime2))/ 1000
  return ops

#method to calculate droprate
def calculateDroprate(traces,op):
  totalSent1 = 0
  totalSent2 = 0
  totalRec = 0
  totalDrop1 = 0
  totalDrop2 = 0
  dropRate = 0
  for i in range(len(traces)):
    if(traces[i].flowid == "1"):
      if(traces[i].event == "+" and traces[i].sendNode=="0"):
        totalSent1 += 1
      if(traces[i].event == "d"):
        totalDrop1 += 1
      if(traces[i].event == "r" and traces[i].packType=="tcp" and traces[i].sendNode=="2"):
        totalRec += 1
    if(traces[i].flowid == "2"):
      if(traces[i].event == "+" and traces[i].sendNode=="4"):
        totalSent2 += 1
      if(traces[i].event == "d"):
        totalDrop2 += 1
      if(traces[i].event == "r" and traces[i].packType=="tcp" and traces[i].sendNode=="2"):
        totalRec += 1
  op.dr1 = float(totalDrop1)/float(totalSent1)
  op.dr2 = float(totalDrop2)/float(totalSent2)
  return op

#method to calculate latency
def calculateLatency(traces,op):
  totalTime1 = 0
  numOfPacks1 = 0
  start1 = 0
  totalTime2 = 0
  numOfPacks2 = 0
  start2 = 0

  for i in range(len(traces)):
    if(traces[i].flowid == "1"):
      if(traces[i].event == "+" and traces[i].packType == "tcp" and traces[i].sendNode=="0"):
        start1 = traces[i].time
      if(traces[i].event == "r" and traces[i].recNode=="0"):
        if((traces[i].time - start1) > 0):
          totalTime1 += traces[i].time - start1
          numOfPacks1 +=1

    if(traces[i].flowid == "2"):
      if(traces[i].event == "+" and traces[i].packType == "tcp" and traces[i].sendNode=="4"):
        start2 = traces[i].time
      if(traces[i].event == "r" and traces[i].recNode=="4"):
        if((traces[i].time - start2) > 0):
          totalTime2 += traces[i].time - start2
          numOfPacks2 +=1

  #numOfLostPack = numOfPacks - numOfPackRec
  op.l1 = float(totalTime1/numOfPacks1) * 1000
  op.l2 = float(totalTime2/numOfPacks2) * 1000
  return op

runSimulations()

