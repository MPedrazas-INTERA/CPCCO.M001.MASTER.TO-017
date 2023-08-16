
"""

SCRIPT: read UCN Files & write shps of concentration at specific times
            uses flopy to create *.shp in model coordinates (0,0 is lower left hand corner)
            uses MODFLOW, not FloPy, numbering in the *.shp file names
            copies projection from model grid using geopandas

INPUT:  ./input/shp_dir/model_dates/<model_dates>.xlsx
        ../model_files/sce/transportRun/<UCN file>

OUTPUT: *.shps with prjs in ./output/ucn_shps/sce/transportRun/
        ./input/shp_dir/model_dates/sce/<transportRun>.csv


@author: jblainey
@modified by mpedrazas
"""
import flopy
import flopy.utils.binaryfile as bf
import pandas as pd
import csv
import os
import time
import glob
import shutil
import geopandas as gpd  
import sys

print('python: {}'.format(".".join(map(str, sys.version_info[:3]))))    # python 3
print('flopy version: {}'.format(flopy.__version__))                    # 3.2.10
print('csv version: {}'.format(csv.__version__))                    # 3.2.10
print('pandas version: {}'.format(pd.__version__))                      # pandas version: 0.23.4

def ucn2shp(sce, transportRun, SPlist):

    # [Step 1] House-keeping:
    print('*'*25 + str(transportRun) + '*'*25)
    shpDir = os.path.join(cwd, 'output', 'ucn_shps', sce, transportRun)
    if not os.path.exists(shpDir):
        os.makedirs(shpDir)

    # delete all file and folders in transportRun folder:
    if delete_mode:
        mfile = [ff for ff in glob.glob(os.path.join(shpDir,'*')) if not os.path.isdir(ff)]
        mdir  = [ff for ff in glob.glob(os.path.join(shpDir,'*')) if os.path.isdir(ff)]
        for mm in mdir:
            shutil.rmtree(mm)
        for mm in mfile:
            os.remove(mm)

    #[Step] Read in UCN File:
    path2ucn = os.path.join(root, 'mruns', sce, transportRun, 'MT3D001.UCN')
    ucnobj = bf.UcnFile(path2ucn, precision='double')
    spucn = ucnobj.get_kstpkper()   # list of kstp, kper tuples in ucn
    times = ucnobj.get_times()

    for sp in SPlist:
        for idx, time in enumerate(times):
            # print(idx, time)
            if idx == sp-1:
                fstr = f"conc_Cr(VI)_SP{sp}.shp"
                print(fstr, sp)
                ucnobj.to_shapefile(os.path.join(shpDir,fstr), totim=time)
    return None

def postprocess_shp(sce, transportRun):
    shpDir = os.path.join(cwd, 'output', 'ucn_shps', sce, transportRun)
    gridShp = gpd.read_file(os.path.join(os.path.dirname(cwd), 'gis', 'shp', 'grid_with_centroids', 'grid_with_centroids.shp')) # model grid shapefile
    my_crs = gridShp.crs
    for shp in glob.iglob(os.path.join(shpDir, '*.shp')):
        print(shp)
        gdf = gpd.read_file(shp) # convert to gdf
        cols = ['lf_data0', 'lf_data1', 'lf_data2', 'lf_data3', 'lf_data4', 'lf_data5', 'lf_data6', 'lf_data7', 'lf_data8']  # columns
        for c in cols:
            gdf[c] = gdf[c]/1000 #divide each column by 1000 to convert ug/m3 to ug/L
        gdf = gdf.set_crs(my_crs)  #set projection to be the same as from model grid shapefile
        gdf.geometry = gridShp.geometry #set geometry to be the same as from model grid shapefile
        print(gdf.crs)
        gdf.to_file(os.path.join(shpDir, shp))
        print(f"Projection file generated for {shp}")
    return None

if __name__ == "__main__":
    t0 = time.time()
    cwd=os.getcwd()

    #[Step 1]: Path to transport model UCN file:
    root = os.path.join(os.path.dirname(cwd))
    sce = 'sce6a_rr2_to2125' #'sce3a_to2125_rr5' #'sce6a_rr2_to2125' #'potentialWells' #'Manual' #'PEST' #'8_Model_RUM-GHB'
    transportRun = 'tran_2023to2125'#['transport_NFA_GHB'] #['transport_RPO_2125', 'transport_NFA_v2', 'transport_NFA_wGHB'] #'transport_NFA_v2'#transport_RPO_2032,transport_NFA_v1_wDSP'transport_RPO_2032'#['transport_short_DSP']#['transport_9L_2032'] #['ManCalib_v13'] #['ManCalib_v10'] #['Calibration_v3'] #['Transport_2014-2020P18_CP']
    delete_mode = False #deletes previous shapefiles in directory of interest.

    SPlist = [133]
    ucn2shp(sce, transportRun, SPlist)
    postprocess_shp(sce, transportRun)


    t1 = time.time()
    total = (t1-t0)/60
    print("Time elapsed : {} minutes".format(round(total, 2)))
