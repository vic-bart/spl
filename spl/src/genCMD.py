import sys

# Global constants
TIMEOUT: dict[int|int] = {} # map size -> timeout in seconds
TIMEOUT[0] = 60 # <100x100 -> 60 seconds
TIMEOUT[10000] = 180 # >100x100 -> 3 minutes
EXE="../../cbs"
FN_FOLDER="../bench_mark/"
RS_FOLDER="../result/"
ML=[
    "empty-8-8",
]

# Global variables
all=[]

def getTimeout(fn_m):
    height = 0
    width = 0

    try:
        with open(fn_m,'r') as f:
            for l in f:
                if l.split()[0] == "height":
                    height = int(l.split()[1])
                elif l.split()[0] == "width":
                    width = int(l.split()[1])
                else:
                    continue
    except FileNotFoundError:
        print(f"The file '{fn_m}' does not exist.")
        return None
    
    # For example, assume (height * width) = 10000
    size = (height * width) + 1 # size = 10001
    x = list(TIMEOUT.keys()) # [0, 10000]
    x.append(size) # [0, 10000, 10001]
    x.sort() # In cases where the size is below max(x)
    return TIMEOUT[x[x.index(size)-1]]

for m in ML:
    fn_m= f"{FN_FOLDER}{m}/{m}.map"
    for i_type in ["random","even"]:
        for i in range(1,26):
            fn_ins=f"{FN_FOLDER}{m}/{m}-{i_type}-{i}.scen"
            with open(fn_ins) as f:
                maxlen=len(f.read().strip().split("\n"))

            for k in range(1,min(400,maxlen)):
                cmd=[
                    EXE,
                    "-m",fn_m,
                    "-a",fn_ins,
                    "-o",f"{RS_FOLDER}{m}-{i_type}-scen-{i}-agents-{k}.csv",
                    "--outputPaths",f"{RS_FOLDER}{m}-{i_type}-scen-{i}-agents-{k}.txt",
                    "-k",k,
                    "-t",getTimeout(fn_m),
                ]
                all.append(cmd)

with open(sys.argv[1],"w") as f:
    [print(*i,file=f) for i in all]