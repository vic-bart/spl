import glob

# Global constants
RS_FOLDER="../result/"
RS_FILE="new_result.txt"
CSV_INDEX=6
TXT_INDEX=8


def get_all_result() -> None:
    rs=[]
    for fn in sorted(glob.glob(f"{RS_FOLDER}/*")):
        rs.append(fn)

    with open(RS_FILE,"w") as f:
        [print(l,file=f) for l in rs]

def count_valid_result() -> None:
    was_csv = False
    is_txt = False
    count = 0

    try:
        with open(RS_FILE,'r') as f:
            for fn in f:
                fn = fn.strip()
                is_txt = True if fn.split(".")[-1] == "txt" else False
                if was_csv and is_txt:
                    count += 1
                    
                was_csv = True if fn.split(".")[-1] == "csv" else False
    except FileNotFoundError:
        print(f"Could not find file {RS_FILE}.")
    
    print(count)

def count_csv_lines() -> None:
    try:
        with open(RS_FILE,'r') as f:
            for fn in f:
                fn = fn.strip()
                is_csv = True if fn.split(".")[-1] == "csv" else False
                if is_csv:
                    with open(fn,'r') as csvf:
                        lines = csvf.readlines()
                        print(len(lines))
    except FileNotFoundError:
        print(f"Could not find file {RS_FILE}.")


# get_all_result()
# count_valid_result()
# count_csv_lines()

# Solved commands = 172236
# Total commands = 579633