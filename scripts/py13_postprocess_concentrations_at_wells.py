"""
Extract concentration timeseries at well locations

"""


import numpy as np
import os
import flopy.utils.binaryfile as bf
import pandas as pd
import matplotlib.pyplot as plt
import flopy
import geopandas as gpd
import matplotlib
matplotlib.use('Qt5Agg')


## Read in observation data
## TODO: resample to average value per SP(?) + integrate calibration data
def read_chemdata(chemfile):

    chemdata_raw = pd.read_excel(chemfile, engine='openpyxl')
    chemdata_raw.insert(0, 'NAME', chemdata_raw['SAMP_SITE_NAME_ID'].str.split('(', expand=True)[0])
    chemdata_raw['NAME'] = chemdata_raw['NAME'].str.strip()  ## remove hidden spaces

    chemdata = chemdata_raw[chemdata_raw['NAME'].isin(list(wells['NAME']))]

    crvi = chemdata[chemdata['STD_CON_LONG_NAME'] == 'Hexavalent Chromium']

    flags = ['R', 'P', 'Y', 'PQ', 'QP', 'AP', 'APQ', 'PA', 'QR']
    crvi_filt = crvi[~crvi['REVIEW_QUALIFIER'].isin(flags)]

    return chemdata, crvi_filt

## read in UCN file, extract results at wells
def process_ucn_file(ucnfile, all_lays = False):

    precis = 'double'

    ucnobj = bf.UcnFile(ucnfile, precision=precis)
    times = ucnobj.get_times()
    data = ucnobj.get_alldata(mflay=None, nodata=-1)/1000 #dividing by 1000 to match units of Obs
    ntimes, nlay, nr, nc = data.shape

    if all_lays:
        nlays = range(nlay)
    else:
        # nlays = [0]       ## first layer only
        nlays = [0, 1, 2, 3]  ##unconfined only
    vals = []
    for idx, row, col in zip(range(len(wells)), wells['Row'], wells['Col']):
        for t_idx, t in enumerate(times):
            for lay in nlays:
                vals.append([data[t_idx][lay][row][col], t, lay + 1, row, col, wells['NAME'].iloc[idx]])  # 237 nodes * 84 times = 19908 vals for L1
    df_conc = pd.DataFrame(vals, columns=['Conc', 'Time', 'Layer', 'Row', 'Column', 'NAME'])
    df_conc.drop_duplicates(inplace=True)

    return data, df_conc

def plot_concentrations(df_conc, crvi, mode):
    wellDict = {'199-H3-25':"North_PT_SensorData", '199-H3-26':"North_PT_SensorData", '199-H3-27':"North_PT_SensorData", '199-H3-2A': "North_AWLN", '199-H4-12A': "North_Manual",
       '199-H4-15A': "North_Manual", '199-H4-17':"North_PT_SensorData", '199-H4-18': "North_Manual", '199-H4-4':"North_PT_SensorData", '199-H4-5': "North_AWLN",
       '199-H4-64': "North_Manual", '199-H4-65': "North_Manual", '199-H4-8': "North_AWLN", '199-H4-84': "North_AWLN", '199-H4-85': "North_Manual",
       '199-H4-86':"North_PT_SensorData", '199-H4-88': "North_AWLN", '199-H4-89': "North_Manual"}

    times['SPstart'] = pd.to_datetime(times['SPstart'])

    if mode == "mod2obs":
        for well in df_conc['SAMP_SITE_NAME'].unique():
            fig, ax = plt.subplots(figsize=(8, 5))
            ucn_toplot = df_conc[df_conc['SAMP_SITE_NAME'] == well]
            data_toplot = crvi[crvi['NAME'] == well]
            ax.plot(pd.to_datetime(ucn_toplot["SAMP_DATE"]), ucn_toplot['WeightedConc'], label=f'Simulated', color = "cornflowerblue")
            ax.scatter(data_toplot['SAMP_DATE_TIME'], data_toplot['STD_VALUE_RPTD'], zorder=10, label = f"Observed", c = "r", edgecolor="darkred", s=10)
            ax.plot(data_toplot['SAMP_DATE_TIME'], data_toplot['STD_VALUE_RPTD'], zorder=10, c = "r", ls="--", alpha=0.5)
            ax.set_title(f'{wellDict[well]}: {well}')
            ax.set_ylabel('Cr(VI) (ug/L)')
            ax.minorticks_on()
            ax.grid(which='major', linestyle='-',
                    linewidth='0.1', color='red')
            ax.grid(which='minor', linestyle=':',
                    linewidth='0.1', color='black')
            ax.legend()
            plt.xticks(rotation=45)
            fig.tight_layout()
            # ax.set_xlabel("Date")
            ax.set_xlim(pd.to_datetime("2014-01-01"), pd.to_datetime("2023-07-31"))
            plt.savefig(os.path.join(cwd, 'output', 'concentration_plots', f"{sce}", f'{well}_2014_2023_MOD2OBS.png'))
            plt.close()

    elif mode == "ucn":
        for well in df_conc['NAME'].unique():
            fig,ax = plt.subplots()
            for lay in [1,2,3,4]:
                # print(lay)
                ucn_toplot = df_conc[df_conc['NAME'] == well][df_conc['Layer'] == lay]
                data_toplot = crvi[crvi['NAME'] == well]
                ax.plot(times['SPstart'], ucn_toplot['Conc'], label = f'model layer {lay}')
            ax.scatter(data_toplot['SAMP_DATE_TIME'], data_toplot['STD_VALUE_RPTD'], label = f"Observed", zorder = 10, c = 'grey', edgecolor="k", s=10)
            ax.set_title(f'{wellDict[well]}: {well}')
            ax.set_ylabel('Cr(VI) (ug/L)')
            ax.minorticks_on()
            ax.grid(which='major', linestyle='-',
                    linewidth='0.1', color='red')
            ax.grid(which='minor', linestyle=':',
                    linewidth='0.1', color='black')
            ax.legend()
            plt.xticks(rotation=45)
            fig.tight_layout()
            ax.set_xlim(pd.to_datetime("2014-01-01"), pd.to_datetime("2023-07-31"))
            plt.savefig(os.path.join(cwd, 'output', 'concentration_plots', f"{sce}", f'{well}_2014_2023_UCN.png'))
            plt.close()
    return None


if __name__ == "__main__":

    cwd = os.getcwd()
    sce = 'calib_2014_2023'
    wells = pd.read_csv(os.path.join(cwd, 'input', 'monitoring_wells_coords_ij.csv'))
    chemfile = os.path.join(os.path.dirname(cwd), 'data', 'hydrochemistry', 'H-North Rebound Study Sampling_DATA.xlsx')
    chemdata, crvi_filt = read_chemdata(chemfile)

    times = pd.read_csv(os.path.join(cwd, 'input', 'sp_2014_2023.csv'))

    mode = "mod2obs" #"mod2obs"
    if mode == "ucn":
        ucnfile = os.path.join(os.path.dirname(cwd), 'mruns', f'{sce}', f'tran_{sce[-9:]}', 'MT3D001.UCN')
        data, df_conc = process_ucn_file(ucnfile)
        ntimes, nlay, nr, nc = data.shape
    elif mode == "mod2obs":
        df_conc = pd.read_csv(os.path.join(os.path.dirname(cwd), 'mruns', f'{sce}', f'tran_{sce[-9:]}', 'post_process', 'mod2obs_monitoring_wells', 'simulated_conc_mod2obs.csv'))

    plot_concentrations(df_conc, crvi_filt, mode)