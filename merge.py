import os,sys

s="m,ins,r, h,t, initAlgo,  initMS, initSOC, initConf, initH, mergeAlgo, mergeMS, mergeSOC,mergeH"
def merge_opt_files(folder_path, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(s)
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith('.opt'):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                    #outfile.write("\n")  # add a newline between files

if __name__ == "__main__":
    fn=sys.argv[1]
    folder = f"./{fn}"       # change to your folder path
    output = f"{fn}.csv"          # name of the merged output file
    merge_opt_files(folder, output)
    print(f"All .opt files merged into {output}")
