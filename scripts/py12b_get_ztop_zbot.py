"""
Script to get ztop and zbot for new wells, to be added to wellinfo file

@rweatherl
04/11/2023: hp added more unconfined wells in 100-D for sce3

"""

import os
import glob
import pandas as pd

cwd = os.getcwd()
ws = os.path.join(os.path.dirname(cwd))

output = os.path.join(cwd, 'output', 'wellinfo')


## current/existing well info
cwells = pd.read_csv(os.path.join(ws, 'model_packages', 'pred_2023_2125', 'mnw2', 'wellinfodxhx_cy2023_2125.csv'), skiprows = [0,2]) #, index_col = 0)
cwells.index = cwells['NAME'].str.split('_').str[0]

## list of RUM wells existing + new
rumwells = pd.read_csv(os.path.join(ws, 'data', 'listRUM2_wells', 'List_of_RUM2_Wells_and_beyond.csv'), index_col = 0)

##information on well screens
wscreens = glob.glob(os.path.join(ws, 'data', 'EDA_wellinfo', '*.csv'))
screens_dfs = []
for i in wscreens:
    temp_df = pd.read_csv(i, index_col = 0)
    screens_dfs.append(temp_df)
sc1, sc2 = screens_dfs[0], screens_dfs[1]
df_sc = sc1.join(sc2, how = 'outer', lsuffix = '_L')

##calculate Ztop and Zbot
rum_sc = rumwells.join(df_sc, how = 'outer')
rum_sc['Ztop'] = rum_sc['DISC_Z'] - rum_sc['STD_SCREEN_DEPTH_TOP_M']
rum_sc['Zbot'] = rum_sc['DISC_Z'] - rum_sc['STD_SCREEN_DEPTH_BOTTOM_M']
rum_sc['XW'], rum_sc['YW'] = rum_sc['EASTING'], rum_sc['NORTHING']

##combine with cwells to include new rum wells with associated info
new_rum = cwells.join(rum_sc, how = 'outer', rsuffix = '_new')
new_rum['XW'].fillna(new_rum['XW_new'], inplace = True)
new_rum['YW'].fillna(new_rum['YW_new'], inplace = True)
new_rum['Ztop'].fillna(new_rum['Ztop_new'], inplace = True)
new_rum['Zbot'].fillna(new_rum['Zbot_new'], inplace = True)

numwells = len(new_rum)

#new_rum.loc[:,:'ISTRTSP'].to_csv(os.path.join(output, 'wellinfodxhx_cy2023_2125_v040423.csv'))
new_rum.loc[:,:'ISTRTSP'].to_csv(os.path.join(output, 'wellinfodxhx_cy2023_2125_v041123.csv'))

# after this, copy the missing well screen elevations to scripts/input/wellinfo_database.csv

