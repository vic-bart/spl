import pathlib,math,random,debug,itertools,time,numpy

# Global constants
BENCH_MARK_FOLDER="../bench_mark/"
MAP_NAME="empty-3-3"
MAP_HEIGHT=3
MAP_WIDTH=3

def get_optimal_path_length(start:tuple[int,int], end:tuple[int,int]) -> int:
    # start:(0,0), end:(2,3)
    length=0
    delta_x = abs(start[0] - end[0])
    delta_y = abs(start[1] - end[1])
    if delta_x > 0 and delta_y > 0:
        length += min(delta_x, delta_y) * math.sqrt(2)
    length += abs(delta_x - delta_y)
    return length

def get_instances_random(starts, ends) -> tuple[tuple[int,int], tuple[int,int]]:
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

def get_instances_all() -> tuple[tuple[tuple[int,int], tuple[int,int]]]:
    vertices = (
        (0,0), (1,0), (2,0), 
        (0,1), (1,1), (2,1), 
        (0,2), (1,2), (2,2), 
    )
    
    perm=[] # 362,880
    for v in itertools.permutations(vertices, None):
        perm.append(v)

    non_trivial=set() # 39,630
    trivial=set() # 97
    for p in perm[1:]: # Skip trivial instance where source == target for all agents

        # Remove trivial instance where source == target for any agent
        if any(vertices[i] == p[i] for i in range(len(vertices))):
            t = tuple(vertices[i] == p[i] for i in range(len(vertices)))

            if t in trivial:
                continue 

            if rotate_90_clockwise(t) in trivial:
                continue

            if rotate_90_anticlockwise(t) in trivial:
                continue

            if rotate_180(t) in trivial:
                continue

            t_mirror = mirror(t)

            if t_mirror in trivial:
                continue 

            if rotate_90_clockwise(t_mirror) in trivial:
                continue

            if rotate_90_anticlockwise(t_mirror) in trivial:
                continue

            if rotate_180(t_mirror) in trivial:
                continue

            trivial.add(t)

        if p in non_trivial:
            continue

        if rotate_90_clockwise(p) in non_trivial:
            continue

        if rotate_90_anticlockwise(p) in non_trivial:
            continue

        if rotate_180(p) in non_trivial:
            continue

        p_mirror = mirror(p)

        if p_mirror in non_trivial:
            continue

        if rotate_90_clockwise(p_mirror) in non_trivial:
            continue

        if rotate_90_anticlockwise(p_mirror) in non_trivial:
            continue

        if rotate_180(p_mirror) in non_trivial:
            continue

        non_trivial.add(p)

    pairs=[]
    for nt in non_trivial:
        pairs.append((vertices, nt))
    
    return tuple(pairs)

def create_scen() -> None:
    pathlib.Path(f"./{MAP_NAME}").mkdir(exist_ok=True)

    scen_type="random"
    instances=get_instances_all()

    for type_id in range(len(instances)):
        scen_file=f"./{MAP_NAME}/{MAP_NAME}-{scen_type}-{type_id+1}.scen"
        lines=["version 1"]
        instance = instances[type_id]
        for i in range(len(instance[0])):
            start, end = (instance[0][i], instance[1][i])
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
    create_scen()
    # debug.draw_paths(MAP_HEIGHT, MAP_WIDTH)
    



# ../../cbs -m ./empty-3-3/empty-3-3.map -a ./empty-3-3/empty-3-3-random-2.scen -o temp.csv --outputPaths temp.txt -k 3 -t 60