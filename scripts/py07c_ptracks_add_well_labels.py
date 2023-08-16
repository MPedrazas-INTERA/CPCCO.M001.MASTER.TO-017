import os
import geopandas as gpd
import pandas as pd
import fiona
import json
from shapely.geometry import shape


def addWellstoPT(startlocs, ptracks, wellinfo, modeldir, modelsce):

    ## 1. merge startlocs to ptrack shapefile
    gdf_0 = startlocs.merge(ptracks, on = 'PID')

    ## 2. merge result to wellinfo, convert to geodataframe
    df = wellinfo.merge(gdf_0, on = 'ID')
   # t = wellinfo[wellinfo['ID'].apply(lambda well: startlocs['ID'].str.contains(well)).any()]
    df = df.rename(columns={'ID':'Well ID'})
    gdf = gpd.GeoDataFrame(df, geometry = 'geometry')

    gdf.to_file(os.path.join(modeldir, f"100hr3_ptracks_wLabels_{modelsce}.shp"))

    return gdf


if __name__ == "__main__":

    mnw2name = 'mnw2_sce10a_rr1'
    modelsce = 'sce10a_rr1_to2125'
    ptradir = 'ptra_2023_2060'

    cwd = os.getcwd()
    welldir = os.path.join(cwd, 'output', 'well_info', mnw2name)
    modeldir = os.path.join(os.path.dirname(cwd), 'mruns', modelsce, ptradir)

    wellinfo = pd.read_csv(os.path.join(welldir, 'extractionwells_master.csv'), usecols = ['ID', 'System', 'Aquifer'])
    wellinfo['ID'] = wellinfo['ID'].str.upper()
    startlocs = pd.read_csv(os.path.join(modeldir, '100hr3_start_locs.dat'),
                            skiprows = [0,1,2,3,4], delim_whitespace=True, header = None, usecols = [0,10],
                            names = ('PID', 'ID'))
    startlocs['ID'] = startlocs['ID'].str.rsplit('_', 1, expand = True)[0]  ## rsplit splits a given number of times starting at the end


    collection = list(fiona.open(os.path.join(modeldir, '100hr3_ptracks.shp'), 'r'))
    df1 = pd.DataFrame(collection)
    # Check Geometry. Attempt to fix issue with sce10a (source: https://gis.stackexchange.com/questions/277231/geopandas-valueerror-a-linearring-must-have-at-least-3-coordinate-tuples)
    def isvalid(geom):
        try:
            shape(geom)
            return 1
        except:
            return 0
    df1['isvalid'] = df1['geometry'].apply(lambda x: isvalid(x))
    df1 = df1[df1['isvalid'] == 1]
    ## If shapefile does not have inherent geometry, try this...
    try:
        ptracks = gpd.read_file(os.path.join(modeldir, '100hr3_ptracks.shp'))
    except:
        collection = list(fiona.open(os.path.join(modeldir, '100hr3_ptracks.shp'), 'r'))
        df1 = pd.DataFrame(collection)
        # Check Geometry
        def isvalid(geom):
            try:
                shape(geom)
                return 1
            except:
                return 0
        df1['isvalid'] = df1['geometry'].apply(lambda x: isvalid(x))
        df1 = df1[df1['isvalid'] == 1]
        collection = json.loads(df1.to_json(orient='records'))
        geometry = gpd.GeoDataFrame.from_features(collection)

        # ptracks_csv = pd.read_csv(os.path.join(modeldir, '100hr3_ptracks_reprojected.csv'))
        # ptracks_csv['geometry'] = geometry



    # gdf = addWellstoPT(startlocs, ptracks, wellinfo, modeldir, modelsce)
