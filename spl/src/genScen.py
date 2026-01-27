import pathlib,math,random,re,debug

# Global constants
BENCH_MARK_FOLDER="../bench_mark/"
MAP_NAME="empty-3-3"
MAP_HEIGHT=3
MAP_WIDTH=3

# Global variables

def get_optimal_path_length(start:tuple[int,int], end:tuple[int,int]) -> int:
    # start:(0,0), end:(2,3)
    length=0
    delta_x = abs(start[0] - end[0])
    delta_y = abs(start[1] - end[1])
    if delta_x > 0 and delta_y > 0:
        length += min(delta_x, delta_y) * math.sqrt(2)
    length += abs(delta_x - delta_y)
    return length

def get_start_and_end(starts, ends) -> tuple[tuple[int,int], tuple[int,int]]:
    """
    Reassigns start and end vertices randomly until a non-trivial pair is found. 
    """
    while True:
        start = (random.randint(0,MAP_WIDTH-1),random.randint(0,MAP_HEIGHT-1))
        end = (random.randint(0,MAP_WIDTH-1),random.randint(0,MAP_HEIGHT-1))
        if start == end:
            continue
        if start in starts:
            continue
        if end in ends:
            continue
        return (start, end)

def create_scen() -> None:
    pathlib.Path(f"./{MAP_NAME}").mkdir(exist_ok=True)

    scen_type="random"
    type_id=2
    scen_file=f"./{MAP_NAME}/{MAP_NAME}-{scen_type}-{type_id}.scen"
    starts=[]
    ends=[]
    lines=["version 1"]

    for _ in range(MAP_HEIGHT * MAP_WIDTH):
        start, end = get_start_and_end(starts, ends)
        starts.append(start)
        ends.append(end)
        length = get_optimal_path_length(start, end)
        lines.append("\t".join((
            str(int(length//4)),
            f"{MAP_NAME}.map",
            str(MAP_HEIGHT),
            str(MAP_WIDTH),
            str(start[0]),
            str(start[1]),
            str(end[0]),
            str(end[1]),
            "{0:.8f}".format(length),
        )))

    with open(scen_file, "w") as f:
        [print(l,file=f) for l in lines]

if __name__ == "__main__":
    # create_scen()
    debug.draw_paths(MAP_HEIGHT, MAP_WIDTH)

# ../../cbs -m ./empty-3-3/empty-3-3.map -a ./empty-3-3/empty-3-3-random-2.scen -o temp.csv --outputPaths temp.txt -k 3 -t 60