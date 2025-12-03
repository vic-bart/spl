import sys
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
                    "-o",f"{rs_folder}{m}/{m}-{i_type}-{i}.csv",
                    "--outputPaths",f"{rs_folder}{m}/{m}-{i_type}-{i}.txt",
                    "-k",k,
                    "-t",60,
                ]
                all.append(cmd)

with open(sys.argv[1],"w") as f:
    [print(*i,file=f) for i in all]