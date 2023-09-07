"""
This script creates a DB of well info including geographic coordinates AND model coordinates

"""

import os
import pandas as pd
import geopandas as gpd
import numpy as np
import sys

def read_model_grid():
    """
    input : grid_with_centroids.shp <-- shapefile of model grid
    :return: grid <-- geopandas dataframe for model grid
    """
    print('reading grid file')
    grid = gpd.read_file(os.path.join(root, 'gis', 'shp', 'grid_with_centroids.shp'))
    print('finished reading grid file')

    return grid

def get_wells_ijk(well_list, screens):

    print("Getting row and column info for each well")

    coordscsv = os.path.join(root, 'data', 'water_levels',
                             "qryWellHWIS.txt")  # dataframe with coords for monitoring wells

    coords = pd.read_csv(coordscsv, delimiter="|")
    wells = coords.loc[coords.NAME.isin(well_list.NAME)]

    ## create GDF from wells dataframe and merge with grid

    mycrs = grid.crs
    wells_gdf = gpd.GeoDataFrame(wells,
                                 geometry=gpd.points_from_xy(wells['XCOORDS'], wells['YCOORDS']),
                                 crs = mycrs)

    gridwells = gpd.sjoin(grid, wells_gdf, how='right')

    df = pd.merge(gridwells, screens, left_on = 'NAME', right_on = 'WELL_NAME')
    df['Ztop'] = df['ZCOORDS'] - df['STD_SCREEN_DEPTH_TOP_M']
    df['Zbot'] = df['ZCOORDS'] - df['STD_SCREEN_DEPTH_BOTTOM_M']

    ## read in shapefile with model layer zbot info
    print('reading botm_elev shapefile') ##
    dfz = gpd.read_file(os.path.join(root,"gis", "shp", "botm_elev", "botm_elev.shp"))
    dfz.drop('node', axis=1, inplace=True)
    # filter out zbot values to only well locations
    dfmerge = pd.merge(df, dfz, how='left', left_on=['I', 'J'], right_on=['row', 'column'])

    ## columns of interest
    df2 = dfmerge.loc[:,['NAME', 'I', 'J', 'XCOORDS', 'YCOORDS', 'ZCOORDS', 'Ztop', 'Zbot', 'geometry_x',
                         'botm_1', 'botm_2', 'botm_3', 'botm_4', 'botm_5', 'botm_6', 'botm_7', 'botm_8', 'botm_9']]

    ## determine which model layers each well is screened in. Qualitative only for now, no screen fracs per layer (yet)
    df2['ScreenLayers'] = ''
    for index, row in df2.loc[:,['Ztop', 'Zbot', 'botm_1', 'botm_2', 'botm_3', 'botm_4', 'botm_5', 'botm_6', 'botm_7', 'botm_8', 'botm_9']].iterrows():
        print(row)
        ztop = row['Ztop']  ## all ztop values within layer 1
        zbot = row['Zbot']

        # Iterate through model layer depths and find where screen intersects
        lays= ['Layer1']        ## all well screens begin in layer 1
        for layer_number in range(1, len(row) - 2):
            print(layer_number)
            layer_depth = row[f'botm_{layer_number}']
            if zbot < layer_depth:
                lays.append(f'Layer{layer_number+1}')
        df2.at[index, 'ScreenLayers'] = ', '.join(lays)

    return df2

if __name__ == "__main__":

    cwd = os.getcwd()
    root = os.path.dirname(cwd)

    output_dir = os.path.join(root, "scripts", "output", "well_info")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    grid = read_model_grid()

    well_list = pd.read_csv(os.path.join(cwd, 'output', 'well_info', 'monitoring_well_list.csv'))
    screens = pd.read_excel(os.path.join(root, 'data', 'well_info', 'Well Screen8-29-2023version-3.3.xlsx'),
                            usecols = ['WELL_NAME', 'STD_SCREEN_DEPTH_TOP_M', 'STD_SCREEN_DEPTH_BOTTOM_M'])
    screens.drop_duplicates('WELL_NAME', keep = 'first', inplace=True)

    df2 = get_wells_ijk(well_list, screens)

    # df2.to_csv(os.path.join(output_dir, 'monitoringwells_xyz_ijk.csv'), index=False)
