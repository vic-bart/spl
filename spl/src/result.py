import glob

# Global constants
RS_FOLDER="../result/"
RS_FILE="result.txt"
CSV_INDEX=6
TXT_INDEX=8

# Global variables
rs=[]
cmds=[]

for fn in sorted(glob.glob(f"{RS_FOLDER}/*")):
    rs.append(fn)

with open(RS_FILE,"w") as f:
    [print(l,file=f) for l in rs]