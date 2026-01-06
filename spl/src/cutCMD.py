import glob,sys,time

# Global constants
CMD_FILE=sys.argv[1]
NEW_CMD_FILE=sys.argv[2]
RS_FOLDER="../result/"
CSV_INDEX=6
TXT_INDEX=8
DEBUG_PERIOD=30 # Seconds

# Global variables
rs=[]
cmds=[]
tot_l=0
cur_l=0
time_last_debug=0
time_start=0
time_end=0

def debug():
    return f"ETA: {((time_end-time_start)*(tot_l-cur_l))//60} minutes remaining. {cur_l}/{tot_l} commands completed."

with open("rs.txt",'r') as f:
    for l in f:
        rs.append(l.strip())

try:
    with open(CMD_FILE,'r') as f:
        tot_l = len(f.readlines())
except FileNotFoundError:
    print(f"The file '{CMD_FILE}' does not exist.")

with open(CMD_FILE,'r') as f:
    cur_l = 1
    for l in f:
        time_start = time.time()
        cur_l += 1
        s = l.split(" ")
        if s[CSV_INDEX] in rs and s[TXT_INDEX] in rs:
            continue
        cmds.append(l.strip())
        time_end = time.time()

        # Debug
        if (time.time() - time_last_debug) < DEBUG_PERIOD:
            pass
        else:
            time_last_debug = time.time()
            print(debug())

with open(NEW_CMD_FILE,"w") as f:
    [print(l,file=f) for l in cmds]