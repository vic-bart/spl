import subprocess, os,glob, time,json,sys,requests
myServer="https://discord.com/api/webhooks/1445640871583416431/R6A4Ug4J2aQoCgWV8JmNtox3ASgH66_jWVU4KLaK_Kj3hJVoZ6xlNHijHkmP7ZYuFgb6"

N=int(sys.argv[2])

MAP_INDEX = 2
SCENARIO_INDEX = 4
AGENT_NUM_INDEX = 10

def send(payload):
    response = requests.post(myServer, json=payload)
    if response.ok:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message: {response.status_code} - {response.text}")

def sendStart():
    print("starting Experiement")
    payload = {
    #"payload_json": '{"content":"BUG!!!!!!!!!!!!!!!!! FUCK YOU!!!!!!!!!"}'
    "content":"------------------Starting a New Experiment---------------------"
    }
    send(payload)

def sendError():
    print("error")
    payload = {
    #"payload_json": '{"content":"BUG!!!!!!!!!!!!!!!!! FUCK YOU!!!!!!!!!"}'
    "content":"BUG!!!!!!!!!!!!!!!!! FUCK YOU!!!!!!!!!"
    }
    send(payload)

def sendFinish():
    print("finished")
    payload = {
    #"payload_json": '{"content":"Experiement finished without bug, hopefully"}'
    "content":"Experiement finished without bug, hopefully"
    }
    send(payload)

def remove_first_line(input_file, output_file):
    # Check if the input file is not empty
    try:
        with open(input_file, 'r') as infile:
            first_char = infile.read(1)
            if not first_char:
                print(f"The file '{input_file}' is empty.")
                return
            # Move the file pointer back to the beginning
            infile.seek(0)
            data = infile.read().splitlines(True)
    except FileNotFoundError:
        print(f"The file '{input_file}' does not exist.")
        return

    # Write to the output file
    with open(output_file, 'w') as outfile:
        outfile.writelines(data[1:])
    return data[0]

#data=remove_first_line('./input.txt', './errors.txt')
with open(sys.argv[1],"r") as f:
    CMDPOOL=[l for l in f]

errors=[]
sendStart()

levels: dict[str|dict[int|list[str]]] = {} # map -> k -> list of cmds for each scenario
is_level_in_pool: dict[str|dict[int|bool]] = {} # map -> k -> scenario in cmd pool or not

waiting_cmds = set()
current_processes = {}

for data in CMDPOOL:
    cmd = tuple(data.strip().split(" "))
    cur_map = cmd[MAP_INDEX]
    cur_scenario = cmd[SCENARIO_INDEX]
    cur_k = cmd[AGENT_NUM_INDEX]

    if cur_map not in levels:
        levels[cur_map] = {}
        is_level_in_pool[cur_map] = {}

    
    if cur_k not in levels[cur_map]:
        levels[cur_map][cur_k] = []
        is_level_in_pool[cur_map][cur_k] = False



    levels[cur_map][cur_k].append(cmd)

for map_name, ks in levels.items():
    print("Running experiments for map:", map_name)
    for k, cmds in ks.items():
        print("  Number of agents:", k)
        print(f"    Running {len(cmds)} commands:")

for map_name, ks in levels.items():
    for k in ks.keys():
        cmds = levels[map_name][k]
        waiting_cmds.update(cmds)

while waiting_cmds or current_processes:
    # Start new processes if we have capacity
    while len(current_processes) < N and waiting_cmds:
        cmd = waiting_cmds.pop()
        print("Starting command:", subprocess.list2cmdline(cmd))
        process = subprocess.Popen(cmd)
        current_processes[process.pid] = (process, cmd)

    # Check for finished processes
    finished_pids = []
    for pid, (process, cmd) in current_processes.items():
        result = process.poll()
        if result is not None:  # Process has finished
            if result != 0:
                sendError()
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                print("Failed command:", subprocess.list2cmdline(cmd))
                errors.append(' '.join(cmd))
            finished_pids.append(pid)

    # Remove finished processes from the current pool
    for pid in finished_pids:
        print("Finishing command:", subprocess.list2cmdline(current_processes[pid][1]))
        del current_processes[pid]


# for data in CMDPOOL:
#     cmd=data.strip().split(" ")
#     print(subprocess.list2cmdline(cmd))

#     if (len(processPool)>=N):
#         finish = False
#         while not finish:
#             time.sleep(1)
#             for p in range(0,len(processPool)):
#                 if p >= len(processPool):
#                     break
#                 result=processPool[p].poll()
#                 if result is not None:
#                     if result!=0:
#                         sendError()
#                         print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
#                         print(processPool[p].args)
#                         print(processPool[p].stderr)
#                         errors.append(' '.join(processPool[p].args))
#                         #with open("errors.txt",'a') as f:
#                         #    print(' '.join(processPool[p].args),file=f)
#                     processPool.pop(p)
#                     finish = True
#                     p-=1
#     else:
#         for p in range(0,len(processPool)):
#                 if p >= len(processPool):
#                     break

#                 result=processPool[p].poll()
#                 if result is not None:
#                     print("result",result)
#                     if result!=0:
#                         sendError()
#                         print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
#                         print(processPool[p])
#                         print(processPool[p].args)
#                         errors.append(' '.join(processPool[p].args))
#                         #with open("errors.txt",'a') as f:
#                         #    print(' '.join(processPool[p].args),file=f)
#                     processPool.pop(p)
#                     finish = True
#                     p-=1

#     try:
#         processPool.append(subprocess.Popen(cmd))
#     except:
#         print(len(processPool))

#     #data=remove_first_line('./errors.txt', './errors.txt')


# sendFinish()
# if errors:
#     with open("erros.txt",'w') as f:
#         [print(i) for i in errors]
