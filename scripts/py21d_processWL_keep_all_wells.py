import numpy as np
import os
import flopy.utils.binaryfile as bf
import pandas as pd
import matplotlib.pyplot as plt
import flopy
import geopandas as gpd
import matplotlib
import matplotlib.patheffects as pe
matplotlib.use('Qt5Agg')
import datetime as dt

def resample_to_monthly(df):
    """
    :param df: columns needs to be named [NAME,EVENT,VAL_FINAL]
    :return: df_monthly
    """
    df_monthly = pd.DataFrame()
    for well in df.NAME.unique():
        # try:
        mywell = df.loc[df.NAME == well]
        mywell.VAL_FINAL = mywell.VAL_FINAL.astype(float)
        mywell.EVENT = pd.to_datetime(mywell.EVENT)
        mywell2 = mywell.resample('MS', on='EVENT').mean() #MS is first day of month, M is last day of month.
        mywell2["NAME"] = well
        df_monthly = df_monthly.append(mywell2)
    df_monthly.dropna(subset=["VAL_FINAL"], inplace=True)
    return df_monthly

def plot_individual_WL_well(wl, wellgroupName):
    figDir = os.path.join('output', 'water_level_plots', 'individual_well', wellgroupName)
    if not os.path.isdir(figDir):
        os.makedirs(figDir)
     # Plot WL from AWLN wells
    list_wl_wells = wl['NAME'].unique()
    for well in list_wl_wells:
        # if well.startswith(("199-D", "199-H", "699-")):
        print(f'Processing well: {well}\n')
        df = wl[wl['NAME']==well]
        df['EVENT'] = pd.to_datetime(df['EVENT'])
        df = df.sort_values(by='EVENT')

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(df['EVENT'], df['VAL_FINAL'])
        ax.set_title(f'{well}')
        ax.set_ylabel('Water Level (m)')
        ax.set_xlabel('Date')
        ax.set_ylim([112,121])
        ax.grid()
        plt.savefig(os.path.join(figDir, f'{well}.png'), dpi=300)
        plt.close()
    return None

def preprocess_100D_WL():

    import glob
    data_files = glob.glob(
        os.path.join(os.path.dirname(cwd), 'data', 'water_levels', '100D', 'Jan2024_CPCCo', '*.xlsx'))
    #version 2 for  Water Level Graph_Inland Wells_D South_v2.xlsx because three rows had messed up Dates.

    all_data = {}
    for file in data_files:
        k = file.split("\\")[-1].split('.')[0]
        print(k)
        xl = pd.ExcelFile(file, engine='openpyxl')  # Open the Excel file
        sheet_names = xl.sheet_names  # Get the list of sheet names

        # Create a dictionary to hold data from this file
        well_data = {}
        for sn in sheet_names:
            if sn.startswith("199-"):
                print(sn)
                # Read the sheet and store it in the file_data dictionary
                well_data[sn] = pd.read_excel(file, sheet_name=sn, engine='openpyxl')
            else:
                print(f"Not reading from the following sheet: {sn}")

        # Store the file_data dictionary in the all_data dictionary under the key 'k'
        all_data[k] = well_data
    finalWL = pd.DataFrame()
    for idx, k in enumerate(all_data.keys()):
        print(k)
        for well in all_data[k].keys():
            print(well)
            if k == "Water Level Graph_Inland Wells_D South":
                all_data[k][well] = all_data[k][well].iloc[9:, :4]
            else:
                all_data[k][well] = all_data[k][well].iloc[9:, :]
            all_data[k][well].columns = all_data[k][well].iloc[0]
            all_data[k][well].drop(all_data[k][well].index[0], inplace=True)
            print(f"{well} Columns: {len(all_data[k][well].columns)}")
            all_data[k][well].rename(columns={'HYD_HEAD_METERS_NAVD88': 'Water Level (m)',
                                              'Elevation (m)': 'Water Level (m)',
                                              'Elevation of the water level in the well(m)': 'Water Level (m)',
                                              'Elevation of the water level in the well (m)': 'Water Level (m)',
                                              'HYD_DATE_TIME_PST': 'Date',
                                              'Date/Time':'Date',
                                              'Date and Time':'Date'}, inplace=True)
            all_data[k][well] = all_data[k][well].dropna(subset=['Water Level (m)'])
            # Filter out rows containing "Aug" in the Date column - erroneous date/time value
            all_data[k][well]['Date'] = all_data[k][well]['Date'].astype(str)
            if len((all_data[k][well]['Date'].str.contains('Aug') | all_data[k][well]['Date'].str.contains('Jul'))) > 0:
                print(f"Erroneous date cells for {well}: {len((all_data[k][well]['Date'].str.contains('Aug') | all_data[k][well]['Date'].str.contains('Jul')))}")
                all_data[k][well] = all_data[k][well][~(all_data[k][well]['Date'].str.contains('Aug') | all_data[k][well]['Date'].str.contains('Jul'))]
            try:
                all_data[k][well].Date = pd.to_datetime(all_data[k][well].Date)
            except:
                all_data[k][well].Date = pd.to_datetime(all_data[k][well].Date, format='%Y-%m-%d %H:%M:%S')
            all_data[k][well]["ID"] = well
            all_data[k][well] = all_data[k][well][["ID","Date", "Water Level (m)"]]
            finalWL = finalWL.append(pd.DataFrame(all_data[k][well]))
    print("Preprocessed WLs RAW Data from CPCCo - dataset received January 2024.")
    return finalWL


