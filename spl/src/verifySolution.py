import re,glob,time

# Global constants
MOTION={}
MOTION['w']=(0,0)
MOTION['r']=(1,0)
MOTION['d']=(0,1)
MOTION['l']=(-1,0)
MOTION['u']=(0,-1)
SOLUTION_FN="solution.csv"
BENCH_MARK_FOLDER="../bench_mark/"
MAP_INDEX=0
SCEN_INDEX=1
TYPE_INDEX=2
AGENT_INDEX=3
SOLUTION_INDEX=4
# START_X_INDEX=
# START_Y_INDEX=
# END_X_INDEX=
# END_Y_INDEX=
DEBUG_PERIOD=10 # Seconds

# Global variables
time_last_debug=0
time_start=0
time_end=0
debug_count=0
debug_total=0


def get_solution() -> list[str]:
    solutions=[]
    with open(SOLUTION_FN,'r') as f:
        for l in f:
            solutions.append(l.split(","))
    return solutions[2:]


def verify_solution() -> None:
    solutions = get_solution()
    for solution in solutions:
        map_name = solution[MAP_INDEX][1:-1]
        scen_type = solution[SCEN_INDEX]
        type_id = solution[TYPE_INDEX]
        agent_count = int(solution[AGENT_INDEX])
        solution_plans = solution[SOLUTION_INDEX].split("\\n")
        bench_mark_fn = f"{BENCH_MARK_FOLDER}{map_name}/{map_name}-{scen_type}-{type_id}.scen"
        with open(bench_mark_fn,'r') as f:
            f = list(f)
            for i in range(1, agent_count+1):
                print(f[i].split())
                exit(0)
                # Verify path reaches target
                # Verify no obstacle conflicts
                # Verify no vertex conflicts
                # Verify no swap conflicts
                # Verify solution cost <= MAPF Tracker solution cost
                


verify_solution()

# map_name,         scen_type,  type_id,    agent_count,    solution_plan,                                              flip_up_down
# "Berlin_1_256",   even,       1,          3,              "2l5ul2u3lu20l19u\n                                         FALSE
#                                                            14l11u\n
#                                                            u31l15dl2dl2dl2dl2d2l2dl2dl2dl41dr4dr4dr4dr3dr18dr4d2rd",