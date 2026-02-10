import pathlib,math,random,debug,itertools,time,numpy

# Global constants
BENCH_MARK_FOLDER="../bench_mark/"
MAP_NAME="empty-3-3"
MAP_HEIGHT=3
MAP_WIDTH=3
DEBUG_PERIOD=5 # Seconds

# Global variables
time_last_debug=0
time_start=0
time_end=0
debug_count=0
debug_total=0

def get_optimal_path_length(start:tuple[int,int], end:tuple[int,int]) -> int:
    # start:(0,0), end:(2,3)
    length=0
    delta_x = abs(start[0] - end[0])
    delta_y = abs(start[1] - end[1])
    if delta_x > 0 and delta_y > 0:
        length += min(delta_x, delta_y) * math.sqrt(2)
    length += abs(delta_x - delta_y)
    return length

def get_vertices_random(starts, ends) -> tuple[tuple[int,int], tuple[int,int]]:
    """
    Reassigns source and target vertices randomly until a non-trivial pair is found. 
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
        start, end = get_vertices_random(starts, ends)
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

def print_nested(xs):
    size = int(math.sqrt(len(xs)))
    string = ""
    for i in range(size):
        for j in range(size):
            string += f"{str(xs[(i * size)+j])} "
        string += "\n"
    print(string)

def rotate_90_anticlockwise(xs):
    size = int(math.sqrt(len(xs)))
    ys = [None] * len(xs)
    i:int
    j:int = 0
    for col in range(size):
        i = size - col - 1
        for row in range(size):
            ys[j] = xs[i]
            i += size
            j += 1
    return tuple(ys)

def rotate_90_clockwise(xs):
    size = int(math.sqrt(len(xs)))
    ys = [None] * len(xs)
    i:int
    j:int = 0
    for col in range(size):
        i = len(xs) + col - size
        for row in range(size):
            ys[j] = xs[i]
            i -= size
            j += 1
    return tuple(ys)

def swap(xs, i, j):
    x = xs[i]
    xs[i] = xs[j]
    xs[j] = x

def rotate_180(xs):
    i:int = 0
    j:int = len(xs) - 1
    ys = list(xs)
    for pixel in range(len(ys) // 2):
        swap(ys, i, j)
        i += 1
        j -= 1
    return tuple(ys)

def flip(xs):
    size = int(math.sqrt(len(xs)))
    i:int = 0
    j:int = len(xs) - size
    ys = list(xs)
    for row in range(size // 2):
        for col in range(size):
            swap(ys, i, j)
            i += 1
            j += 1
        j -= 2 * size
    return tuple(ys)

def mirror(xs):
    size = int(math.sqrt(len(xs)))
    i:int
    j:int
    ys = list(xs)
    for col in range(size // 2):
        i = col
        j = size - 1 - col
        for row in range(size):
            swap(ys, i, j)
            i += size
            j += size
    return tuple(ys)

if __name__ == "__main__":
    # create_scen()
    # debug.draw_paths(MAP_HEIGHT, MAP_WIDTH)
    vertices = (
        (0,0), (1,0), (2,0), 
        (0,1), (1,1), (2,1), 
        (0,2), (1,2), (2,2), 
    )
    # vertices = (
    #     'a', 'b', 'c',
    # )
    perm=[]
    for v in itertools.permutations(vertices, None):
        perm.append(v)
    # print(perm)
    print(len(perm)) # 362,880

    non_trivial=set()
    trivial=set()
    # try:
    for p in perm[1:]: # Skip trivial instance where source == target for all agents

        # Remove trivial instance where source == target for any agent
        if any(vertices[i] == p[i] for i in range(len(vertices))):
            t = tuple(vertices[i] == p[i] for i in range(len(vertices)))
            if rotate_90_clockwise(t) in trivial:
                continue

            if rotate_90_anticlockwise(t) in trivial:
                continue

            if rotate_180(t) in trivial:
                continue

            t = mirror(t)

            if rotate_90_clockwise(t) in trivial:
                continue

            if rotate_90_anticlockwise(t) in trivial:
                continue

            if rotate_180(t) in trivial:
                continue

            trivial.add(t)
            non_trivial.add(p)
            continue

        if rotate_90_clockwise(p) in non_trivial:
            continue

        if rotate_90_anticlockwise(p) in non_trivial:
            continue

        if rotate_180(p) in non_trivial:
            continue

        p = mirror(p)

        if rotate_90_clockwise(p) in non_trivial:
            continue

        if rotate_90_anticlockwise(p) in non_trivial:
            continue

        if rotate_180(p) in non_trivial:
            continue

        non_trivial.add(p)
    # except KeyboardInterrupt:
    #     pass

    print(len(non_trivial)) # 65,090
    print(len(trivial)) # 133

    pairs=[]
    for nt in non_trivial:
        pairs.append((vertices, nt))
    
    # print(pairs)



# ../../cbs -m ./empty-3-3/empty-3-3.map -a ./empty-3-3/empty-3-3-random-2.scen -o temp.csv --outputPaths temp.txt -k 3 -t 60