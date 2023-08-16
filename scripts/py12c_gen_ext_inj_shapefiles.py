import os
import pandas as pd
import geopandas as gpd 
import numpy as np 
from distutils.dir_util import copy_tree 
from shapely.geometry import Point
import fileinput

#from datetime import date

'''
hpham@intera.com
Prepare predictive scenarios and generate MNW2 package for the 2023-2125 flow model
- Read in shapefile of current and past pumping
- Assign inj/ext rates for a given scenario
- Duplicate the NFA MNW2 folder in (100HR3\model_packages\pred_2023_2125\mnw2)
- Create a new MNW2 foder for a new scenario (e.g. MNW2_sce1)
- Go to the new created folder
- Run 'allocateqwell.exe' to get a new mnw2 package
- 

'''
def create_new_dir(directory):
    # directory = os.path.dirname(file_path)
    try:
        os.stat(directory)
    except:
        os.mkdir(directory)
        print(f'Created a new directory {directory}\n')

def gen_inj_ext_shapefiles(dst, dst2):
    # ifile = pd.read_csv(os.path.join(dst2, f'wellratedxhx_cy2023_2125.csv'))

    # 06/06/2023 Generate new injection/extraction shapefile ===================
    # extraction well layer ----------------------------------------------------
    ifile_ext_wells = os.path.join(dst, 'extraction_wells.shp')
    df = gpd.read_file(ifile_ext_wells)
    flag = df[f'{sce}a']!=0
    df=df[flag]
    ofile_ext_wells = os.path.join(dst2, 'extraction_wells.shp')
    df.to_file(ofile_ext_wells)

    # injection well layer ---------------------------------------------------
    ifile_inj_wells = os.path.join(dst, 'injection_wells.shp')
    df = gpd.read_file(ifile_inj_wells)
    flag = df[f'{sce}a']!=0 ### You need to make sure that this column name represents the final {sce}a_rr{rr} version.
    df=df[flag]
    ofile_inj_wells = os.path.join(dst2, 'injection_wells.shp')
    df.to_file(ofile_inj_wells)
    return df

def gen_inj_ext_from_master(dst3):

    # ifile_all = os.path.join(os.path.dirname(os.getcwd()), 'gis', 'shp', 'wellrate_added_sce10_pp.shp')
    ifile_all = os.path.join(dst3, 'wellinfodxhx_cy2023_2125.csv')
    # gdf = gpd.read_file(ifile_all)
    df = pd.read_csv(ifile_all, skiprows = [0,2], usecols = [0,1,2])
    gdf = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df.XW, df.YW))

    ext = gdf[gdf['ID'].str.contains("_E_")]
    inj = gdf[gdf['ID'].str.contains("_I_")]

    flag = gdf[f'{sce2}'] != 0
    ext = ext[flag]
    inj = inj[flag]
    inj = inj[~inj.ID.str.contains('SF')]

    ofile_ext_wells = os.path.join(dst3, 'extraction_wells.shp')
    ext.to_file(ofile_ext_wells)

    ofile_inj_wells = os.path.join(dst3, 'injection_wells.shp')
    inj.to_file(ofile_inj_wells)


if __name__ == "__main__":
    wdir = os.path.dirname(os.getcwd())

    ######## Function in this script will update the extraction/injection shapefiles =====
    ######## for the {sce}a_rr{rr} version of the {sce}_rr{rr} you define below: =========
    sce, rr = 'sce4', 6

    sce2 = 'sce4'  ## scenario shapefiles needing updating not in the "a" series. Remember to update rr
    mnw2sce = f'mnw2_{sce2}_rr{rr}'

    #### ==================================================================================
    dst = os.path.join(wdir,'model_packages','pred_2023_2125',f'mnw2_{sce}_rr{rr}') #READ SHAPEFILES FROM HERE
    dst2 = os.path.join(wdir,'model_packages','pred_2023_2125',f'mnw2_{sce}a_rr{rr}') #SHAPEFILES WILL BE UPDATED HERE

    dst3 = os.path.join(wdir,'model_packages','pred_2023_2125',f'mnw2_{sce2}_rr{rr}')

    try:
        gen_inj_ext_shapefiles(dst, dst2)
    except:
        gen_inj_ext_from_master(dst3)

    print('Done :)')
