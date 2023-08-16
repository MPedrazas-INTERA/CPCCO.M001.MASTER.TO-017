import pandas as pd 
'''
hpham@intera.com, 02/15/2023
Resample daily rs to monthly rs

'''
import os

# wdir = f'c:/Users/hpham/Documents/100HR3/scripts/download_river_stage/'
cwd = os.getcwd()
wdir = os.path.join(cwd, 'river_stage_cal_v020823_sspa')


# list_files = ['RiverStage_at_gauges_for_100HR3_modeling_v021423_default.csv',
#               'RiverStage_at_gauges_for_100HR3_modeling_v021523_MPR.csv',
#               'RiverStage_at_gauges_for_100HR3_modeling_v021523_100APT.csv']
list_files = ['RiverStage_05092022_15min_hp_check.csv']
for ifile in list_files:
    #ifile = f'{wdir}/RiverStage_at_gauges_for_100HR3_modeling_v021523_100APT.csv'
    print(ifile)
    ifile=f'{wdir}/{ifile}'
    ofile = ifile.split('.')[0] + '_mo.csv'

    df=pd.read_csv(ifile)
    df['EVENT'] = pd.to_datetime(df['EVENT'])
    df2=df.copy()

    df3 = df.resample('M', on='EVENT').mean()
    # df3.to_csv(ofile)

##snip to calibration period
# calib = df3.loc['2014-01-01':'2022-12-31']
# calib.to_excel(os.path.join(cwd, 'output', 'riv_ghb_central_tendencies', 'RiverStage_monthly.xlsx'))