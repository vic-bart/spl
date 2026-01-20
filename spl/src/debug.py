import re,glob,time,yaml

# Global constants
RESULT_FOLDER="../result/"
DEBUG_PERIOD=10 # Seconds
TIMEOUT: dict[int|int] = {} # map size -> timeout in seconds
TIMEOUT[0] = 60 # <100x100 -> 60 seconds
TIMEOUT[10000] = 180 # >100x100 -> 3 minutes
CMD_FILE="cmd.txt"

# Global variables
time_last_debug=0
time_start=0
time_end=0
debug_count=0
debug_total=0

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

def count_solutions_without_paths() -> None:
    result=[]
    for fn in sorted(glob.glob(f"{RESULT_FOLDER}/*")):
        result.append(fn)
    is_txt=False
    solutions_without_paths=0

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
            if paths == 0:
                solutions_without_paths += 1

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

    print(f"{solutions_without_paths} solutions without paths.")

def get_solutions_without_paths() -> None:
    result=[]
    for fn in sorted(glob.glob(f"{RESULT_FOLDER}/*")):
        result.append(fn)
    is_txt=False
    solutions_without_paths=[]

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
            fn = fn.strip()
            is_txt = True if fn.split(".")[-1] == "txt" else False
            if not is_txt:
                continue
            with open(fn,'r') as f:
                paths = len(f.readlines())
            if paths == 0:
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
                solutions_without_paths.append(cmd)

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

    with open(CMD_FILE,"w") as f:
        [print(*i,file=f) for i in solutions_without_paths]

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

def count_solutions_with_malformed_paths() -> None:
    result=[]
    for fn in sorted(glob.glob(f"{RESULT_FOLDER}/*")):
        result.append(fn)
    is_txt=False
    solutions_with_malformed_paths=0
    pattern = re.compile(r"""
        \d+:
    """, re.VERBOSE)

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
        for fn in result: # ../result/Berlin_1_256-even-scen-1-agents-128.txt
            is_txt = True if fn.split(".")[-1] == "txt" else False
            if not is_txt:
                continue
            with open(fn,'r') as f:
                paths = f.readlines()
                total_paths = int(pattern.findall(paths[-1])[0][:-1]) + 1
            agent_count = int(fn.split("-")[-1].split(".")[0])
            if total_paths != agent_count:
                solutions_with_malformed_paths += 1

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

    print(f"{solutions_with_malformed_paths} solutions with malformed paths.")

def get_solutions_with_malformed_paths() -> None:
    result=[]
    for fn in sorted(glob.glob(f"{RESULT_FOLDER}/*")):
        result.append(fn)
    is_txt=False
    solutions_with_malformed_paths=[]
    pattern = re.compile(r"""
        \d+:
    """, re.VERBOSE)

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
        for fn in result: # ../result/Berlin_1_256-even-scen-1-agents-128.txt
            is_txt = True if fn.split(".")[-1] == "txt" else False
            if not is_txt:
                continue
            with open(fn,'r') as f:
                paths = f.readlines()
                total_paths = int(pattern.findall(paths[-1])[0][:-1]) + 1
            agent_count = int(fn.split("-")[-1].split(".")[0])
            if total_paths != agent_count:
                m = fn.split("-random")[0].split("-even")[0].split("/")[-1]
                map_name = f"../bench_mark/{m}/{m}.map"
                scen = fn.split("/")[-1].split("scen-")
                scen = f"{scen[0]}{scen[1].split('-')[0]}"
                cmd=(
                    "../../cbs",
                    "-m",map_name,
                    "-a",f"../bench_mark/{m}/{scen}.scen",
                    "-o",f"{fn.split('.txt')[0]}.csv",
                    "--outputPaths",fn,
                    "-k",str(agent_count),
                    "-t",f"{getTimeout(map_name)}",
                )
                solutions_with_malformed_paths.append(cmd)

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

    with open(CMD_FILE,"w") as f:
        [print(*i,file=f) for i in solutions_with_malformed_paths]


get_solutions_with_malformed_paths()