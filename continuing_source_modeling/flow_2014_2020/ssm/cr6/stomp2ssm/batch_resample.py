"""
batch_resample.py
--------------------

This is the front end to a python module that calculates the
release to the water table in a STOMP model and then writes that information
to a MODFLOW/MT3d SSM file.

The program:

 0. Takes a start directory path (basepath)
 1. Reads a file (mappath) that relates zone names to numbers
    mappath must be of form
       line 0 : header
       >line 0: site name,zone index

    the zone names are assumed to be directory names nested
    inside of (basepath) where STOMP output has been stored.

 2. for each of the zone names/subdirectories:
    a. it reads a target file (saturation_file) that contains
       saturation for nodes in columns and STOMP timesteps in rows.
    b. for each row/timestep, obtains the lowest column index
       where the saturation is 1.0.  The user may specificy an
       (offset), which should be an integer telling the program
       to grab the nearby column.
    c. for each row/timestep, goes to the corresponding
       concentration file; pulls the concentration data from the
       (colindex) column, multiplies by (scale) and yields the
       concentration (or release, depending on scale) at the
       water table for that timestep.

 3. given file (mpath) that specifies the MODFLOW timesteps, it
      resamples the above data into for MODFLOW stress periods
      by averaging over STOMP steps for each stress period

 4. writes the MT3d SSM file (ssm_file) by finding the MODFLOW
     node indicies corresponding to each zone and dumping the
     resampled concentration/release timeseries to to (ssm_file)

     (firstrow) is added as the header to the SSM file
     (nnodes) is added as the second line in the SSM file
     (value_flag) is added at the end of each timestep in the SSM file


This program assumes the following scripts are in the same directory as this
script:
     - __init__.py
     - release_rates.py
     - parse_zone.py
     - resample_time.py
     - proc_surf.py

Developed by Kevin J. Smith 02/09/2017 as part of
   CHPRC.C003.HANOFF Rel 60 (100K model) 
   CHPRC.C003.HANOFF Rel 61 (Composite Analysis)


This program does not use any third-party libraries and was
developed for python 3.x


2/13/2017 KJS
  - this file was modified to target proc_surf.py.  The script no longer
     looks for a breathing  phreatic surface but simply pulls one column
     out of the target file (target_surf_file)
2/16/2017 KJS
  - zomemap was modified to contain an additional multiplier as the last column;
     for the values in that zone, it will be multiplied by the scalar AND the multiplier
2/8/2018 JBF
  - added sorting to mt3d_data.keys and orientation
"""
import os
import resample_time_gaussian as rt
import release_rates as rr
import parse_zone as pz
import proc_surf as ps


def read_map(fname):
    d = dict()
    with open(fname, 'r') as f:
        for ix, line in enumerate(f.readlines()):
            if ix == 0:
                continue
            key, val, mult = line.strip().split(",")
            d[key] = val,float(mult)
    return d


if __name__=="__main__":
    """  -----------------  BEGIN User Input -------------------------
    The following parameters are specified by the USER
    
    """
    """
    basepath = os.path.join(
            "/srv/samba/working_data/Helal/100K_GWM/transport/pest/chrome","slave_15")
    the 'top' directory where all the data is stored
    """
    basepath ="../"
    mappath = os.path.join(basepath, "site2zone.csv")
    """ the path to the file that relates site names to zones """

    ssm_file = os.path.join(basepath, "100HR3_2014_2020_transport_stomp2ssm.ssm")
    """ the path to the SSM file """
    value_flag = 15
    """ added to the end of each node in the SSM file"""
    firstrow = " F T T F T T"
    """ the first line in the SSM file """
    nnodes = 95000
    """ the second line in the SSM file"""

    
    target_surf_file = "gw_conc_1-24.dat"
    """ the name of the saturation files (they are all assumed to have the same name)"""
    if os.path.isfile('../stress_periods_2014-2020_decimal.csv'):
        sp_file = "stress_periods_2014-2020_decimal.csv"
    else:
        sp_file = "stress_periods_decimal_only2016.csv"
    """ the name of the stress period file; assumed to be in the (basepath) directory"""
    mpath = os.path.join(basepath, sp_file)
    """ the path to the stress period file that defines MODFLOW sp/timesteps """

    colindex = 4
    """ the column in the concentration/release files to use """
    scale = 52000000
    """ a scalar multiplier for conentration/release data """
    offset = 0
    """ the offset to use from the column defining the the water table """

    tmult = 1
    """ scalar multipler for time in the modflow stress periods file """

    zonefile = os.path.join(basepath, "cr6_source_zones.dat")
    """ the file that relates the MODFLOW zones and node locations """




    """ -------------- End of USER Input ------------------ """

    zonemap = read_map(mappath)
    """ internal - holds the zone/site name information """
    paths = {i:os.path.join(basepath, i) for i in zonemap.keys()}
    """ internal; the paths to each of the site directories"""
    mt3d_data = dict()
    """ internal - holds the mt3d data """
    max_sp = 0
    """ internal - used to hold the max number of stress periods """

    for zone in paths.keys():
        mult = zonemap[zone][1]
        path = paths[zone]
        tpath = os.path.join(path, "release_timeseries.csv")
        outfile = os.path.join(path, "resampled.csv")
        satpath = os.path.join(path, target_surf_file)
        try:
            ps.write_f(tpath, ps.proc_surf(satpath, colindex),  scale=scale*mult)
            #rr.values_at_saturation(satpath, tpath, colindex, scale, offset)
            mt3d_data[zone] = rt.process(mpath, tpath, outfile, tmult)
            #print(mt3d_data[zone])
            max_sp = mt3d_data[zone][-1][0]
        except FileNotFoundError:
            pass

    zones = dict()
    for zone in zonemap.keys():
        zones[zone] = list(pz.find_zones(zonefile, int(zonemap[zone][0])))

    with open(ssm_file, "w") as f:
        f.write(firstrow+"\n")
        f.write("{0:10}\n".format(nnodes))
        for sp in range(max_sp):
            f.write(" {0}\n".format("-1"))
            f.write(" {0}\n".format(sum(len(zones[s]) for s in mt3d_data.keys())))

            for zone in sorted(mt3d_data.keys(),reverse=True):
                value = mt3d_data[zone][sp][-1]
                orientation = sorted(zones[zone],reverse=True)
                for row in orientation:
                    s = "{0:10}{1:10}{2:10}{3:10.3e}{4:10}\n".format(
                            row[2], row[0], row[1], value, value_flag)
                    f.write(s)

