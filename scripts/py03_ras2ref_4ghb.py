import geopandas as gpd
import numpy as np
#import matplotlib.pyplot as plt
#import re
import os
import sys
import pandas as pd
import rasterio
#from shapely.geometry import Point
#import georaster as gr  # 1.26.1
import flopy

'''
- hpham@intera.com, ver: 02/15/2023
- Extract values from a raster file, export to csv files, and
- compare with the GHB stages from SSPA
- update optimized conductance values

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


if __name__ == "__main__":

    # [1] Load input files ----------------------------------------------------
    wdir = f'../model_packages/hist_2014_2021/ghb//'  
    #ifile_ghb_shp = f'{wdir}/Shapefile/GHB_Lay6.shp' # GHB cell locations  
    ifile_ghb_shp = f'{wdir}/Shapefile/GHB_with_offset_Heads.shp' # offset of GHB cell locations      
    ifile_conductance = f'../scripts/input/ghb_cell_locations_exported_from_GMS.csv' # sp=1
    ifile_grid_centroid = f'input/grid_with_centroids.csv'
            
    flow_model_ws = f'c:/Users/hpham/OneDrive - INTERA Inc/projects/50_100HR3/10_NFA_ECF_Check/model_files/flow/flow_calib/'
    ml = flopy.modflow.Modflow.load(
        "DHmodel_2014to2020.nam",
        model_ws=flow_model_ws,
        #load_only=["dis", "bas6", "ghb"],
        verbose=True,
        check=False,
        #forgive=False,
        exe_name="mf2k-mst-chprc08dpl",
        )
    top = ml.dis.gettop()
    bot = ml.dis.getbotm() # Rounded up, can't use
    nlay, nr, nc, nper = ml.dis.nlay, ml.dis.nrow, ml.dis.ncol, ml.dis.nper

    print(bot[1-1,433-1, 741-1])

    # Read bot elev from sspa
    dfbot14 = pd.read_csv(f'../model_packages/hist_2014_2021/ghb/BottomCSV/Layers1to4.csv')
    dfbot58 = pd.read_csv(f'../model_packages/hist_2014_2021/ghb/BottomCSV/Layers5to8.csv')
    dfbot9 = pd.read_csv(f'../model_packages/hist_2014_2021/ghb/BottomCSV/Layers9.csv')
    dfbot_sspa = pd.concat([dfbot14, dfbot58, dfbot9], axis=0)
    dfbot_sspa=dfbot_sspa.rename(columns={'col':'column', 'Layer':'layer', 'Bottom':'bot'})

    # readind the shapefile of GHB cell locations (southern BC only), head (before 2020), and K
    # Do not use the value from SSPA for 2020. It was incorrect. 
    # Need to update GHB conductance. The values in the shapefile were not optimized parameters
    gdf = gpd.read_file(ifile_ghb_shp)
    df_tmp=gdf[['ET_ID','row','column']]
    df_tmp["centroid_x"] = gdf.centroid.x
    df_tmp["centroid_y"] = gdf.centroid.y
    gdf['row'][gdf['row']==500] = 433
    #df_tmp = gdf[['centroid_x','centroid_y']]
    xy = [(df_tmp["centroid_x"], df_tmp["centroid_y"]) for i, df_tmp in df_tmp.iterrows()]
    
    # get coordinate of grid centroid
    dfgrd = pd.read_csv(ifile_grid_centroid)
    dfgrd=dfgrd[['I','J']]
    dfgrd=dfgrd.rename(columns={'I':'row', 'J':'column'})
    #dfbot = pd.DataFrame()
    #for lay in range(1,nlay+1, 1):
    #    dfgrd['layer'] = lay
    #    dfgrd['bot'] = np.reshape(bot[lay-1,:,:], [nr*nc,1])
    #    dfbot=pd.concat([dfbot, dfgrd], axis=0)


    # read in optimized conductance values
    dfghb=pd.read_csv(ifile_conductance)

    # Merge df to get cell bottom elevation
    dfghb = pd.merge(dfghb, dfbot_sspa, how='left', on=['row', 'column','layer'])
    
    #raster_file = sys.argv[1]
    #yr=2020
    list_yr = range(2014, 2022+1, 1)
    sp_of_start_yr = 97 # sp97: start year 2014
    ofile = f'{wdir}/raster_files/interpolated_wl_2014_2020_at_GHB_offset.csv'
    ofile_shp = f'{wdir}/Shapefile/GHB_CY2022_v022823.shp'
    list_months = range(1,12+1,1)
    #list_months = [6,10]
    #for i in range(1,12+1,1):
    count = 97
    for yr in list_yr:
        #for i in range(1,12+1,1): # for cy 2015
        for i in list_months: # for cy 2015
            if yr>=2021:
                raster_file = f'{wdir}/raster_files/PROD_Termby_043022_WL_{i}.asc'
            elif yr==2020:
                raster_file = f'{wdir}/raster_files/PROD_Termby_02102020_WL_{i}.asc'
            #elif yr==2015:
            #    raster_file = f'{wdir}/raster_files/PROD_Termby_AS_03042016_WL_{i}.asc'
            elif yr<=2019:
                wdir2 = f'../data/interpolated_WLs/WL_Gauge/WL_ASC/{yr}/'
                raster_file = f'{wdir2}/WL_{i}.asc'
                    

            #
            print(f'Reading {raster_file}\n')
            # Specify an output file --------------------------------------------------
            #ofile = sys.argv[2]
            

            # reading input point csv file --------------------------------------------
            '''
            xy_file = f'input/grid_with_centroids.csv'
            print(f'\nReading input cell coordinate csv file: {xy_file}\n')
            df_coor = pd.read_csv(xy_file)
            nrows, ncols = df_coor['I'].max(), df_coor['J'].max()
            print(f'nrow = {nrows}, ncols={ncols}\n')
            xy = [(df_coor['centroid_x'], df_coor['centroid_y'])
                for i, df_coor in df_coor.iterrows()]
            '''
            # Extract concentration values from a raster file
            print(
                f'Reading input raster file: {raster_file} and extracting data at grid cells\n')
            res = extract_raster(raster_file, xy)


            
            #shp_file_poly = f'../gis/shp/grid_with_centroids.shp'
            #print(f'Reading input polygon grid file: {shp_file_poly}\n')
            #gdf_poly = gpd.read_file(shp_file_poly)
            #gdf_poly = gdf_poly[['I', 'J', 'CELLACTIVE', 'geometry']]
            # gdf_poly.to_file('input/grid.shp')

            gdf[f'head{count}'] = res
            #gdf_poly['val'].loc[gdf_poly['val'] < 0] = 0
            #gdf_poly['val'].loc[gdf_poly['val'] > 1e12] = 0



            # save to csv file for checking -------------------------------------------
            #ofile2 = ofile.split('.')[0] + f'yr{yr}mo{i}.csv'
            #gdf['X'] = df_coor['centroid_x']
            #gdf['Y'] = df_coor['centroid_y']
            #if count==0:
            #    dfout2 = gdf[['I', 'J',  'X', 'Y']] # select important cols
            #    #dfout2[f'WL_{i}_{yr}'] = gdf['val'].copy()
            #    dfout2[f'head{count}'] = gdf['val'].copy()
            #else:
            #    dfout2[f'head{count}'] = gdf['val'].copy()

            # Reshape
            #arr = np.reshape(res, (663, 1164))
            #arr = np.reshape(gdf['val'].to_numpy(), (nrows, ncols))
            #arr[arr > 1e12] = 0
            #arr[arr < -1e12] = 0

            # arr[270:663, 640:1164] = 0  # remove plumes from other areas (for NO3 only? )
            
            # arr to ref file ---------------------------------------------------------
            #print(f'Saved {ofile}\n')
            #np.savetxt(ofile, arr, delimiter=" ", fmt='%.6f')
            count+=1
        # Get only ghb cells --------------------------------------------------
        #if yr==2015:
        #    # 114	6/1/2015	6/30/2015	30
        #    # 118	10/1/2015	10/31/2015	31
        #    cols = ['row', 'column'] + [f'head{i}' for i in [114,118]] + ['geometry']
        #else:
        #cols = ['row', 'column'] + [f'head{i}' for i in range(sp_of_start_yr, 180+1,1)] + ['geometry']
        #dfout2.rename(columns={'I':'row', 'J':'column'}, inplace=True)
        #ghb_hed = pd.merge(gdf[cols], dfout2, how='left', on=['row', 'column'])
        #ghb_hed=ghb_hed[ghb_hed['row']==433]

        # Check 
        #for i in list_months:
        #    ghb_hed[f'diff{i+1}'] = ghb_hed[f'WL_{i}_{yr}'] -  ghb_hed[f'head{sp_of_start_yr+i-1}'] # 
            #ghb_hed[f'diff{i+1}'] = ghb_hed[f'WL_{i}_{yr}'] -  ghb_hed[f'head{108+i}']

    #
    #gdf['row'] = 433

    # Saving to polygon grid file for checking -------------------      
    opt_exp_shp_file = False   
    if opt_exp_shp_file:
        gdf.to_file(ofile_shp)
        print(f'Saved {ofile_shp} \n')    
    #
    print(f'Saved {ofile} \n')
    gdf.to_csv(ofile, index=False)

    # 
    #chk = ghb_hed.describe()

    # Prepare data for GW Vistas after 2019 only. Kkeep SSPA values before 2020, 
    # those values are in the GW Vistas files. 
    dfghb_final = pd.DataFrame()
    for sp in range(97, 204+1, 1):
        dfWL = gdf[['row','column',f'head{sp}']]
        
        # Merge to get GHB stage values
        dftmp = dfghb[['row', 'column', 'layer', 'cond', 'bot']].copy()

        df_merged = pd.merge(dftmp, dfWL, how='left', on=['row', 'column'])
        df_merged['SP'] = sp
        df_merged.rename(columns={f'head{sp}':'head'}, inplace=True)

        dfghb_final = pd.concat([dfghb_final, df_merged], axis=0)
    
        # later: Add GHB for below the river

    # Delete cells that have GHB stages < bottom ele + 0.001
    dfghb_final['check'] = 'good'
    dfghb_final['bot']=dfghb_final['bot'].astype(float)
    flag = dfghb_final['head'] < dfghb_final['bot']+0.001
    dfghb_final['check'][flag] = 'delete'
        
    dfghb_final=dfghb_final[['layer','row', 'column', 'head', 'cond', 'SP','bot','check']]
    flag = dfghb_final['row'] != 433
    dfghb_final['head'].loc[flag] = 120 # assign 120 for the GHB heads below the river

    dfghb_final.to_csv(f'../model_packages/hist_2014_2021/ghb/GHBdata2GWV_v022823_all.csv', index=False)
    dfghb_final2 = dfghb_final[dfghb_final['check']=='good']
    dfghb_final2.to_csv(f'../model_packages/hist_2014_2021/ghb/GHBdata2GWV_v022823_good.csv', index=False)

    # flopy to update GHB =====================================================
    # load an MODLOW flow model -------------------------------------------
    opt_update_ghb = False
    if opt_update_ghb: 

    
        #
        stress_period_data = ml.ghb.stress_period_data.data
        ghb = ml.ghb.stress_period_data.get_dataframe()
        ghb_period = {}
        # Need to re-do 2020 later. 
        for per in [1]: # number of stress periods
            ghb_period_array = []
            for k,i,j,stage,cond in zip(ghb.k,ghb.i,ghb.j,ghb[f'bhead{per-1}'],ghb[f'cond{per-1}']):
                ghb_period_array.append([k, i, j, stage, cond])
            ghb_period[per] = ghb_period_array 
        
        x = np.array(ghb_period_array, dtype=[('k', '<i4'), ('i', '<i4'), ('j', '<i4'), ('bhead', '<f4'), ('cond', '<f4')])    
        
        stress_period_data[83]
        stress_period_data = {85-1: ghb_period_array}                     
        ghb = flopy.modflow.ModflowGhb(mf, stress_period_data=stress_period_data)

    #gdf.columns
    #ghb_hed.plot()
    # Reference/Source
    # https://github.com/rosskush/spatialpy/blob/main/spatialpy/utils/extraction.py

