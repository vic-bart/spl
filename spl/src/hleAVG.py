import sys
import glob
# Global constants
RS_FOLDER="../result/37/"

# Global variables
hle=[]

# ../../cbs -m ../bench_mark/empty-8-8/empty-8-8.map -a ../bench_mark/empty-8-8/empty-8-8-random-1.scen -o ../result/1.csv --outputPaths ../result/1.txt -k 30 -t 60
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
# 16 = 63066.083333333336
# 24 = 63708.89453125
# 32 = 63927.203125
# 33 = 63966.328125
# 34 = 64046.78125
# 35 = 64115.2421875
# 36 = 64132.10590277778 (max)
# 37 = 64123.146875
# 48 = 63777.99375
# 64 = 61635.5390625