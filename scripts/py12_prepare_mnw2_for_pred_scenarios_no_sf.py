import os
import pandas as pd
import geopandas as gpd 
import numpy as np 
from distutils.dir_util import copy_tree 
from shapely.geometry import Point
import fileinput

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
    #src = os.path.join(wdir,'model_packages','pred_2023_2125','mnw2_nfa')
    #dst = os.path.join(wdir,'model_packages','pred_2023_2125',f'mnw2_{sce}')
    #copy_tree(src, dst)
    
    
    #    
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
    os.chdir(dst2)
    os.remove('100hr3_2023to2125.mnw2')


    #check
    #df_check = df3[df3['XW'].isnull()]
    #df_check.NAME
    #print(df_check)
    os.chdir(os.path.join(wdir,'scripts'))
    return df3

def gen_shp_sys_wells(gdf, type_, ofile):
    # Save file for plume mapping
    #type_ = 'E'
    gdf=gdf[gdf['Active']==1]
    gdf=gdf[gdf[f'{sce}']!=0] # well with rates 
    gdf=gdf[(gdf['Type']==type_)]
    cols = ['ID','NAME','XCOORDS','YCOORDS',f'{sce}','geometry']
    
    #gdf=gdf[cols]
    print(gdf)
    #dst = os.path.join(wdir,'model_packages','pred_2023_2125',f'mnw2_{sce}a')
    #ofile = os.path.join(dst, 'extraction_wells.shp')
    gdf.to_file(ofile)
    ax = gdf.plot(figsize=(15, 10))
    for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf.NAME):
        ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")

    print(f'Saved {ofile}\n') 
    return None

def assign_pmp_rates(ifile,sce,ofile):
    # [01] read in the live edit shpfile of pmp rate and sce
    rt = gpd.read_file(ifile)
    #rt.plot()
    #rt.columns
    #rt.head(3)
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

    # If sce1_flag = man (manually defined by hph)
    flag=rt[f'{sce}_flag']=='man'
    rt2[f'{sce}'].loc[flag]=rt2[f'{sce}_val'].loc[flag]


    #
    #point_xy = [Point(x, y) for x, y in zip(rt2['XCOORDS'].astype('float32'), rt2['YCOORDS'].astype('float32'))]
    point_xy = [Point(x, y) for x, y in zip(rt2['Xnew'], rt2['Ynew'])]
    rt3 = gpd.GeoDataFrame(rt2, geometry=point_xy)
    if opt_save_shp_file:
        rt3.to_file(ofile)
        print(f'saved {ofile}\n')
        #rt3.plot()
        
        # Save file for plume mapping ---------------------------------------------
        type_='E'
        ofile_ext_wells = os.path.join(dst, 'extraction_wells.shp')
        gen_shp_sys_wells(rt3, type_, ofile_ext_wells)
        type_='I'
        ofile_inj_wells = os.path.join(dst, 'injection_wells.shp')
        gen_shp_sys_wells(rt3, type_, ofile_inj_wells)
    else: 
        print(f'NOTES: Did not saved shape files\n')





    # Choose final wells
    rt2=rt2[rt2['Active']==1]
    rt2=rt2[(rt2['Type']=='E') | (rt2['Type']=='I')]
    rt2=rt2[(rt2[f'{sce}_flag']!='stop')]

    # Total injection extraction rate:
    selected_cols = ['ID','XCOORDS','YCOORDS','Type','System','SP109_2023', 'SP110_2023',\
                     'avg1422','avg2122','max1422',f'{sce}_flag',f'{sce}',f'{sce}a'] #'sce2','sce3'
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
    #for i in range(1,2+1,1): # convert to m3/d for two first sp
    #    rt3[i] = rt2[i]*gpmtom3d

    for i in range(1,sp_pmp1+1,1): # assign rate Jan2023 to Dec2032
        rt3[i] = rt2[f'{sce}']*gpmtom3d
    for i in range(sp_pmp1+1,nsp+1,1): # Jan 2033 to end (2125)
        rt3[i] = 0



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
    #for i in range(1,2+1,1): # convert to m3/d for two first sp
    #    rt3[i] = rt2[i]*gpmtom3d

    for i in range(1,sp_pmp1+1,1): # assign rate Jan2023 to Dec2032
        rt3[i] = rt2[f'{sce}']*gpmtom3d
    for i in range(sp_pmp1+1,nsp+1,1): # Jan 2033 to end (2125)
        rt3[i] = 0

    # for RUM-2, allow pumping until 2040
    flag = rt2[f'{sce}a']!=0
    for i in range(sp_pmp1+1,sp_pmp2+1,1): # assign rate Jan2032 to Dec2040
        rt3[i][flag] = rt2[f'{sce}a_val']*gpmtom3d
        #print(i)

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
        
    # 06/06/2023 ==============================================================
    # Generate new injection/extraction shapefile =============================

    # injection well layer ----------------------------------------------------
    ifile_ext_wells = os.path.join(dst, 'extraction_wells.shp')
    df = gpd.read_file(ifile_ext_wells)
    flag = df[f'{sce}a']!=0
    df=df[flag]
    ofile_ext_wells = os.path.join(dst2, 'extraction_wells.shp')
    df.to_file(ofile_ext_wells)

    # injection well layer ---------------------------------------------------
    ifile_inj_wells = os.path.join(dst, 'injection_wells.shp')
    df = gpd.read_file(ifile_inj_wells)
    flag = df[f'{sce}a']!=0
    df=df[flag]
    ofile_inj_wells = os.path.join(dst2, 'injection_wells.shp')
    df.to_file(ofile_inj_wells)


