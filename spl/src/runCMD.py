import subprocess,time,sys,requests,shutil,enum

# Global constants
DISCORD_SERVER="***REMOVED***"
N=int(sys.argv[2])  # Max 8 because the bus only has ~8 data lines, so >8 processes means waiting on data lines to be free means the processes slow down x10000 ~ Andy
MAP_INDEX=2
SCENARIO_INDEX=4
AGENT_NUM_INDEX=10
CONSECUTIVE_FAILURES=2
with open(sys.argv[1],"r") as f:
    CMDPOOL=[l for l in f]
DEBUG_PERIOD=1800 # in seconds
MINIMUM_DISK_SPACE=1073741824 # in B, 1 GiB
RS_FILE="result.txt"
class CMD_STATE(enum.Enum):
    SOLVED=0
    ERROR=1
    NO_SOLUTION=2
    WAITING=3
    IN_POOL=4
    DONE=5
TIMEOUT: dict[int|int] = {} # map size -> timeout in seconds
TIMEOUT[0] = 60 # <100x100 -> 60 seconds
TIMEOUT[10000] = 180 # >100x100 -> 3 minutes

# Global variables
instances: dict[str|dict[int|list[str]]] = {} # dict[map] -> dict[k] -> dict[scenario] -> CMD_STATE
is_level_in_pool: dict[str|dict[int|bool]] = {} # dict[map] -> dict[k] -> is level in pool
highest_k_solved: dict[str|int] = {} # dict[map] -> k of highest level solved
waiting_cmds = set()
current_processes = {}
current_maps = []
errors=[]
no_solutions=[]

time_last_debug=0
time_start=time.time()

def sendDiscord(msg) -> None:
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

def debug() -> str:
    s = ""
    for map_name, ks in instances.items():
        s += f"{map_name.split('/')[2].upper()}\n"
        for k, cmds in ks.items():
            waiting = True
            failed = 0
            solved = 0
            for _, state in cmds.items():
                if state == CMD_STATE.SOLVED:
                    solved += 1
                if state != CMD_STATE.WAITING:
                    waiting = False
                if state == CMD_STATE.NO_SOLUTION:
                    failed += 1
            e = "⏳"
            if waiting:                 # All cmds waiting
                e = "⏱️"
            elif failed == len(cmds):   # All cmds found no solution
                e = "❌"
            elif solved > 0:            # At least one cmd solved
                e = "✅"

            if failed > 0:
                s += f"{k}={e} (({solved}+{failed})/{len(cmds)}), "
            else:
                s += f"{k}={e} ({solved}/{len(cmds)}), "
        s = f"{s[:-2]}\n\n"
    return s

def is_map_failed(map_name) -> bool:
    if map_name not in current_maps:
        return False
    l = highest_k_solved[map_name]
    r = min(l + CONSECUTIVE_FAILURES, max(instances[map_name].keys()))
    for k in range(l + 1, r + 1):
        for _, state in instances[map_name][k].items():
            if state != CMD_STATE.NO_SOLUTION:
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
            current_maps.append(map_name)

        if k not in instances[map_name]:
            instances[map_name][k] = {}
            is_level_in_pool[map_name][k] = False

        if cmd not in instances[map_name][k]:
            instances[map_name][k][cmd] = CMD_STATE.WAITING

    for map_name in instances.keys():
        highest_k_solved[map_name] = min(instances[map_name].keys())

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
        return
    
    # For example, assume (height * width) = 10000
    size = (height * width) + 1 # size = 10001
    x = list(TIMEOUT.keys()) # [0, 10000]
    x.append(size) # [0, 10000, 10001]
    x.sort() # In cases where the size is below max(x)
    return TIMEOUT[x[x.index(size)-1]]

def update_cmds() -> None:
    was_csv = False
    is_txt = False

    try:
        with open(RS_FILE,'r') as f:
            for fn in f:
                fn = fn.strip()
                is_txt = True if fn.split(".")[-1] == "txt" else False
                if was_csv and is_txt:
                    m = fn.split("-random")[0].split("-even")[0].split("/")[-1]
                    map_name = f"../bench_mark/{m}/{m}.map"
                    k = int(fn.split("agents-")[-1].split(".")[0])
                    scen = fn.split("/")[-1].split("scen-")
                    scen = f"{scen[0]}{scen[1].split('-')[0]}"
                    cmd=(
                        "../../cbs",
                        "-m",map_name,
                        "-a",f"../bench_mark/{m}/{scen}.scen",
                        "-o",f"{fn.split('.txt')[0]}.csv",
                        "--outputPaths",fn,
                        "-k",str(k),
                        "-t",f"{getTimeout(map_name)}",
                    )
                    instances[map_name][k][cmd] = CMD_STATE.DONE
                    highest_k_solved[map_name] = max(highest_k_solved[map_name], k)
                    
                was_csv = True if fn.split(".")[-1] == "csv" else False
    except FileNotFoundError:
        print(f"Could not find file {RS_FILE}.")

