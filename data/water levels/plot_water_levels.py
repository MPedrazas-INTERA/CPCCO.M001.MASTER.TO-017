import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')


cwd = os.getcwd()
wdir = os.path.dirname(cwd)


### --- 1. Import and structure all data --- ###
def import_data():

    data_files = glob.glob(os.path.join(cwd, '*.xlsx'))

    all_data = {}
    for file in data_files:
       # print(file.split("\\")[-1].split('.')[0]) ## extract filename directoy and use as dict key
        k = file.split("\\")[-1].split('.')[0]
        all_data[k] = pd.read_excel(file, sheet_name = None) #, index_col = 0, parse_dates=True)

    strings = [data_files[i].split("\\")[-1].split('.')[0] for i, e in enumerate(data_files)] ## isolate file names without .xlsx extension
    dict1, dict2, dict3 = all_data[strings[0]].copy(), all_data[strings[1]].copy(), all_data[strings[2]].copy() ## separate data from nested dict into simple dict. create copy to avoid edits to original data.


    for k in dict1:
        dict1[k] = dict1[k].iloc[9:]
        dict1[k].columns = dict1[k].iloc[0]
        dict1[k].drop(dict1[k].index[0], inplace=True)
        dict1[k].index.name = 'DT'
        dict1[k].set_index('Date and Time', inplace=True)
        dict1[k].index = pd.to_datetime(dict1[k].index)
        # print(dict1[k].columns)  ##check correct column name assignment

    for k in dict2:
        dict2[k].set_index('Date/Time', inplace=True)
        dict2[k].index = pd.to_datetime(dict2[k].index)

    for k in dict3:
        dict3[k].set_index('HYD_DATE_TIME_PST', inplace=True)
        dict3[k].index = pd.to_datetime(dict3[k].index)


    return dict1, dict2, dict3


def generate_plots(dict, col):

    # dict = dict3
    # col = 'HYD_HEAD_METERS_NAVD88'
    for k in dict.keys():
        print(k)
        toplot = dict[k].resample('D').mean()
        fig, ax = plt.subplots(figsize=(8, 5))
        ## dict3 are manual measurements -- scatter plot best
        if dict == dict3:
            ax.scatter(toplot.index, toplot.loc[:,col])
        else:
            ax.plot(toplot.index, toplot.loc[:,col])
        ax.grid(True)
        ax.set_title(f'{k}')
        ax.set_ylabel('Water Level (m.asl)')
        # ax.set_ylim(113.5,118)
        plt.xticks(rotation = 45)
        fig.tight_layout()
        plt.savefig(os.path.join(cwd, 'plots', f'{k}.png'))

    return None

if __name__ == "__main__":

    dict1, dict2, dict3 = import_data() ## run once at beginning of workflow

    col = 'Elevation (m)' #'HYD_HEAD_METERS_NAVD88'
    generate_plots(dict2, col) ## provide column label to be plotted



### --- QC --- ###

##quick check for overlapping occurences##
# wells1, wells2, wells3 = list(dict1.keys()), list(dict2.keys()), list(dict3.keys())
# import itertools
# l = list(itertools.chain(wells1, wells2, wells3))
# from collections import Counter
# Counter(l)