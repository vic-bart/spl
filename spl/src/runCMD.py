from matplotlib import lines
import subprocess, os,glob, time,json,sys,requests,math

# Global constants
DISCORD_SERVER="https://discord.com/api/webhooks/1445640871583416431/R6A4Ug4J2aQoCgWV8JmNtox3ASgH66_jWVU4KLaK_Kj3hJVoZ6xlNHijHkmP7ZYuFgb6"
N=int(sys.argv[2])  # Max 8 because the bus only has ~8 data lines, so >8 processes means waiting on data lines to be free means the processes slow down x10000 ~ Andy
MAP_INDEX = 2
SCENARIO_INDEX = 4
AGENT_NUM_INDEX = 10
CONSECUTIVE_FAILURES = 2
with open(sys.argv[1],"r") as f:
    CMDPOOL=[l for l in f]
DEBUG_PERIOD=1800 # in seconds

# Global variables
instances: dict[str|dict[int|list[str]]] = {} # dict[map] -> dict[k] -> dict[scenario] -> status[0=solved,1=error,2=no solution,3=waiting]
is_level_in_pool: dict[str|dict[int|bool]] = {} # dict[map] -> dict[k] -> is level in pool
highest_k_solved: dict[str|int] = {} # dict[map] -> k of highest level solved
waiting_cmds = set()
current_processes = {}
errors=[]
no_solutions=[]

time_last_debug=0
time_start=time.time()

def sendDiscord(msg):
    # This API limits messages to 2000 characters.
    while len(msg) > 2000:
        payload = {"content": msg[:2000]}
        response = requests.post(DISCORD_SERVER, json=payload)
        time.sleep(3) # Delay to avoid being rate limited by the API
        if response.ok:
            print(f"[DISCORD] Sent message: {msg[:2000]}")
        else:
            print(f"[DISCORD] Failed to send message: {msg}\n{response.status_code} - {response.text}")
        msg = msg[2000:]

    payload = {"content": msg}
    response = requests.post(DISCORD_SERVER, json=payload)
    if response.ok:
        print(f"[DISCORD] Sent message: {msg}")
    else:
        print(f"[DISCORD] Failed to send message: {msg}\n{response.status_code} - {response.text}")

def debug():
    s = ""
    for map_name, ks in instances.items():
        s += f"{map_name.split('/')[2].upper()}\n"
        for k, cmds in ks.items():
            waiting = True
            failed = True
            solved = 0
            for _, status in cmds.items():
                if status == 0:
                    solved += 1
                if status != 3:
                    waiting = False
                if status != 2:
                    failed = False
            if waiting:         # All cmds waiting
                e = "⏱️"
            elif failed:        # All cmds found no solution
                e = "❌"
            elif solved > 0:    # At least one cmd solved
                e = "✅"
            s += f"{k}={e} ({solved}/{len(cmds)}), "
        s = f"{s[:-2]}\n\n"
    return s

def is_map_failed(map_name) -> bool:
    l = highest_k_solved[map_name]
    r = min(l + CONSECUTIVE_FAILURES, max(instances[map_name].keys()))
    for k in range(l + 1, r + 1):
        for _, status in instances[map_name][k].items():
            if status != 2:
                return False
    return True

def create_cmds() -> None:
    for data in CMDPOOL:
        cmd = tuple(data.strip().split(" "))
        map_name = cmd[MAP_INDEX]
        k = int(cmd[AGENT_NUM_INDEX])

        if map_name not in instances:
            instances[map_name] = {}
            is_level_in_pool[map_name] = {}
            highest_k_solved[map_name] = 0

        if k not in instances[map_name]:
            instances[map_name][k] = {}
            is_level_in_pool[map_name][k] = False

        if cmd not in instances[map_name][k]:
            instances[map_name][k][cmd] = 3

def create_pool() -> None:
    for map_name in instances.keys():
        l = highest_k_solved[map_name]
        r = min(l + CONSECUTIVE_FAILURES, max(instances[map_name].keys()))
        for k in range(l + 1, r + 1):
            for cmd in instances[map_name][k].keys():
                waiting_cmds.update([cmd])

def update_pool() -> None:
    for map_name in instances.keys():

        if highest_k_solved[map_name] == max(instances[map_name].keys()):
            continue

        l = highest_k_solved[map_name]
        r = min(l + CONSECUTIVE_FAILURES, max(instances[map_name].keys()))
        for k in range(l + 1, r + 1):
            if not is_level_in_pool[map_name][k]:
                for cmd in instances[map_name][k].keys():
                    waiting_cmds.update([cmd])
                is_level_in_pool[map_name][k] = True

def run_pool() -> None:
    while len(current_processes) < N and waiting_cmds:
        cmd = waiting_cmds.pop()
        # print("[RUN_CMD] Starting command", subprocess.list2cmdline(cmd))
        process = subprocess.Popen(cmd)
        current_processes[process.pid] = (process, cmd)

def check_pool() -> None:
    finished_pids = []
    for pid, (process, cmd) in current_processes.items():
        result = process.poll()
        if result is not None:                      # Process has finished
            map_name = cmd[MAP_INDEX]
            k = int(cmd[AGENT_NUM_INDEX])
            if result == 0:                         # Solved
                instances[map_name][k][cmd] = 0
                highest_k_solved[map_name] = max(highest_k_solved[map_name], k)
                # print("[RUN_CMD] Solved", subprocess.list2cmdline(current_processes[pid][1]))
            elif result == 2:                       # Not solved
                instances[map_name][k][cmd] = 2
                no_solutions.append(' '.join(cmd))
                # print("[RUN_CMD] Not solved", subprocess.list2cmdline(current_processes[pid][1]))
            else:                                   # Bug
                instances[map_name][k][cmd] = 1
                errors.append(' '.join(cmd))
                sendDiscord(f"[DISCORD] BUG: !!!!!!!!!!!!!!!!! FUCK YOU!!!!!!!!! {subprocess.list2cmdline(cmd)}")
                # print("[RUN_CMD] ERROR: Failed", subprocess.list2cmdline(cmd))
            finished_pids.append(pid)
    for pid in finished_pids:
        del current_processes[pid]

create_cmds()
create_pool()

print(debug())
sendDiscord("[DISCORD] Starting experiment.")
sendDiscord(debug())

# Loop
while waiting_cmds or current_processes:
    
    run_pool()      # Start new processes if we have capacity
    check_pool()    # Check for finished processes

    for map_name in instances.keys():   # Check for consecutive failures
        if is_map_failed(map_name):
            sendDiscord(f"[DISCORD] FAILURE: {map_name} exceeded consecutive failures.")
            # print(f"[RUN_CMD] FAILURE: Consecutive failures exceeded for map {map_name} with {k} agents.")
            highest_k_solved[map_name] = max(instances[map_name].keys())

    update_pool()   # Add new processes for levels that have not been solved and exist within the consecutive failure limit

    # Debug
    if (time.time() - time_last_debug) < DEBUG_PERIOD:
        pass
    else:
        time_last_debug = time.time()
        print(debug())

# Debug
time.sleep(1)   # Wait to allow process terminal output to finish
print(debug())
sendDiscord("[DISCORD] Experiment finished without bug, hopefully.")
sendDiscord(debug())
print(time.time()-time_start)

if errors:
    with open("errors.txt",'w') as f:
        [f.write("%s\n" % l) for l in errors]
if no_solutions:
    with open("no_solutions.txt",'w') as f:
        [f.write("%s\n" % l) for l in no_solutions]