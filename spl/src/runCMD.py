import subprocess,time,sys,requests,shutil,enum

# Global constants
with open("discord-key.txt","r") as f:
    DISCORD_SERVER=f.read().strip()
N=int(sys.argv[2])  # Max 34 because >36 processes start waiting on data lines to be free, slowing them down x10000
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
    SKIP=6
CMD_INDEX=0
CMD_STATE_INDEX=1

# Global variables

instances: dict[str|dict[int|dict[str|list[tuple[str], CMD_STATE]]]] = {} 
# dict[map] -> dict[k] -> dict[scenario] -> list[cmd, CMD_STATE]

is_level_in_pool: dict[str|dict[int|bool]] = {} 
# dict[map] -> dict[k] -> is level in pool

highest_k_solved: dict[str|int] = {} 
# dict[map] -> k of highest level solved

waiting_cmds = set()
current_processes = {}
current_maps = []
errors=[]
no_solutions=[]

time_last_debug=0
time_start=0
time_end=0
debug_count=0
debug_total=0

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
        s += f"{map_name.upper()}\n"
        for k, scens in ks.items():
            waiting = True
            failed = 0
            solved = 0
            for _, (_, cmd_state) in scens.items():
                if cmd_state == CMD_STATE.SOLVED:
                    solved += 1
                if cmd_state != CMD_STATE.WAITING:
                    waiting = False
                if cmd_state == CMD_STATE.NO_SOLUTION:
                    failed += 1
            e = "⏳"
            if waiting:                 # All cmds waiting
                e = "⏱️"
            elif failed == len(scens):   # All cmds found no solution
                e = "❌"
            elif solved > 0:            # At least one cmd solved
                e = "✅"

            if failed > 0:
                s += f"{k}={e} (({solved}+{failed})/{len(scens)}), "
            else:
                s += f"{k}={e} ({solved}/{len(scens)}), "
        s = f"{s[:-2]}\n\n"
    return s

def is_map_failed(map_name) -> bool:
    if map_name not in current_maps:
        return False
    l = highest_k_solved[map_name]
    r = min(l + CONSECUTIVE_FAILURES, max(instances[map_name].keys()))
    for k in range(l + 1, r + 1):
        for _, (_, cmd_state) in instances[map_name][k].items():
            if cmd_state != CMD_STATE.NO_SOLUTION:
                return False
    return True

def create_cmds() -> None:
    prev_k = None

    for data in CMDPOOL:
        cmd = tuple(data.strip().split(" "))
        map_name = cmd[MAP_INDEX].split("/")[-2]
        k = int(cmd[AGENT_NUM_INDEX])
        scen = cmd[SCENARIO_INDEX].split(map_name)[-1][1:-5]

        if map_name not in instances:
            instances[map_name] = {}
            is_level_in_pool[map_name] = {}
            current_maps.append(map_name)
            highest_k_solved[map_name] = k

        if k not in instances[map_name]:
            instances[map_name][k] = {}
            is_level_in_pool[map_name][k] = False

            if k - prev_k > 1:
                for k in range(prev_k+1, k):
                    instances[map_name][k] = {}
                    is_level_in_pool[map_name][k] = True
                    instances[map_name][k][scen] = [(""), CMD_STATE.SKIP]

        if scen not in instances[map_name][k]:
            instances[map_name][k][scen] = [cmd, CMD_STATE.WAITING]

        prev_k = k


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
                    instances[map_name][k][scen][1] = CMD_STATE.DONE
                    highest_k_solved[map_name] = max(highest_k_solved[map_name], k)
                    
                was_csv = True if fn.split(".")[-1] == "csv" else False
    except FileNotFoundError:
        print(f"Could not find file {RS_FILE}.")

def create_pool() -> None:
    for map_name in instances.keys():
        l = 1
        r = min(highest_k_solved[map_name] + CONSECUTIVE_FAILURES, max(instances[map_name].keys()))
        for k in range(l, r + 1):
            for scen, (cmd, cmd_state) in instances[map_name][k].items():
                if cmd_state == CMD_STATE.WAITING:
                    waiting_cmds.update([cmd])
                    instances[map_name][k][scen][CMD_STATE_INDEX] = CMD_STATE.IN_POOL