if __name__ == "__main__":
    #### [00] input files and parameters ======================================
    wdir = f'c:/Users/hpham/Documents/100HR3/'
    #wdir = os.path.dirname(os.getcwd())
    
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
    #ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v041123_recheck.shp') # for sce3, first run (rr2, 04/13/23)
    
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
    #ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v041923_fi.shp') # 
    #ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v042623_fi.shp') # 
    
    # For Sce3a_rr8, 04/21/2023 (checked and fixed desired rates)
    #ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v042023_fi.shp') # 
    #ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v042123_fi.shp') # 
    
    # For Sce3_rr6, rr7 and sce4_rr1, 04/20/2023 (added a new injection well nw_6 - ext)
    #ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v042523_fi.shp') # 
    #ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v042623_fi.shp') # 

    # For Sce3_rr10
    #ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v042623_fi.shp') # 
    #ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v042723_fi.shp') #  

    # For Sce3_rr11
    #ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v042623_fi.shp') # 
    #ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v050323_fi.shp') # 
    
    # For Sce4b, 05/22/2023
    ifile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v050223_fi.shp') # 
    ofile = os.path.join(wdir,'gis','shp','wellrate_added_sce3_v052223_fi.shp') # 
    

    nsp = 598
    #sp_pmp2 = 120 # last sp of pmp, Dec2032
    sp_pmp1 = 120 # last = Dec2032 # last sp of pmp from unconfined aq.

    #sce, rr = 'sce2', 1    # sys constrainted, no sources
    #sce, rr = 'sce3', 12    # no sys constrained, no sources
    sce, rr = 'sce2', 1 # no sys constrained, with sources
                        # for sce4b, hpham runn sce4 again and later rename to sce4b
    #### ======================================================================

    #
    if sce=='sce2' or sce=='sce3' or sce=='sce99':
        sp_pmp2 = 120 + 8*12 # rr4: add 8 more years of pumping after 2032. 
    elif sce=='sce4':
        #sp_pmp2 = 400 # pumping to 2125 (end of simulation)
        sp_pmp2 = 120 + 8*12 # pumping to 2125 (end of simulation)

    # merge current system well and RUM wells (only run it once)

    #### ======================================================================
    #### No modification needed after this line ===============================
    #### ======================================================================
    
    ### [00] Create a working directory =======================================
    src = os.path.join(wdir,'model_packages','pred_2023_2125','mnw2_nfa')
    dst = os.path.join(wdir,'model_packages','pred_2023_2125',f'mnw2_{sce}_rr{rr}')
    dst2 = os.path.join(wdir,'model_packages','pred_2023_2125',f'mnw2_{sce}a_rr{rr}')
    copy_tree(src, dst)
    #os.chdir(dst)
    #os.remove('100hr3_2023to2125.mnw2')
    #os.chdir(f'{wdir}/scripts')


    #os.remove(dst)
    #os.remove(dst2)
    create_new_dir(dst) # create folder to write outputs
    create_new_dir(dst2) # create folder to write outputs

    #### [01] Asign pmp rates based on sce from live shpfile edit in QGIS =====
    opt_save_shp_file = True # save ofile? 
    df_new_rate=assign_pmp_rates(ifile, sce, ofile)
    

    # Generate wellinfo file ==================================================
    gen_well_info_csv_file(df_new_rate,sce) # must run to create new folder
    
    #### [02] Generate a MNW2 package ========================================    
    opt_run_allocateqwell = True
    gen_mnw2(df_new_rate, sce, opt_run_allocateqwell) # Uncomment to run
    #### ======================================================================

    ### [03] Generate scexa such as sce2a and sce3 ============================
    gen_mnw2a(df_new_rate, sce, opt_run_allocateqwell) # Uncomment to run

    print(f'Done all!!!')
