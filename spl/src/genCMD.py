import sys
def getTimeout(fn_m):
    i = 0
    height = 0
    width = 0

    try:
        with open(fn_m, 'r') as file:
            for line in file:
                if i == 0:
                    pass
                elif i == 1:
                    height = int(line.split()[-1])
                elif i == 2:
                    width = int(line.split()[-1])
                else:
                    return (3*60) if (height*width>1000) else (60)
                i += 1
    except FileNotFoundError:
        print(f"The file '{fn_m}' does not exist.")
        return None

exe="../release/cbs"
fn_folder="../bench_mark/"
rs_folder="../result/"
all=[]
ml=[
    "empty-8-8",
]
for m in ml:
    fn_m= f"{fn_folder}{m}/{m}.map"
    for i_type in ["random","even"]:
        for i in range(1,26):
            fn_ins=f"{fn_folder}{m}/{m}-{i_type}-{i}.scen"
            with open(fn_ins) as f:
                maxlen=len(f.read().strip().split("\n"))

            for k in range(1,min(400,maxlen)):
                cmd=[
                    exe,
                    "-m",fn_m,
                    "-a",fn_ins,
                    "-o",f"{rs_folder}{m}-{i_type}-scen-{i}-agents-{k}.csv",
                    "--outputPaths",f"{rs_folder}{m}-{i_type}-scen-{i}-agents-{k}.txt",
                    "-k",k,
                    "-t",60,
                ]
                all.append(cmd)

with open(sys.argv[1],"w") as f:
    [print(*i,file=f) for i in all]