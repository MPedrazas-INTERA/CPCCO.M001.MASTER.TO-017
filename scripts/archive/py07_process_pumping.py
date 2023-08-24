import os
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from datetime import date

'''
hpham@intera.com
Read in volume pumping data (provided by sspa),convert to gpm, and format to match 
the input requrement of allocateqwell.exe

Two output files are wellrate_xxx.csv and wellinfo_xxx.csv. Two files are needed for allocateqwell.exe
Last check: 03/17/2023

- Prepare predictive scenarios and generate MNW2 package for the 2023-2125 flow model

'''

def gen_well_info_database(): # jUst need to run once
    ifile_wellinfo = os.path.join(wdir,'scripts','input','tmp','wellinfodxhx.csv')        
    dfwellinfo = pd.read_csv(ifile_wellinfo, skiprows=[0,2])
    dfwellinfo['wname'] = dfwellinfo['NAME'].str.split('_', 2, expand=True)[0]
    dfwellinfo['Type'] = dfwellinfo['NAME'].str.split('_', 2, expand=True)[1]
    dfwellinfo['System'] = dfwellinfo['NAME'].str.split('_', 2, expand=True)[2]
    dfwellinfo=dfwellinfo.drop(columns=['NAME'])
    dfwellinfo=dfwellinfo.drop_duplicates(subset=['wname'])
    ofile = os.path.join(wdir,'scripts','input','wellinfo_database.csv')
    #dfwellinfo.to_csv(ofile, index=False)

def gen_well_info_csv_file(df_new_rate, ofile):
    ifile_wellinfo=os.path.join(wdir,'scripts','input','wellinfo_database.csv')
    dftmp1 = pd.read_csv(ifile_wellinfo)
    dftmp1['Type'] = 'E'
    dftmp2 = dftmp1.copy()
    dftmp2['Type'] = 'I'
    dfwellinfo = pd.concat([dftmp1, dftmp2], axis=0)
    dfwellinfo['NAME'] = dfwellinfo['wname'] + "_" + dfwellinfo['Type'].astype(str) + "_" + dfwellinfo['System'].astype(str)

    list_wells = list(df_new_rate['ID'].unique())
    df_new_rate['NAME'] = df_new_rate['ID'].copy()
    
    #df2.columns
    # merge df2 (all wells with rates) with existing df wellinfo 
    df3 = pd.merge(df_new_rate['NAME'],dfwellinfo, how='left', on=['NAME'])
    df3.columns
    sel_col  = ['NAME', 'XW', 'YW', 'NNODES', 'LOSSTYPE', 'PUMPLOC', 'Qlimit', 'PPFLAG', 'PUMPCAP', 'ScrnCorrFac', 'Ztop', 'Zbot', 'Rw', 'Group', 'ISTRTSP']
    df3=df3[sel_col]



    # Add three heading row
    df3.loc[-1] = ''
    df3.loc[-2] = df3.columns
    df3.loc[-3] = '' 
    df3.index = df3.index + 3  # shifting index
    df3 = df3.sort_index()  # sorting by index
    df3['NAME'].loc[0] = df3.shape[0]-3
    df3['XW'].loc[0] = 0
    
    # Write to file
    #ofile = os.path.join(wdir,'model_packages','hist_2014_2021','mnw2','wellinfodxhx_cy2014_2022.csv')
    df3.to_csv(ofile, header=False, index=False)



    print(f'Saved {ofile}\n')
    
    #check
    #df_check = df3[df3['XW'].isnull()]
    #df_check.NAME
    #print(df_check)
    return df3

def gen_calib_wellrate_csv_file(df2,df_prv_rate,ofile):
    cur_col = list(df2.columns)
    new_col = ['ID'] + list(range(last_prv_sp+1,last_prv_sp+n_new_sp+1,1))
    dict_col_name = dict(zip(cur_col, new_col))
    df2=df2.rename(columns=dict_col_name)    

    # Merge with the well rate file before 2021
    
    df_new_rate = pd.merge(df_prv_rate, df2, how='outer', on=['ID'])
    df_new_rate=df_new_rate.fillna(0)
    #ofile = os.path.join(wdir,'model_packages','hist_2014_2021','mnw2','wellratedxhx_cy2014_2022.csv')
    df_new_rate.to_csv(ofile, index=False)  
    print(f'Saved {ofile}\n')  
    return df_new_rate

