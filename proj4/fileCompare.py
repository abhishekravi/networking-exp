import sys
import hashlib

#compares files line by line
def compareFiles():
	if(len(sys.argv) == 3):	
		f1 = open(sys.argv[1],"r")
		f2 = open(sys.argv[2],"r")
		diff = True
		while True:
			line1 = f1.readline()
			line2 = f2.readline()
			if not line1 and not line2:
				break		
			if line1 != line2:
				diff = False
				break
		print("same?:" , diff)
		print("md5 checksum same?",compareMd())
	else:
		print("expected input: [file1 name] [file2 name]")

def compareMd():
	mdm1 = hashlib.md5(open(sys.argv[1], 'r').read()).hexdigest()
	mdm2 = hashlib.md5(open(sys.argv[2], 'r').read()).hexdigest()
	return mdm1 == mdm2
		
compareFiles()
