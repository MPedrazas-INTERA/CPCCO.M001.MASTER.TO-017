import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt

'''
- input file "processed_wellrate_DX_HX_2006_2023.csv" was generated by py07_process_pumping.py
- 
'''

def gen_plot(wel, df2, ofile):
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        df2.plot(ax=ax, y=wel,style='-o', alpha=0.6)
        ax.grid(axis='both', alpha=0.2)
        ax.set_ylabel('Pumping Rates (gpm)')
        ax.set_title(f'Well: {wel}')
        #ofile = f'output/plot_pmp_each_well/check_{wel}.png'
        fig.savefig(ofile, dpi=300, transparent=False, bbox_inches='tight')
        print(f'Saved {ofile}\n')

if __name__ == "__main__":
    ifile1 = f'output/processed_wellrate_DX_HX_to_Feb2023_all_fields_4checking_gpm.csv'
    ifile2 = f'output/processed_wellrate_DX_HX_2006_2023.csv'
    
    opt_plot_pmp_rate_each_well = True

    gpmtom3d = (24*60)/1*231*(25.4/1000/1)**3 # 

    #
    dfcoor = pd.read_csv(ifile1) # get well coordinates
    dfcoor.columns
    dfcoor.head(5)
    col_keep = ['NAME2', 'NAME', 'HMI', 'Type', 'System', 'XCOORDS', 'YCOORDS', 'Active','SP109_2023_1','SP110_2023_2','avg']
    dfcoor=dfcoor[col_keep]
    dfcoor=dfcoor.rename(columns={'NAME2':'ID'})
    
    # Load pmp data
    df=pd.read_csv(ifile2) 
    df = df.set_index(df['ID'])
    
    df.columns
    #df=df.drop(columns=['NAME','ID'])
    df=df.drop(columns=['ID'])
    

    #
    df=df/gpmtom3d
    dfstat=df.copy()
    dfstat['Max'] = dfstat.abs().max(axis=1)
    #col = ['ID'] + list(range(1,108+1,1))
    #df=df[col]
    df2=df.T

    #
    df[(df<1e-3) & (df>-1e-3)] = np.nan
    df['min1422'] = df.abs().min(axis=1)
    df['max1422'] = df.abs().max(axis=1)
    df['avg1422'] = df.abs().mean(axis=1)
    # Merge
    df = pd.merge(dfcoor, df, how='left', on=['ID'])
    df.head(5)
    df.columns   
    col_1 = ['ID','NAME','HMI', 'Type', 'System', 'XCOORDS', 'YCOORDS', 'Active',\
             'SP109_2023_1','SP110_2023_2','avg','min1422', 'max1422',
       'avg1422']
    col_sp = [f'{i}' for i in range(1,108+1,1)]
    col = col_1+col_sp
    df[col].to_csv(f'output/processed_wellrate_DX_HX_2006_2023_coords.csv', index=False) 




    #
    date = pd.date_range(start='1/1/2014', end='12/31/2022', freq='M')
    #len(date)
    df2 = df2.set_index(date)



    # [01] Plot each well
    list_wells = df2.columns
#    wel = '199-D2-10_I_DX'
    
    #df2.plot(y=wel)
    
    if opt_plot_pmp_rate_each_well:
        for wel in list_wells:
            ofile = f'output/plot_pmp_each_well/check_{wel}.png'
            gen_plot(wel, df2, ofile) # Uncomment to run
    
    # Get some stats
    df3 = df2.describe()

    # List of wells that extract max capacity
    #list_well_max_capacity = []

    # [02] Plot for a group of wells
    dict_group = {'100D_G1':['199-D4-84_E_DX','199-D4-85_E_DX','199-D4-95_E_DX','199-D4-98_E_DX','199-D4-99_E_DX'],
                  '100D_G2':['199-D4-84_E_DX'],}
    for gr in dict_group:
        print(gr)
        wel = dict_group[gr]
        ofile = f'output/plot_pmp_each_well_group/check_{gr}.png'       
        gen_plot(wel, df2, ofile)
