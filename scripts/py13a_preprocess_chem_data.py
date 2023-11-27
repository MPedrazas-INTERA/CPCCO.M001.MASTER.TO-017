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

    data_files = glob.glob(os.path.join(wdir, 'data', 'hydrochemistry', '*.xlsx'))
    all_files = [pd.read_excel(file) for file in data_files]

    chemdata_raw = pd.concat(all_files)

    chemdata_raw.insert(0, 'NAME', chemdata_raw['SAMP_SITE_NAME_ID'].str.split('(', expand=True)[0])
    chemdata_raw['NAME'] = chemdata_raw['NAME'].str.strip()  ## remove hidden spaces

    chemdata = chemdata_raw[chemdata_raw['NAME'].isin(list(wells['NAME']))]

    # crvi = chemdata[chemdata['STD_CON_LONG_NAME'] == 'Hexavalent Chromium']
    crvi = chemdata[chemdata['STD_CON_ID'] == '18540-29-9']

    flags = ['R', 'P', 'Y', 'PQ', 'QP', 'AP', 'APQ', 'PA', 'QR'] #what is G for 199-H3-84
    crvi_filt = crvi[~crvi['REVIEW_QUALIFIER'].isin(flags)]
    crvi_filt.insert(1, 'DATE', pd.to_datetime(crvi_filt['SAMP_DATE_TIME']).dt.date)

    crvi_filt.drop_duplicates(subset = ['NAME', 'DATE', 'STD_VALUE_RPTD'], inplace=True)
    crvi_filt['DATE'] = pd.to_datetime(crvi_filt['DATE'])
    crvi_filt.sort_values(by=['NAME', 'DATE'], inplace=True)

    return chemdata, crvi_filt

if __name__ == "__main__":

    wells = pd.read_csv(os.path.join(cwd, 'input', 'monitoring_wells_coords_ij.csv'))

    chemdata, crvi_filt = read_chemdata()
    # crvi_filt[['NAME', 'DATE', 'STD_VALUE_RPTD']].to_csv(os.path.join(cwd, "output", "concentration_data", "2021to2023", "Cr_obs_v2.csv"), index=False)
