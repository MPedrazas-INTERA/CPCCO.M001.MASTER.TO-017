"""
Smoothing EDA Cr VI Observations by quarters or model SPs for PEST

@author: MPedrazas
"""
import pandas as pd;
import os;
from datetime import datetime, date, time
import numpy as np

def filter_Cr_data(database, input_wells, output_dir):
    # [1] Get columns of interest:
    df_Cr_comments = database[['SAMP_SITE_NAME', 'SAMP_DATE_TIME','STD_VALUE_RPTD',
                'STD_ANAL_UNITS_RPTD','FILTERED_FLAG', 'LAB_QUALIFIER',
                'REVIEW_QUALIFIER','SAMP_COMMENT', 'RESULT_COMMENT','COLLECTION_PURPOSE_DESC']].copy()
    df_Cr = database[['SAMP_SITE_NAME', 'SAMP_DATE_TIME','STD_VALUE_RPTD',
                      'REVIEW_QUALIFIER','COLLECTION_PURPOSE_DESC', 'LAB_CODE']].copy()
    df_Cr['SAMP_DATE_TIME'] = pd.to_datetime(df_Cr['SAMP_DATE_TIME'])
    df_Cr['SAMP_DATE'] = df_Cr['SAMP_DATE_TIME'].dt.date

    # [2] Filter out data outside of model temporal extent:
    df_Cr = df_Cr.loc[(df_Cr['SAMP_DATE_TIME'] <= datetime(2021, 10, 11))]
    df_Cr = df_Cr.loc[(df_Cr['SAMP_DATE_TIME'] >= datetime(2014, 1, 1))]

    # [3] Filter out flagged data:
    flags = ['R','P', 'R','Y','PQ' ,'QP','AP','APQ','PA','QR'] #flag H is no longer a filter 09/13/2021
    flagged_data = df_Cr.loc[(df_Cr['REVIEW_QUALIFIER'].isin(flags))] #drop datapoints with any flag
    for f in flags:
        df_Cr = df_Cr.loc[(df_Cr['REVIEW_QUALIFIER'] != f)] #drop datapoints with any flag
    df_Cr = df_Cr.loc[(df_Cr['COLLECTION_PURPOSE_DESC'] != 'Characterization')] #drop datapoints used for characterization
    df_Cr = df_Cr.loc[(df_Cr['LAB_CODE'] != 'Field')]  # drop datapoints with LAB_CODE Field

    # [4] Check data is from wells of interest:
    wells = input_wells.NAME.to_list()
    df_Cr = df_Cr.loc[df_Cr['SAMP_SITE_NAME'].isin(wells)]


    # [5] Make sure there aren't wells without data in model's temporal extent:
    lst = []
    for i, well in enumerate(wells):
        df = df_Cr[df_Cr['SAMP_SITE_NAME'] == well]
        if len(df['STD_VALUE_RPTD']) == 0:
            print("This well doesn't have data in time period of interest:\n ", well)
            lst.append(well)
    for i in lst: #drop wells without data in model time period:
        df_Cr = df_Cr.loc[(df_Cr['SAMP_SITE_NAME'] != i)]

    # [6] Export data
    fname = 'Cr_obs_all.csv'
    df_Cr.to_csv(os.path.join(output_dir, fname), index=False)
    print(f"Saved: {os.path.join(output_dir, fname)}")
    wells = list(df_Cr.SAMP_SITE_NAME.unique())

    # [7] Average repetitive observations from the same day:
    df_Cr2 = df_Cr.copy()
    df_Cr2['Time'] = pd.to_datetime(0, format='%H')
    df_Cr2['Time'] = df_Cr2['Time'].dt.time
    df_Cr2['SAMP_DATE'] = pd.to_datetime(df_Cr2['SAMP_DATE'])
    df_Cr2['SAMP_DATE'] = df_Cr2['SAMP_DATE'].dt.date
    dates = df_Cr2['SAMP_DATE']; times = df_Cr2['Time']
    datetimes = pd.to_datetime(dates.astype(str)+ ' ' + times.astype(str))
    df_Cr2['Datetime'] = datetimes
    df_Cr2['Datetime'] = pd.to_datetime(datetimes)

    lst_dups =[]
    for i, well in enumerate(wells):
        df = df_Cr2.loc[df_Cr2['SAMP_SITE_NAME'] == well]
        dups = df.duplicated(subset=['Datetime'], keep=False)
        dups = dups.to_frame()
        lst_dups.append(dups)
    df_dups = pd.concat(lst_dups, axis=0)
    df_dups = df_dups[df_dups[0] ==True]

    df_Cr_dups = df_Cr2.copy()
    df_Cr_dups =df_Cr_dups[df_Cr_dups.index.isin(df_dups.index)]

    # Find average for same-day duplicates:
    date_lst, well_lst,conc_lst = [],[],[]
    for well in wells:
        df = df_Cr_dups[df_Cr_dups['SAMP_SITE_NAME'] == well]
        for date in df['Datetime'].unique():
            df2 = df[df['Datetime'] == date]
            date_lst.append(date)
            conc_lst.append(df2['STD_VALUE_RPTD'].mean())
            well_lst.append(well)
    df_dups_avg = pd.DataFrame({'SAMP_SITE_NAME': well_lst,'SAMP_DATE': date_lst,'STD_VALUE_RPTD': conc_lst})

    df_Cr_no_dups = df_Cr.drop(axis=0, index=df_Cr_dups.index, inplace=False)
    df_Cr_w_avg_dups = df_Cr_no_dups.append(df_dups_avg)
    df_Cr_w_avg_dups = df_Cr_w_avg_dups[df_Cr_w_avg_dups['SAMP_SITE_NAME'].isin(wells)]
    df_Cr_w_avg_dups = df_Cr_w_avg_dups[['SAMP_SITE_NAME','SAMP_DATE','STD_VALUE_RPTD']]
    fname = 'Cr_obs_avg_dups.csv'
    df_Cr_w_avg_dups.to_csv(os.path.join(output_dir, fname), index=False)
    print(f"Saved: {os.path.join(output_dir, fname)}")
    return df_Cr

