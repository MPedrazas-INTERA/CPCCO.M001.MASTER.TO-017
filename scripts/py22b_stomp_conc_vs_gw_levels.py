'''
Script to visualize:
- Concentration depth profile from STOMP output
- Water level distribution over simulated period

Can be used to compare water level fluctuations and concentration at depth to infer PRZ dynamics

Original concentration depth script found at continuing_source_modeling/scripts/07_zplots.py

@rweatherl January 2024

'''

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
matplotlib.use('Qt5Agg')
import glob

matplotlib.rcParams.update({'font.size': 12})
plt.rc('axes', axisbelow=True)

def zplot_multiple_years(column):

    calib_files = glob.glob(os.path.join(cdir, 'flow_2014_Oct2023', 'stomp', 'cr6', column, '*.csv'))
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

def zplot_one_year():

    for col in columns:
        print(col)
        file_path = glob.glob(os.path.join(cdir, sce, 'stomp', 'cr6', col, '*2023.csv'))
        rates_raw = pd.read_csv(file_path[0], skiprows=3,index_col=None)
        ## years = ['2023']

        fig, ax = plt.subplots(figsize=(6,10))
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
        plt.title(f'{col}\nOctober 2023')
        # plt.tight_layout()
        # plt.show()
        # plt.savefig(os.path.join(os.getcwd(), 'output', 'zplots', f'{column}_Oct2023.png'))
        # plt.close()

    return None

### Violin plots -- individual wells per plot
def violin_plots_individual_well(timeframe, subset):

  #  timeframe = 'All' #'Oct 2022 - Oct 2023' #'All'  ##can uncomment when testing, comment out when running entire script!!

    if subset == True:
        wells = wells_subset
    elif subset == False:
        wells = h['ID'].unique()

    for well in wells:

        fig, ax = plt.subplots(figsize=(6,10))

        # fig.suptitle(f'{well}\n{timeframe} - {timestep}', fontsize = 9)
        # ax.set_title(f'{well}\n{timeframe}')

        ## Note that for obs data, some wells do not have a meaningful number of data points in smaller timeframes
        if timeframe == 'Jan 2014 - Oct 2023':
            toplot = h[h['ID'] == well]
        elif timeframe == 'Oct 2022 - Oct 2023':
            toplot = h[h['ID'] == well][h['Date'] >= '10/01/2022']
        elif timeframe == '2021 - Oct 2022':
            toplot = h[h['ID'] == well][h['Date'] <= '10/01/2021']
        else:
            print('plotting period not defined, toplot empty')
        sample_size = len(toplot)
        sns.violinplot(data = toplot, x = 'ID', y = 'Water Level (m)', inner = None, ax = ax, zorder=10)  ## inner = 'quart',
        ax.grid(axis='y', color='black', zorder=0)
        ax.grid(axis='y', which='minor', zorder=0)
        ax.minorticks_on()
        if zone == '100H':
            ax.set_ylim(113,117)
        elif zone == '100D':
            # ax.set_ylim(113.75,144)
            ax.set_ylim(113.375, 143.375)
        ax.set_xlabel('')
        ax.set_xticks([])
        ax.set_ylabel('Water Level Elevation (m)')
        ax.set_axisbelow(True)
        ax.set_title(f'{well}\n{timeframe} - {timestep}\nSample Size = {sample_size}\n', fontsize=9)
        # plt.tight_layout()

        # ypos = 121.5 # Adjust the ypos based on your data
        ## moved this to title
        # ax.text(-0.25, ypos, f'Sample Size = {sample_size}',
        #         horizontalalignment='center', verticalalignment='center', color='black', fontsize=8)

        # plt.savefig(os.path.join(odir, f'violin_{well}_{timeframe}_{timestep}_v02.png'), dpi = 300)
        # plt.close()
    print('violin plots written!')
    #%%
    return None

