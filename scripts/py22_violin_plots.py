import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
matplotlib.use('Qt5Agg')
# plt.rc('axes', axisbelow=True)


### Violin plots -- individual wells per plot
def violin_plots_individual_well(timeframe):
#%%
    timeframe = 'All' #'Oct 2022 - Oct 2023' #'All'  ##uncomment when testing

    for well in df_wells['ID'].unique():

        fig, ax = plt.subplots(figsize=(2,3))

        fig.suptitle(f'{well}\n{timeframe}')
        # ax.set_title(f'{well}\n{timeframe}')

        if timeframe == 'All':
            toplot = df_wells[df_wells['ID'] == well]
        elif timeframe == 'Oct 2022 - Oct 2023':
            toplot = df_wells[df_wells['ID'] == well][df_wells['Date'] >= '10/01/2022']
        elif timeframe == '2021 - Oct 2022':
            toplot = df_wells[df_wells['ID'] == well][df_wells['Date'] <= '10/01/2021']
        else:
            print('plotting period not defined, toplot empty')

        sns.violinplot(data = toplot, x = 'ID', y = 'Water Level (m)', inner = None, ax = ax, zorder=10)  ## inner = 'quart',
        ax.grid(axis='y', color='black', zorder=0)
        ax.grid(axis='y', which='minor', zorder=0)
        ax.minorticks_on()
        if zone == '100H':
            ax.set_ylim(113,117)
        elif zone == '100D':
            ax.set_ylim(115,119)
        ax.set_xlabel('')
        ax.set_xticks([])
        ax.set_ylabel('Water Level Elevation (m)')
        ax.set_axisbelow(True)
        plt.tight_layout()
        # plt.savefig(os.path.join(odir, f'violin_{well}_{timeframe}.png'), dpi = 300)
        # plt.close()
#%%
### Violin plots -- source cells
def violin_plots_individual_cell(timeframe):

    for cell in source_sub['NAME'].unique():

        fig, ax = plt.subplots(figsize=(2, 3))

        fig.suptitle(f'{cell}\n{timeframe}')
        # ax.set_title(f'{well}\n{timeframe}')

        if timeframe == 'All':
            toplot = source_sub[source_sub['NAME'] == cell]
        elif timeframe == 'Oct 2022 - Oct 2023':
            toplot = source_sub[source_sub['NAME'] == cell][source_sub['Date'] >= '10/01/2022']
        elif timeframe == '2021 - Oct 2022':
            toplot = source_sub[source_sub['NAME'] == cell][source_sub['Date'] <= '10/01/2022']
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
        # plt.savefig(os.path.join(odir, f'violin_source_{cell}_{timeframe}.png'), dpi = 300)
        # plt.close()

if __name__ == "__main__":

    cwd = os.getcwd()

    zone = '100D'

    odir = os.path.join(cwd, 'output', 'violin_plots', f'{zone}')
    if not os.path.isdir(odir):
        os.makedirs(odir)

    if zone == '100H':          ## not updated to latest directory format (12/15/2023)
        df_wells = pd.read_csv(os.path.join('output', 'water_level_data', 'obs_2021_Oct2023', 'measured_WLs_monthly.csv'),
                               parse_dates=['Date'])
        df_wells = df_wells.loc[df_wells['ID'].isin(['199-H4-84', '199-H4-86'])]
        # source = pd.read_csv(
        #     os.path.join('output', 'water_level_data', 'calib_2014_2023', 'sim_hds_flopy_100H_sources.csv'),
        #     parse_dates=['Date'])
        # source_sub = source[source['NAME'].isin(['183-H-SEB_2', '100-H-46-WS_0'])]
    elif zone == '100D':
        df_wells = pd.read_csv(os.path.join('output', 'water_level_data', 'obs_2021_Oct2023', 'measured_WLs_monthly_100D.csv')) #,
                            #   index_col = 1, parse_dates=True)
        # df_wells = df_wells[df_wells['MAPUSE'] == True]

    else:
        print('zone not defined')

    violin_plots_individual_well(timeframe='All')  ## 'Oct 2022 - Oct 2023' #'2021 - Oct 2022'
    #
    # violin_plots_individual_cell(timeframe='2021 - Oct 2022')

    #%%  QA
    #
    # for well in df_wells['ID'].unique():
    #     fig, ax = plt.subplots()
    #     toplot = df_wells[df_wells['ID'] == well]
    #     ax.scatter(toplot.index, toplot['Water Level (m)'])



### xtras ###

## List of logs
# logs = ['100-D-56-2', '100-D-100_exv1', '100-D-100_exv2', '100-D-100_slope', '100-D-100_sw3_exv',
#         '100-D-100_unexv', '100-H-46','100-H-46_exv', '100-H-RB', '100-H-RB_exv', '100-H-SEB']


# #%% Violin plots -- all wells one plot
#
# timeframe = 'rebound period' ## 'rebound period'  'all'
# fig, ax = plt.subplots()
# if timeframe == 'all':
#     toplot = df_wells
#     ax.set_title('Jan 2021 - Oct 2023')
# elif timeframe == 'rebound period':
#     ax.set_title('Oct 2022 - Oct 2023')
#     toplot = df_wells[df_wells['Date'] >= '10/01/2022']
# else:
#     print('plotting period not defined')
# sns.violinplot(data = toplot, x = 'ID', y = 'Water Level (m)', ax = ax, zorder=10)
# ax.grid(axis='y', color = 'black', zorder=0)
# ax.grid(axis='y', which='minor', zorder=0)
# ax.minorticks_on()
# ax.set_ylim(113,117)
# ax.set_xlabel('')
# # ax.set_axisbelow(True)
# plt.show()
