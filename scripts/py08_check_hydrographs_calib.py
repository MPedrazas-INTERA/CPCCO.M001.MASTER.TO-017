import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import flopy.utils.binaryfile as bf


'''
Readme
    - Check hydrographs calibrated model


'''


if __name__ == "__main__":
    # xxx
    wdir = 'c:/Users/hpham/Documents/100HR3'
    # []
    # well location ijk
    ifile_well_loc = f'{wdir}/scripts/input/obs_well_ijk_cy2020.csv'
    ifile_date = f'{wdir}/scripts/input/sp_2014_2022.csv'
    
    hed_file1 = f'{wdir}/model_run/flow_2014_2022/100hr3.hed' # co
    #hed_file2 = f'{wdir}/flow_calib_9L_rev_cy2020ghb/DHmodel_2014to2020.hds' # revised GHB, low cond

    # 
    dfwel = pd.read_csv(ifile_well_loc)
    dfdate = pd.read_csv(ifile_date)
    dfdate['start'] = pd.to_datetime(dfdate['start'])
    hds1 = bf.HeadFile(hed_file1)

    # Save ts of simulated head at a selected location for checking
    hds1_all = hds1.get_alldata()

    
    #df_hed1[f'hed1_r{ir}c{ic}'] = hds1_all[:,il-1,ir-1,ic-1]
    
    
    list_wells = list(dfwel['name'].unique())
    for well in list_wells:
        dfwell2 = dfwel[dfwel['name']==well]
        dfwell2=dfwell2.reset_index()
        ir, ic = dfwell2['row'][0],  dfwell2['col'][0]
        list_lay = dfwell2['lay'].to_list()
        df=dfdate[['sp','start']]
        df=df.rename(columns={'start':'Date'})
        col = []
        for il in list_lay:
            col.append(f'Layer_{il}')
            df[f'Layer_{il}'] = hds1_all[:,il-1,ir-1,ic-1]
            tmp=hds1_all[:,il-1,ir-1,ic-1]
            len(tmp)
        
        # Plot
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        df.plot(ax=ax, x='Date', y=col)
        #df.plot(ax=ax, x='Time',style=':o', y=['ObsVal'])
        ax.set_title(f'Well: {well}')
        ax.set_ylabel(f'Simulated head (m)')
        ax.grid(axis='both', alpha=0.2)

        #ax.set_ylim([117.5, 120])
        ofile = f'output/hydrographs_2014to2022/WL_{well}.png'
        fig.savefig(ofile, dpi=300, transparent=False, bbox_inches='tight')

    
    #
    print('Done all!!!')
