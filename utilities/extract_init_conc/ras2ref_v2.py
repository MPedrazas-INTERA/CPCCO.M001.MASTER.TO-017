import geopandas as gpd
import numpy as np
#import matplotlib.pyplot as plt
#import re
import os
import sys
import pandas as pd
import rasterio
from shapely.geometry import Point
import georaster as gr  # 1.26.1

'''
- xxx


'''


def create_new_dir(directory):
    # directory = os.path.dirname(file_path)
    try:
        os.stat(directory)
    except:
        os.mkdir(directory)
        print(f'Created a new directory {directory}\n')


def create_output_folders():
    create_new_dir('output')
    # create_new_dir('output/png')
    # create_new_dir('output/shp')
    # create_new_dir(f'output/png/conc_{var}')
    # create_new_dir(f'output/shp/conc_{var}')


def extract_raster(raster_path, xy):
    # raster_path : path to raster
    # xy: list or array of tuples of x,y i.e [(x1,y1),(x2,y2)...(xn,yn)]
    # returns list of length xy or sampled values
    raster = rasterio.open(raster_path)
    nodata = raster.nodata

    values = []
    for i, xyi in enumerate(xy):
        try:
            value = list(raster.sample([xyi]))[0][0]
        except:
            value = np.nan

        if value == nodata:  # if value is nodata from rasdter, set to nan
            value = np.nan

        values.append(value)

    # values = [item[0] for item in values] # list comprehension to get the value
    return values

def writearray(array, ncols, fname, dtype):
    """
    Write a 2D array to an output file in 10E12.4 format or 10I10 format
    Input parameters
    ----------------
    array is a 2d array with shape(nrow,ncol)
    Integer or double
    fname is the name of the output file
    dtype is a string
    Can be 'int' or 'double'
    """
    assert(len(array.shape) == 2)
    assert(dtype == 'int' or dtype == 'double')
    nrow, ncol = array.shape

    # print 'writing array to ' + fname

    """
	lookupdict={}
	with open('C:/Projects/Google Drive/PhD/Inversion_of_CategoricalFields/Task1/hylookuptable.dat','r') as fin:
		for line in fin.readlines():
			key,val = line.split()
			# print key,val
			lookupdict.update({int(key):np.double(val)})
	fin.close()
	# print lookupdict
	newarray = np.zeros((ny,nx),dtype='double')
	for key, val in lookupdict.iteritems(): newarray[array==key] = np.double(val)
	"""
    with open(fname, 'w') as fout:
        for i in range(0, nrow):
            jprev = 0
            jnew = 0
            while(jnew < ncol):
                if(jprev+ncols) > ncol:
                    jnew = ncol
                else:
                    jnew = jprev+ncols
                line = ''
                # print jnew,jprev
                for k in range(jprev, jnew):
                    if(dtype == 'int'):
                        line = line+'{:3d}'.format(array[i][k])
                    elif(dtype == 'double'):
                        # line = line + '{:ncols.4e}'.format(array[i][k])
                        # line = line + f'{array[i][k]:12.4e}'
                        # line = line + f'{array[i][k]:15.7e}'  # bot*.ref
                        line = line + f'{array[i][k]:14.6e}'  # thk*.ref
                        # f'{number:9.4f}'

                jprev = jnew
                fout.write(f'{line}\n')

    fout.close()
    print(f'Saved {fname}\n')

