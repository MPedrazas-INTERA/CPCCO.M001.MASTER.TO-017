import os
import pandas as pd
import geopandas as gpd 
import numpy as np 
from distutils.dir_util import copy_tree 
from shapely.geometry import Point
import fileinput
import sys

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

def gen_well_info_database(): # jUst need to run once
    ifile_wellinfo = os.path.join(wdir,'scripts','input','tmp','wellinfodxhx.csv')        
    dfwellinfo = pd.read_csv(ifile_wellinfo, skiprows=[0,2])
    dfwellinfo['wname'] = dfwellinfo['NAME'].str.split('_', 2, expand=True)[0]
    dfwellinfo['Type'] = dfwellinfo['NAME'].str.split('_', 2, expand=True)[1]
    dfwellinfo['System'] = dfwellinfo['NAME'].str.split('_', 2, expand=True)[2]
    dfwellinfo=dfwellinfo.drop(columns=['NAME'])
    dfwellinfo=dfwellinfo.drop_duplicates(subset=['wname'])
    ofile = os.path.join(wdir,'scripts','input','wellinfo_database.csv')
    #dfwellinfo.to_csv(ofile, index=False)

def gen_well_info_csv_file(df_new_rate,sce):
    ifile_wellinfo=os.path.join(wdir,'scripts','input','wellinfo_database.csv')
    dftmp1 = pd.read_csv(ifile_wellinfo)
    dftmp1['Type'] = 'E'
    dftmp2 = dftmp1.copy()
    dftmp2['Type'] = 'I'
    dfwellinfo = pd.concat([dftmp1, dftmp2], axis=0)
    dfwellinfo['NAME'] = dfwellinfo['wname'] + "_" + dfwellinfo['Type'].astype(str) + "_" + dfwellinfo['System'].astype(str)

    list_wells = list(df_new_rate['ID'].unique())
    df_new_rate['NAME'] = df_new_rate['ID'].copy()
    
    #df2.columns
    # merge df2 (all wells with rates) with existing df wellinfo 
    df3 = pd.merge(df_new_rate['NAME'],dfwellinfo, how='left', on=['NAME'])
    df3.columns
    
    sel_col  = ['NAME', 'XW', 'YW', 'NNODES', 'LOSSTYPE', 'PUMPLOC', 'Qlimit', 'PPFLAG', 'PUMPCAP', 'ScrnCorrFac', 'Ztop', 'Zbot', 'Rw', 'Group', 'ISTRTSP']
    df3=df3[sel_col]
    df3['PUMPLOC'].iloc[0]
    nwell = str(df3.shape[0])
    
    #df3['NNODES'] = df3['NNODES'].astype(float).round(decimals=0)
    
    #list_col = ['PUMPLOC','Qlimit','PPFLAG','PUMPCAP','ScrnCorrFac','Ztop','Zbot','Rw','Group','ISTRTSP']
    #for col in list_col:
    #    print(col)
    #    df3[col] = df3[col].astype(int) #.round(decimals=0)

    # Add three heading row
    df3.loc[-1] = ''
    df3.loc[-2] = df3.columns
    df3.loc[-3] = '' 
    df3.index = df3.index + 3  # shifting index
    df3 = df3.sort_index()  # sorting by index
    df3['NAME'].loc[0] = df3.shape[0]-3
    df3['XW'].loc[0] = 0
    
    # Write to file
    
    #create_new_dir(odir_pred_pmp_rates) # create folder to write outputs
    # Create a dupplicate of 100HR3\model_packages\pred_2023_2125\mnw2
    src = os.path.join(wdir,'model_packages','pred_2023_2125','mnw2_nfa')
    #dst = os.path.join(wdir,'model_packages','pred_2023_2125',f'mnw2_{sce}')
    copy_tree(src, dst)
    
    ofile = os.path.join(dst, f'wellinfodxhx_cy2023_2125.csv') 
    #ofile = os.path.join(wdir,'model_packages','hist_2014_2021','mnw2','wellinfodxhx_cy2014_2022.csv')

    df3.to_csv(ofile, header=False, index=False)

    # Update nwell in allocateQWell.in
    os.chdir(dst)
    #cmd_string = '"' + "sed -i 's/132/" + f'{str(nwell)}' + "/g' allocateQWell.in" + '"'
    #print(f'cmd={cmd}\n')
    #os.system(cmd)
    #subprocess.call(cmd_string)
    #subprocess.call("sed -i 's/132/84/g' allocateQWell.in")
    #subprocess.call(["sed -i -e 's/132/84/g' allocateQWell.in"], shell=True)

    # Read in the file
    with open('allocateQWell.in', 'r') as file :
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace('132', f'{nwell}')

    # Write the file out again
    with open('allocateQWell.in', 'w') as file:
        file.write(filedata)
    # Copy files from sce3 to sce3a
    src = os.path.join(wdir,'model_packages','pred_2023_2125',f'mnw2_{sce}_rr{rr}')
    #dst = os.path.join(wdir,'model_packages','pred_2023_2125',f'mnw2_{sce}')
    copy_tree(src, dst2)


    #check
    #df_check = df3[df3['XW'].isnull()]
    #df_check.NAME
    #print(df_check)
    os.chdir(os.path.join(wdir,'scripts'))
    return df3