### Violin plots -- src cells
def violin_plots_individual_cell(timeframe):

    for cell in src_sub['NAME'].unique():

        fig, ax = plt.subplots(figsize=(2, 3))

        fig.suptitle(f'{cell}\n{timeframe}')
        # ax.set_title(f'{well}\n{timeframe}')

        if timeframe == 'All':
            toplot = src_sub[src_sub['NAME'] == cell]
        elif timeframe == 'Oct 2022 - Oct 2023':
            toplot = src_sub[src_sub['NAME'] == cell][src_sub['Date'] >= '10/01/2022']
        elif timeframe == '2021 - Oct 2022':
            toplot = src_sub[src_sub['NAME'] == cell][src_sub['Date'] <= '10/01/2022']
        else:
            print('plotting period not defined, toplot empty')

        sns.violinplot(data = toplot, x = 'NAME', y = 'Head', ax = ax, zorder=10)
        ax.minorticks_on()
        ax.grid(axis='y', color = 'black', zorder=0)
        ax.grid(axis='y', which='minor', zorder=0)
        ax.set_ylim(111,118)
        ax.set_ylabel('Water Level Elevation (m)')
        ax.set_xlabel('')
        ax.set_xticks([])
        # ax.set_axisbelow(True)
        plt.tight_layout()
        # plt.savefig(os.path.join(odir, f'violin_src_{cell}_{timeframe}.png'), dpi = 300)
        # plt.close()

## side-by-side figure(s) of STOMP z-plot and individual well violin plots for direct comparison
def combined_zplot_violinplot(timeframe, subset):

    if subset == True:
        wells = wells_subset
    elif subset == False:
        wells = h['ID'].unique()

    for well in wells:
        if timeframe == 'Jan 2014 - Oct 2023':
            toplot = h[h['ID'] == well]
        elif timeframe == 'Oct 2022 - Oct 2023':
            toplot = h[h['ID'] == well][h['Date'] >= '10/01/2022']
        elif timeframe == '2021 - Oct 2022':
            toplot = h[h['ID'] == well][h['Date'] <= '10/01/2021']
        else:
            print('plotting period not defined, toplot empty')
        sample_size = len(toplot)

        for col in columns:

            stomp_file_path = glob.glob(os.path.join(cdir, sce, 'stomp', 'cr6', col, '*2023.csv'))
            stomp_conc_raw = pd.read_csv(stomp_file_path[0], skiprows=3, index_col=None)

            fig, (ax0, ax1) = plt.subplots(nrows = 1, ncols = 2, figsize=(6,10), sharey = True)

            ax0.set_ylim(stomp_conc_raw.iloc[0, 5], stomp_conc_raw.iloc[-1, 5])
            ax0.plot(stomp_conc_raw.loc[:, ' Aqueous cr6 Concentration (mol/m^3 )'],
                    stomp_conc_raw.loc[:, ' Z-Direction Node Positions (m)'],
                    color='xkcd:burnt orange', linewidth=2)
            ax0.grid(True, which='both')
            ax0.grid(which='major', color='k', alpha=0.85)
            ax0.grid(which='minor', color='grey', alpha=0.35)
            ax0.minorticks_on()
            ax0.set_xlabel(r'Aqueous Cr(VI) (mol/m$^3$)')
            ax0.set_ylabel('Elevation (m)')
            ax0.set_title(f'Soil Column\n{col}\nOctober 2023\n')

            sns.violinplot(data=toplot, x='ID', y='Water Level (m)', inner=None, ax=ax1, zorder=10)  ## inner = 'quart',
            ax1.grid(axis='y', color='black', zorder=0)
            ax1.grid(axis='y', which='minor', zorder=0)
            ax1.set_xlabel('')
            ax1.set_xticks([])
            ax1.set_ylabel('')
            ax1.set_title(f'Well {well}\n{timeframe} - {timestep}\nSample Size = {sample_size}\n') #, fontsize=9)
            ax1.minorticks_on()

            # plt.savefig(os.path.join(odir, 'with_stomp_profile', f'{col}_{well}_{timeframe}_{timestep}.png'), dpi = 300)
            # plt.close()
    return None

