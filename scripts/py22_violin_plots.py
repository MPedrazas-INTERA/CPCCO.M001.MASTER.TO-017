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
    timeframe = 'All' #'Oct 2022 - Oct 2023' #'All'  ##uncomment when testing, comment out when running entire script

    for well in h['ID'].unique():

        fig, ax = plt.subplots(figsize=(2,3))

        fig.suptitle(f'{well}\n{timeframe} - {timestep}', fontsize = 9)
        # ax.set_title(f'{well}\n{timeframe}')

        if timeframe == 'All':
            toplot = h[h['ID'] == well]
        elif timeframe == 'Oct 2022 - Oct 2023':
            toplot = h[h['ID'] == well][h['Date'] >= '10/01/2022']
        elif timeframe == '2021 - Oct 2022':
            toplot = h[h['ID'] == well][h['Date'] <= '10/01/2021']
        else:
            print('plotting period not defined, toplot empty')

        sns.violinplot(data = toplot, x = 'ID', y = 'Water Level (m)', inner = None, ax = ax, zorder=10)  ## inner = 'quart',
        ax.grid(axis='y', color='black', zorder=0)
        ax.grid(axis='y', which='minor', zorder=0)
        ax.minorticks_on()
        if zone == '100H':
            ax.set_ylim(113,117)
        elif zone == '100D':
            ax.set_ylim(115,121)
        ax.set_xlabel('')
        ax.set_xticks([])
        ax.set_ylabel('Water Level Elevation (m)')
        ax.set_axisbelow(True)
        plt.tight_layout()

        sample_size = len(toplot)
        ypos = 121.5 # Adjust the ypos based on your data
        ax.text(-0.25, ypos, f'Sample Size = {sample_size}',
                horizontalalignment='center', verticalalignment='center', color='black', fontsize=8)

        # plt.savefig(os.path.join(odir, f'violin_{well}_{timeframe}_{timestep}.png'), dpi = 300)
        # plt.close()
    print('violin plots written!')

#%%
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

if __name__ == "__main__":

    cwd = os.getcwd()

    zone = '100D'
    timestep = 'monthly'
    timeframe = 'All'

    odir = os.path.join(cwd, 'output', 'violin_plots', f'{zone}')
    if not os.path.isdir(odir):
        os.makedirs(odir)

    if zone == '100H':          ## might need to be updated
        h = pd.read_csv(os.path.join('output', 'water_level_data', 'obs_2021_Oct2023', 'measured_WLs_monthly.csv'),
                               parse_dates=['Date'])
        h = h.loc[h['ID'].isin(['199-H4-84', '199-H4-86'])]
        src = pd.read_csv(
            os.path.join('output', 'water_level_data', 'calib_2014_2023', 'sim_hds_flopy_100H_srcs.csv'),
            parse_dates=['Date'])
        src_sub = src[src['NAME'].isin(['183-H-SEB_2', '100-H-46-WS_0'])]
    elif zone == '100D':
        h_0 = pd.read_csv(os.path.join(cwd, 'output', 'water_level_data', 'obs_2014_Oct2023', 'measured_WLs_all_100D.csv'),
                               usecols=['ID', 'DATE', 'Water Level (m)'], index_col = 'DATE', parse_dates=True)
        # h['DATE'] = pd.to_datetime(h['DATE'])
        if timestep == 'daily':
            h = h_0.groupby('ID').resample('D').mean().dropna().reset_index()
        elif timestep == 'monthly':
            h = h_0.groupby('ID').resample('M').mean().dropna().reset_index()
        else:
            print('timestep not defined')
    else:
        print('zone not defined')

    violin_plots_individual_well(timeframe=timeframe)  ## 'Oct 2022 - Oct 2023' #'2021 - Oct 2022'
    #
    # violin_plots_individual_cell(timeframe='2021 - Oct 2022')

#%%  QA
    # #
    # for well in df_daily['ID'].unique():#['199-D5-17']: #h['ID'].unique():
    #     fig, ax = plt.subplots()
    #     toplot = df_daily[df_daily['ID'] == well]
    #     ax.scatter(toplot['DATE'], toplot['Water Level (m)'])
    #     plt.title(f'{well}')
    #     # plt.savefig(os.path.join(cwd, 'output', 'qa', f'scatterplot_{well}_WLs.png'), dpi = 300)
    #     # plt.close()


### xtras ###

## List of logs
# logs = ['100-D-56-2', '100-D-100_exv1', '100-D-100_exv2', '100-D-100_slope', '100-D-100_sw3_exv',
#         '100-D-100_unexv', '100-H-46','100-H-46_exv', '100-H-RB', '100-H-RB_exv', '100-H-SEB']


# #%% Violin plots -- all wells one plot
#
# timeframe = 'rebound period' ## 'rebound period'  'all'
# fig, ax = plt.subplots()
# if timeframe == 'all':
#     toplot = h
#     ax.set_title('Jan 2021 - Oct 2023')
# elif timeframe == 'rebound period':
#     ax.set_title('Oct 2022 - Oct 2023')
#     toplot = h[h['Date'] >= '10/01/2022']
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