def average_bySPs(input_dir, output_dir, model_time):
    ###[Step 1]: Import observations
    fname = 'Cr_obs_avg_dups.csv' #Cr obs with averaged same-day duplicates
    dfObs = pd.read_csv(os.path.join(output_dir, fname))
    dfObs['SAMP_DATE'] = pd.to_datetime(dfObs['SAMP_DATE'])

    ### [Step 2]: Import SP times to use for average
    df_times = pd.read_csv(os.path.join(input_dir, f'sp_{model_time}.csv'))  # print times
    df_times.date = pd.to_datetime(df_times.date)
    # df_times["End Date"] = df_times.date + pd.Timedelta(days = df_times.days) #didnt work so I will instead add days to each SP in loop

    ### [Step 5]: Average observations by SPs:
    date_lst, well_lst, conc_lst, tte_lst = [], [], [],[]
    for well in dfObs['SAMP_SITE_NAME'].unique(): #['199-D5-34']
        oneWellataTime = dfObs[dfObs['SAMP_SITE_NAME'] == well]
        for i, sp in enumerate(df_times.date): #loop through SPs
            oneSPataTime = oneWellataTime.loc[(oneWellataTime['SAMP_DATE'] < sp + pd.Timedelta(days = df_times.days.iloc[i])) &
                                              (oneWellataTime['SAMP_DATE'] >= sp)]
            date_lst.append(sp)
            conc_lst.append(oneSPataTime['STD_VALUE_RPTD'].mean())
            well_lst.append(well)
            tte_lst.append(df_times.tte.iloc[i])
    df_sp_avg = pd.DataFrame({'SAMP_SITE_NAME': well_lst, 'SAMP_DATE': date_lst, 'STD_VALUE_RPTD': conc_lst, "tte": tte_lst})
    df_sp_avg.dropna(axis = 0, subset=["STD_VALUE_RPTD"], inplace=True)

    ### [Step 4:]: Export observations averaged by SP
    fname = 'Cr_obs_avg_bySPs.csv'
    df_sp_avg.to_csv(os.path.join(output_dir, fname), index=False)
    print(f"Saved: {os.path.join(output_dir, fname)}")


if __name__ == "__main__":
    cwd = os.getcwd()
    input_dir = os.path.join(cwd, 'input')
    output_dir = os.path.join(cwd, 'output', 'concentration_data')
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    model_time = '2014_2020'

    input_wells = pd.read_csv(os.path.join(cwd, 'output', 'well_info', 'monitoring_wells_coords_ij.csv'), delimiter=",")
    # EDA_conc_database = pd.read_excel(os.path.join(cwd,'input', 'concentration_data','EDA_Pull_2021.xlsx'), skiprows=0, engine='openpyxl')
    EDA_conc_database = pd.read_excel(os.path.join(os.path.dirname(cwd), 'data', 'hydrochemistry', 'EDA_Pull_2021.xlsx'),
                                      skiprows=0, engine='openpyxl')
    df_Cr = filter_Cr_data(EDA_conc_database, input_wells, output_dir)

    average_bySPs(input_dir, output_dir, model_time)