def gen_shp_sys_wells(gdf, type_):
    # Save file for plume mapping
    gdf=gdf[gdf['Active']==1]
    gdf=gdf[gdf[f'{sce}']!=0] # well with rates
    gdf=gdf[(gdf['Type']==type_)]
    cols = ['ID','NAME','XCOORDS','YCOORDS',f'{sce}','geometry']
    
    gdf=gdf[cols]
    print(gdf)
    dst = os.path.join(wdir,'model_packages','pred_2023_2125',f'mnw2_{sce}_rr{rr}')
    dst2 = os.path.join(wdir,'model_packages','pred_2023_2125',f'mnw2_{sce}a_rr{rr}')
    if type_== 'E':
        gdf.to_file(os.path.join(dst, 'extraction_wells.shp'))
        gdf.to_file(os.path.join(dst2, 'extraction_wells.shp'))
    elif type_== 'I':
        gdf.to_file(os.path.join(dst, 'injection_wells.shp'))
        gdf.to_file(os.path.join(dst2, 'injection_wells.shp'))
    ax = gdf.plot(figsize=(15, 10))
    for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf.NAME):
        ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")
    print(f'Saved {ofile} for plume maps\n')

def assign_pmp_rates(ifile,sce,ofile):
    # [01] read in the live edit shpfile of pmp rate and sce
    rt0 = gpd.read_file(ifile)

    add_SFwells_toDB = False #only turn this on if you need to add the soil flushing wells to the database (shapefile)
    if add_SFwells_toDB:
        if rr==1:
            sf_df = pd.read_csv(os.path.join(os.getcwd(), "output", "soil_flushing","source_cells_100D_xy.csv"))
        ##Must add here wells instead of manually via QGIS.
            sf_gdf = gpd.GeoDataFrame(
            sf_df, geometry=gpd.points_from_xy(sf_df.XCOORDS, sf_df.YCOORDS))
            sf_gdf.drop(columns=["I","J"], inplace=True)
            sf_gdf.rename(columns={"flag":f"{sce}_flag", "val":f"{sce}_val"}, inplace=True)
            sf_gdf[f"{sce}a_flag"] = 'stop' #not a RUM well, therefore no need to pump after sp_pmp1
            sf_gdf[f"{sce}a_val"] = 0 #not a RUM well, therefore no need to pump after sp_pmp1
            ###Chose base_sce to copy that well configuration and add soil flushing wells:
            if sce=="sce6":
                base_sce = "sce4"
            elif sce=="sce5":
                base_sce = "sce3"
            else:
                print("error, for soil flushing, what sce do you want to copy well config from?")
                sys.exit
            rt0[f"{sce}_val"] = rt0[f"{base_sce}_val"]
            rt0[f"{sce}a_val"] = rt0[f"{base_sce}a_val"]
            rt0[f"{sce}_flag"] = rt0[f"{base_sce}_flag"]
            rt0[f"{sce}a_flag"] = rt0[f"{base_sce}a_flag"]
            rt = pd.concat([rt0, sf_gdf])
            rt.reset_index(drop=True, inplace=True)
        elif rr > 1:
            rt0[f"{sce}_rr{rr-1}"] = rt0[f"{sce}"]  ###save previous run as rr#
            rt0[f"{sce}a_rr{rr-1}"] = rt0[f"{sce}a"] ###save previous run as rr#
            rt = rt0.copy()
    if not add_SFwells_toDB:
        rt = rt0.copy()
        #rt.plot()

    rt.columns
    rt.head(3)
    rt['ID'] = rt['NAME'] + "_" + rt['Type'].astype(str) + "_" + rt['System'].astype(str)

    # [02] Assign rate
    rt2=rt.copy()

    #rt2=rt2.rename(columns={'SP109_2023':1, 'SP110_2023':2})
    rt2[f'{sce}'] = 0
    
    # If sce1_flag = max -> assign max1244 (max rate between 2014 and 2022)
    flag=(rt[f'{sce}_flag']=='max') & (rt['Type']=='E')
    rt2[f'{sce}'].loc[flag]=-rt['max1422'].loc[flag]
    
    # If injection well, make rate > 0
    flag=(rt[f'{sce}_flag']=='max') & (rt['Type']=='I')
    rt2[f'{sce}'].loc[flag]=rt['max1422'].loc[flag]

    # If col = 'avg', use the Feb 2023 rate (most current)
    flag=(rt[f'{sce}_flag']=='avg')
    rt2[f'{sce}'].loc[flag]=rt['avg_cy2022'].loc[flag]

    # If sce1_flag = stop -> stop
    flag=rt[f'{sce}_flag']=='stop'
    rt2[f'{sce}'].loc[flag]=0

    # If sce1_flag = man (manually defined by user)
    flag=rt[f'{sce}_flag']=='man'
    rt2[f'{sce}'].loc[flag]=rt2[f'{sce}_val'].loc[flag]

    ###Same for {sce}a: #MP addition
    rt2[f'{sce}a'] = 0
    flag = (rt[f'{sce}a_flag'] == 'max') & (rt['Type'] == 'E')
    rt2[f'{sce}a'].loc[flag] = -rt['max1422'].loc[flag]
    flag = (rt[f'{sce}a_flag'] == 'max') & (rt['Type'] == 'I')
    rt2[f'{sce}a'].loc[flag] = rt['max1422'].loc[flag]
    flag = (rt[f'{sce}a_flag'] == 'avg')
    rt2[f'{sce}a'].loc[flag] = rt['avg_cy2022'].loc[flag]
    flag = rt[f'{sce}a_flag'] == 'stop'
    rt2[f'{sce}a'].loc[flag] = 0
    flag = rt[f'{sce}a_flag'] == 'man'
    rt2[f'{sce}a'].loc[flag] = rt2[f'{sce}a_val'].loc[flag]

    #Save shapefile with calcualted rates for sce:
    point_xy = [Point(x, y) for x, y in zip(rt2['XCOORDS'].astype('float32'), rt2['YCOORDS'].astype('float32'))]
    rt3 = gpd.GeoDataFrame(rt2, geometry=point_xy)
    if opt_save_shp_file:
        rt3.to_file(ofile)
        print(f'saved {ofile}\n')
        rt3.plot()
    else: 
        print(f'NOTES: Did not save {ofile}\n')


    # Save file for plume mapping ---------------------------------------------
    type_='E'
    gen_shp_sys_wells(rt3, type_)
    type_='I'
    gen_shp_sys_wells(rt3, type_)

    # Choose final wells
    rt2=rt2[rt2['Active']==1]
    rt2=rt2[(rt2['Type']=='E') | (rt2['Type']=='I')]
    rt2=rt2[(rt2[f'{sce}_flag']!='stop')]

    # Total injection extraction rate:
    selected_cols = ['ID','XCOORDS','YCOORDS','Type','System','SP109_2023', 'SP110_2023',\
                     'avg1422','avg2122','max1422',f'{sce}_flag',f'{sce}',f'{sce}a_flag', f'{sce}a']
    rt4=rt2[selected_cols]
    rt_sum=rt4.groupby(by=['Type','System']).sum()
    print(rt_sum)
    rt4.to_csv('output/temp.csv')
    # difference between the total injection and extraction rates
    #diff = rt_sum['sce1']['E'] - rt_sum['sce1']['I']
    ### Increase injection rate
    #flag = rt2['Type']=='I'
    #rt2[flag]
    return rt2


