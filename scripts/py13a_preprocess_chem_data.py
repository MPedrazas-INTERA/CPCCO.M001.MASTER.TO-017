"""
Pre-process raw hydrochem data
"""


import numpy as np
import os
import pandas as pd
import glob
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')

cwd = os.getcwd()
wdir = os.path.dirname(cwd)

## Read in observation data
def read_chemdata():

    zone = '100D'

    if zone == '100H':
        data_files = glob.glob(os.path.join(wdir, 'data', 'hydrochemistry', 'H-North*.xlsx'))
        all_files = [pd.read_excel(file) for file in data_files]
        chemdata_raw = pd.concat(all_files)
        chemdata = chemdata_raw[chemdata_raw['NAME'].isin(list(wells['NAME']))]
    if zone == '100D':
        chemdata = pd.read_excel(os.path.join(wdir, 'data', 'hydrochemistry', 'D-South Rebound Study Sampling_contaminantdatathru_10172023.xlsx'))

    chemdata.insert(0, 'NAME', chemdata['SAMP_SITE_NAME_ID'].str.split('(', expand=True)[0])
    chemdata['NAME'] = chemdata['NAME'].str.strip()  ## remove hidden spaces

    # crvi = chemdata[chemdata['STD_CON_LONG_NAME'] == 'Hexavalent Chromium']
    crvi = chemdata[chemdata['STD_CON_ID'] == '18540-29-9']

    flags = ['R', 'P', 'Y', 'PQ', 'QP', 'AP', 'APQ', 'PA', 'QR']
    crvi_filt = crvi[~crvi['REVIEW_QUALIFIER'].isin(flags)]
    crvi_filt.insert(1, 'DATE', pd.to_datetime(crvi_filt['SAMP_DATE_TIME']).dt.date)

    crvi_filt.drop_duplicates(subset = ['NAME', 'DATE', 'STD_VALUE_RPTD'], inplace=True)
    crvi_filt['DATE'] = pd.to_datetime(crvi_filt['DATE'])
    crvi_filt.sort_values(by=['NAME', 'DATE'], inplace=True)

    return chemdata, crvi_filt

if __name__ == "__main__":

    wells = pd.read_csv(os.path.join(cwd, 'input', 'monitoring_wells_coords_ij.csv'))

    zone = '100D'

    odir = os.path.join(cwd, 'output', 'concentration_data', '2021to2023', f'{zone}')
    if not os.path.isdir(odir):
        os.makedirs(odir)

    chemdata, crvi_filt = read_chemdata()
    crvi_filt[['NAME', 'DATE', 'STD_VALUE_RPTD', 'STD_ANAL_UNITS_RPTD']].to_csv(os.path.join(odir, "Cr_obs_100D.csv"), index=False)
