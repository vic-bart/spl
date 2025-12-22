from matplotlib import lines
import subprocess, os,glob, time,json,sys,requests,math

# Global constants
DISCORD_SERVER="https://discord.com/api/webhooks/1445640871583416431/R6A4Ug4J2aQoCgWV8JmNtox3ASgH66_jWVU4KLaK_Kj3hJVoZ6xlNHijHkmP7ZYuFgb6"
N=int(sys.argv[2])
MAP_INDEX = 2
SCENARIO_INDEX = 4
AGENT_NUM_INDEX = 10
CONSECUTIVE_FAILURES = 2
with open(sys.argv[1],"r") as f:
    CMDPOOL=[l for l in f]
DEBUG_PERIOD=10 # in seconds

# Global variables
waiting_cmds = []
current_processes = {}
errors=[]
no_solutions=[]

time_last_debug=0
time_start=time.time()

# Generate commands
for data in CMDPOOL:
    cmd = data.strip().split(" ")
    cmd = tuple(cmd)
    waiting_cmds.append(cmd)    

while waiting_cmds or current_processes:
    if (time.time() - time_last_debug) < DEBUG_PERIOD:
        pass
    else:
        time_last_debug = time.time()
        print(time.time()-time_start)
    
    # Start new processes if we have capacity
    while len(current_processes) < N and waiting_cmds:
        cmd = waiting_cmds.pop()
        print("[RUN_CMD] Starting command", subprocess.list2cmdline(cmd))
        process = subprocess.Popen(cmd)
        current_processes[process.pid] = (process, cmd)

    # Check for finished processes
    finished_pids = []
    for pid, (process, cmd) in current_processes.items():
        result = process.poll()
        if result is not None:  # Process has finished
            if result == 2: # Solution was not found
                print("[RUN_CMD] NO SOLUTION: No solution found for command", subprocess.list2cmdline(cmd))
                no_solutions.append(' '.join(cmd))
            elif result != 0:
                print("[RUN_CMD] ERROR: Failed command", subprocess.list2cmdline(cmd))
                errors.append(' '.join(cmd))
            else:   # Solution was found
                pass
            finished_pids.append(pid)

    # Remove finished processes from the current pool
    for pid in finished_pids:
        print("[RUN_CMD] Finishing command", subprocess.list2cmdline(current_processes[pid][1]))
        del current_processes[pid]


time.sleep(1)   # Wait to allow process terminal output to finish
print(time.time()-time_start)

if errors:
    with open("errors.txt",'w') as f:
        [f.write("%s\n" % l) for l in errors]
if no_solutions:
    with open("no_solutions.txt",'w') as f:
        [f.write("%s\n" % l) for l in no_solutions]