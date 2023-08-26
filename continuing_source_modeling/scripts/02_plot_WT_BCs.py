"""
Script to plot mod2obs output water tables on east and west side of each STOMP bore.
Good QC before input to STOMP

author: rweatherl

"""

import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import glob
import itertools
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Qt5Agg')

lib = plt.style.library
plt.rcParams.update({'font.size': 15})
plt.rcParams.update({'font.size': 15})
plt.rcParams['xtick.labelsize'] = 15
plt.rcParams['ytick.labelsize'] = 15
plt.rcParams['font.size'] = 15
plt.rcParams['legend.fontsize'] = 15


## user define model scenario
case = 'flow_2014_2023'

cwd = os.getcwd()
ws = os.path.join(os.path.dirname(cwd), case, 'bc_mod2obs')
odir = os.path.join(cwd, 'output', 'WT_BC_plots', case)
if not os.path.exists(odir):
    os.makedirs(odir)

### 1. READ BC DATA
bc_list = []
for file in glob.glob(os.path.join(ws, '100*.dat')):
    bc_list.append(file)
# result_files = [i for sub in result_files for i in sub] ##flatten into one list

bcs = {}
for file in bc_list:
    # print(file)
    bcs[file] = pd.read_csv(file, sep = '\t', header = None, usecols = [0,1,3],
                            names = ['bore', 'date', 'WT (masl)'], parse_dates = True, index_col = 0)
    bcs[file]['date'] = pd.to_datetime(bcs[file]['date']) #.dt.strftime('%m-%d-%Y')

newkeys = []
for k in bcs.keys(): ##keys start as pathnames by defult
    newkeys.append(k[len(str(ws))+1:-4])   ##isolate name of bore from path
##change dict keys to bore names
bcs2 = dict(zip(newkeys, bcs.values()))


#### 4. PLOTTING

for bore in bcs2.keys():
    east = bcs2[bore][bcs2[bore].index.str.contains('-E')]
    west = bcs2[bore][bcs2[bore].index.str.contains('-W')]
    fig, ax = plt.subplots(figsize = (10,5))
    ax.set_title(f'Water Table at {bore}')
    ax.plot(east['date'], east['WT (masl)'], color = 'blue', label  = 'East')
    ax.plot(west['date'], west['WT (masl)'], '--', color='green', label='West')
    ax.legend()
    ax.grid(True)
    ax.set_xlabel('Year')
    ax.set_xlim(east['date'].min(),east['date'].max())
    ax.set_ylabel('Water Level (masl)')

    ax.tick_params(axis='x', rotation=45)
    ax.xaxis.set_major_locator(mdates.YearLocator(5))           ## labeled tick marker every 5 years
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(mdates.YearLocator())

    plt.tight_layout()
    plt.show()


    plt.savefig(os.path.join(odir, f'WT_{bore}_BC_at_bores.png'))