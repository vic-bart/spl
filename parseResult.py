from os import wait,path
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import sys,random,pickle
from util import *

motherload=readAll(sys.argv[1])
print(motherload[0])

print("total ins: ",len(motherload))
withConf=getConf(motherload)
print(f"{len(withConf)} has intial conflict")

maps=getMAP(motherload)
mergeAlgo=getAlgo(motherload)

print(f"all maps has: {maps}")
print(f"all algo has: {mergeAlgo}")
#["empty-8-8", "empty-16-16", "random-32-32-10", "warehouse-10-20-10-2-1"]
#mergeAlgo=["stop", "superMCP","MCP","Sub-OPTIMAL-P1","Sub-OPTIMAL","OPTIMAL"]
#mergeAlgo=["Sub-OPTIMAL-P1","Sub-OPTIMAL","OPTIMAL"]

maxDIF=-1
maxDIFID=-1
for mi,m in enumerate(maps):
    print(m)
    #plt.subplot(1,4,mi+1)
    if path.exists(f"{m}.bin"):
        with open(f"{m}.bin","rb") as f:
            final = pickle.load(f)
    else:
        localL = filterItem(motherload,lambda l: m in l["m"])
        IDXs,data=organizeIDX(localL,mergeAlgo)
        #final=scatterProcess(IDXs,data)
        final=difProcess(IDXs,data)
        with open(f"{m}.bin","wb") as f:
            pickle.dump(final,f)

    difPlot(final,plt,m)
    #scatterPlot(final,plt,m)

plt.tight_layout()
plt.show()
#plt.show()

print(maxDIFID,maxDIF)
temp=filterItem(motherload,byID(maxDIFID))
[print(i) for i in temp]