def gen_mnw2(rt2, sce, opt_run_allocateqwell):
    ### [03] Generate a new MNW2 package ======================================
    gpmtom3d = (24*60)/1*231*(25.4/1000/1)**3 # 
    #selected_cols = ['ID']
    rt3=rt2[['ID']]

    for i in range(1,sp_pmp1+1,1): # assign rate Jan2023 to Dec2032
        rt3[i] = rt2[f'{sce}']*gpmtom3d
    for i in range(sp_pmp1+1,nsp+1,1): # Jan 2033 to end (2125)
        rt3[i] = 0

    if soil_flushing:
        print("Turning on soil flushing wells for specified pumping periods")
        for well in rt3.ID.unique():
            if well.startswith("SF"):
                for i in range(1,nsp+1,1):  # assign rates for soil flushing
                    if i not in soil_flushing_range:
                        rt3[i].loc[rt3.ID == well] = 0 #soil-flushing wells, assign zero outside of soil flushing range.
                    if i in soil_flushing_range:
                        rt3[i].loc[rt3.ID == well] = rt2[f"{sce}"].loc[rt2.ID == well].iloc[0]*gpmtom3d #assign rate during soil flushing range

        print("Turning off other injection wells in DX during soil-flushing (except 2)")
        rt3 = rt3.merge(rt2[["ID", "System", "Type"]], how="inner", on="ID") ##need this info to find injectors in DX.
        ### For soil flushing rr2, turn OFF other injection wells in DX system during flushing.
        turnoffWells = rt3.loc[~rt3.ID.str.startswith("SF") & (rt3.System == "DX")& (rt3.Type == "I")]
        for well in turnoffWells.ID.unique():
            if (well != '199-D5-128_I_DX') and (well !='199-D5-148_I_DX'):
                for i in range(1,nsp+1,1):  # assign rate during soil_flushing range
                    if i in soil_flushing_range:
                        rt3[i].loc[rt3.ID == well] = 0
        rt3.drop(columns=["System", "Type"], inplace=True) #no longer need these columns

    #print(rt3.head())

    # Save pmp rate to file
    #dst = os.path.join(wdir,'model_packages','pred_2023_2125',f'mnw2_{sce}')
    ofile = os.path.join(dst, f'wellratedxhx_cy2023_2125.csv')      
    #print(f'Generated file "wellratedxhx_cy2023_2125.csv" \n')
    rt3.to_csv(ofile, index=False)
    print(f'saved {ofile}\n')
    
    # go to dst folder and run 'allocatewell.exe' to create a new mnw2
    if opt_run_allocateqwell:
        os.chdir(dst)
        os.system('allocateqwell.exe > out.log')
        os.chdir(os.path.join(wdir,'scripts'))
        
    
