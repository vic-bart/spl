import re,glob,time,json

# Global constants
RESULT_FOLDER="../result/"
DEBUG_PERIOD=10 # Seconds
TIMEOUT: dict[int|int] = {} # map size -> timeout in seconds
TIMEOUT[0] = 60 # <100x100 -> 60 seconds
TIMEOUT[10000] = 180 # >100x100 -> 3 minutes
CMD_FILE="cmd.txt"
MOTION={}
MOTION["w"]=(0,0)
MOTION["r"]=(0,1)
MOTION["u"]=(1,0)
MOTION["l"]=(0,-1)
MOTION["d"]=(-1,0)

# Global variables
time_last_debug=0
time_start=0
time_end=0
debug_count=0
debug_total=0

def get_timeout(fn_m):
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

def get_command(fn, k) -> str:
    m = fn.split("-random")[0].split("-even")[0].split("/")[-1]
    map_name = f"../bench_mark/{m}/{m}.map"
    scen = fn.split("/")[-1].split("scen-")
    scen = f"{scen[0]}{scen[1].split('-')[0]}"
    return f"../../cbs -m {map_name} -a ../bench_mark/{m}/{scen}.scen -o {fn.split('.txt')[0]}.csv --outputPaths {fn} -k {str(k)} -t {get_timeout(map_name)}"

def count_solutions_with_paths() -> None:
    result=[]
    for fn in sorted(glob.glob(f"{RESULT_FOLDER}/*")):
        result.append(fn)
    is_txt=False
    solutions_with_paths=0

    # Debug
    global time_last_debug
    global time_start
    global time_end
    global debug_count
    global debug_total
    time_start = time.time()
    debug_total = len(result)
    #######

    try:
        for fn in result: # "../result/Berlin_1_256-even-scen-1-agents-100.txt
            is_txt = True if fn.split(".")[-1] == "txt" else False
            if not is_txt:
                continue
            with open(fn,'r') as f:
                paths = len(f.readlines())
            if paths > 0:
                solutions_with_paths += 1

            # Debug
            debug_count += 1
            time_end = time.time()
            if (time.time() - time_last_debug) < DEBUG_PERIOD:
                pass
            else:
                time_last_debug = time.time()
                print(f"ETA: {(((time_end-time_start)/debug_count)*(debug_total-debug_count))//60} minutes remaining. {debug_count}/{debug_total} solutions processed.")
            #######

    except:
        pass

    print(f"{solutions_with_paths} solutions with paths.")

def get_solutions_with_malformed_paths(save:bool=False) -> None:
    result=[]
    for fn in sorted(glob.glob(f"{RESULT_FOLDER}/*")):
        result.append(fn)
    is_txt=False
    solutions_with_malformed_paths=[]
    pattern_agent = re.compile(r"""
        \d+:
    """, re.VERBOSE)
    pattern_goal = re.compile(r"""
        \d+,\d+
    """, re.VERBOSE)
    empty_solution=0
    malformed_solution=0
    valid_solution=0

    # Debug
    global time_last_debug
    global time_start
    global debug_count
    global debug_total
    time_start = time.time()
    debug_total = len(result)
    #######

    # try:
    for fn in result: # ../result/Berlin_1_256-even-scen-1-agents-128.txt

        # Debug
        debug_count += 1
        if (time.time() - time_last_debug) < DEBUG_PERIOD:
            pass
        else:
            time_last_debug = time.time()
            print(f"ETA: {(((time_last_debug-time_start)/debug_count)*(debug_total-debug_count))//60} minutes remaining. {debug_count}/{debug_total} solutions processed.")
        #######

        is_txt = True if fn.split(".")[-1] == "txt" else False
        if not is_txt:
            continue

        # ../result/Berlin_1_256-even-scen-1-agents-136.txt
        # ../bench_mark/Berlin_1_256/Berlin_1_256-even-10.scen
        fn = fn.split("-")
        map_name = "-".join(fn[:-5]).split("/")[-1]
        scen_type = fn[-5]
        type_id = int(fn[-3])
        agent_count = int(fn[-1].split(".")[0])
        scen_file = f"../bench_mark/{map_name}/{map_name}-{scen_type}-{type_id}.scen"
        with open(scen_file,'r') as f:
            instances = f.readlines()
        instance = instances[agent_count].split("\t")
        goal = f"{instance[-2]},{instance[-3]}"

        fn = "-".join(fn)
        with open(fn,'r') as f:
            paths = f.readlines()

        if not paths:
            cmd = get_command(fn, agent_count)
            solutions_with_malformed_paths.append(cmd)
            empty_solution += 1
            continue

        match = pattern_goal.findall(paths[-1])
        if match and match[-1] != goal:
            cmd = get_command(fn, agent_count)
            solutions_with_malformed_paths.append(cmd)
            malformed_solution += 1
            continue

        match = pattern_agent.findall(paths[-1])
        if not match:
            cmd = get_command(fn, agent_count)
            solutions_with_malformed_paths.append(cmd)
            malformed_solution += 1
            continue

        total_paths = int(match[0][:-1]) + 1
        if total_paths != agent_count:
            cmd = get_command(fn, agent_count)
            solutions_with_malformed_paths.append(cmd)
            malformed_solution += 1
            continue

        valid_solution += 1

    # except:
    #     print("Exception")
        
    print(f"""
        Empty solutions: {empty_solution}\n
        Malformed solutions: {malformed_solution}\n
        Valid solutions: {valid_solution}
    """)
    
    if save:
        with open(CMD_FILE,"w") as f:
            [print(l,file=f) for l in solutions_with_malformed_paths]

