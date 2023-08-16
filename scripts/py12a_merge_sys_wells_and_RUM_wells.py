import os
import pandas as pd
import geopandas as gpd
import numpy as np 
from shapely.geometry import Point

'''
hpham@intera.com
To convert some RUM-2 monitoring wells to extraction wells, this script
merge current system well layer with the RUM-2 monitoring well layer.

'''



if __name__ == "__main__":
    #### [00] input files and parameters ======================================
    wdir = f'c:/Users/hpham/Documents/100HR3/'
    #wdir = os.path.dirname(os.getcwd())
    ifile_RUM2 = os.path.join(wdir, 'gis', 'shp', 'list_RUM2_Wells_vApril2023.shp')
    ifile = os.path.join(wdir,'gis','shp','processed_wellrate_DX_HX_2006_2023_coords_v032123.shp')
    
    # output files
    #ofile = os.path.join(wdir,'gis','shp','wellrate_sce_v040423.shp')
    ofile = os.path.join(wdir,'gis','shp','wellrate_sce_v040423_checking.shp')
    
    # read in files -----------------------------------------------------------
    rt = gpd.read_file(ifile)
    dfRUM2 = gpd.read_file(ifile_RUM2)
    dfRUM2 = dfRUM2.rename(columns = {'RUM-2 Well':'NAME'})
    # Keep only RUM2 wells that are not in rt
    dfRUM2 = dfRUM2[~dfRUM2['NAME'].isin(rt['NAME'])]
    dfRUM2 = dfRUM2[~dfRUM2['geometry'].isnull()]
    
    dfRUM2['ID'] = dfRUM2['NAME'] + "_" + dfRUM2['Type'] + "_" + dfRUM2['System']
    dfRUM2['Active'] = 1
    dfRUM2.plot()


    
    # processing
    rt.plot()
    rt.columns
    rt.head(3)
    type(rt)
    rt=rt[rt['Active']==1]
    rt=rt.drop(columns=['avg'])

    # merging
    #rt2=rt.sjoin(dfRUM2, how='outer', on=['ID','NAME', 'Type', 'System','XCOORDS','YCOORDS','Active'])
    
    rt=rt.drop(columns=['geometry'])
    dfRUM2=dfRUM2.drop(columns=['geometry'])

    rt2 = pd.merge(rt, dfRUM2,how='outer', on=['ID','NAME', 'Type', 'System','XCOORDS','YCOORDS','Active'] )
    rt2.columns

    col = [f'{i}' for i in range(1,108+1,1)] # avg 2014-2022
    rt2['avg1422'] = rt2[col].mean(axis=1,skipna=True)
    
    col = [f'{i}' for i in range(85,108+1,1)] # avg 2021-2022
    rt2['avg2122'] = rt2[col].mean(axis=1,skipna=True)
    
    col = [f'{i}' for i in range(97,108+1,1)] # avg_cy2022
    rt2['avg_cy2022'] = rt2[col].mean(axis=1,skipna=True)
    
    # pandas to geopandas
    point_xy = [Point(x, y) for x, y in zip(rt2['XCOORDS'].astype('float32'), rt2['YCOORDS'].astype('float32'))]
    rt3 = gpd.GeoDataFrame(rt2, geometry=point_xy)
       
    
    rt3.to_file(ofile)
    type(rt3)
    rt3.columns
    rt3.plot()
    print(f'saved {ofile}\n')


    
