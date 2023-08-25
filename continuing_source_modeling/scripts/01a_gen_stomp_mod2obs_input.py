"""
Generates input file for mod2obs to get simulated heads at potential STOMP cell locations.
BASED ON SCRIPT: S:\PSC\CHPRC.C003.HANOFF\Rel.126\predictive_model\scripts\06a_gen_fake_sim_hds_mod2obs_v2.py

To edit:
 - set 'model' to model run of interest.
 - under 'gen_ifile_mod2obs_sample_file' definition: 'df_wells' and 'df_final' csv name
 - under 'add_1stSP2mod2obs_ofile' definition: 'file' name at beginning, 'dt' and 'first_dt' definitions, + 'df3' csv name
 - under 'calc_conc_fracs' definition: 'finalDF' csv name
 - under 'datbywell' definition: 'df2' csv name
 - edit inputdir and outputdir as needed!

@author: mpedrazas
edited by rweatherl for STOMP-specific workflow
"""
import pandas as pd
import os
# import geopandas as gpd
import numpy as np



##For 100-HR, this will not change unless new source cells are considered.
def get_RC_faces(cwd): #east and west
    df_grid = pd.read_excel(os.path.join(os.path.dirname(cwd), 'input', 'grid_with_centroids.csv'), engine = 'openpyxl')
    ## note 8/26/22: where is this file?
    df_wells = pd.read_excel(os.path.join(os.path.dirname(cwd), 'output', 'TOB_Package', 'intermediate', 'Cr_wells_ijk_xy.xlsx'),
                             engine='openpyxl')

    df_grid['R_C'] = df_grid['I'].astype(str) + "_" + df_grid['J'].astype(str)
    df_wells['R_C'] = df_wells['i'].astype(str) + "_" + df_wells['j'].astype(str)
    df = df_wells.merge(df_grid, on=['R_C'], how='left', suffixes=('', '_y'))
    df.to_csv(os.path.join(outputDir, 'row_col_centroids4wells.csv'), index=False)

    return None


#For 100-HR, this will not change unless new source cells are considered.
def gen_ifile_mod2obs_coords(inputDir, wells, lays = 'all'):
    #This is USEFUL to generate a mod2obs input file for every layer in each well.
    ###Select wells of interest if subset, otherwise select all

    df_wells_all = pd.read_csv(os.path.join(inputDir, 'mod2obs_forSTOMP', 'mod2obs_pred_9L',
                                              'Bore_coordinates.csv'), header=None)
    df_wells = pd.DataFrame()
    if wells == 'all':
        df_wells = df_wells_all.loc[:,['ID', 'X', 'Y']]
    else: #select list of wells
        for well in wells:
            print(well)
            df = df_wells_all[df_wells_all.ID == well]
            df_wells = df_wells.append(df)
    # df_wells = df_wells[['WELL_NAME','EASTING','NORTHING']]

    ### Add layer column for all layers to run mod2obs transport
    df_return = pd.DataFrame()
    if lays == 'all':
        lays = 9
    for wellid in df_wells.ID.unique():
        df_temp = df_wells.loc[df_wells['ID'] == wellid]
        for lay in range(lays): # Make wells exist for all nine layers of model
            df_temp["LAYER"] = lay + 1
            df_temp['NICK_NAME'] = df_temp['ID'].str.replace('_E_DX', '')
            df_temp['NICK_NAME'] = df_temp['NICK_NAME'].str.replace('_E_HX', '')
            df_temp['NICK_NAME'] = df_temp['NICK_NAME'].str.replace('699-', '')
            if df_temp.ID.iloc[0].startswith("199"):
                df_temp["NICK_NAME"] = f"{df_temp['NICK_NAME'].iloc[0][4:]}-L{lay + 1}"
            elif df_temp.ID.iloc[0].startswith("PW_FY2023"):
                df_temp["NICK_NAME"] = f"{df_temp['NICK_NAME'].iloc[0][4:]}-L{lay+1}"
            else:
                df_temp["NICK_NAME"] = f"{df_temp['NICK_NAME'].iloc[0]}-L{lay+1}"
            df_return = df_return.append(df_temp)
    df_return[['NICK_NAME','X','Y',"LAYER"]].to_csv(os.path.join(outputDir, 'Bore_coordinates.csv'), index=False, header=False)

    return None

def gen_ifile_mod2obs_sample_file(times, inputDir, ifile):
    #%% ###### create mod2obs input file with dummy values (-9999) in order to get continuous simulated hds

    sp_file = pd.read_csv(os.path.join(inputDir, times))
    sp = pd.to_datetime(sp_file['SPstart']) #, format='%m/%d/%Y')

    df_wells = pd.read_csv(os.path.join(inputDir, 'Bore_coordinates.csv'), header= None)  ##for csm model

    wells = list(df_wells[0].unique())

    dfs = []
    for i, well in enumerate(wells):
        print(well)
        df_new = pd.DataFrame(columns=['WELL_NAME','Date','Time','Head (m)'])
        df_new['Date'] = sp
        df_new['WELL_NAME'] = well
        df_new['Time'] = pd.to_datetime(0, format='%H')
        df_new['Time'] = df_new['Time'].dt.time
        df_new['Head (m)'] = -9999
        dfs.append(df_new)
    df_final = pd.concat(dfs)
    df_final.Date = df_final.Date.dt.strftime("%m/%d/%Y")
    df_final.to_csv(os.path.join(inputDir, ifile), index=False, header=False) #csv file for mod2obs

    print('Saved {}'.format(ifile))

    return None

if __name__ == "__main__":

    cwd = os.getcwd()
    inputDir = os.path.join(os.path.dirname(cwd), 'input')
    case = 'flow_2014_2023'

    #outputDir = os.path.join(os.path.dirname(cwd), 'scenarios', f'{case}', 'BC_mod2obs')
    outputDir = os.path.join(os.path.dirname(cwd), f'{case}', 'BC_mod2obs')
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

    # wells = ['199-H4-83', '199-H4-84', '199-D5-151', '199-D5-160', '199-H4-86']

    ### [STEP 1] STOMP OPTION. Only run this function if you want to find faces for model cell where well is located.
    #get_RC_faces(cwd, wells) #useful for STOMP cell

    # [STEP 2] run this function to get Bore_coordinates.csv ifile for wells for lays = 1 for dummy layer value (flow)
    #gen_ifile_mod2obs_coords(inputDir) #output is Bore_coordinates.csv

    ### [STEP 3] Generate mod2obs input file based on Bore_coordinates.csv and times.xlsx
    times = 'stress_periods_2014-2023.csv'
    gen_ifile_mod2obs_sample_file(times, inputDir, 'Bore_Sample_File_in_model_calib.csv') # user set output name