def gen_mnw2a(rt2, sce, opt_run_allocateqwell):
    ### [03] Generate a new MNW2 package ======================================
    gpmtom3d = (24*60)/1*231*(25.4/1000/1)**3 # 
    #selected_cols = ['ID']
    rt3=rt2[['ID']]

    for i in range(1,sp_pmp1+1,1): # assign rate Jan2023 to Dec2035
        rt3[i] = rt2[f'{sce}']*gpmtom3d
    for i in range(sp_pmp1+1,nsp+1,1): # Jan 2033 to end (2125)
        rt3[i] = 0

    # for strategic wells, allow pumping until sp_pmp2
    flag = rt2[f'{sce}a']!=0
    for i in range(sp_pmp1+1,sp_pmp2+1,1): # assign rate Jan2032 to Dec2040
        rt3[i][flag] = rt2[f'{sce}a']*gpmtom3d
        #print(i)

    if soil_flushing:
        print("Turning on soil flushing wells for specified pumping periods")
        for well in rt3.ID.unique():
            if well.startswith("SF"): #soil-flushing wells, assign zero outside of soil flushing range.
                for i in range(1,nsp+1,1):  # assign rates for soil flushing
                    if i not in soil_flushing_range:
                        rt3[i].loc[rt3.ID == well] = 0 #soil-flushing wells, assign zero outside of soil flushing range.
                    if i in soil_flushing_range:
                        rt3[i].loc[rt3.ID == well] = rt2[f"{sce}"].loc[rt2.ID == well].iloc[0]*gpmtom3d #assign rate during soil flushing range

        print("Turning off other injection wells in DX during soil-flushing (except for 2 wells)")
        rt3 = rt3.merge(rt2[["ID", "System", "Type"]], how="inner", on="ID")
        ### For soil flushing rr2, turn OFF other injection wells in DX system during flushing.
        turnoffWells = rt3.loc[~rt3.ID.str.startswith("SF") & (rt3.System == "DX") & (rt3.Type == "I")]
        for well in turnoffWells.ID.unique():
            if (well != '199-D5-128_I_DX') and (well != '199-D5-148_I_DX'):
                for i in range(1, nsp+1, 1):  #assign 0 as rate during soil flushing
                    if i in soil_flushing_range:
                        rt3[i].loc[rt3.ID == well] = 0
        rt3.drop(columns=["System", "Type"], inplace=True)
    #print(rt3.head())

    # Save pmp rate to file
    #dst = os.path.join(wdir,'model_packages','pred_2023_2125',f'mnw2_{sce}a')
    ofile = os.path.join(dst2, f'wellratedxhx_cy2023_2125.csv')      
    #print(f'Generated file "wellratedxhx_cy2023_2125.csv" \n')
    rt3.to_csv(ofile, index=False)
    print(f'saved {ofile}\n')
    
    # go to dst folder and run 'allocatewell.exe' to create a new mnw2
    if opt_run_allocateqwell:
        os.chdir(dst2)
        os.system('allocateqwell.exe > out.log')
        os.chdir(os.path.join(wdir,'scripts'))

    ###If not working properly,
    ### Run in command prompt: allocateqwell.exe allocateQWell. in
        