def update_pool() -> None:
    for map_name in instances.keys():
        if highest_k_solved[map_name] == max(instances[map_name].keys()):
            continue
        l = highest_k_solved[map_name]
        r = min(l + CONSECUTIVE_FAILURES, max(instances[map_name].keys()))
        for k in range(l + 1, r + 1):
            for scen, (cmd, cmd_state) in instances[map_name][k].items():
                if cmd_state == CMD_STATE.WAITING:
                    waiting_cmds.update([cmd])
                    instances[map_name][k][scen][CMD_STATE_INDEX] = CMD_STATE.IN_POOL

def run_pool() -> None:
    while len(current_processes) < N and waiting_cmds:
        cmd = waiting_cmds.pop()
        process = subprocess.Popen(cmd)
        current_processes[process.pid] = (process, cmd)

def check_pool() -> None:
    finished_pids = []
    for pid, (process, cmd) in current_processes.items():
        result = process.poll()
        if result is not None: # Process has finished

            map_name = cmd[MAP_INDEX].split("/")[-2]
            k = int(cmd[AGENT_NUM_INDEX])
            scen = cmd[SCENARIO_INDEX].split(map_name)[-1][1:-5]

            if result == 0: # Solved
                instances[map_name][k][scen][CMD_STATE_INDEX] = CMD_STATE.SOLVED
                highest_k_solved[map_name] = max(highest_k_solved[map_name], k)
                if (highest_k_solved[map_name] == max(instances[map_name].keys())) and (map_name in current_maps):
                    current_maps.remove(map_name)
            elif result == 2: # Not solved
                instances[map_name][k][scen][CMD_STATE_INDEX] = CMD_STATE.NO_SOLUTION
                no_solutions.append(' '.join(cmd))
            else: # Bug
                instances[map_name][k][scen][CMD_STATE_INDEX] = CMD_STATE.ERROR
                errors.append(' '.join(cmd))
                sendDiscord(f"BUG: !!!!!!!!!!!!!!!!! FUCK YOU!!!!!!!!! {subprocess.list2cmdline(cmd)}")
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

# WIP (need to modify to access result folder directly, not txt file summary of 
# directory)
# print("Updating commands.")
# update_cmds()

print("Creating pool.")
create_pool()

# Debug
time_start = time.time()
debug_total = len(CMDPOOL)
#######

# Loop
try: 
    while waiting_cmds or current_processes:
        
        run_pool()      # Start new processes if we have capacity
        check_pool()    # Check for finished processes

        for map_name in instances.keys():   # Check for consecutive failures
            if is_map_failed(map_name):
                current_maps.remove(map_name)
                highest_k_solved[map_name] = max(instances[map_name].keys()) # So further of its instances don't get added to waiting_cmds in update_pool()
                print(f"[RUN_CMD] FAILURE: {map_name} exceeded consecutive failures.")

        update_pool()   # Add new processes for levels that have not been solved and exist within the consecutive failure limit
        check_disk()

        # Debug
        time_end = time.time()
        if (time.time() - time_last_debug) < DEBUG_PERIOD:
            pass
        else:
            debug_count = 0
            for map_name in instances.keys():
                for k in instances[map_name]:
                    for scen, (cmd, cmd_state) in instances[map_name][k].items():
                        debug_count = debug_count + 1 if cmd_state != CMD_STATE.WAITING else debug_count
            time_last_debug = time.time()
            print(debug())
            print(f"ETA: {(((time_end-time_start)/debug_count)*(debug_total-debug_count))//60} minutes remaining. {debug_count}/{debug_total} completed.")
        #######
except KeyboardInterrupt:
    pass

# Debug
time.sleep(1)   # Wait to allow process terminal output to finish
sendDiscord("Experiment finished without bug, hopefully.")

if errors:
    with open("errors.txt",'w') as f:
        [f.write("%s\n" % l) for l in errors]
if no_solutions:
    with open("no_solutions.txt",'w') as f:
        [f.write("%s\n" % l) for l in no_solutions]