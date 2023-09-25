"""
parse_zone.py
-----------------


scroll through a modflow file and find row column layer pairs per zone

"""

import os

def find_zones(fname, zone):
    """ for the given zone, return row colum layer indicies for that zone """
    with open(fname, 'r') as f:
        for ix, line in enumerate(f.readlines()):
            if ix ==0:
                continue
            vals = list(map(int, line.strip().split()))
            if vals[3] == zone:
                yield [vals[0], vals[1], vals[2]]


if __name__ == "__main__":
    basepath = os.path.join("unversioned",
            "100k_release_model_forKevin")
    cpath = os.path.join(basepath, "Cr6_source_zones.dat")
    zone = 3
    z = list(find_zones(cpath, zone))
    print(z)

