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
## TODO: resample to average value per SP + integrate calibration data
def read_chemdata(chemfile):

    chemdata_raw = pd.read_excel(chemfile)
    chemdata_raw.insert(0, 'NAME', chemdata_raw['SAMP_SITE_NAME_ID'].str.split('(', expand=True)[0])
    chemdata_raw['NAME'] = chemdata_raw['NAME'].str.strip()  ## remove hidden spaces

    chemdata = chemdata_raw[chemdata_raw['NAME'].isin(list(wells['NAME']))]

    crvi = chemdata[chemdata['STD_CON_LONG_NAME'] == 'Hexavalent Chromium']

    return chemdata, crvi

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

def plot_concentrations(df_conc, crvi):

    times['SPstart'] = pd.to_datetime(times['SPstart'])

    for well in df_conc['NAME'].unique():
        fig,ax = plt.subplots()
        for lay in [1,2,3,4]:
            # print(lay)
            ucn_toplot = df_conc[df_conc['NAME'] == well][df_conc['Layer'] == lay]
            data_toplot = crvi[crvi['NAME'] == well]
            ax.plot(times['SPstart'], ucn_toplot['Conc'], label = f'model layer {lay}')
            ax.scatter(data_toplot['SAMP_DATE_TIME'], data_toplot['STD_VALUE_RPTD'], zorder = 10, c = 'black')
        ax.legend()
        plt.grid(True)
        plt.title(f'{well}')

        # plt.savefig(os.path.join(cwd, 'output', 'concentration_plots', f'{well}_2014_2023_draft.png'))

    return None


if __name__ == "__main__":

    cwd = os.getcwd()

    wells = pd.read_csv(os.path.join(cwd, 'output', 'water_level_plots', 'monitoring_wells_coords_ij.csv'))
    chemfile = os.path.join(os.path.dirname(cwd), 'data', 'hydrochemistry', 'H-North Rebound Study Sampling_DATA.xlsx')

    times = pd.read_csv(os.path.join(cwd, 'input', 'sp_2014_2023.csv'))

    ucnfile = os.path.join(os.path.dirname(cwd), 'mruns', 'calib_2014_2023', 'tran_2014_2023', 'MT3D001.UCN')

    chemdata, crvi = read_chemdata(chemfile)

    data, df_conc = process_ucn_file(ucnfile)
    ntimes, nlay, nr, nc = data.shape

    plot_concentrations(df_conc, crvi)