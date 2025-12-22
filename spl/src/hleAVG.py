import sys
import glob
# Global constants
RS_FOLDER="../result/1/"

# Global variables
hle=[]

# runtime,#high-level expanded,
# 6.20293,11795,

path = f"{RS_FOLDER}*.csv"
for fn in glob.glob(path):
    try:
        with open(fn,'r') as f:
            for l in f:
                try:
                    hle.append(int(l.split(',')[1]))
                except:
                    continue
    except FileNotFoundError:
        print(f"The file '{fn}' does not exist.")

print(sum(hle) / len(hle))
# 1  = 11795.0
# 8  = 11795.0
# 16 = 11795.0
# 32 = 11795.0
# 64 = 11795.0