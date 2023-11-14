import os
import pandas as pd
import numpy as np
import glob
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')


gpm2m3d = (24*60)/1*231*(25.4/1000/1)**3 #

cwd = os.getcwd()
wdir = os.path.dirname(cwd)


### --- 1. Import file with well name to PLC ID for name mapping --- ###
wnames = pd.read_excel(os.path.join(cwd, 'P&T_Well_to_PLC-ID_HXDX_072023.xlsx'), index_col = 'PLC ID')
wnames.replace(['spare', 'Spare'], np.nan, inplace=True)
## take the most recent well name and store in one column
wnames['final'] = wnames.loc[:,'Well ID 2010':'Well ID 2023'].stack().groupby(level=0).last().reindex(wnames.index)
wnames['Type_short'] = 0
ext = wnames.index.str.contains('E')
wnames['Type_short'][ext] = 'E'
inj = wnames.index.str.contains('J')
wnames['Type_short'][inj] = 'I'
wnames['Well'] = wnames['final'] + '_' + wnames['Type_short'] + '_' + wnames['System']
# names = wnames[['Well', 'PLC ID']].set_index('PLC ID')['Well'].to_dict()
namesdict = wnames['Well'].to_dict()
## set values to PLC names when well name is NaN:
for k, v in namesdict.items():
    if pd.isnull(v):
        namesdict[k] = k
    else:
        pass

### --- 2. Import new well details to update wellinfo file --- ###
# wellinfo_prior = pd.read_csv(
#     os.path.join(wdir, '..', 'model_packages', 'hist_2014_2022', 'mnw2', 'wellinfodxhx_cy2014_2022.csv'),
#     header=None)
coords = pd.read_excel(
    os.path.join(wdir, 'well_info', 'Well Horizontal and Vertical Survey8-23-2023version-3.3.xlsx'),
    usecols=['WELL_NAME', 'EASTING', 'NORTHING', 'DISC_Z'], index_col='WELL_NAME')  ## in meters
screen_info = pd.read_excel(os.path.join(wdir, 'well_info',
                                         'Well Construction Interval Detail 199-D5-160 (C9542)8-23-2023version-3.3.xlsx'),
                            index_col='WELL_NAME')
## top and bottom of screen as depth from land surface
screen = screen_info[screen_info['INTERVAL_TYPE'] == 'Screen']
ztop = coords.loc['199-D5-160', 'DISC_Z'] - screen.loc['199-D5-160', 'STD_DEPTH_TOP_M']
zbot = coords.loc['199-D5-160', 'DISC_Z'] - screen.loc['199-D5-160', 'STD_DEPTH_BOTTOM_M']



### --- 3. Generate updated wellrates file: import existing and new files to combine --- ###

### Import new file with pumping volumes, resample to monthly time steps and convert to m3/day
def process_raw_data_jan_jul(ifile):

    """Process data that was provided in one spreadsheet including jan - july 2023 """

    ifile = hx23_ifile ## use for testing

    df = pd.read_csv(ifile, skiprows=1, index_col='Date', parse_dates = True, infer_datetime_format=True)
    df = df.filter(regex='Date|Volume')
    df.rename(columns=namesdict, inplace=True)
    df_m = df.resample('M').first().diff().shift(freq='-1M')
    ndays = df_m.index.to_series().diff(periods=1).dt.days
    # Convert from total gallon in a month to gpm
    for col in df_m.columns:
        df_m[col] = df_m[col] / ndays / 24 / 60

    df_m = df_m.iloc[1:]*gpm2m3d  # Convert from gpm to m3/d
    df_m[df_m.filter(like='_E_').columns] = -1*df_m[df_m.filter(like='_E_').columns]

    df_m.reset_index(inplace=True, drop=True) ## indices as stress periods
    df_m = df_m.T
    df_m.index.name = 'ID'

    return df_m

def process_raw_data_aug_oct():                 ## IN PROGRESS
    """Process data that was provided in separate spreadsheets per month"""

    import pathlib

#%%
    pumping_dict = {}
    pumping_dict_daily = {}

    files_list = glob.glob(os.path.join(cwd, '*ExportHourly*.csv'))
    for file in files_list:
        k = pathlib.PurePath(file).parts[-1].split(sep='_')[1]  ## obtain month from path to use as key
        pumping_dict[k] = pd.read_csv(file, skiprows=1, index_col='Date', parse_dates= True, infer_datetime_format=True)
        pumping_dict[k] = pumping_dict[k].filter(regex='Date|Volume')
        pumping_dict[k].rename(columns=namesdict, inplace=True)

    pumping = pd.concat(pumping_dict.values())
    pumping_m = pumping.resample('M').first().diff().shift(freq='-1M')
    diff = pumping_m.index.to_series().diff()
    days_per_month = diff.dt.days
    for row in pumping_m.index:             # Convert from total gallon in a month to gpm
        pumping_m.loc[row] = pumping_m.loc[row] / days_per_month[row] / 24 / 60

    pumping_m_m3d = pumping_m.iloc[1:]*gpm2m3d  # Convert from gpm to m3/d
    pumping_m_m3d[pumping_m_m3d.filter(like='_E_').columns] = -1*pumping_m_m3d[pumping_m_m3d.filter(like='_E_').columns]

    pumping_m_m3d.reset_index(inplace=True, drop=True)
    pumping_T = pumping_m_m3d.T
    pumping_T.index.name = 'ID'


#%%

    return None



if __name__ == "__main__":


    ### Import existing wellrates
    wrates_prior = pd.read_csv(
        os.path.join(wdir, '..', 'model_packages', 'hist_2014_2022', 'mnw2', 'wellratedxhx_cy2014_2022.csv'),
        index_col='ID')

    ## first data dump pumping files -- cover january to early august 2023
    hx23_ifile = os.path.join(wdir, 'pumping', 'HX_Totals_2023.csv')
    dx23_ifile = os.path.join(wdir, 'pumping', 'DX_Totals_2023.csv')

    hx23 = process_raw_data_jan_jul(hx23_ifile)
    dx23 = process_raw_data_jan_jul(dx23_ifile)

    hxdx23 = pd.concat([hx23, dx23])


    ## updated well rates file
    wrates = wrates_prior.join(hxdx23, how = 'outer')
    wrates_d = wrates[~wrates.index.duplicated(keep='first')] ## drop rows with duplicate indices
    wrates_d.columns = list(range(1,len(wrates.columns)+1)) ##column headers correspond to stress periods

    ## investigate missing well names
    # ## MJ15 is a recirculation well!! HJ25 can be ignored.
    ## cpcco: "There is no well hooked up to HJ25... ignore that column with data for HJ25 and don't include it"
    missing = wrates_d.filter(like = 'FIT', axis=0)
    ## once all questions on missing wells are answered, treat accordingly. In this case, we can drop.
    wrates_d.drop(missing.index, inplace=True)
    wrates_d.replace(np.nan, 0, inplace=True)

    ## write wellrates output for allocateqwell
    #wrates_d.to_csv(os.path.join(wdir, '..', 'model_packages', 'hist_2014_2023', 'mnw2', 'wellratesdxhx_cy2014_jul2023_v02.csv'))



    ### --- QC --- ###

    # prior = list(wrates_prior.index)
    # new = list(hxdx23.index)
    #
    # t = [x for x in prior if x not in new] ## wells in prior wellrates db that are not present in new data
    # t2 = [x for x in new if x not in prior] ## wells/IDs in new data that are not present in prior wellrates data