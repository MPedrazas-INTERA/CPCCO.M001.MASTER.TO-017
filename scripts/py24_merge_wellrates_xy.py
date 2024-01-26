import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


cwd = os.getcwd()
wdir = os.path.dirname(cwd)



pumping_rates = pd.read_csv(os.path.join(wdir, 'model_packages', 'hist_2014_Oct2023', 'mnw2',
                                        'wellratesdxhx_cy2014_oct2023.csv'))
pumping_coords = pd.read_csv(os.path.join(wdir, 'model_packages', 'hist_2014_Oct2023', 'mnw2',
                                        'wellinfodxhx_cy2014_oct2023.csv'), skiprows=[0,2])

pumping_merged = pd.merge(pumping_rates, pumping_coords[["NAME", "XW", "YW", "Ztop", "Zbot"]], left_on="ID", right_on="NAME")

# Create a GeoDataFrame from the merged DataFrame
geometry = [Point(xy) for xy in zip(pumping_merged['XW'], pumping_merged['YW'])]

dummy = gpd.read_file(os.path.join(wdir, "gis", "shp", "River.shp")) #get correct projection
gdf = gpd.GeoDataFrame(pumping_merged, geometry=geometry, crs = dummy.crs)

# Export as a shapefile
output_shapefile = os.path.join(wdir,  "gis", "shp", 'wellinfo_cy2014_Oct2023_from_mnw2.shp')
gdf.to_file(output_shapefile, driver='ESRI Shapefile')