def gen_pred_wellrate_csv_file(dfpred,npred_sp_with_pmp,ofile):
    cur_col = list(dfpred.columns)
    new_col = ['ID'] + list(range(1,nmonths,1))
    dict_col_name = dict(zip(cur_col, new_col))
    dfpred=dfpred.rename(columns=dict_col_name)
    df_mean_pmp_rate = dfpred[range(12+1,nmonths,1)].mean(axis=1)
    #for i in range(nmonths-1, npred_sp_with_pmp+1,1): # for NFA
    for i in range(nmonths, npred_sp_with_pmp+1,1):  # for cy2023 cal   
        dfpred[i] = df_mean_pmp_rate.copy()
    for i in range(npred_sp_with_pmp+1,npred_sp_total+1, 1):
        dfpred[i] = 0

    # Merge with the well rate file before 2021   
    #df_new_rate = pd.merge(df_prv_rate, dfpred, how='outer', on=['ID'])
    #df_new_rate=df_new_rate.fillna(0)
    #ofile = os.path.join(wdir,'model_packages','hist_2014_2021','mnw2','wellratedxhx_cy2014_2022.csv')
    dfpred.to_csv(ofile, index=False)  
    print(f'Saved {ofile}\n')  
    return dfpred

def check_cal(df):
    ifilecheck = os.path.join(wdir,'model_packages','hist_2014_2021','mnw2','wellratedxhx_2125.csv')
    dfcheck=read_welrate_csv(ifilecheck)

    ifilecheck = os.path.join(wdir,'model_packages','hist_2014_2021','mnw2','wellrate_updated_2021_v081922.csv')
    df100apt=read_welrate_csv(ifilecheck)
    df100apt=df100apt[['ID'] + list(range(181,192+1,1))]
    col100apt = dict(zip(range(181,192+1,1), range(1,12+1,1)))
    df100apt=df100apt.rename(columns=col100apt)

    list_wells = dfcheck['ID'].unique()
    col=list(range(1,12+1,1))
    for wel in list_wells:
        df1 = df[col][df['wname2']==wel]
        df2 = dfcheck[col][dfcheck['ID']==wel]
        df3 = df100apt[col][df100apt['ID']==wel]
        df4plt = pd.concat([df1, df2, df3])
        if df4plt.shape[0] >2:
            df4plt=df4plt.reset_index(drop=True)
            df4plt.index = ["hp's cal", "rw_mp's cal", "100APT's cal"]
            # Plot
            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
            df4plt.T.plot(ax=ax, style=['-o', ':x','--*'], alpha=0.6)
            ax.grid(axis='both', alpha=0.2)
            ax.set_title(f'Well: {wel}')
            ofile = f'output/png/check_{wel}.png'
            fig.savefig(ofile, dpi=300, transparent=False, bbox_inches='tight')
            print(f'Saved {ofile}\n')