if __name__ == "__main__":
    cwd = os.getcwd()
    sce = "calib_2014_Oct2023"
    #inputDir =  r"C:\GH_Repos\100HR3-Rebound\data\water_levels\fromJose"
    rootDir = os.path.dirname(cwd)
    # inputDir =  f'D:/projects/CPCCO.M001.MASTER.TO-017/data/water_levels/fromJose/'
    inputDir =  os.path.join(rootDir, "data", "water_levels", "fromJose")
    wldir = os.path.join(cwd, 'output', 'water_level_data')
    wells = pd.read_csv(os.path.join(cwd, 'input', 'monitoring_wells_list_100D.csv'))

    AWLN = pd.read_csv(os.path.join(inputDir,"AWLN.txt"), delimiter="|")
    ManAWLN = pd.read_csv(os.path.join(inputDir,"ManAWLN.txt"), delimiter="|")
    ManHEIS = pd.read_csv(os.path.join(inputDir,"qryManHEIS.txt"), delimiter="|")

    # Filter dataframes to include only wells of interest
    #wells = wells[wells['NAME'].isin(wells.NAME.unique())] # hp: remove to keeps all wells
    #AWLN = AWLN[AWLN['NAME'].isin(wells.NAME.unique())]
    #ManAWLN = ManAWLN[ManAWLN['NAME'].isin(wells.NAME.unique())]
    #ManHEIS = ManHEIS[ManHEIS['NAME'].isin(wells.NAME.unique())]

    #Rebound = pd.read_csv(os.path.join(wldir, 'obs_2021_Oct2023', 'measured_WLs_all_100D.csv')) #py08a
    Rebound = pd.read_csv(os.path.join(rootDir, 'outlier_test', 'output', 'WL_no_outlier_v122023.csv')) # WLs without outliers
    Rebound.rename(columns={"ID":"NAME", "Water Level (m)":"VAL_FINAL", "Date": "EVENT"}, inplace=True)

    ### New dataset WLs (RAW) until Jan 2024
    Rebound2 = preprocess_100D_WL()
    Rebound2.rename(columns={"ID":"NAME", "Water Level (m)":"VAL_FINAL", "Date": "EVENT"}, inplace=True)


    AWLN = AWLN[["NAME", "EVENT", "VAL_FINAL"]]
    AWLN['TYPE'] = 'XD'
    ManAWLN = ManAWLN[["NAME", "EVENT", "VAL_FINAL"]]
    ManAWLN['TYPE'] = 'MAN'
    ManHEIS = ManHEIS[["NAME", "EVENT", "VAL"]]
    ManHEIS['TYPE'] = 'MAN'
    ManHEIS.rename(columns={"VAL":"VAL_FINAL"}, inplace=True)

    # Plot WL for each well (for checking) ====================================
    namedict = ["AWLN", "ManAWLN", "ManHEIS", "Rebound", "Rebound2"]
    cnt = 0
    for df in [AWLN, ManAWLN, ManHEIS, Rebound, Rebound2]:
        print(namedict[cnt])
        # plot_individual_WL_well(df, namedict[cnt]) #takes a long time to run
        cnt +=1

    ###threshold for Rebound and Rebound2, only use data after 07/01/2023,
    # even though data since 04/01/2023. I DONT LIKE THIS IDEA.
    # for df in [Rebound, Rebound2]:
    #     df.EVENT = pd.to_datetime(df.EVENT)
    #     print(f"Before threshold 07/01/2023: {min(df.EVENT)}, count: {len(df.EVENT)}")
    #     df = df.loc[df.EVENT >= pd.to_datetime("07/01/2023")]
    #     print(f"After threshold 07/01/2023: {min(df.EVENT)}, count: {len(df.EVENT)}")

    ### threshold for Jose data pull AWLN (ends in 06/30/2023). NOT TRUE. Ends in 09/09/2023
    # print(f"Jose data pull AWLN check: {max(AWLN.EVENT)}")

    # Drop duplicates for each dataset separately FIRST
    for df in [AWLN, ManAWLN, ManHEIS, Rebound, Rebound2]:
        print(f"Before removing duplicates: {len(df)}")
        df.drop_duplicates(ignore_index=True, inplace=True)
        print(f"After removing duplicates: {len(df)}")

    ### doublecheck ManHEIS (validated until 09/29/23)
    WL_obs1 = pd.concat([AWLN[["NAME","EVENT","VAL_FINAL", "TYPE"]],
                        ManAWLN[["NAME","EVENT","VAL_FINAL","TYPE"]],
                        ManHEIS[["NAME","EVENT","VAL_FINAL","TYPE"]]], axis=0, join='outer', ignore_index=True)
    # Removed duplicates in raw data, SUBSET [[VAL, EVENT, NAME, TYPE]]
    WL_obs1_noDups = WL_obs1.drop_duplicates(ignore_index=True)
    print(f"WL_obs1: {len(WL_obs1)}, WL_obs1_noDups: {len(WL_obs1_noDups)}")

    ### Now concatenate AWLN + HEIS with REBOUND DATA. Can't use TYPE column because MIXED.
    WL_obs2 = pd.concat([WL_obs1_noDups[["NAME","EVENT","VAL_FINAL"]],
                        Rebound[["NAME","EVENT","VAL_FINAL"]],
                        Rebound2[["NAME","EVENT","VAL_FINAL"]]], axis=0, join='outer', ignore_index=True)
    WL_obs2_noDups = WL_obs2.drop_duplicates(ignore_index=True)
    print(f"WL_obs2: {len(WL_obs2)}, WL_obs2_noDups: {len(WL_obs2_noDups)}")

    # Get data after 2021 only    
    WL_obs2_noDups['EVENT'] = pd.to_datetime(WL_obs2_noDups['EVENT']) #takes long time
    WL_obs2_noDups = WL_obs2_noDups[WL_obs2_noDups['EVENT'] > dt.datetime(2014,1,1)]

    # Save file:
    obsdir = os.path.join(wldir, "obs_2014_Jan2024") ###UPDATE foldername with new round of data
    if not os.path.isdir(obsdir):
        os.makedirs(obsdir)
    WL_obs2_noDups.to_csv(os.path.join(obsdir, "measured_WLs_all_wells.csv"), index=False)

    ###Only 100-D wells now:
    WL_obs2_noDups_100D = WL_obs2_noDups[WL_obs2_noDups['NAME'].isin(wells.NAME.unique())]
    WL_obs2_noDups_100D.to_csv(os.path.join(obsdir, "measured_WLs_100D_wells.csv"), index=False)

    # Resampled to monthly
    WL_obs2_noDups.reset_index(drop=True, inplace=True)
    WL_obs2_monthly = resample_to_monthly(WL_obs2_noDups)
    # WL_obs2_noDups = WL_obs2_noDups.set_index(WL_obs2_noDups['EVENT'])
    # WL_obs2_monthly = WL_obs2_noDups.groupby('NAME').resample('M').mean()
    WL_obs2_monthly.reset_index(inplace=True)

    # Add well coordinates (hpham)
    ifile_coords = f'input/qryWellHWIS_07202023.txt'
    dfcoords = pd.read_csv(ifile_coords, delimiter='|')
    dfcoords = dfcoords[['NAME','XCOORDS', 'YCOORDS']]

    # add coordinates to WL_obs_monthly
    WL_obs2_monthly = pd.merge(WL_obs2_monthly,dfcoords, how='left', on=['NAME'])

    # add column month and year
    WL_obs2_monthly['Year'] = WL_obs2_monthly['EVENT'].dt.year
    WL_obs2_monthly['Month'] = WL_obs2_monthly['EVENT'].dt.month

    WL_obs2_monthly.to_csv(os.path.join(obsdir, "measured_WLs_monthly_all_wells.csv"), index=False)

    ###Only 100-D wells now:
    WL_obs2_monthly_100D = WL_obs2_monthly[WL_obs2_monthly['NAME'].isin(wells.NAME.unique())]
    WL_obs2_monthly_100D.to_csv(os.path.join(obsdir, "measured_WLs_monthly_100D_wells.csv"), index=False)


    # Save to the format for water level mapping using the R-script
    WL_obs2_monthly_22 = WL_obs2_monthly.copy()
    WL_obs2_monthly_22 = WL_obs2_monthly_22[WL_obs2_monthly_22['Year'] == 2023] # Get CY 2023 data only

    WL_obs2_monthly_22['EVENT'] = WL_obs2_monthly_22['Month']
    WL_obs2_monthly_22['VAL'] = WL_obs2_monthly_22['VAL_FINAL']
    WL_obs2_monthly_22 = WL_obs2_monthly_22[['NAME','XCOORDS','YCOORDS', 'EVENT', 'VAL']]
    #WL_obs_monthly2['TYPE'] = 'XD'
    
    WL_obs2_monthly_22.to_csv(os.path.join(obsdir, "measured_WLs_monthly_all_wells_for_wl_mapping.csv"), index=False)
    
    # Choose MAN measurement over AWLN if MAN measurements are available
    # Not done yet

