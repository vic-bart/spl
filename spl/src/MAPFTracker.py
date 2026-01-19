import re,glob,time,yaml

# Global constants
MOTION={}
MOTION[(0,0)]="w"
MOTION[(0,1)]="r"
MOTION[(1,0)]="d"
MOTION[(0,-1)]="l"
MOTION[(-1,0)]="u"
SOLUTION_FN="solution"
RESULT_FOLDER="../result/"
DEBUG_PERIOD=10 # Seconds

# Global variables
time_last_debug=0
time_start=0
time_end=0
debug_count=0
debug_total=0

def get_result() -> list[str]:
    result=[]
    for fn in sorted(glob.glob(f"{RESULT_FOLDER}/*")):
        result.append(fn)
    return result

def convert_solution_string(solution:str="", encoded:bool=True) -> str:
    # (0,0) -> (0,1) -> (1,1) -> (2,1) -> (2,0) -> (2,0) -> (1,0)
    # drruwl
    # d2ruwl (if encoded)

    pattern = re.compile(r"""
        \d+,\d+
    """, re.VERBOSE)

    motions=[]
    prev_position=None
    for match in pattern.finditer(solution):
        position = match.group().split(",")
        if prev_position is not None:
            x = int(position[0])-prev_position[0]
            y = int(position[1])-prev_position[1]
            motions.append(MOTION[(x,y)])
        prev_position = (int(position[0]),int(position[1]))
    motion = "".join(motions)
    
    if not encoded:
        return motion
    
    encoded_motions=[]
    prev_move=None
    repeated_move=1
    for move in motion:
        if prev_move is not None:
            if move == prev_move:
                repeated_move += 1
            else: # move != prev_move
                repeated_move = "" if repeated_move == 1 else repeated_move
                encoded_motions.append(f"{repeated_move}{prev_move}")
                repeated_move=1
        prev_move = move
    repeated_move = "" if repeated_move == 1 else repeated_move
    encoded_motions.append(f"{repeated_move}{prev_move}")
    encoded_motion = "".join(encoded_motions)
    
    return encoded_motion

def create_solution_plan(fn:str) -> list[str]:
    pattern = re.compile(r"""
        \(.+\)
    """, re.VERBOSE)
    solutions=[]
    with open(fn,'r') as f:
        for l in f:
            match = pattern.findall(l)
            solutions.append(convert_solution_string(*match))
    return solutions

def create_solution_csv() -> None:
    result=get_result()
    is_txt=False
    lines=["map_name,scen_type,type_id,agent_count,solution_plan,flip_up_down"]
    flip_up_down="FALSE"

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
        for fn in result: # ../result/Berlin_1_256-even-scen-1-agents-2.txt
            is_txt = True if fn.split(".")[-1] == "txt" else False
            if is_txt:
                solution_plan = "\n".join(create_solution_plan(fn))
                fn = fn.split("-")
                map_name = "-".join(fn[:-5]).split("/")[-1]
                scen_type = fn[-5]
                type_id = fn[-3]
                agent_count = fn[-1].split(".")[0]
                lines.append(f'"{map_name}",{scen_type},{type_id},{agent_count},"{solution_plan}",{flip_up_down}')

            # Debug
            debug_count += 1
            time_end = time.time()
            if (time.time() - time_last_debug) < DEBUG_PERIOD:
                pass
            else:
                time_last_debug = time.time()
                print(f"ETA: {(((time_end-time_start)/debug_count)*(debug_total-debug_count))//60} minutes remaining. {debug_count}/{debug_total} solutions formatted.")
            #######

    except:
        pass

    with open(f"{SOLUTION_FN}.csv","w") as f:
        [print(l,file=f) for l in lines]

def create_solution_yaml() -> None:
    result=get_result()
    is_txt=False
    data=[]

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
        for fn in result: # ../result/Berlin_1_256-even-scen-1-agents-2.txt
            is_txt = True if fn.split(".")[-1] == "txt" else False
            if is_txt:
                solution_plan = create_solution_plan(fn)
                fn = fn.split("-")
                map_name = "-".join(fn[:-5]).split("/")[-1]
                scen_type = fn[-5]
                type_id = int(fn[-3])
                agent_count = int(fn[-1].split(".")[0])
                entry = {
                    'map_name': map_name,
                    'scen_type': scen_type,
                    'type_id': type_id,
                    'agent_count': agent_count,
                    'solution_plan': solution_plan
                }
                data.append(entry)

            # Debug
            debug_count += 1
            time_end = time.time()
            if (time.time() - time_last_debug) < DEBUG_PERIOD:
                pass
            else:
                time_last_debug = time.time()
                print(f"ETA: {(((time_end-time_start)/debug_count)*(debug_total-debug_count))//60} minutes remaining. {debug_count}/{debug_total} solutions formatted.")
            #######

    except:
        pass

    with open(f"{SOLUTION_FN}.yaml", "w") as f:
        [yaml.dump(d, f, explicit_start=True, sort_keys=False, indent=4) for d in data]

create_solution_yaml()