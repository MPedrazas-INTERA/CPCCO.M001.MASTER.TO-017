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

###########TASK 1
df = pumping_rates.transpose()  ## clip to timeseries data and transpose
df.columns = df.iloc[0]
df.drop('ID', inplace=True)
df.reset_index(inplace=True)
df.rename(columns={"index": "SP"}, inplace=True)
df.SP = df.SP.astype(int)
df = df.loc[df.SP >= 109]
myLst = []
for well in df.columns[1:]:
    oneWellataTime = df[well]
    for n in range(10):
        oneRateataTime = oneWellataTime.iloc[n]
        myLst.append([well, n+1, oneRateataTime])

dfwellinfo = pd.DataFrame(myLst, columns = ['ID','EVENT', 'VAL m3/d'])

dfwellinfo['NAME'] = dfwellinfo['ID'].str.split('_', 2, expand=True)[0]
dfwellinfo['TYPE'] = dfwellinfo['ID'].str.split('_', 2, expand=True)[1]
dfwellinfo['OU'] = dfwellinfo['ID'].str.split('_', 2, expand=True)[2]
dfwellinfo['TYPE'] = dfwellinfo['TYPE'].replace({'I': 'Injection', 'E': 'Extraction'})

gpm2m3d = (24 * 60) / 1 * 231 * (25.4 / 1000 / 1) ** 3  ## m3d2gpm=0.183453
dfwellinfo["VAL"] = dfwellinfo["VAL m3/d"]/gpm2m3d    #OR *m3d2gpm
dfwellinfo["UNITS"] = 'gpm'

dfwellinfo2 = dfwellinfo[["NAME", "OU", "VAL", "UNITS", "EVENT", "TYPE"]]
dfwellinfo2.to_csv(os.path.join("output", "well_info", "calib_2014_Oct2023", "pumpingrates_2023_from_mnw2_v2.csv"), index=False)

###########TASK 2
pumping_merged = pd.merge(pumping_rates, pumping_coords[["NAME", "XW", "YW", "Ztop", "Zbot"]], left_on="ID", right_on="NAME")

# Create a GeoDataFrame from the merged DataFrame
geometry = [Point(xy) for xy in zip(pumping_merged['XW'], pumping_merged['YW'])]

dummy = gpd.read_file(os.path.join(wdir, "gis", "shp", "River.shp")) #get correct projection
gdf = gpd.GeoDataFrame(pumping_merged, geometry=geometry, crs = dummy.crs)

# Export as a shapefile
output_shapefile = os.path.join(wdir,  "gis", "shp", 'wellinfo_cy2014_Oct2023_from_mnw2.shp')
# gdf.to_file(output_shapefile, driver='ESRI Shapefile')