def process_pmp(wdir,sys, list_yr,opt_plot_for_checking):
    df = pd.DataFrame()        
    for yr in list_yr:
        ifile = os.path.join(wdir, f'{sys}_Totals_{yr}.csv')
        #dict_wname = dict(zip(dfwname['HMI'], dfwname[f'Well ID {yr}']))
        df_tmp = pd.read_csv(ifile, skiprows=1,index_col='Date')        
        df_tmp = df_tmp.filter(regex='Date|Volume')
        df_tmp.columns = df_tmp.columns.str.replace('[FIT,_,Volume]', '', regex=True)
        #df_tmp.fillna(0, inplace=True)
        #print(df_tmp)
        df = pd.concat([df, df_tmp], axis=0)
        #df['System'] = sys

    #

    df2 = df.copy()
    df2.index = pd.to_datetime(df2.index)
    df2=df2.sort_index(ascending=True)
    df2.columns
    #df2_tmp = df2.filter(regex='E|I')

    # plot for checking
    #opt_plot_for_checking = False
    if opt_plot_for_checking:
        list_wells =list(df2.columns)
        for wel in list_wells:
            fig, ax = plt.subplots(1, 1, figsize=(20, 10),dpi=300)
            df2.plot(ax=ax, y=wel)
            #df2.plot(y=wel)
            #df2[wel]
            ax.set_title(f'Well: {wel}')
            ax.set_ylabel('Volume (gallons)')
            ax.grid(axis='both', alpha=0.2)
            ofile =f'output/png_check_vol/vol_{wel}.png'
            fig.savefig(ofile, dpi=300, transparent=False, bbox_inches='tight')
            print(f'Saved {ofile}\n')

    # 
    if sys=='HX': # Special processing for HE15
        #df2['HE15_copy'] = df2['HE15'].copy()
        df2['HE15_after_Aug22'] = df2['HE15'].copy()
        df2=df2.rename(columns={'HE15':'HE15_before_Aug22'})        
        df2['HE15_after_Aug22'][df2.index < pd.to_datetime(date(2022,7,31))] = np.nan
        #df2['HE15_before_Aug22'][df2.index >= pd.to_datetime(date(2022, 8, 1))] = 0
        #df2['HE15_after_Aug22'].plot()
        #df2['HE15_before_Aug22'].plot()
        df2['HE15_before_Aug22_diff']=df2['HE15_before_Aug22'].diff().shift(-1)
        df2['HE15_before_Aug22_diff'][df2.index < pd.to_datetime(date(2022,7,22))]=0
        df2['HE15_before_Aug22_diff'][df2.index > pd.to_datetime(date(2022,7,30))]=0
        
        df2['HE15_before_Aug22'][df2.index > pd.to_datetime(date(2022,7,21))] = \
              df2['HE15_before_Aug22'][df2.index == pd.to_datetime(date(2022,7,21))][0]

        df2['HE15_before_Aug22'][df2.index > pd.to_datetime(date(2022,7,30))] = np.nan
        df2['HE15_before_Aug22']=df2['HE15_before_Aug22']+df2['HE15_before_Aug22_diff']
        df2.to_csv('tmp.csv')



    df3 = df2.resample('M').first().diff().shift(freq='-1M') # monthly    
    #df3.columns = df3.columns.str.replace('[FIT,_,Volume]', '', regex=True)

    ndays = df3.index.to_series().diff(periods=1).dt.days
    #ndays.index
    #df3.index[0]

    # Convert from total gallon in a month to gpm
    for col in df3.columns:
        df3[col] = df3[col]/ndays/24/60
        
    #     
    
    df3=df3*gpmtom3d # Convert from gpm to m3/d
    #df3.rename(index={df3.index[0]:'HMI'}, inplace=True) # 1st row only
    #df3.iloc[0,:] = df3.columns # Copy eng wname to the first row
    #df3=df3.rename(columns=dict_wname) # HMI -> regular well name

    #df3=df3.reset_index()
    #print(df3.index)
    nmonths = df3.shape[0]
    df3=df3.iloc[1:] # remove the first row

    df3 = df3.T
    #df3.columns
    #df3.index
    #df3['HMI'] = df3.index
    df3=df3.reset_index()

    df3 = df3.rename(columns={'index':'NAME', 0:'HMI'})
    
    
    list_cols = list(df3.columns)
    list_cols.remove('NAME')

    df3['Type'] = ''
    flag = df3['NAME'].str.contains('E')    
    df3['Type'][flag] = 'E'
    for col in list_cols:
        df3[col][flag] = (-1)*df3[col][flag] # negative rate for ext wells

    flag = df3['NAME'].str.contains('J')
    df3['Type'][flag] = 'I'
    df3['System'] = sys
    

    # Save temporal data    
    #df3.to_csv(f'output/temp_wellrate_2022_{sys}.csv')    
    df3.fillna(0, inplace=True)
    
    return df3, nmonths

def read_welrate_csv(ifilecheck):
    dfcheck = pd.read_csv(ifilecheck)
    dfcheck_col = list(dfcheck.columns)
    dfcheck_col.remove('ID')
    dict_col = dict(zip(dfcheck_col, range(1,len(dfcheck_col)+1,1)))
    dfcheck=dfcheck.rename(columns=dict_col)
    return dfcheck