if __name__ == "__main__":
    wdir = f'c:/Users/hpham/Documents/100HR3/'
    #wdir = f'c:/Users/hpham/Documents/100HR3/scripts/extract_init_conc/'
    run = 'cy2022_rum2' # cy2022_rum2 or 'cy2022_unconfined_aq'
    
    # [1] Load input files ----------------------------------------------------
    #raster_file = sys.argv[1]
    #raster_file = "input/plume_cy2020/HexCr_20201.tif" # mapped plumes for cy2020
    
    # CY2021

    #raster_file = "input/plume_cy2021/Hexavalent Chromium_LO.tif" # mapped plumes unconfined aq for cy2021
    #raster_file = f'{wdir}/GIS/raster/CrVI_CY2021_RUM/Hexavalent Chromium.tif" # mapped plumes RUM aq cy2021'
    
    # CY2022
    #raster_file = f'{wdir}/GIS/raster/CrVI_CY2021_RUM/Hexavalent Chromium.tif" # mapped plumes RUM aq cy2021'
    
    # MODFLOW grid file
    
    shp_file_poly = f'{wdir}/scripts/extract_init_conc/input/grid_with_centroids.shp'
    xy_file = f'{wdir}/scripts/extract_init_conc/input/grid_xy.csv'

    # Specify an output file --------------------------------------------------
    #ofile = sys.argv[2]
    #ofile = "output/HexCr_2020.dat" # mapped plumes for cy2020
    #ofile = "output/HexCr_2021_unconfined.dat" # mapped plumes unconfined for cy2021
    #ofile = f'{wdir}/output/HexCr_2021_RUM.dat' # mapped plumes RUM for cy2021

    if run == 'cy2022_unconfined_aq':
        raster_file = f'{wdir}/gis/raster/mapped_CrVI_CY2022/unconfined_aq/Hexavalent Chromium_LO.tif' # mapped plumes unconfined aq 2022
        ofile = f'{wdir}/scripts/extract_init_conc/output/HexCr_2022_unconfined.dat' # mapped plumes RUM for cy2022
    elif run == 'cy2022_rum2':
        raster_file = f'{wdir}/gis/raster/mapped_CrVI_CY2022/rum2/Hexavalent Chromium.tif' # mapped plumes RUM2 cy2022'
        ofile = f'{wdir}/scripts/extract_init_conc/output/HexCr_2022_RUM.dat' # mapped plumes RUM for cy2022



    # =========================================================================
    # No changes are needed after this line ===================================
    # =========================================================================

    # reading input point csv file --------------------------------------------
    
    print(f'\nReading input cell coordinate csv file: {xy_file}\n')
    df_coor = pd.read_csv(xy_file)
    nrows, ncols = df_coor['I'].max(), df_coor['J'].max()
    print(f'nrow = {nrows}, ncols={ncols}\n')
    xy = [(df_coor.X, df_coor.Y)
          for i, df_coor in df_coor.iterrows()]

    # Extract concentration values from a raster file
    print(
        f'Reading input raster file: {raster_file} and extracting concentrations at grid cells\n')
    res = extract_raster(raster_file, xy)

    # Export to shapefile for checking ----------------------------------------
    # # polygon: Cols = ['I', 'J', 'CELLACTIVE', 'geometry']
    
    print(f'Reading input polygon grid file: {shp_file_poly}\n')
    gdf_poly = gpd.read_file(shp_file_poly)
    #gdf_poly = gdf_poly[['I', 'J', 'CELLACTIVE', 'geometry']]
    # gdf_poly.to_file('input/grid.shp')

    gdf_poly['Conc'] = res
    gdf_poly['Conc'].loc[gdf_poly['Conc'] < 0] = 0
    gdf_poly['Conc'].loc[gdf_poly['Conc'] > 1e12] = 0

    # Saving cocentration to polygon grid file for checking -------------------
    ofile1 = ofile.split('.')[0] + '.shp'
    print(
        f'Saving cocentration to polygon grid file for checking: {ofile1}\n')
    gdf_poly.to_file(ofile1) # save shp file

    # save to csv file for checking -------------------------------------------
    ofile2 = ofile.split('.')[0] + '.csv'
    gdf_poly['X'] = df_coor['X']
    gdf_poly['Y'] = df_coor['Y']
    #dfout2 = gdf_poly[['I', 'J', 'CELLACTIVE', 'X', 'Y', 'Conc']]
    dfout2 = gdf_poly[['I', 'J', 'X', 'Y', 'Conc']]
    print(f'Saving to output .csv file: {ofile2}\n')
    dfout2.to_csv(ofile2)

    # Reshape
    #arr = np.reshape(res, (663, 1164))
    arr = np.reshape(gdf_poly['Conc'].to_numpy(), (nrows, ncols))
    #arr[arr > 1e12] = 0
    #arr[arr < -1e12] = 0
    arr[np.isnan(arr)] = 0
    # A[np.isnan(A)] = 0

    # arr[270:663, 640:1164] = 0  # remove plumes from other areas (for NO3 only? )
    # arr to ref file
    print(f'Saving to output .dat file: {ofile}\n')
    #np.savetxt(ofile, arr, delimiter=" ", fmt='%.6f')

    # save to ref file
    dtype='double'
    ncols=10
    writearray(arr, ncols, ofile, dtype)

# Reference/Source
# https://github.com/rosskush/spatialpy/blob/main/spatialpy/utils/extraction.py
