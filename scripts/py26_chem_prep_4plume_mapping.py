import pandas as pd
import datetime as dt 
import matplotlib.pyplot as plt


''''
Created by hpham, 02/12/2024
This script combine the monthly average Cr(VI) data to make it an unique data file
This data file will be sent to Elanor for generating monthy plume maps
'''

def plot_compare_conc(df1, df2):
    list_wells = list(df1['NAME'].unique()) + list(df2['NAME'].unique())
    list_wells.remove('35-S')
    for wel in list_wells:    
        #
        print(f'plotting well {wel}\n')
        #if (not df1_monthly.loc[wel].empty) or (not df2_monthly.loc[wel]):
        fig, ax = plt.subplots(figsize=(12, 6))
        df1_monthly.loc[wel].sort_values(by='Dataset 1').plot(ax=ax, style = '-o')
        df2_monthly.loc[wel].sort_values(by='Dataset 2').plot(ax=ax, style = '-x') # label='Data set 1', 

        # Customize the plot
        ax.set_title(f'{wel}')
        #ax.set_xlabel('Date')
        ax.set_xlim(dt.datetime(2023,1,1), dt.datetime(2024,2,28))
        ax.set_ylabel('Cr(VI) Concentration (ug/L)')
        ax.grid(which='both', axis='both', alpha = 0.25)
        plt.legend()
        #plt.show()
        
        ofile = f'output/concentration_data/compare_ds/Chk_{wel}.png'
        plt.savefig(ofile)
        plt.close()


if __name__ == "__main__":
    # Specify input files
    ifile_coors = f'input/qryWellHWIS_07202023.txt'
    ifile_2014_2023 = f'output/concentration_data/2014to2023/100D/Cr_obs_2014_2023_100D_mp.csv'
    ifile_2023_2024 = f'output/concentration_data/2023to2024/100D/Cr_obs_100D.csv'

    # Specify output file of monthly average concentration
    ofile = f'output/concentration_data/2023to2024/100D/Cr_obs_100D_combined_monthly_avg.csv'
    
    # Read in files
    df1 = pd.read_csv(ifile_2014_2023) # 2014-01-02 to 2023-12-11
    df2 = pd.read_csv(ifile_2023_2024) # data from 2023-04-01 to 2024-01-01
    df_coors = pd.read_csv(ifile_coors, delimiter='|')
    df_coors = df_coors[['NAME', 'XCOORDS', 'YCOORDS']]

    
    # get statistics
    df1['DATE']=pd.to_datetime(df1['DATE']) 
    df1_stats = df1['DATE'].describe()
    df1 = df1[df1['DATE'] > dt.datetime(2022,12,31)]
    df1 = df1[df1['DATE'] < dt.datetime(2023,11,1)]

    df2['DATE']=pd.to_datetime(df2['DATE'])
    df2 = df2[df2['DATE'] >= dt.datetime(2023,11,1)]
    df2_stats = df2['DATE'].describe()

    # Resample df1 to monthly
    df1 = df1.drop(columns=['REVIEW_QUALIFIER'])
    df1.set_index('DATE', inplace=True, drop=True)
    #df1 = df1.rename(columns={'STD_VALUE_RPTD':'VAL'})
    df1 = df1.rename(columns={'STD_VALUE_RPTD':'Dataset 1'})

    df1_monthly = df1.groupby('NAME').resample('M').mean()
    #df1_monthly=df1_monthly.reset_index(drop=False)
    
    
    # Select columns 
    df2 = df2[['NAME','DATE', 'VAL']]
    df2 = df2.rename(columns={'VAL':'Dataset 2'})
    df2.set_index('DATE', inplace=True, drop=True)
    df2_monthly = df2.groupby('NAME').resample('M').mean()

    # Plot to compare two Dataframes
    #plot_compare_conc(df1, df2) # 

    # combine two dataframes
    df1_monthly_cp = df1_monthly.copy()
    df2_monthly_cp = df2_monthly.copy()
    df1_monthly_cp = df1_monthly_cp.rename(columns={'Dataset 1':'VAL'})
    df2_monthly_cp = df2_monthly_cp.rename(columns={'Dataset 2':'VAL'})
    
    # Combine two datasets
    df_monthly = pd.concat([df1_monthly_cp, df2_monthly_cp], axis=0)


    # reset index
    df_monthly = df_monthly.reset_index()

    # Check to find dupplicated rows
    duplicated_rows = df_monthly[df_monthly.duplicated()]

    # add coordinate
    df_monthly=pd.merge(df_monthly, df_coors, how='left', on=['NAME'])


    # save to file 
    df_monthly.to_csv(ofile, index=False)

    print('Done all!')
        
    
    