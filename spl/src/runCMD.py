from matplotlib import lines
import subprocess, os,glob, time,json,sys,requests,math

# Global constants
DISCORD_SERVER="https://discord.com/api/webhooks/1445640871583416431/R6A4Ug4J2aQoCgWV8JmNtox3ASgH66_jWVU4KLaK_Kj3hJVoZ6xlNHijHkmP7ZYuFgb6"
N=min(8, int(sys.argv[2]))  # Max 8 because the bus only has ~8 data lines, so >8 processes means waiting on data lines to be free means the processes slow down x10000 ~ Andy
MAP_INDEX = 2
SCENARIO_INDEX = 4
AGENT_NUM_INDEX = 10
CONSECUTIVE_FAILURES = 2
with open(sys.argv[1],"r") as f:
    CMDPOOL=[l for l in f]
DEBUG_PERIOD=1 # in seconds

# Global variables
levels: dict[str|dict[int|list[str]]] = {} # dict[map] -> dict[k] -> list[cmds for each scenario]
highest_k_solved: dict[str|int] = {} # dict[map] -> k of highest level solved
is_level_in_pool: dict[str|dict[int|bool]] = {} # dict[map] -> dict[k] -> is level in pool
cmd_states: dict[str|dict[int|dict[tuple[str]|int]]] = {} # dict[map] -> dict[k] -> dict[cmd] -> command status, 0:solved, 1:waiting, 2:no solution
waiting_cmds = set()
current_processes = {}
errors=[]
no_solutions=[]

time_last_debug=0

def sendDiscord(msg):
    payload = {"content": msg}
    response = requests.post(DISCORD_SERVER, json=payload)
    if response.ok:
        print(f"[DISCORD] Sent message: {msg}")
    else:
        print(f"[DISCORD] Failed to send message: {msg}\n{response.status_code} - {response.text}")

def debug():
    global time_last_debug
    if (time.time() - time_last_debug) < DEBUG_PERIOD:
        return
    else:
        time_last_debug = time.time()
    l = ""
    for map_name, ks in cmd_states.items():
        for k, cmds in ks.items():

            # Get number of solved commands and state of level
            count = 0
            solved = 0
            for cmd in cmds:
                if cmds[cmd] == 0:
                    solved += 1
                count += cmds[cmd]

            if count == len(cmds):  # All cmds waiting
                e = "⏱️"
            elif count == (2 * len(cmds)):  # All cmds found no solution
                e = "❌"
            else:   # At least one cmd solved
                e = "✅"

            l += f"{k}={e}({solved}/{len(cmds)}), "
        print(f"{map_name.upper()}\n{l[:-2]}")

# sendDiscord("[DISCORD] Starting experiment.")

# Generate commands
for data in CMDPOOL:
    cmd = data.strip().split(" ")
    cmd = tuple(cmd)
    cur_map = cmd[MAP_INDEX]
    cur_scenario = cmd[SCENARIO_INDEX]
    cur_k = int(cmd[AGENT_NUM_INDEX])

    if cur_map not in levels:
        levels[cur_map] = {}
        is_level_in_pool[cur_map] = {}
        cmd_states[cur_map] = {}
        highest_k_solved[cur_map] = 0

    if cur_k not in levels[cur_map]:
        levels[cur_map][cur_k] = []
        is_level_in_pool[cur_map][cur_k] = False
        cmd_states[cur_map][cur_k] = {}

    levels[cur_map][cur_k].append(cmd)
    cmd_states[cur_map][cur_k][cmd] = 1
    
# Debug
debug()
# for map_name, ks in levels.items():
#     print("[RUN_CMD] Running experiments for map", map_name)
#     for k, cmds in ks.items():
#         print("  Number of agents:", k)
#         print(f"    Running {len(cmds)} commands:")

# Initialise command pool
for map_name in levels.keys():
    min_k = highest_k_solved[map_name]
    max_k = highest_k_solved[map_name] + CONSECUTIVE_FAILURES
    for k in range(min_k + 1, max_k + 1):
        cmds = levels[map_name][k]
        waiting_cmds.update(cmds)

while waiting_cmds or current_processes:
    debug()
    
    # Start new processes if we have capacity
    while len(current_processes) < N and waiting_cmds:
        cmd = waiting_cmds.pop()
        # print("[RUN_CMD] Starting command", subprocess.list2cmdline(cmd))
        process = subprocess.Popen(cmd)
        current_processes[process.pid] = (process, cmd)

    # Check for finished processes
    finished_pids = []
    for pid, (process, cmd) in current_processes.items():
        result = process.poll()
        if result is not None:  # Process has finished
            fin_map = cmd[MAP_INDEX]
            fin_scenario = cmd[SCENARIO_INDEX]
            fin_k = int(cmd[AGENT_NUM_INDEX])
            if result == 2: # Solution was not found
                # sendDiscord("[DISCORD] NO SOLUTION: Experiment found no solution.")
                # print("[RUN_CMD] NO SOLUTION: No solution found for command", subprocess.list2cmdline(cmd))
                no_solutions.append(' '.join(cmd))
                cmd_states[fin_map][fin_k][cmd] = 2
            elif result != 0:
                # sendDiscord("[DISCORD] BUG: !!!!!!!!!!!!!!!!! FUCK YOU!!!!!!!!!")
                # print("[RUN_CMD] ERROR: Failed command", subprocess.list2cmdline(cmd))
                errors.append(' '.join(cmd))
            else:   # Solution was found
                cmd_states[fin_map][fin_k][cmd] = 0
                highest_k_solved[fin_map] = max(highest_k_solved[fin_map], fin_k)
                pass
            finished_pids.append(pid)

    # Remove finished processes from the current pool
    for pid in finished_pids:
        # print("[RUN_CMD] Finishing command", subprocess.list2cmdline(current_processes[pid][1]))
        del current_processes[pid]

    # Check for consecutive failures
    try:
        for map_name in levels.keys():
            map_failed = True
            min_k = highest_k_solved[map_name]
            max_k = highest_k_solved[map_name] + CONSECUTIVE_FAILURES
            for k in range(min_k + 1, max_k + 1):
                if not map_failed:
                    break
                for cmd, cmd_state in cmd_states[map_name][k].items():
                    if cmd_state != 2:
                        map_failed = False
                        break
        if map_failed:
            # sendDiscord("[DISCORD] FAILURE: Experiment exceeded consecutive failures.")
            # print("[RUN_CMD] FAILURE")
            # print(f"[RUN_CMD] Consecutive failures exceeded for map {map_name} with {k} agents.")
            for k in is_level_in_pool[map_name].keys():
                is_level_in_pool[map_name][k] = True
    except:
        pass

    # Add new processes for levels that have not been solved and exist within the consecutive failure limit
    for map_name in levels.keys():
        min_k = highest_k_solved[map_name]
        max_k = highest_k_solved[map_name] + CONSECUTIVE_FAILURES
        for k in range(min_k + 1, max_k + 1):
            if not is_level_in_pool[map_name][k]:
                cmds = levels[map_name][k]
                waiting_cmds.update(cmds)
                is_level_in_pool[map_name][k] = True

time.sleep(1)   # Wait to allow process terminal output to finish
debug()
# sendDiscord("[DISCORD] Experiment finished without bug, hopefully.")

if errors:
    with open("errors.txt",'w') as f:
        [f.write("%s\n" % l) for l in errors]
if no_solutions:
    with open("no_solutions.txt",'w') as f:
        [f.write("%s\n" % l) for l in no_solutions]