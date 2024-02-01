import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib


cwd = os.getcwd()
wdir = os.path.dirname(cwd)

if __name__ == "__main__":

    ifile = f'd:/projects/CPCCO.M001.MASTER.TO-017/scripts/output/water_level_data/obs_2014_Oct2023/measured_WLs_monthly_all_wells.csv'

    # Read file
    df = pd.read_csv(ifile)
    df['EVENT'] = pd.to_datetime(df['EVENT'])

    # Specify wells to plot
    #list_wells = ['199-D5-17', '199-D5-19', '199-D5-133']
    #list_wells = ['199-D5-128', '199-D5-129', '199-D5-133']
    #list_wells = ['199-D5-160', '199-D5-162', '199-D5-163', '199-D5-133']

    list_wells = ['199-D5-160', '199-D5-162', '199-D5-163', '199-D5-103', '199-D5-150']
        
    df2 = df[df['NAME'].isin(list_wells)]
    #df2['EVENT'] = pd.to_datetime(df2['EVENT'])

    # Group by 'name' and plot time series for each group
    grouped_df = df2.groupby('NAME')

    plt.figure(figsize=(10, 6))

    for name, group in grouped_df:
        print(group.index)
        plt.plot(group['EVENT'], group['VAL_FINAL'], label=name)

    plt.xlabel('Date')
    plt.ylabel('Observed Groundwater Elevation (m)')
    #plt.title(f'Observed Groundwater Elevation (m)')

    plt.legend()
    plt.grid()
    plt.show()
