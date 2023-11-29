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

def resample_to_monthly(wells, df):
    """
    :param df: columns need to be named NAME/ID and EVENT/DATE
    :param woi: list of WELLS of interest
    :return: df_monthly
    """
    df.rename(columns={"EVENT":"DATE", "NAME":"ID", "VAL": "Water Level (m)", "VAL_FINAL": "Water Level (m)"}, inplace=True)
    df.DATE = pd.to_datetime(df.DATE)
    df_monthly = pd.DataFrame()
    for well in wells.NAME.unique():
        try:
            mywell = df.loc[df.ID == well]
            mywell2 = mywell.resample('MS', on='DATE').mean() #MS is first day of month, M is last day of month.
            mywell2["ID"] = well
            df_monthly = df_monthly.append(mywell2)
        except:
            pass
    df_monthly.dropna(subset=["Water Level (m)"], inplace=True)
    return df_monthly

if __name__ == "__main__":
    cwd = os.getcwd()
    sce = "calib_2014_Oct2023"
    inputDir =  r"C:\GH_Repos\100HR3-Rebound\data\water_levels\fromJose"
    wldir = os.path.join(cwd, 'output', 'water_level_data')
    wells = pd.read_csv(os.path.join(cwd, 'input', 'monitoring_wells_coords_ij_v2.csv'))

    AWLN = pd.read_csv(os.path.join(inputDir,"AWLN.txt"), delimiter="|")
    ManAWLN = pd.read_csv(os.path.join(inputDir,"ManAWLN.txt"), delimiter="|")
    ManHEIS = pd.read_csv(os.path.join(inputDir,"qryManHEIS.txt"), delimiter="|")

    # Filter dataframes to include only wells of interest
    wells = wells[wells['NAME'].isin(wells.NAME.unique())]
    AWLN = AWLN[AWLN['NAME'].isin(wells.NAME.unique())]
    ManAWLN = ManAWLN[ManAWLN['NAME'].isin(wells.NAME.unique())]
    ManHEIS = ManHEIS[ManHEIS['NAME'].isin(wells.NAME.unique())]

    Rebound = pd.read_csv(os.path.join(wldir, 'obs_2021_Oct2023', 'measured_WLs_all.csv'))
    Rebound.rename(columns={"ID":"NAME", "Water Level (m)":"VAL_FINAL", "Date": "EVENT"}, inplace=True)

    AWLN = AWLN[["NAME", "EVENT", "VAL_FINAL"]]
    ManAWLN = ManAWLN[["NAME", "EVENT", "VAL_FINAL"]]
    ManHEIS = ManHEIS[["NAME", "EVENT", "VAL"]]
    ManHEIS.rename(columns={"VAL":"VAL_FINAL"}, inplace=True)

    # Convert 'EVENT' column to datetime for proper matching
    for df in [AWLN, ManAWLN, ManHEIS, Rebound]:
        df['EVENT'] = pd.to_datetime(df['EVENT'])

    WL_obs = pd.concat([Rebound, AWLN, ManAWLN, ManHEIS], axis=0, join='outer', ignore_index=True)
    # Removed duplicates in raw data
    WL_obs_noDups = WL_obs.drop_duplicates(ignore_index=True)

    # Resampled to monthly
    WL_obs_monthly = resample_to_monthly(wells, WL_obs_noDups)

    # Save file:
    if not os.path.isdir(os.path.join(wldir, "obs_2014_Oct2023")):
        os.makedirs(os.path.join(wldir, "obs_2014_Oct2023"))
    WL_obs_noDups.to_csv(os.path.join(wldir, "obs_2014_Oct2023", "measured_WLs_all.csv"), index=True)
    WL_obs_monthly.to_csv(os.path.join(wldir, "obs_2014_Oct2023", "measured_WLs_monthly.csv"), index=True)