if __name__ == "__main__":
    #wdir = os.path.join('..', 'received_030323')    
    wdir = f'c:/Users/hpham/Documents/100HR3/'
    
    ifile_wname = os.path.join(wdir,'data','pumping','received_030723', 'P&T_Well_to_PLC-ID.csv')
    dfwel = pd.read_csv(os.path.join(wdir,'gis','csv','Coords_all_Hanford_wells.csv'))
    ifile_prev_wellrate = os.path.join(wdir,'scripts','input','tmp','wellratedxhx.csv')        
    min_rate, max_rate = -5e-3, 5e-3 # ignore small rates (m3/d)
    pred_pmp_start, pred_pmp_stop, pred_stop = '1/1/2021', '12/31/2032', '12/31/2125'
    
    last_prv_sp = 84 # of the calibrated model
    n_new_sp = 24 # 2 years, 2021 and 2022 (for calib model)
    gpmtom3d = (24*60)/1*231*(25.4/1000/1)**3 # 
    list_yr = [2021, 2022, 2023]
    list_systems = ['DX', 'HX']

    # = [00] read in some files ===============================================
    df_prv_rate = pd.read_csv(ifile_prev_wellrate)
    # some preprocessing
    npred_sp_with_pmp = len(pd.date_range(start=pred_pmp_start, end=pred_pmp_stop, freq='M'))
    #npred_sp_total = len(pd.date_range(start=pred_pmp_start, end=pred_stop, freq='M'))
    npred_sp_total = 598+24

    # [01] Generate well info database, Just need to run once to get input/wellinfo_database.csv
    #gen_well_info_database() 

    # [02] ====================================================================
    #list_systems = ['HX']
    # Get diction of well name
    dfwname = pd.read_csv(ifile_wname)
    dfwname.columns
    #dfwname2=dfwname[dfwname['PLC Well'].str.lower()!='spare']    
    #wname2021 = dict(zip(dfwname['HMI'], dfwname['Well ID 2021']))
    #wname2022 = dict(zip(dfwname['HMI'], dfwname['Well ID 2022']))

    # Read in pumping/injectin vol for DX and HX systems
    #sys = 'DX'
    plot_vol=False
    wdir2=os.path.join(wdir, 'data','pumping','received_030323',)
    dx,nmonths = process_pmp(wdir2,'DX', list_yr,plot_vol)
    hx,nmonths = process_pmp(wdir2,'HX', list_yr,plot_vol)
    #hx=hx.iloc[1:]
        
    df = pd.concat([dx, hx], axis=0)

    df=df.reset_index(drop=True)

    #df.drop(columns=df.columns[1], axis=1,inplace=True)
    
    # Rename Engineering well name to well name
    cur_col = list(df.columns)
    cur_col.remove('NAME')
    cur_col.remove('Type')
    cur_col.remove('System')
    col_name=[]
    for i, col in enumerate(cur_col):
        col_name.append(f'SP{i+last_prv_sp+1}_{str(col.year)}_{str(col.month)}')
    dic_col_name = dict(zip(cur_col, col_name))
    
    # Rename df
    df=df.rename(columns=dic_col_name)
    df['HMI'] = df['NAME'].copy()

    len(col_name)

    # Get dataframe for a given year
    #df_final = pd.DataFrame()
    for i, yr in enumerate(list_yr):        
        df2 = df.filter(regex=f"NAME|HMI|Type|System|{yr}")
        dict_wname = dict(zip(dfwname['HMI'], dfwname[f'Well ID {yr}']))
        df2['NAME']= df2['NAME'].replace(dict_wname)
        #df2.to_csv(f'output/check_pmp_rate_{yr}.csv')
        
        if i==0:
            df3 =df2.copy()
        else:
            df2=df2.drop(columns=['HMI'])
            df3 = pd.merge(df3, df2,how='outer', on=['NAME','Type','System'])
    # save to file 
    # Next, remove some wells
    df3=df3[df3['NAME']!='MJ15'] # caustic recirc line so volume reported is not effluent injection
    df3=df3[df3['NAME']!='HJ25'] # Instruction from Sylvana to not include this well. Email 03/08/2023
    df3.fillna(0, inplace=True)
    
    #df.to_csv(f'output/check_pmp_rate_all_yrs.csv')
    df=df3.copy()
    
    df['NAME2'] = df['NAME'].astype(str) + "_" + df['Type'].astype(str) + "_" + df['System'].astype(str)
    df=pd.merge(df, dfwel, how='left', on='NAME')
    df['Active'] = 1
    col = range(1,nmonths,1)
    
    df[col_name].iloc[1:] = df[col_name].iloc[1:].astype(float)
    
    df[col_name].fillna(0, inplace=True)
    #df['Sum']=0
    #df['Sum'].iloc[1:] = df[col_name].iloc[1:].sum(axis=1)
    df['Sum'] = df[col_name].sum(axis=1)
    df['Active'][df['Sum']==0] = 0
    #df=pd.merge(df, dfwname, how='left', on=['HMI','System'])
    df.columns   



    # 
    col1 = ['NAME2','NAME','HMI','Type','System', 'XCOORDS', 'YCOORDS', 'ZCOORDS', 'Active']
    df=df[col1+col_name]
    # Save for checking
    df.to_csv(f'output/processed_wellrate_DX_HX_to_Feb2023_all_fields_4checking.csv', index=False)
    dfgpm = df.copy()
    dfgpm[col_name] = dfgpm[col_name]/gpmtom3d
    dfgpm['avg']=dfgpm[col_name].mean(axis=1)
    dfgpm.to_csv(f'output/processed_wellrate_DX_HX_to_Feb2023_all_fields_4checking_gpm.csv', index=False)

    
    # export to file wellrate_xxx.csv
    #
    df2 = df[df['Active']==1]

    dfplot = df2.copy()
    dfplot2=dfplot.groupby(['Type','System']).sum()
    dfplot2=dfplot2.reset_index()
    dfplot2= dfplot2.T
    dfplot2=dfplot2.rename(columns={0:'E_DX',1:'E_HX',2:'I_DX',3:'I_HX'})
    dfplot2 = dfplot2.iloc[7:]
    dfplot2['E_DX'] = dfplot2['E_DX']*(-1)
    dfplot2['E_HX'] = dfplot2['E_HX']*(-1)
    
    # Plot for checking
    fig, ax = plt.subplots(1, 1, figsize=(20, 10),dpi=300)
    dfplot2.plot(ax=ax, figsize=(20,10), style=['-o','-x',':s',':d'])
    ax.set_ylabel('Absolute Flow Rates (m3/d)')
    ax.grid(axis='both', alpha=0.2)
    fig.savefig('test.png', dpi=300, transparent=False, bbox_inches='tight')



    col1 = ['NAME2']
    df2=df2[col1+col_name]
    for col in col_name:
        #flag = df2[col].astype(float).isin([min_rate, max_rate])
        flag = (df2[col]<max_rate) & (df2[col]>min_rate)
        df2[col][flag] = 0
        #df2[col][(df2[col]<5e-3) & (df2[col]>-5e-3)] = 0
        #print(df2[col][df2[col]>0].describe())
        #df2[col].plot.hist(bins=100)
    dfNFA = df2.copy()

    
    # =========================================================================
    # = [03] CALIBRATED MODEL =================================================
    # =========================================================================
    # Generate wellrate for the CALIBRATED 2014-2022 model ===========================
    ofile = os.path.join(wdir,'model_packages','hist_2014_2021','mnw2','wellratedxhx_cy2014_2022_check.csv')
    dfcalib=df2.filter(regex='NAME2|2021|2022') # Choose data in 2021-2022 only
    dfrate_2014_2022=gen_calib_wellrate_csv_file(dfcalib,df_prv_rate,ofile)
    dfrate_2014_2022.to_csv(f'output/processed_wellrate_DX_HX_2006_2023.csv', index=False) # for checking
    
    # Generate wellinfo csv file for the calibrated 2014-2022 model =====
    ofile = os.path.join(wdir,'model_packages','hist_2014_2021','mnw2','wellinfodxhx_cy2014_2022_check.csv')
    gen_well_info_csv_file(dfrate_2014_2022, ofile)

    
    # =========================================================================
    # = [04] PREDICTIVE MODEL =================================================
    # =========================================================================
    # Wellrate for PREDICTIVE NFA model 2021-2125 ===========================        
    dfpred=df2.copy()
    ofile = os.path.join(wdir,'model_packages','pred_2021_2125','mnw2','wellratedxhx_cy2021_2125.csv')
    
    dfrate_2021_2125=gen_pred_wellrate_csv_file(dfpred,npred_sp_with_pmp,ofile)  
    #####add_future_rates(dfrate_2021_2125)
   
    # Generate wellinfor csv file for the calibrated 2014-2022 model =====
    ofile = os.path.join(wdir,'model_packages','pred_2021_2125','mnw2','wellinfodxhx_cy2021_2125.csv')
    #gen_well_info_csv_file(dfrate_2021_2125, ofile)

    # =========================================================================
    # = [05] PREDICTIVE MODEL =================================================
    # =========================================================================
    # Wellrate for PREDICTIVE NFA model 2023-2125 ===========================        
    ofile = os.path.join(wdir,'model_packages','pred_2023_2125','mnw2_nfa','wellratedxhx_cy2023_2125.csv')
    
    dfrate_2023_2125=dfrate_2021_2125.copy()
    dfrate_2023_2125.columns
    # Delete the first 24 columns (24 sps of cy2022 and cy2023)
    old_sp_names = list(range(25,npred_sp_total+1,1))
    new_sp_names = list(range(1,npred_sp_total+1-n_new_sp,1))
    dict_new_col_names = dict(zip(old_sp_names, new_sp_names))

    col_keep = ['ID'] + old_sp_names
    dfrate_2023_2125=dfrate_2023_2125[col_keep]
    dfrate_2023_2125=dfrate_2023_2125.rename(columns=dict_new_col_names)
    # Set rates for Jan and Feb of 2023 as avg, not measured values as currently used
    dfrate_2023_2125[1]= dfrate_2023_2125[3].copy() # val in col 3 to end is the same
    dfrate_2023_2125[2]= dfrate_2023_2125[3].copy()
    dfrate_2023_2125.to_csv(ofile, index=False)
   
    # Generate wellinfor 
    ofile = os.path.join(wdir,'model_packages','pred_2023_2125','mnw2_nfa','wellinfodxhx_cy2023_2125.csv')
    gen_well_info_csv_file(dfrate_2023_2125, ofile)




    # [06] ====================================================================
    # Check calculation =======================================================
    #check_cal()

            

    # Missing well names
    '''
    ME22: 199-D8-55 (2021), 2022 listed as "spare"
    ME26: Well 199-D8-68 was disconnected in March 2022 and converted from extraction to Injection officially in August 
    ME40: 199-H4-80 (2021), 2022 listed as "spare"
    ME42: 199-D5-20 (2021, 2022). Well 199-D5-20 was disconnected in early Jan and converted from extraction to injection in March 2022
    ME57: no name, 2022 listed as "spare", why rate in Feb2023 = -149.069 m3/d?
    MJ15: no name, 2022 listed as "spare". Note - this PLCID is used for caustic recirc line so volume reported is not effluent injection
    HE21: 199-H1-34 (2021), 2022 listed as "spare"
    HE27: 199-H1-39 (2021), 2022 listed as "spare". Well 199-H1-39 operated into Feb 2022 and then was coverted from an extraction well (HE27) to an injection well
    HE40: 199-H1-32 (2021), 2022 listed as "spare"
    HE41: 199-H1-33 (2021), 2022 listed as "spare"
    HE42: 199-H3-4 (2021), 2022 listed as "spare"
    HJ25: no name, 2022 listed as "spare"
            Check why the volumetric values are negative at injection well HJ25, starting August 2022 (See Figure 1)? 
            I don’t understand either but there is no well hooked up to it. I would ignore that column with data for HJ25
            and don’t include it.

    '''



    


