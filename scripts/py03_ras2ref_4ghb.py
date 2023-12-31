import geopandas as gpd
import numpy as np
import os
import pandas as pd
import rasterio
import flopy

'''
- hpham@intera.com, ver: 02/15/2023
- Extract values from a raster file, export to csv files, and
- compare with the GHB stages from SSPA
- update optimized conductance values

'''


def create_new_dir(directory):
    try:
        os.stat(directory)
    except:
        os.mkdir(directory)
        print(f'Created a new directory {directory}\n')


def create_output_folders():
    create_new_dir('output')

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
        if value == nodata:  # if value is nodata from raster, set to nan
            value = np.nan
        values.append(value)
    return values

if __name__ == "__main__":

    # [1] Load input files ----------------------------------------------------
    cwd = os.getcwd()
    wdir = os.path.join(os.path.dirname(cwd),'model_packages','hist_2014_Oct2023','ghb')
    ifile_ghb_shp = f'{wdir}/Shapefile/GHB_with_offset_Heads.shp' # offset of GHB cell locations
    ifile_conductance = f'{cwd}/input/ghb_cell_locations_exported_from_GMS.csv' # sp=1
    ifile_grid_centroid = f'input/grid_with_centroids.csv'
            
    flow_model_ws = os.path.join(os.path.dirname(cwd),'model_files','flow_2014_2023')
    exe_dir = os.path.join(os.path.dirname(cwd), "executables","windows")
    ml = flopy.modflow.Modflow.load(
        "100hr3.nam",
        model_ws=flow_model_ws,
        load_only=["dis", "bas6"], #, "ghb"],
        verbose=True,
        check=False,
        exe_name=os.path.join(exe_dir,"mf2k-mst-chprc08dpl")
        )
    top = ml.dis.gettop()
    bot = ml.dis.getbotm() # Rounded up, can't use
    nlay, nr, nc, nper = ml.dis.nlay, ml.dis.nrow, ml.dis.ncol, ml.dis.nper

    print(bot[1-1,433-1, 741-1])

    # Read bot elev from sspa
    dfbot14 = pd.read_csv(f'{wdir}/BottomCSV/Layers1to4.csv')
    dfbot58 = pd.read_csv(f'{wdir}/BottomCSV/Layers5to8.csv')
    dfbot9 = pd.read_csv(f'{wdir}/BottomCSV/Layers9.csv')
    dfbot_sspa = pd.concat([dfbot14, dfbot58, dfbot9], axis=0)
    dfbot_sspa=dfbot_sspa.rename(columns={'col':'column', 'Layer':'layer', 'Bottom':'bot'})

    # reading the shapefile of GHB cell locations (southern BC only), head (before 2020), and K
    # Do not use the value from SSPA for 2020. It was incorrect. 
    # Need to update GHB conductance. The values in the shapefile were not optimized parameters
    gdf = gpd.read_file(ifile_ghb_shp)
    df_tmp=gdf[['ET_ID','row','column']]
    df_tmp["centroid_x"] = gdf.centroid.x
    df_tmp["centroid_y"] = gdf.centroid.y
    gdf['row'][gdf['row']==500] = 433
    xy = [(df_tmp["centroid_x"], df_tmp["centroid_y"]) for i, df_tmp in df_tmp.iterrows()]
    
    # get coordinate of grid centroid
    dfgrd = pd.read_csv(ifile_grid_centroid)
    dfgrd=dfgrd[['I','J']]
    dfgrd=dfgrd.rename(columns={'I':'row', 'J':'column'})

    # read in optimized conductance values
    dfghb=pd.read_csv(ifile_conductance)

    # Merge df to get cell bottom elevation
    dfghb = pd.merge(dfghb, dfbot_sspa, how='left', on=['row', 'column','layer'])

    list_yr = range(2014, 2023+1, 1)
    sp_of_start_yr = 97 # sp97 in ghb: start year 2014
    ofile = f'{wdir}/raster_files/interpolated_wl_2014_2023_at_GHB_offset.csv'
    list_months = range(1,12+1,1)

    count = 97
    for yr in list_yr:
        for i in list_months:
            if yr == 2023: #we only need ghb until July 2023
                raster_file = os.path.join(wdir,"raster_files",'2022', f'PROD_Termby_043022_WL_{i}.asc') #for 2023, using interp WLs from 2022
            if yr == 2022:
                raster_file = os.path.join(wdir,"raster_files",f'{yr}', f'PROD_Termby_043022_WL_{i}.asc')
            if yr==2021:
                raster_file = os.path.join(wdir,"raster_files",f'{yr}', f'PROD_Termby_043022_WL_{i}.asc')
            elif yr==2020:
                raster_file = os.path.join(wdir,"raster_files",f'{yr}', f'PROD_Termby_02102020_WL_{i}.asc')
            elif yr<=2019:
                wdir2 = os.path.join(wdir,"raster_files","before2020","WL_Gauge","WL_ASC",f"{yr}")
                raster_file = f'{wdir2}/WL_{i}.asc'

            # Extract concentration values from a raster file
            print(
                f'Reading input raster file: {raster_file} and extracting data at grid cells\n')
            res = extract_raster(raster_file, xy)
            gdf[f'head{count}'] = res
            count+=1

    # Saving to polygon grid file for checking -------------------      
    opt_exp_shp_file = False
    if opt_exp_shp_file:
        ofile_shp = f'{wdir}/Shapefile/GHB_CY2023.shp'
        gdf.to_file(ofile_shp)
        print(f'Saved {ofile_shp} \n')    

    print(f'Saved {ofile} \n')
    gdf.to_csv(ofile, index=False)

    # Prepare data for GW Vistas
    dfghb_final = pd.DataFrame()
    for sp in range(97, 97+118, 1): #July 2023 is SP 115, which is head211. #Oct 2023 is SP 118
        dfWL = gdf[['row','column',f'head{sp}']]
        # Merge to get GHB stage values
        dftmp = dfghb[['row', 'column', 'layer', 'cond', 'bot']].copy()
        df_merged = pd.merge(dftmp, dfWL, how='left', on=['row', 'column'])
        df_merged['SP'] = sp
        df_merged.rename(columns={f'head{sp}':'head'}, inplace=True)
        dfghb_final = pd.concat([dfghb_final, df_merged], axis=0)
        # later: Add GHB for below the river

    ### Delete cells that have GHB stages < bottom ele + 0.001-------------------
    dfghb_final['check'] = 'good'
    dfghb_final['bot']=dfghb_final['bot'].astype(float)
    flag = dfghb_final['head'] < dfghb_final['bot']+0.001
    dfghb_final['check'][flag] = 'delete'

    ### Assign 120 for the GHB heads below the river (based on MPR) -------------------
    dfghb_final=dfghb_final[['layer','row', 'column', 'head', 'cond', 'SP','bot','check']]
    flag = dfghb_final['row'] != 433
    dfghb_final['head'].loc[flag] = 120

    dfghb_final.to_csv(f'{wdir}/GHB_2014_toOct2023_all.csv', index=False)
    dfghb_final2 = dfghb_final[dfghb_final['check']=='good']
    dfghb_final2["SP"] = dfghb_final2["SP"] - 96 #Make stress periods start at SP 1, instead of 97.
    dfghb_final2.to_csv(f'{wdir}/GHB_2014_toOct2023_good_V2.csv', index=False)

    ### Instead of loading to GWV to generate GHB, you can generate GHB here:
    gen_ghb_package = True
    dfghb_final2 = pd.read_csv(f'{wdir}/GHB_2014_toOct2023_good.csv') ###2014-2023 dataset
    # dfghb_final2 = pd.read_csv(f'../model_packages/hist_2014_2023/ghb/GH_2014_2022_good_check.csv') ###2014-2022 dataset (QC/QA)
    if gen_ghb_package:
        # template = "         1       433       685 115.59502 800.00000         0" #got this from old GHB
        fout = open(os.path.join(wdir, "100hr3_Oct2023_MP.ghb"), 'w')
        fout.write("# MODFLOW2000 General Head Boundary Package\n")
        fout.write("PARAMETER  0  0\n")
        fout.write("      7333         0\n") #MAXIMUM NUMBER OF GHB CELLS FOR ANY GIVEN SP
        tmp = [] #only used once to find maximum number of ghb cells for any given SP
        for sp in dfghb_final2.SP.unique():
            print(sp)
            mydf = dfghb_final2.loc[dfghb_final2.SP == sp]
            tmp.append(len(mydf))
            fout.write(f"{len(mydf) :>10}{0 :>10}                      Stress Period {sp}\n")
            for idx in range(len(mydf)):
                #dfghb_final2.cond.unique() cond ranges from 65 to 500 to 1885, sig figs will differ
                if (mydf.cond.iloc[idx] < 10000) and (mydf.cond.iloc[idx] > 1000):
                #formatting :>10 means right aligned in the ten spaces allocated
                    fout.write(f"""{mydf.layer.iloc[idx] :>10}{mydf.row.iloc[idx] :>10}{mydf.column.iloc[idx] :>10} {(mydf["head"].iloc[idx]).round(5):.5f} {mydf["cond"].iloc[idx]:.4f}\n""")#         0  \n""")
                elif (mydf.cond.iloc[idx] < 1000) and (mydf.cond.iloc[idx] > 100):
                    fout.write(f"""{mydf.layer.iloc[idx] :>10}{mydf.row.iloc[idx] :>10}{mydf.column.iloc[idx] :>10} {mydf["head"].iloc[idx].round(5):.5f} {mydf["cond"].iloc[idx]:.5f}\n""")#         0  \n""")
                elif (mydf.cond.iloc[idx] < 100) and (mydf.cond.iloc[idx] > 10):
                    fout.write(f"""{mydf.layer.iloc[idx] :>10}{mydf.row.iloc[idx] :>10}{mydf.column.iloc[idx] :>10} {mydf["head"].iloc[idx].round(5):.5f} {mydf["cond"].iloc[idx]:.6f}\n""")#         0  \n""")
                else:
                    print("ERROR. You did not accoutn for conductances <10 or >10,000")
        fout.close()
        print(f"Generated GHB Package, your maximum number of GHB cells for any given SP is {max(tmp)}")

    # flopy to update GHB (WARNING: Not used because sig figs and spacing don't match old GHB)=====================================================
    # load a MODLOW flow model -------------------------------------------
    opt_update_ghb = False
    if opt_update_ghb: #(WARNING: Not used because sig figs and spacing don't match old GHB)
        stress_period_data = {}
        for sp in dfghb_final2.SP.unique()[:5]:
            if sp in stress_period_data.keys():
                print(f" {sp} already contains ghb data")
            else:
                print(f" adding ghb data for sp {sp}")
                mydf = dfghb_final2.loc[dfghb_final2.SP == sp]
                myLst = []
                for idx in range(len(mydf)):
                    myLst.append([
                        mydf.layer.iloc[idx],
                        mydf.row.iloc[idx],
                        mydf.column.iloc[idx],
                        "{:.5f}".format(mydf["head"].iloc[idx]),
                        "{:.5f}".format(mydf["cond"].iloc[idx])
                    ])
                    stress_period_data.update({sp - 1: myLst})  ###FloPy is ZERO-BASED index

        ghb = flopy.modflow.ModflowGhb(ml, stress_period_data=stress_period_data, filenames="100hr3_draft.ghb")
        ghb.write_file(check=True)
        ### Reference: https://flopy.readthedocs.io/en/3.3.2/source/flopy.modflow.mfghb.html