def draw_paths(map_height, map_width) -> None:
    fn="./temp2.txt"
    lines=[]
    pattern=re.compile(r"""
        \d+,\d+
    """, re.VERBOSE)
    paths=[]

    with open(fn,'r') as f:
        for l in f:
            match = pattern.findall(l)
            path = [tuple(int(d) for d in m.split(",")) for m in match]
            paths.append(path)

    last_timestep=max([len(path) for path in paths])
 
    for timestep in range(last_timestep):
        solution=[]
        for row in range(map_height):
            solution.append([])
            for _ in range(map_width):
                solution[row].append(".")
        for k in range(len(paths)):
            try:
                x = paths[k][timestep][0]
                y = paths[k][timestep][1]
                solution[x][y] = str(k)
            except:
                x = paths[k][-1][0]
                y = paths[k][-1][1]
                solution[x][y] = str(k)
        lines.append(f'{" " * map_width}\n{"\n".join([" ".join(row) for row in solution])}')
    

    with open("debug.txt", "w") as f:
        [print(l,file=f) for l in lines]

def shrink_json():
    with open("./solution.json", "r") as f:
        data = json.load(f)

    length = len(data)//2
    # shrinked_data = data[:length]
    shrinked_data = data[length:]
    with open("./shrink2.json", "w") as f:
        json.dump(shrinked_data, f, indent=2)

def create_mapf_visualiser_result(fn:str):
    pattern = re.compile(r"""
        \(.+\)
    """, re.VERBOSE)
    with open(fn,'r') as f:
        lines = f.readlines()
        matches=[pattern.findall(l)[0].split("->") for l in lines]
    
    # Correct coordinate system; (y,x) to (x,y)
    for m in matches:
        for i in range(len(m)):
            coord = m[i].split("(")[-1].split(")")[0].split(",")
            m[i] = f"({coord[1]},{coord[0]})"

    planning_result=[]
    for t in range(max([len(m) for m in matches])):
        l=f"{t}:"
        for m in matches:
            try:
                l += f"{m[t]},"
            except IndexError:
                l += f"{m[-1]},"
        planning_result.append(l)
    print(planning_result)
    return planning_result

def get_mapf_visualiser_results():
    result=[
        "./cbsh2-rtc-empty-3-3-random-2-agents-8.txt"
    ]
    # result=[]
    # for fn in sorted(glob.glob(f"{RESULT_FOLDER}/*")):
    #     result.append(fn)

    try:
        for fn in result:
            planning_result = create_mapf_visualiser_result(fn)
    except KeyboardInterrupt:
        pass

    with open(f"mapf-visualiser.txt","w") as f:
        [print(l,file=f) for l in planning_result]

def check_cost():
    results=[]
    for fn in sorted(glob.glob(f"{RESULT_FOLDER}/*")):
        is_txt = True if fn.split(".")[-1] == "txt" else False
        if is_txt:
            results.append(fn)

    RUNTIME_INDEX=0
    SOLUTION_COST_INDEX=5
    OPTIMAL_COST_INDEX=6
    lines=[]
    for fn in results:
        fn = f"..{fn.split(".")[2]}.csv"
        with open(fn,'r') as f:
            filelines = f.readlines()
            for i in range(-1, -len(filelines), -1):
                result = filelines[i].split(",")
                try:
                    if int(float(result[RUNTIME_INDEX])) != 60 or int(float(result[RUNTIME_INDEX])) != 180:
                        break
                except ValueError as e:
                    print(e)

            if int(float(result[RUNTIME_INDEX])) == 60 or int(float(result[RUNTIME_INDEX])) == 180:
                continue

        if result[SOLUTION_COST_INDEX] > result[OPTIMAL_COST_INDEX]:
            lines.append(f"{fn}: Solution >> ABOVE >> Optimal")
        elif result[SOLUTION_COST_INDEX] < result[OPTIMAL_COST_INDEX]:
            lines.append(f"{fn}: Solution << BELOW << Optimal")

    with open("checked_costs.txt","w") as f:
        [print(l,file=f) for l in lines]


if __name__ == "__main__":
    # get_solutions_with_malformed_paths(save=True)
    # shrink_json()
    # get_mapf_visualiser_results()
    check_cost()