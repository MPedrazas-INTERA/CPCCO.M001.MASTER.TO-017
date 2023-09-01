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
# output.to_csv(os.path.join(ws, 'model_files', 'tran_2014_2023', 'post_process', 'ConcTarg', 'mwell_concentrations_crvi.csv'))

ofile = os.path.join(ws, 'model_files', 'tran_2014_2023', 'post_process', 'ConcTarg', '100hr3_conc_crvi_v2.in')
with open(ofile, 'w') as fid:
    fid.write(f'#Headtarg.exe input file\n')
    fid.write(f'NTARG	{df.shape[0]}\n')
    fid.write(f'DISFILE	..\..\..\..\..\model_files\\flow_2014_2023\\100hr3.dis\n')
    fid.write(f'XOFF	571750\n')
    fid.write(f'YOFF	154830\n')
    fid.write(f'ROTATION	0\n')
    fid.write(f'CONCFILE	..\..\MT3D001.UCN\n')
    fid.write(f'CUTOFF	0.000000001\n')
    fid.write(f'LOGLIN	lin\n')
    fid.write(f'#End In\n')
    fid.write(f'# NAME	Decimal	XCOORDS	YCOORDS	MidScrElev(m)	STD_VALUE_RPTD\n')
    fid.close()

    ## mode 'a' appends to end of an existing file
    output.to_csv(ofile, mode='a', header=False, index=False, sep='\t')
