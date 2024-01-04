import os
import pandas as pd
import glob
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
matplotlib.rcParams.update({'font.size': 18})

def plot_multiple_years():

    column = '100-D-56-2'

    calib_files = glob.glob(os.path.join(wdir, 'flow_2014_Oct2023', 'stomp', 'cr6', column, '*.csv'))
    calib_files = [item for item in calib_files if 'geo' not in item]   ## drop the geo csv
    rates_raw = {f: pd.read_csv(f, skiprows = 3, index_col = None) for f in calib_files}
    years = ['2014', '2015', '2016', '2017', '2018', '2019', '2021', '2022', '2023']
    rates=dict(zip(years,list(rates_raw.values())))

    fig, ax = plt.subplots()
    for k in rates_raw.keys():
        ax.set_ylim(rates_raw[k].iloc[0,5],rates_raw[k].iloc[-1,5])
        ax.plot(rates_raw[k].loc[:,' Aqueous cr6 Concentration (mol/m^3 )'], rates_raw[k].loc[:,' Z-Direction Node Positions (m)'])
        ax.grid(True)
        ax.legend(years)
        # ax.set_xlabel('Aqueous cr6 (mol/m3)')
        plt.title(f'{column}')
        # plt.show()
        # plt.savefig(os.path.join(os.getcwd(), 'output', f'calibration_run_2015_2023_{column}.png'))


    return None

def plot_one_year():
#%%

    for column in columns:
        print(column)
        file_path = glob.glob(os.path.join(wdir, sce, 'stomp', 'cr6', column, '*2023.csv'))

        rates_raw = pd.read_csv(file_path[0], skiprows=3,index_col=None)
        ## years = ['2023']

        fig, ax = plt.subplots(figsize=(5,10))
        ax.set_ylim(rates_raw.iloc[0,5],rates_raw.iloc[-1,5])
        ax.plot(rates_raw.loc[:,' Aqueous cr6 Concentration (mol/m^3 )'], rates_raw.loc[:,' Z-Direction Node Positions (m)'],
                color='xkcd:burnt orange', linewidth=2)
        ax.grid(True, which = 'both')
        ax.grid(which='major', color='k', alpha=0.85)
        ax.grid(which='minor', color='grey', alpha=0.35)
        ax.minorticks_on()
        # ax.legend(years)
        ax.set_xlabel(r'Aqueous Cr(VI) (mol/m$^3$)')
        ax.set_ylabel('Elevation (m)')
        plt.title(f'{column}\nOctober 2023')
        plt.tight_layout()
        # plt.show()
        plt.savefig(os.path.join(os.getcwd(), 'output', 'zplots', f'{column}_Oct2023.png'))
        plt.close()
#%%

    return None

if __name__ == '__main__':

    wdir = os.path.dirname(os.getcwd())

    sce = 'flow_2014_Oct2023'

    columns = ['100-D-56-2', '100-D-100_exv1', '100-D-100_exv2',
               '100-D-100_slope', '100-D-100_sw3_exv','100-D-100_unexv']

    plot_one_year()
