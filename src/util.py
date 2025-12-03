import matplotlib.cm as cm
import pickle
import random
#def findItem(L,idx):
#    return [l for l in L if l[0:4]==list(idx)]
mergeAlgo=None
colormap=None
markers=None

def readAll(fs):
    with open(fs) as f:
        keys = f.readline().strip().split(",")[:-1]
        keys = [k.strip() for k in keys]
        return [dict(zip(keys,list(map(conv,l.strip().split(",")[:-1])))) for l in f]

def conv(s):
    s=s.strip()
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s

def filterItem(L, cond):
    return [l for l in L if cond(l)]

def byID(idx):
    return lambda l: l.items() > idx.items()

def grabInsIDX(L):
    retval=[]
    for l in L:
        retval.append({"m":l["m"],"ins":l["ins"],"r":l["r"],"h":l["h"]})
    return retval

DUMMYID={"m":0,"ins":0,"r":0,"h":0}
def deID(l):
    return {k:v for k,v in l.items() if k not in DUMMYID}

def organizeIDX(localL,mergeAlgo):
    merge2i=lambda i:mergeAlgo.index(i)
    IDX2i=lambda i:IDXS.index(i)
    IDXS=grabInsIDX(localL)
    x=dict()
    '''
    for idx in IDXS:
        x[IDX2i(idx)]=[]
        for i in range(len(mergeAlgo)):
            x[IDX2i(idx)].append([])
    '''

    for idx in IDXS:
        tmp=filterItem(localL, byID(idx))
        #[print(i) for i in tmp]
        #print("lens",len(tmp), len(mergeAlgo))
        assert len(tmp)==len(mergeAlgo)

        sanity=[9999999 for _ in mergeAlgo ]
        final=[9999999 for _ in mergeAlgo ]
        for l in tmp:
            i=merge2i(l["mergeAlgo"])
            if l["mergeSOC"]:
                sanity[i]=l["mergeSOC"]
                final[i]=l
            #x[IDX2i(idx)][i].append(l["mergeSOC"])
            final[i]=deID(l)

        if 9999999 not in sanity:
            #assert sanityCheck(sanity,mergeAlgo)
            x[IDX2i(idx)]=final
        #dif=findDif(sanity)
        #dif=max(sanity)-min(sanity)
        #if dif and dif>maxDIF:
        #    maxDIF=dif
        #    maxDIFID=idx
    return IDXS,x

def getMAP(L):
    maplist=[]
    for i in L:
        temp=i["m"].replace("/map.map","").split("/")[-1]
        if not temp in maplist: maplist.append(temp)
    return maplist

def getAlgo(L):
    algoList=[]
    for i in L:
        #[print(idx,content) for idx,content in enumerate(i)]
        temp=i["mergeAlgo"]
        if not temp in algoList: algoList.append(temp)
    global mergeAlgo
    mergeAlgo=algoList
    return algoList

def getConf(L):
    return filterItem(L,lambda l:l["initConf"]!=0)
'''
    print("with init conf",len(withConf))
    mergeFail=filterItem(withConf,lambda l: l[-2]==-1)
    print("with merge fail",len(mergeFail))
    temp=grabInsIDX(mergeFail)
    m=dict()
    for l in mergeFail:
        if l[0] in m:
            m[l[0]]+=1
        else:
            m[l[0]]=1
    print(m)
    exit()
'''

def sanityCheck(l):
    print(l)
    assert len(l)==len(mergeAlgo)
    return min(l)==l[-1]

    for i in range(len(l)-1):
        if l[i] and l[i+1]:
            if (not l[i+1]>=l[i]):
                print(l)
                return False
    return True

def findDif(l):
    if l[3]!=9999999 and l[-1]!=9999999:
        return l[3]-l[-1]
    return None

def genColor(n):
    colormap=cm.get_cmap("brg",n)
    temp=[colormap(i) for i in range(n)]
    random.shuffle(temp)
    return temp