if __name__ == "__main__":
    #### [00] input files and parameters ======================================
    # wdir = f'c:/Users/hpham/Documents/100HR3/'
    wdir = os.path.dirname(os.getcwd())
    
    #ifile = os.path.join(wdir,'gis','shp','processed_wellrate_DX_HX_2006_2023_coords_v032123.shp') #old for sce1
    #ifile = os.path.join(wdir,'gis','shp','wellrate_sce_v040323.shp') # for sce2, first round
    #ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce2_v040423.shp') # for sce2, 3rd rerun (rr3)
    #ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce2_v040623.shp') # for sce2, 3rd rerun (rr3)
    #
    #ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce2_v040423.shp') # first round as input
    #ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce2_v040623.shp') # 2nd round as input
    #ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce2_v041023.shp') # 3rd round as input
    
    # Sce3_rr1
    #ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v041123.shp') # for sce3, first run (rr1)
    #ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v041123_fi.shp') # for sce3, first run (rr1)
    
    # Sce3_rr2
    #ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v041123_fi.shp') # for sce3, first run (rr2, 04/13/23)
    #ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v041323_fi.shp') # for sce3, first run (rr2, 04/13/23)
    
    # Sce3_rr3, 04/17/2023
    #ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v041323_fi.shp') # 
    #ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v041723_fi.shp') # 
    
    # Sce3_rr4, 04/18/2023 (still seeing a plume in 100-H Area, RUM-2. )
    #ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v041723_fi.shp') # 
    #ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v041823_fi.shp') # 
    
    # For Sce3_rr5, 04/19/2023 (added a new injection well nw_5 - inj)
    #ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v041823_fi.shp') # 
    #ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v041923_fi.shp') # 

    # For Sce3_rr6, rr7 and sce4_rr1, 04/20/2023 (added a new injection well nw_6 - ext)
    # ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v041923_fi.shp') #
    # ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v042023_fi.shp') #
    
    # For Sce3a_rr8, 04/21/2023 (checked and fixed desired rates)
    #ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v042023_fi.shp') # 
    #ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v042123_fi.shp') # 
    
    # For Sce3_rr6, rr7 and sce4_rr1, 04/20/2023 (added a new injection well nw_6 - ext)
    #ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v042523_fi.shp') # 
    #ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v042623_fi.shp') #

    #For sce5_rr1, add soil flushing wells to sce3a (based off sce3a_rr8)
    #ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v042623_fi.shp') #
    #ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v042723_fi.shp') #

    #For sce6_rr1, add soil flushing wells (4 rounds) to sce4a
    # ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v050223_fi.shp') #
    # ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v050323_fi.shp') #

    #For sce6_rr2, add soil flushing wells (6 rounds) to sce4a + shutff injectors in DX during soil flushing
    # ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v050323_fi.shp') #
    # ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v050823_fi.shp') #

    #For sce8_rr1 add soil flushing wells to new well configuration
    # ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v051123_fi.shp') #
    # ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v051223_fi.shp') #

    ifile = os.path.join(wdir, 'gis', 'shp', 'wellrate_added_sce10.shp')

    nsp = 598
    sp_pmp1 = 120 # To end of 2032
    sp_pmp2 = 456 # To end of 2060

    sce = 'sce10'

    rr = 1
    soil_flushing = True
    soil_flushing_range = [28, 29, 30, 31, 32, 33, 34,  # Apr-Oct 2025
                           52, 53, 54, 55, 56, 57, 58,  # Apr-Oct 2027
                           76, 77, 78, 79, 80, 81, 82,  # Apr-Oct 2029
                           100, 101, 102, 103, 104, 105, 106,  # Apr-Oct 2031
                           124, 125, 126, 127, 128, 129, 130,  # Apr-Oct 2033
                           148, 149, 150, 151, 152, 153, 154,  # Apr-Oct 2035
                           172, 173, 174, 175, 176, 177, 178, ## Apr-Oct 2037
                           196, 197, 198, 199, 200, 201, 202  ## Apr-Oct 2039
                           ]
    #### ======================================================================

    # if sce=='sce2' or sce=='sce3' or sce=='sce5':
    #     sp_pmp2 = 120 + 8*12  #add 8 more years of pumping after 2032 = 2040
    # elif sce=='sce4' or sce=='sce6' or sce=='sce8':
    #     sp_pmp2 = 336 #336 ##Trying End of 2050 for cleanup with soil-flushing #400 #598 nto working properly # pumping to 2125 (end of simulation)
    #     ###In this case, must manually update SP401 to 598 in MNW2, bug in allocateqwell.exe

    #### ======================================================================
    #### No modification needed after this line ===============================
    #### ======================================================================
    
    ### [00] Create a working directory =======================================
    dst = os.path.join(wdir,'model_packages','pred_2023_2125',f'mnw2_{sce}_rr{rr}')
    create_new_dir(dst) # create folder to write outputs
    dst2 = os.path.join(wdir,'model_packages','pred_2023_2125',f'mnw2_{sce}a_rr{rr}')
    create_new_dir(dst2) # create folder to write outputs

    #### [01] Asign pmp rates based on sce from live shpfile edit in QGIS =====
    opt_save_shp_file = True # save ofile?
    df_new_rate =assign_pmp_rates(ifile, sce, ofile)

    # Generate wellinfo file ==================================================
    gen_well_info_csv_file(df_new_rate,sce) # must run to create new folder
    
    #### [02] Generate a MNW2 package ========================================    
    opt_run_allocateqwell = True
    gen_mnw2(df_new_rate, sce, opt_run_allocateqwell) # Uncomment to run
    #### ======================================================================

    ### [03] Generate scexa such as sce2a and sce3 ============================
    gen_mnw2a(df_new_rate, sce, opt_run_allocateqwell) # Uncomment to run

    print(f'Done all!!!')
