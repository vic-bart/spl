(first read-through of Andy's batch scripts)

# genCMD
## Notes
- `exe` = executable from compiling MAPF_T (i.e. the cbs executable).
- `fn_folder` = folder containing benchmarks (what does fn stand for?)
- `fn_opt_temp` = ?
- `all` = global buffer variable that temporarily stores the final commands before writing them out to a file.
- `ml` = never used, but I think it's the variable m is meant to be iterating over.
- `BIGI` = BIG-Index? Might not be relevant for MAPF_T

## Changes
- `./cbs -m random-32-32-20.map -a random-32-32-20-random-1.scen -o test.csv --outputPaths=paths.txt -k 30 -t 60` is an example cmd to run tests on MAPF-P
- `../release/cbs -m ../bench_mark/empty-8-8.map -a ../bench_mark/empty-8-8.scen -o test.csv --outputPaths=paths.txt -k 30 -t 60`