## side-by-side figure(s) of STOMP z-plot and all well violin plots for direct comparison
def combined_zplot_multiple_violinplots(timeframe, wells_subset):
    #%%

    wells = wells_subset

    for col in columns:

        fig, axes = plt.subplots(nrows=1, ncols=len(wells)+1, figsize=(10, 10), sharey=True)

        stomp_file_path = glob.glob(os.path.join(cdir, sce, 'stomp', 'cr6', col, '*2023.csv'))
        stomp_conc_raw = pd.read_csv(stomp_file_path[0], skiprows=3, index_col=None)

        axes[0].set_ylim(stomp_conc_raw.iloc[0, 5], stomp_conc_raw.iloc[-1, 5])
        axes[0].plot(stomp_conc_raw.loc[:, ' Aqueous cr6 Concentration (mol/m^3 )'],
                stomp_conc_raw.loc[:, ' Z-Direction Node Positions (m)'],
                color='xkcd:burnt orange', linewidth=2)
        axes[0].grid(True, which='both')
        axes[0].grid(which='major', color='k', alpha=0.85)
        axes[0].grid(which='minor', color='grey', alpha=0.35)
        axes[0].minorticks_on()
        axes[0].set_xlabel(r'Aqueous Cr(VI) (mol/m$^3$)')
        axes[0].set_ylabel('Elevation (m)')
        axes[0].set_title(f'Soil Column\n{col}\nOctober 2023\n')

        for i, well in enumerate(wells):

            if timeframe == 'Jan 2014 - Oct 2023':
                toplot = h[h['ID'] == well]
            elif timeframe == 'Oct 2022 - Oct 2023':
                toplot = h[h['ID'] == well][h['Date'] >= '10/01/2022']
            elif timeframe == '2021 - Oct 2022':
                toplot = h[h['ID'] == well][h['Date'] <= '10/01/2021']
            else:
                print('plotting period not defined, toplot empty')
            sample_size = len(toplot)
            ax = axes[i+1]  ## the magic!
            sns.violinplot(data=toplot, x='ID', y='Water Level (m)', inner=None, ax=ax, zorder=10)  ## inner = 'quart',
            ax.grid(axis='y', color='black', zorder=0)
            ax.grid(axis='y', which='minor', zorder=0)
            ax.set_xlabel(f'{well}')
            ax.set_xticks([])
            ax.set_ylabel('')
            ax.set_title(f'{timeframe}\n{timestep}\nSample Size = {sample_size}\n') #, fontsize=9)
            ax.minorticks_on()
        # plt.tight_layout()
        # plt.savefig(os.path.join(odir, 'with_stomp_profile', f'{col}_wells_{timeframe}_{timestep}.png'), dpi = 300)
        # plt.close()

if __name__ == '__main__':

    ## set global parameters

    zone = '100D'
    timestep = 'Monthly'
    timeframe = 'Jan 2014 - Oct 2023' ## 'Oct 2022 - Oct 2023' #'2021 - Oct 2022'

    sce = 'flow_2014_Oct2023'

    cdir = os.path.join(os.path.dirname(os.getcwd()), 'continuing_source_modeling')

    odir = os.path.join('output', 'violin_plots', f'{zone}')
    if not os.path.isdir(odir):
        os.makedirs(odir)

    ## read in observed water level data
    if zone == '100H':          ## has not been updated
        h = pd.read_csv(os.path.join('output', 'water_level_data', 'obs_2021_Oct2023', 'measured_WLs_monthly.csv'),
                               parse_dates=['Date'])
        h = h.loc[h['ID'].isin(['199-H4-84', '199-H4-86'])]
        src = pd.read_csv(
            os.path.join('output', 'water_level_data', 'calib_2014_2023', 'sim_hds_flopy_100H_srcs.csv'),
            parse_dates=['Date'])
        src_sub = src[src['NAME'].isin(['183-H-SEB_2', '100-H-46-WS_0'])]
    elif zone == '100D':
        h_0 = pd.read_csv(os.path.join('output', 'water_level_data', 'obs_2014_Oct2023', 'measured_WLs_all_100D.csv'),
                               usecols=['ID', 'DATE', 'Water Level (m)'], index_col = 'DATE', parse_dates=True)
        # h['DATE'] = pd.to_datetime(h['DATE'])
        if timestep == 'Daily':
            h = h_0.groupby('ID').resample('D').mean().dropna().reset_index()
        elif timestep == 'Monthly':
            h = h_0.groupby('ID').resample('M').mean().dropna().reset_index()
        else:
            print('timestep not defined')
    else:
        print('zone not defined')


    ## for plotting all at once
    columns = ['100-D-56-2', '100-D-100_exv1', '100-D-100_exv2',
               '100-D-100_slope', '100-D-100_sw3_exv', '100-D-100_unexv']

    ## define any subset of interest!
    wells_subset = ['199-D5-103', '199-D5-151', '199-D5-152']

    # violin_plots_individual_well(timeframe=timeframe, subset=True)
    #
    # violin_plots_individual_cell(timeframe='2021 - Oct 2022')

    # zplot_one_year()

    ## zplot_multiple_years(column = column)

    # combined_zplot_violinplot(timeframe, subset=True)

    ## this function requires a subset/list of wells to include.
    # combined_zplot_multiple_violinplots(timeframe, wells_subset)


