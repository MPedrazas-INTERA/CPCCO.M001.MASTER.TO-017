"""
release_rates.py
------------------



This is custom code for Helal's 100K project.


- read a stomp saturation file
- for every row in that file (the t-th timestep)
   - find the last column where the value is 1.0
   - go offset N columns and get the column index
       - right is positive
       - left is negative
   - the above column index corresponds to a node; for that node,
       - open the corresponding dat file
       - get the ith column and the row corresponding to the t-th timestep
       - multiply that value by a number
   return the result


At the end, we have the release at the saturation boundary for
 every timestep in the file

"""

import os
import sys
SAT_THRESH = 1.0

import itertools

def stream_file(filename):
    """ just get lines from a file """
    with open(filename, 'r') as f:
        for line in f:
            yield line

def stream_rows(filename):
    """ convert a line into a bunch of numbers """
    for ix, line in enumerate(stream_file(filename)):
        try:
            vals = list(map(float, line.split()))
            yield vals
        except ValueError as e:
            pass

def get_sat_index(values):
    """ for a list of values, get the index
    of the last one that is 1.0 """
    for ix, v in enumerate(values):
        if v<1.0:
            return ix-1

def parse_rows(filename, offset=0):
    """ parse a row of numbers
    
    yields: time and the column index

    """

    for row in stream_rows(filename):
        time = row[0]
        values = row[1:]
        ix = get_sat_index(values)
        N = offset+ix
        yield time, N

def release_file_indexes(basedir, fnamebase="gw_conc"):
    """ returns a dict of the filename index"""
    fnames = os.listdir(basedir)
    for name in fnames:
        if fnamebase in name:
            try:
                ix = int(name.split(fnamebase)[1].split(".dat")[0])
                yield ix
            except IndexError:
                pass

def file_map(basedir, fnamebase="gw_conc", offset=0):
    """ returns a dictionary that relates the node index buried in a file
    name to the column index in the saturation file

    offset should be zero almost always; if you want to offset the node,
    do it in parse_rows
    """
    vals = sorted(list(release_file_indexes(basedir, fnamebase)))
    keys = [ix+offset for ix, v in enumerate(vals)] # no +1 because time col isn't counted
    return dict(zip(keys, vals))

def get_col_from_conc(filename, colindex=4):
    """ for the given rows indexes and the column index, return the values """
    with open(filename, "r") as f:
        for ix, line in enumerate(f):
            try:
                yield list(map(float, line.split()))[colindex]
            except ValueError as e:
                pass

def get_values_for_conc(filename, rows, colindex=4):
    remaining = len(rows)
    for ix, val in enumerate(get_col_from_conc(filename, colindex)):
        if ix in rows:
            yield val
            remaining-=1
        if remaining==0:
            return

def get_values_for_files(datadict, basedir, fnamebase="gw_conc", colindex=4):
    """ given a dictionary (datadict) where they keys are nodes and values are
    row indicies; for every key, open the corresponding data file and extract
    the rows for the given column index (colindex)
    """
    out = dict()
    for key in datadict.keys():
        fname=os.path.join(basedir, "{0}{1}.dat".format(fnamebase, key))
        vals = list(get_values_for_conc(fname, datadict[key], colindex=colindex))
        if len(vals)!=len(datadict[key]):
            """ why???"""
            raise Exception("{0} {1} {2}".format(key, len(vals), len(datadict[key])))
        out[key] = vals
    return out

def row_indicies_for_node(node, nodes):
    """ given a list of nodes (one for each timestep),
    return the row index for those nodes matching the node"""

    return [ix for ix in range(len(nodes)) if nodes[ix]==node]

def node_dict(nodes):
    """ given a list of nodes (one for each timestep):
    return a dict that contains
       keys: the node
       vals: the row indicies corresponding to that node
    """
    d = dict()
    for node in sorted(list(set(nodes))):
        d[node] = row_indicies_for_node(node, nodes)
    return d

def values_at_saturation(fname, outputfile, colindex, scale, offset):
    """ This is the "main" function

    It calculates the release at the point of saturation for each timestep.

    given
      - fname, the path to the input saturation file
        (usually saturation.dat)
      - outputfile, the path to the resultant .csv file
      - colindex, the index (0-indexed) of the column in the concentration files
         that we are calling 'values'
      - sale, a scalar multiplication factor for the values
      - offset, number that means which column to reference in the saturation file
         0 means use the last column where saturation = 1
         1 means use the first column where saturation < 1
         2 means use the second column where saturation <1 , etc...

    result:
       - returns the data as an array containing the results below (minus the header)

       - writes a csv file (outputfile) is created containing the following columns

         0. row index (0 == first line without comments)
         1. timestep for that row
         2. column in the saturation file that was referenced
         3. the node that the column corresponds to
         4. the value in the corresponding concentration file
         5. the scaled value in the corresponding concentration file

    I noticed that there is one more row in the saturation file than there is in the
    concentration files, so I'm reading N-1 rows from the saturation file.

    """

    rows = list(parse_rows(fname, offset=offset))[0:-1]
    """ -1 because an there's an extra row in the saturation file """
    times, columns = zip(*rows)
    unique_ix = sorted(list(set(columns)))
    fmap = file_map(os.path.dirname(fname))
    nodes = [fmap[c] for c in columns]

    d = node_dict(nodes)
    out = get_values_for_files(d, os.path.dirname(fname), colindex=colindex)

    data = list(itertools.chain.from_iterable(
         (list(zip(d[i], out[i])) for i in list(set(nodes)))))
    data.sort(key = lambda x: x[0])
    row_indicies, values = zip(*data)

    data = zip(row_indicies, times, columns, nodes, values, [v*scale for v in values])
    """ the final data set """
    header = ",".join([
        "Row (after comments)", "Time","Column", "Node","Value","Scaled Value"])

    with open(outputfile, "w") as f:
        """ write the results to a csv"""
        f.write((header+ "\n"))
        for item in data:
            f.write((",".join(map(str, item))+"\n"))

    return data

if __name__ == "__main__":
    basepath = os.path.join(
            "unversioned", "100k_release_model_forKevin", "120-KW-5")

    fname = os.path.join(
            basepath, "saturation.out")

    offset = 0
    colindex = 3
    scale = 1
    outputfile = os.path.join(basepath, "release_timeseries.csv")
    values_at_saturation(fname, outputfile, colindex, scale, offset)
