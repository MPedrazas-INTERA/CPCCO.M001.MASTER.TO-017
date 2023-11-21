"""
proc_surf.py
-------------------


reads a surface output file (.dat file), pulls out a user specified
column and writes the data to a file

"""
import os

def proc_surf(fnamein, col_idx=4):
    idx = 0
    with open(fnamein, "r") as f:
        for ix, line in enumerate(f.readlines()):
            try:
                v = list(map(float, line.strip().split()))
                ts = v[0]
                v = v[col_idx]
                yield idx, ts, col_idx, -1, v
                idx+=1
            except ValueError:
                pass

def write_f(fnameout, iterable, scale=1):

    with open(fnameout, "w") as f:
        f.write(",".join([
            "Row (after comments)",
            "Time",
            "Column",
            "Node",
            "Value",
            "scaled Value"])+"\n")

        for line in iterable:
            scaled = line[-1]*scale
            f.write(",".join(map(str, line)))
            f.write(",{0}\n".format(scaled))

if __name__ == "__main__":
    bdir = os.path.join("unversioned","100k_release_model_forKevin")
    fname = os.path.join(bdir, "120-KW-5","gw_conc21.dat")
    fout = os.path.join(bdir, "120-KW-5","temp.csv")
    write_f(fout, proc_surf(fname, 4), 1)
    
