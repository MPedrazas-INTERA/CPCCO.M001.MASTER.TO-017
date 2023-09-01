import numpy as np
import os
import flopy.utils.binaryfile as bf
import pandas as pd
import matplotlib.pyplot as plt
import flopy
import geopandas as gpd
import matplotlib
matplotlib.use('Qt5Agg')


cwd =os.getcwd()
ws = os.path.dirname(cwd)

## import wells and ijk coords
wells = pd.read_csv(os.path.join(cwd, 'output', 'well_info', 'monitoringwells_xyz_ijk.csv')) #, index_col = 'NAME')
wells['MidScrElev(m)'] = (wells['Ztop'] + wells['Zbot'])/2

## import measured data
chemfile = os.path.join(os.path.dirname(cwd), 'data', 'hydrochemistry', 'H-North Rebound Study Sampling_DATA.xlsx')
chemdata_raw = pd.read_excel(chemfile)
chemdata_raw.insert(0, 'NAME', chemdata_raw['SAMP_SITE_NAME_ID'].str.split('(', expand=True)[0])
chemdata_raw['NAME'] = chemdata_raw['NAME'].str.strip()  ## remove hidden spaces

chemdata = chemdata_raw[chemdata_raw['NAME'].isin(list(wells['NAME']))]

crvi = chemdata[chemdata['STD_CON_LONG_NAME'] == 'Hexavalent Chromium']

flags = ['R', 'P', 'Y', 'PQ', 'QP', 'AP', 'APQ', 'PA', 'QR']
crvi_filt = crvi[~crvi['REVIEW_QUALIFIER'].isin(flags)][['NAME', 'SAMP_DATE_TIME', 'STD_VALUE_RPTD']] ## CrVI reported in ug/L

df = pd.merge(crvi_filt, wells, on = 'NAME')[['NAME', 'SAMP_DATE_TIME', 'XCOORDS', 'YCOORDS', 'MidScrElev(m)', 'STD_VALUE_RPTD']]
df.sort_values(by='SAMP_DATE_TIME', ascending=True, inplace=True)

start = pd.Timestamp('2014-01-01 00:00:00')

df['Decimal'] = (df['SAMP_DATE_TIME'] - start).dt.total_seconds()/(24*60*60)

output = df[['NAME', 'Decimal', 'XCOORDS', 'YCOORDS', 'MidScrElev(m)', 'STD_VALUE_RPTD']]
output.to_csv(os.path.join(ws, 'model_files', 'tran_2014_2023', 'post_process', 'ConcTarg', 'mwell_concentrations_crvi.csv'))