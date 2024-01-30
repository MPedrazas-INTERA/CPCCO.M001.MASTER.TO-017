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

## Read in rebound-period observation data provided by cpcco
def read_chemdata():

    zone = '100D'

    if zone == '100H':
        data_files = glob.glob(os.path.join(wdir, 'data', 'hydrochemistry', 'H-North*.xlsx'))
        all_files = [pd.read_excel(file) for file in data_files]
        chemdata_raw = pd.concat(all_files)
        chemdata = chemdata_raw[chemdata_raw['NAME'].isin(list(wells['NAME']))]
    if zone == '100D':
        chemdata = pd.read_excel(os.path.join(wdir, 'data', 'hydrochemistry',
                                              'D-South Rebound Study Sampling_contaminantdatathru_10172023.xlsx'), engine="openpyxl")

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

def compare_data():

    """
    Use this function to compare data from different sources, e.g. data provided from client vs data downloaded
    internally vs data stored on S: for previous work
    """
#%%
    ## CrVI data from EDA downloaded from H.Pham 12/20/2023
    eda_data = pd.read_excel(os.path.join(wdir, 'data', 'hydrochemistry', 'EDA_CrVI_v122023_hp.xlsx'),
                                  parse_dates=True, engine="openpyxl")
    eda_data.insert(0, 'NAME', eda_data['SAMP_SITE_NAME_ID'].str.split('(', expand=True)[0])
    eda_data['NAME'] = eda_data['NAME'].str.strip()  ## remove hidden spaces

    ## CrVI data from EDA downloaded from M.Pedrazas Oct 2023
    eda_data2 = pd.read_excel(os.path.join(wdir, 'data', 'hydrochemistry', 'EDA_Pull_2021.xlsx'),
                                  parse_dates=True, engine="openpyxl")
    eda_data2.insert(0, 'NAME', eda_data2['SAMP_SITE_NAME_ID'].str.split('(', expand=True)[0])
    eda_data2['NAME'] = eda_data2['NAME'].str.strip()  ## remove hidden spaces

    flags = ['R', 'P', 'Y', 'PQ', 'QP', 'AP', 'APQ', 'PA', 'QR']
    eda_data = eda_data[~eda_data['REVIEW_QUALIFIER'].isin(flags)]
    eda_data.insert(1, 'DATE', pd.to_datetime(eda_data['SAMP_DATE_TIME']).dt.date)
    eda_data.drop_duplicates(subset = ['NAME', 'DATE', 'STD_VALUE_RPTD'], inplace=True)
    eda_data['DATE'] = pd.to_datetime(eda_data['DATE'])
    eda_data.sort_values(by=['NAME', 'DATE'], inplace=True)

    eda_data2 = eda_data2[~eda_data2['REVIEW_QUALIFIER'].isin(flags)]
    eda_data2.insert(1, 'DATE', pd.to_datetime(eda_data2['SAMP_DATE_TIME']).dt.date)
    eda_data2.drop_duplicates(subset = ['NAME', 'DATE', 'STD_VALUE_RPTD'], inplace=True)
    eda_data2['DATE'] = pd.to_datetime(eda_data2['DATE'])
    eda_data2.sort_values(by=['NAME', 'DATE'], inplace=True)

    # new = pd.concat([crvi_filt, eda_data, eda_data2]) #MP
    # new.drop_duplicates(inplace=True)

    return eda_data, eda_data2

def combine_data(crvi_filt, eda_data, eda_data2):

    new = pd.concat([crvi_filt, eda_data, eda_data2])
    new.drop_duplicates(inplace=True)
    new_sub = new[['NAME', 'DATE', 'STD_VALUE_RPTD',
                      'REVIEW_QUALIFIER']] #MP fix, disregard cols 'COLLECTION_PURPOSE_DESC', 'LAB_CODE' because they're not in crvi_filt
    new_sub.drop_duplicates(inplace=True)
    ## to slice only wells from rebound study dataset...
    rbd_wells = list(crvi_filt['NAME'].unique())

    new_sub = new_sub[new_sub['NAME'].isin(rbd_wells)]
    # new_sub = new_sub[new_sub['DATE'] >= '2014-01-01']

    figdir = os.path.join('output', 'qa', 'crvi_data_source_comparison', "version2")
    if not os.path.isdir(figdir):
        os.makedirs(figdir)

    for well in crvi_filt['NAME'].unique():
        fig,ax = plt.subplots()
        toplot = crvi_filt[crvi_filt['NAME'] == well]
        toplotx = eda_data[eda_data['NAME'] == well]
        toplotx2 = eda_data2[eda_data2['NAME'] == well]
        toplot_new = new_sub[new_sub['NAME'] == well]
        # toplotold = old[old['NAME'] == well]
        ax.scatter(toplotx['SAMP_DATE_TIME'], toplotx['STD_VALUE_RPTD'], label='EDA v1', s = 100)
        ax.scatter(toplotx2['SAMP_DATE_TIME'], toplotx2['STD_VALUE_RPTD'], label='EDA v2', s = 50)
        ax.scatter(toplot['SAMP_DATE_TIME'], toplot['STD_VALUE_RPTD'], label='cpcco provided', s = 40)
        ax.scatter(toplot_new['DATE'], toplot_new['STD_VALUE_RPTD'], label='combined', s = 30)
        # ax.scatter(toplotold['SAMP_DATE_TIME'], toplotold['STD_VALUE_RPTD'], label='old data')
        plt.title(f'{well}')
        plt.legend()
        # Add footnote
        plt.text(0.5, -0.1, "100HR3-Rebound\\scripts\\py13a_preprocess_chem_data.py",
                 horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, c="grey")
        plt.savefig(os.path.join(figdir, f'{well}.png'), dpi = 300)
        plt.close()

    return new_sub

if __name__ == "__main__":

    wells = pd.read_csv(os.path.join(cwd, 'input', 'monitoring_wells_coords_ij_100D.csv'))

    zone = '100D'

    odir = os.path.join(cwd, 'output', 'concentration_data', '2021to2023', f'{zone}')
    if not os.path.isdir(odir):
        os.makedirs(odir)

    chemdata, crvi_filt = read_chemdata()
    crvi_filt[['NAME', 'DATE', 'STD_VALUE_RPTD', 'STD_ANAL_UNITS_RPTD']].to_csv(os.path.join(odir, "Cr_obs_100D_mp.csv"), index=False)
    eda_data, eda_data2 = compare_data()

    new_sub = combine_data(crvi_filt,eda_data, eda_data2)

    new_sub.to_csv(os.path.join('output', 'concentration_data', '2014to2023', '100D', 'Cr_obs_2014_2023_100D_mp.csv'),
                   index = False)