def genMarkers(n):
    marker_styles = ['o', 's', '^', 'v', '<', '>', 'p', '*', 'h', 'H', 'D', 'd', 'X', '|', '_']
    random.shuffle(marker_styles)
    return marker_styles[:n]

def scatterProcess(IDXs,data):
    print(mergeAlgo)
    x_idx=[k for k in data]
    finalx=[[] for _ in mergeAlgo]
    finaly=[[] for _ in mergeAlgo]
    for xi in x_idx:
        assert len(data[xi])==len(mergeAlgo)
        for yi in range(len(data[xi])):
            finalx[yi].append(IDXs[xi]["r"])
            finaly[yi].append(data[xi][yi]["mergeSOC"])
            #tmpl=[i for i in data[xi][yi]["mergeSOC"] if i]
            #for y in tmpl:
            #    finalx[yi].append(xi["r"])
            #    finaly[yi].append(y)

    return (finalx,finaly)

def scatterPlot(final,plt,m):
    global colormap,markers
    if colormap is None:
        colormap=genColor(len(mergeAlgo))
        markers=genMarkers(len(mergeAlgo))
    (finalx,finaly)=final
    for i in range(len(finaly)):
        plt.scatter(finalx[i],finaly[i],marker=markers[i],facecolors="none",edgecolors=colormap[i],label=mergeAlgo[i])

    plt.figure()
    #plt.xticks(x_idx)
    plt.title(m)
    plt.xlabel("agent number")
    plt.ylabel("SoC")
    plt.legend()

def difProcess(IDXs,data):
    x_idx=[k for k in data]
    print(len(x_idx),max(x_idx))
    p1Dif=[None for _ in data]
    p2Dif=[None for _ in data]
    hDif=[None for _ in data]
    for i,xi in enumerate(x_idx):
        #assert len(data[xi])==len(mergeAlgo)
        p1Dif[i]=data[xi][0]["mergeSOC"]-data[xi][1]["mergeSOC"]
        p2Dif[i]=max(0,data[xi][1]["mergeSOC"]-data[xi][2]["mergeSOC"]) + p1Dif[i]
        hDif[i]=data[xi][2]["mergeH"]-data[xi][1]["mergeH"]

    '''
    combined = list(zip(x_idx,p1Dif,p2Dif,hDif))
    combined.sort(key=lambda x : x[1])
    x_idx,p1Dif,p2Dif,hDif = zip(*combined)
    x_idx,p1Dif,p2Dif,hDif = map(list,(x_idx,p1Dif,p2Dif,hDif))
    '''
    combined = list(zip(p1Dif,p2Dif,hDif))
    combined.sort(key=lambda x : x[0])
    p1Dif,p2Dif,hDif = zip(*combined)
    p1Dif,p2Dif,hDif = map(list,(p1Dif,p2Dif,hDif))
    return (x_idx,p1Dif,p2Dif,hDif)

def difPlot(final,plt,m):
    global colormap,markers
    if colormap is None:
        colormap=genColor(3)
        markers=genMarkers(3)

    (x_idx,p1Dif,p2Dif,hDif)=final
    print("max human sacrifice",max(hDif))
    assert len(x_idx)==len(p1Dif)==len(p2Dif)==len(hDif)
    fig , ax1 = plt.subplots()
    ax1.plot(x_idx,p1Dif,color=colormap[0],label="replanning robots only")
    ax1.plot(x_idx,p2Dif,color=colormap[1],label="replanning robots and human")
    ax1.set_xlabel("instance")
    ax1.set_ylabel("Cost improvments (robots)")

    ax2=ax1.twinx()
    ax2.plot(x_idx,hDif,color=colormap[2],label="human cost sacrifice")
    ax2.set_ylabel("Cost sacrifice (human)")
    ax2.tick_params(axis='y',labelcolor=colormap[2])

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left')

    plt.title(m)
