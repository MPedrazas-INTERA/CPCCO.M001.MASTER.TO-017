"""
Generates input file for mod2obs to get simulated heads or concentrations at desired locations.

To edit for new runs:
 - under 'gen_ifile_mod2obs_sample_file' definition: 'df_wells' and 'df_final' csv name
 - edit inputdir and outputdir as needed!

@author: mpedrazas
"""
import pandas as pd
import os
import numpy as np



def read_file(ifile, mode ='flow'):
    if mode =='flow':
        cols = ['WellName', 'Date', 'Time', 'Groundwater level (m)']
    elif mode == 'transport':
        cols = ['WellName', 'Date', 'Time', 'Concentration']
    # Read
    df = pd.read_csv(ifile, delim_whitespace=True,
                     skipinitialspace=True, names=cols)
    df['Date'] = pd.to_datetime(df['Date'])

    return df


def gen_ifile_mod2obs_coords(inputDir, wells, lays = 'all'):
    #This is USEFUL to generate a mod2obs input file for every layer in each well.
    ###Select wells of interest if subset, otherwise select all

    # df_wells_all = pd.read_csv(os.path.join(inputDir, 'monitoring_wells_master.csv'))
    df_wells_all = pd.read_csv(os.path.join(inputDir, 'monitoring_wells_coords_ij_V2.csv'))
    df_wells = pd.DataFrame()
    if wells == 'all':
        # df_wells = df_wells_all.loc[:,['ID', 'centroid_x', 'centroid_y']]  ## headings for 'monitoring_wells_master.csv'
        df_wells = df_wells_all.loc[:,['NAME', 'X', 'Y']]
    else: #define sub-list of wells
        for well in wells:
            print(well)
            df = df_wells_all[df_wells_all.ID == well]
            df_wells = df_wells.append(df)

    ### Add layer column for all layers to run mod2obs transport
    df_return = pd.DataFrame()

    structure = 'NAME'
    if lays == 'all':
        lays = 9
    if structure == 'ID':
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
                    df_temp["NICK_NAME"] = f"PW_{df_temp['NICK_NAME'].iloc[0][-1]}-L{lay+1}"
                    # df_temp["NICK_NAME"] = f"{df_temp['NICK_NAME'].iloc[0][0:3]}{i+1}-L{lay+1}"
                else:
                    df_temp["NICK_NAME"] = f"{df_temp['NICK_NAME'].iloc[0]}-L{lay+1}"
                df_return = df_return.append(df_temp)
    elif structure == 'NAME':
        for wellid in df_wells['NAME'].unique():
            df_temp = df_wells.loc[df_wells['NAME'] == wellid]
            for lay in range(lays):
                df_temp['LAYER'] = lay + 1
                df_temp["NICK_NAME"] = f"{df_temp['NAME']}-L{lay + 1}"
                df_return = df_return.append(df_temp)
    else:
        pass

    df_return[['NICK_NAME','X','Y',"LAYER"]].to_csv(os.path.join(outputDir, 'Bore_coordinates_wRUM.csv'), index=False, header=False)

    return df_return

def gen_ifile_mod2obs_sample_file(times, timeDir, outputDir, sce):
    #%% ###### create dummy values for mod2obs input file in order to get continuous simulated hds or conc

    sp_file = pd.read_csv(os.path.join(timeDir, times))
    sp = pd.to_datetime(sp_file['start_date'], format='%m/%d/%Y')

    ## use this range in df_new for daily timesteps
    # sp_daily = pd.date_range(start = '2014-01-01', end = '2023-08-01')

    dfs = []
    df_wells = pd.read_csv(os.path.join(outputDir, 'flow_2014_2023', "Bore_coordinates_wRUM.csv"), header= None)

    wells = list(df_wells[0].unique())

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
    df_final.to_csv(os.path.join(outputDir, 'Bore_Sample_File_in_model_daily_wRUM.csv'), index=False, header=False)

    print('Saved {}'.format('Bore_Sample_File_in_model.csv'))
    return None


if __name__ == "__main__":

    sce = 'calib_2014_2023'

    cwd = os.getcwd()
    # inputDir = os.path.join(cwd, 'output', 'well_info', sce)
    inputDir = os.path.join(cwd, 'input')
    timeDir = os.path.join(cwd, 'input')

    outputDir = os.path.join(cwd, 'output', 'mod2obs', sce) ##output directory in model run of choice
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

    # wells = ['199-H3-10', '199-H4-90', '199-H3-30', '199-H3-13', '199-H3-12', '199-H3-32']  ## RUM-2 monitoring wells
    wells = 'all'

    # [STEP 1] run this function to get Bore_coordinates.csv ifile for wells for all layers (transport)
    # or lays = 1 for dummy layer value (flow)
   bore_coords = gen_ifile_mod2obs_coords(inputDir, wells) #, lays=1) #output is Bore_coordinates.csv

    ### [STEP 2] Generate mod2obs input file based on Bore_coordinates.csv and times.xlsx
    #Note. Remember to change date format in excel.
    # times = "sp_2023to2125.csv"
    times = 'sp_2014_2023.csv'
    gen_ifile_mod2obs_sample_file(times, timeDir, outputDir, sce) #output is Bore_Sample_File_in_model.csv


