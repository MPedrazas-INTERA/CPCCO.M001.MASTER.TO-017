

import os
import pandas as pd
import geopandas as gpd
import numpy as np
import flopy
import flopy.utils.binaryfile as bf

def read_model_grid(root):
    """
    input : grid_with_centroids.shp <-- shapefile of model grid
    :return: grid <-- geopandas dataframe for model grid
    """
    print('reading grid file')
    grid = gpd.read_file(os.path.join(root, 'gis', 'shp', 'grid_with_centroids', 'grid_with_centroids.shp'))
    print('finished reading grid file')
    return grid

def source_cells_coordinates(grid):

    zones = gpd.read_file(os.path.join(root, 'gis', 'shp', 'cr6_cs_zonation2_filtered.shp'))
    zones.rename(columns={'row':'I', 'column':'J'}, inplace=True)

    zones_xy = gpd.GeoDataFrame(zones.merge(grid, on=['I','J'])[['I','J','zone', 'centroid_x','centroid_y', 'geometry_x']],
                                geometry = 'geometry_x')

    return zones_xy

if __name__ == "__main__":

    cwd = os.getcwd()
    root = os.path.join(os.path.dirname(cwd))

    ## load in gw interest areas for clipping to 100D
    gwia = gpd.read_file(os.path.join(root, 'gis', 'shp', 'GWIA_2017.shp'))
    gwia_d = gwia.loc[gwia['GWIA_NAME'] == '100-HR-D']

    ### generate source cell file with i, j, x, and y info ###
    grid = read_model_grid(root)
    zones_xy = source_cells_coordinates(grid)
    zones_xy_100d = gpd.clip(zones_xy, gwia_d)
    # zones_xy_100d.to_csv(os.path.join(cwd, 'output', 'soil_flushing', 'source_cells_100D_ij_rowcol.csv'))



