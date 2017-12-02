import sys
from PRM import dist

dataFile = open(sys.argv[1], "r")

dataText = dataFile.read()
prmDataText = []
rrtDataText = []
mode = 0
ctr = 0
for line in dataText.splitlines():
	if ctr == 5:
		ctr = 0
		if mode == 0:
			mode = 1
		else:
			mode = 0
	if line != "":
		if mode == 0:
			prmDataText.append(line)
		elif mode == 1:
			rrtDataText.append(line)
	ctr += 1

def parseData(dataText, data):
	for i in range(0, len(dataText), 4):
		pointsText = dataText[i].split(" ")
		data.append(dict(
			points = ((float(pointsText[2]), float(pointsText[3])), (float(pointsText[4]), float(pointsText[5]))),
			length = float(dataText[i + 3].split(" ")[2]),
			time = float(dataText[i + 2].split(" ")[2]),
			nodes = float(dataText[i + 1].split(" ")[2])
		))

prmData = []
parseData(prmDataText, prmData)
rrtData = []
parseData(rrtDataText, rrtData)

avgPRMTime = 0
avgPRMLengthPct = 0
avgRRTTime = 0
avgRRTLengthPct = 0
for i in range(len(prmData)):
	d = dist(prmData[i]["points"][0], prmData[i]["points"][1])
	avgPRMTime += prmData[i]["time"]
	avgPRMLengthPct += prmData[i]["length"] / d
	avgRRTTime += rrtData[i]["time"]
	avgRRTLengthPct += rrtData[i]["length"] / d
avgPRMTime /= len(prmData)
avgPRMLengthPct /= len(prmData)
avgRRTTime /= len(rrtData)
avgRRTLengthPct /= len(rrtData)
print "PRM Time (Average): " + str(avgPRMTime)
print "PRM Length / True Distance (Average): " + str(avgPRMLengthPct) 
print "RRT Time (Average): " + str(avgRRTTime)
print "RRT Length / True Distance (Average): " + str(avgRRTLengthPct)


