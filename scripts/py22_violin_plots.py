import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
matplotlib.use('Qt5Agg')
# plt.rc('axes', axisbelow=True)

cwd = os.getcwd()

df_wells = pd.read_csv(os.path.join('output', 'water_level_data', 'obs_2021_2023', 'measured_WLs_monthly.csv'),
                       parse_dates = ['Date'])
sub_wells = df_wells.loc[df_wells['ID'].isin(['199-H4-84', '199-H4-86'])]
df_source = pd.read_csv(os.path.join('output', 'water_level_data', 'calib_2014_2023', 'sim_hds_flopy_100H_sources.csv'),
                        parse_dates=['Date'])
df_source_sub = df_source[df_source['NAME'].isin(['183-H-SEB_2', '100-H-46-WS_0'])]

#%% Violin plots -- individual wells per plot

for well in ['199-H4-84', '199-H4-86']:
    fig, ax = plt.sub_wells_wellsplots(figsize=(2,3))
    toplot = df_wells[df_wells['ID'] == well][df_wells['Date'] >= '10/01/2022']
    sns.violinplot(data = toplot, x = 'ID', y = 'Water Level (m)', ax = ax, zorder=10)
    ax.grid(axis='y', color='black', zorder=0)
    ax.grid(axis='y', which='minor', zorder=0)
    ax.minorticks_on()
    ax.set_ylim(113,117)
    ax.set_xlabel('')
    ax.set_title('Water Level\nRebound Period')
    # ax.set_axisbelow(True)
    plt.tight_layout()
    plt.show()

#%% Violin plots -- all wells one plot

timeframe = 'all' ## 'rebound period'  'all'
fig, ax = plt.subplots()
if timeframe == 'all':
    toplot = sub_wells
    ax.set_title('Jan 2021 - Oct 2023')
elif timeframe == 'rebound period':
    ax.set_title('Oct 2022 - Oct 2023')
    toplot = sub_wells[sub_wells['Date'] >= '10/01/2022']
else:
    print('no plotting period defined')
sns.violinplot(data = toplot, x = 'ID', y = 'Water Level (m)', ax = ax, zorder=10)
ax.grid(axis='y', color = 'black', zorder=0)
ax.grid(axis='y', which='minor', zorder=0)
ax.minorticks_on()
ax.set_ylim(113,117)
ax.set_xlabel('')
# ax.set_axisbelow(True)
plt.show()

#%% Violin plots -- source cells
timeframe = 'rebound period' ## 'rebound period'  'all'
fig, ax = plt.subplots()
if timeframe == 'all':
    toplot = df_source_sub
    ax.set_title('Jan 2021 - Oct 2023')
elif timeframe == 'rebound period':
    ax.set_title('Oct 2022 - Oct 2023')
    toplot = df_source_sub[df_source_sub['Date'] >= '10/01/2022']
else:
    print('no plotting period defined')
sns.violinplot(data = toplot, x = 'NAME', y = 'Head', ax = ax, zorder=10)
ax.minorticks_on()
ax.grid(axis='y', color = 'black', zorder=0)
ax.grid(axis='y', which='minor', zorder=0)
ax.set_ylim(112,117)
ax.set_xlabel('')
# ax.set_axisbelow(True)
plt.show()


### xtras ###

## List of logs
logs = ['100-D-56-2', '100-D-100_exv1', '100-D-100_exv2', '100-D-100_slope', '100-D-100_sw3_exv',
        '100-D-100_unexv', '100-H-46','100-H-46_exv', '100-H-RB', '100-H-RB_exv', '100-H-SEB']