def create_pool() -> None:
    for map_name in instances.keys():
        l = 1
        r = min(highest_k_solved[map_name] + CONSECUTIVE_FAILURES, max(instances[map_name].keys()))
        for k in range(l, r + 1):
            for cmd in instances[map_name][k].keys():
                if instances[map_name][k][cmd] == CMD_STATE.WAITING:
                    waiting_cmds.update([cmd])
                    instances[map_name][k][cmd] = CMD_STATE.IN_POOL

def update_pool() -> None:
    for map_name in instances.keys():

        if highest_k_solved[map_name] == max(instances[map_name].keys()):
            continue

        l = highest_k_solved[map_name]
        r = min(l + CONSECUTIVE_FAILURES, max(instances[map_name].keys()))
        for k in range(l + 1, r + 1):
            for cmd in instances[map_name][k].keys():
                if instances[map_name][k][cmd] == CMD_STATE.WAITING:
                    waiting_cmds.update([cmd])
                    instances[map_name][k][cmd] = CMD_STATE.IN_POOL

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
                instances[map_name][k][cmd] = CMD_STATE.SOLVED
                highest_k_solved[map_name] = max(highest_k_solved[map_name], k)
                if (highest_k_solved[map_name] == max(instances[map_name].keys())) and (map_name in current_maps):
                    current_maps.remove(map_name)
                # print("[RUN_CMD] Solved", subprocess.list2cmdline(current_processes[pid][1]))
            elif result == 2:                       # Not solved
                instances[map_name][k][cmd] = CMD_STATE.NO_SOLUTION
                no_solutions.append(' '.join(cmd))
                # print("[RUN_CMD] Not solved", subprocess.list2cmdline(current_processes[pid][1]))
            else:                                   # Bug
                instances[map_name][k][cmd] = CMD_STATE.ERROR
                errors.append(' '.join(cmd))
                sendDiscord(f"BUG: !!!!!!!!!!!!!!!!! FUCK YOU!!!!!!!!! {subprocess.list2cmdline(cmd)}")
                # print("[RUN_CMD] ERROR: Failed", subprocess.list2cmdline(cmd))
            finished_pids.append(pid)
    for pid in finished_pids:
        del current_processes[pid]

def check_disk() -> None:
    _, _, free = shutil.disk_usage("/")
    if free < MINIMUM_DISK_SPACE:
        sendDiscord("Disk space exceeded!")
        raise Exception("Disk space exceeded!")



print("Creating commands.")
create_cmds()
print("Updating commands.")
update_cmds()
print("Creating pool.")
create_pool()

print(debug())

# Loop
try: 
    while waiting_cmds or current_processes:
        
        run_pool()      # Start new processes if we have capacity
        check_pool()    # Check for finished processes

        for map_name in instances.keys():   # Check for consecutive failures
            if is_map_failed(map_name):
                current_maps.remove(map_name)
                highest_k_solved[map_name] = max(instances[map_name].keys()) # So further of its instances don't get added to waiting_cmds in update_pool()
                # sendDiscord(f"FAILURE: {map_name} exceeded consecutive failures.")
                print(f"[RUN_CMD] FAILURE: {map_name} exceeded consecutive failures.")

        update_pool()   # Add new processes for levels that have not been solved and exist within the consecutive failure limit

        # Debug
        if (time.time() - time_last_debug) < DEBUG_PERIOD:
            pass
        else:
            time_last_debug = time.time()
            print(debug())
        
        check_disk()
except KeyboardInterrupt:
    pass



# Debug
time.sleep(1)   # Wait to allow process terminal output to finish
print(debug())
sendDiscord("Experiment finished without bug, hopefully.")
print(time.time()-time_start)

if errors:
    with open("errors.txt",'w') as f:
        [f.write("%s\n" % l) for l in errors]
if no_solutions:
    with open("no_solutions.txt",'w') as f:
        [f.write("%s\n" % l) for l in no_solutions]