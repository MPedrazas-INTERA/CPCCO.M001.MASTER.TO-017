""""
Script to plot bore-by-bore release rate curves as calculated with STOMP and resampled with ssm workflow
Based on R script by H. Rashid
R.Weatherl July 2022
"""

import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import glob
import matplotlib
from textwrap import wrap, fill
import re
matplotlib.use('Qt5Agg')


##user define case##
case = 'sce3a_to2125_rr3_test'

cwd = os.getcwd()
ws = os.path.join(os.path.dirname(cwd), 'scenarios', case, 'ssm', 'cr6')
outputDir = os.path.join(os.path.dirname(cwd), 'scenarios', case, 'plots')
if not os.path.exists(outputDir):
    os.makedirs(outputDir)

### Read site(bore) - weight data
zones = pd.read_csv(os.path.join(ws, 'site2zone.csv'), header = None, usecols = [0,2], names = ['site', 'weight'])
# zones['weight'] = zones['weight'].replace(to_replace=0.0, value = 99999)   ##replace 0 with some high value as it is a divided weight
zones = zones[zones['weight'] != 0]
z = zones.groupby('site')['weight'].apply(list).to_dict()


### READ STOMP RELEASE RATE DATA
def read_ssm_resampled():

    bore_list = os.listdir(os.path.join(ws))
    result_files = []
    for bore in bore_list:
        # print(bore)
        result_files.append(glob.glob(os.path.join(ws, bore, 'resampled.csv')))
        # file = pd.read_csv(os.path.join(ws, bore, 'resampled.csv'))
    result_files = [x for x in result_files if x != []]  ## 100-D-100-unexv_1 is empty!
    result_files = [i for sub in result_files for i in sub] ##flatten into one list

    ##structuring for release rates
    rrs = {}
    for file in result_files:
        # print(file)
        rrs[file.split('\\')[-2]] = pd.read_csv(file) ## file.split sets bore name as key directy from path. depends on bore name location in path
    rrs2 = dict([(k,v) for k, v in rrs.items() if k in z.keys()]) ##isolate to bores only within z (weight > 0)

    ## unit conversion and multiplier factor/weight --  multiplier (mult) different for each bore
    ## weights are taken from site2zone.csv. Some differences with weights used by Helal's R scripts. Check this.
    for bore, mult in z.items():
        print(mult[0])
        rrs2[bore]['rr'] = (rrs2[bore]['sum/dt'] * 365.25 / 1000000) / mult[0]  ##Daily to annual, ug to g.

    return rrs, rrs2    ## return both for QA and plotting -- rrs2 is final

### READ WATER TABLE DATA

def read_wt_data(rrs2, sps):

    wtpath = os.path.join(os.path.dirname(cwd), 'scenarios', case, 'bc_mod2obs')
    wt_files = glob.glob(os.path.join(wtpath, 'make*.csv'))
    wts = {}
    #re.split('[\\\\_.]', k)[-2]
    for file in wt_files:
        print(file)
        ## Take only first set when E and W water tables are the same (see script + plots from 02_plot_WT_BCs.py)
        wts[re.split('[\\\\_.]', file)[-2]] = pd.read_csv(file).iloc[:len(sps)] ## dict key is set as bore name using regex split (splits by multiple strings)

    ## 3. APPEND WT HEADS TO RRS2 DFs
    for bore in list(rrs2.keys()):
        for wt in list(wts.keys()):
            print(wt)
            if wt in bore:
                rrs2[bore]['Head'] = wts[wt]['Head']

    return wts

#### 4. PLOTTING
def plot_release_rates(rrs2, wts):
    """
    Resulting plot of release rate curves at each bore
    """

    ## create a dict of full site name for plot outputs
    sites = ['100-D-100 Excavation Pit',
                       '100-D-100 Excavation Slope',
                       '100-D-100 Sidewall',
                       '100-D-56 Pipeline',
                       '100-D-56 Pipeline',
                       '100-D-56 Pipeline',
                       '100-H-46 Excavation Pit',
                       '100-H Retention Basin',
                       '100-H Retention Basin Excavation Pit',
                       '100-H Retention Basin Excavation Pit',
                       '100-H Solar Evaporation Basin']
    title_dict = dict(zip(rrs2.keys(), sites))      ## make sure key-val pairs match as expected


    lib = plt.style.library
    plt.rcParams.update({'font.size': 17})
    plt.rcParams['xtick.labelsize'] = 17
    plt.rcParams['ytick.labelsize'] = 17
    plt.rcParams['legend.fontsize'] = 17

    x = pd.to_datetime(wts['100-D-100']['Date']) ##snag date column from any of the wts dataframes as x axis

    if year == '2022':
        xmin = pd.to_datetime('01-01-2014')
        xmax = pd.to_datetime('01-01-2023')
    elif year == '2032':
        xmin = pd.to_datetime('01-01-2023')
        xmax = pd.to_datetime('01-01-2033')
    elif year == '2125':
        xmin = pd.to_datetime('01-01-2023')
        xmax = pd.to_datetime('01-01-2126')

    for bore in rrs2.keys():
        if rrs2[bore]['rr'].all() > 0:          ##do not plot when rr = 0 over entire timeseries
            mean = [rrs2[bore]['Head'].mean()] * len(rrs2[bore]['Head'])
            fig, ax = plt.subplots(figsize = (10,6))
            # ax.set_title(f'Cr(VI) at {bore}')
            ax.set_title(f'Cr(VI) at {title_dict[bore]}')
            ax.plot(x, rrs2[bore]['rr'], color = 'xkcd:crimson', label  = 'Release Rate')
            # ax.plot(rrs2[bore], rrs2[bore]['rr'], color='red', label='Release Rate')
            ax.grid(True)
            ax.set_xlabel('Year')
            ax.set_ylim(0, rrs2[bore]['rr'].max()*1.3)      ##axis limits a function of individual RR curves
            ax.set_xlim(xmin,xmax)
            ax.set_ylabel('Release Rate (kg/year)')

            ax2 = ax.twinx()
            ax2.plot(x, rrs2[bore]['Head'], label = 'Water Table')
            ax2.plot(x, mean, '--', color='purple', linewidth=2, label = 'Average Water Table')
            ax2.set_ylabel('Water Table Elevation (m)')
            ax2.set_ylim(rrs2[bore]['Head'].min()*0.98, rrs2[bore]['Head'].max()*1.01) ##axis limits function of specific WT location

            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            labels3 = [fill(l, 20) for l in labels]
            labels4 = [fill(l, 20) for l in labels2]
            ax.legend(lines + lines2, labels3 + labels4)

            ##tick parameters to be adjusted between calibration/prediction case
            ax.tick_params(axis='x', rotation=45)
            # ax.xaxis.set_major_locator(mdates.YearLocator(10))           ## labeled tick marker every 5 years
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax.xaxis.set_minor_locator(mdates.YearLocator())

            plt.tight_layout()
            # plt.show()
            plt.savefig(os.path.join(outputDir, f'{bore}_2023_2125.png'))

    return None

if __name__ == '__main__':

    ## 108 stress periods in the 2014-2022 calibration model.
    ## 120 stress periods in the 2023 - 2032 predictive end-of-pumping model
    ## 598 stress periods in the 2023 - 2125 predictive end-of-simulation model
    year = '2125'
    if year == '2022':
        sps = range(1, 109)
    elif year == '2032':
        sps = range(1,121)
    elif year == '2125':
        sps = range(1,599)

    rrs, rrs2 = read_ssm_resampled()

    wts = read_wt_data(rrs2, sps)

    plot_release_rates(rrs2, wts)

# mean2 = pd.DataFrame()
# for bore in rrs2.keys():
#     if rrs2[bore]['rr'].all() > 0:
#         print(bore)
#         temp_df = pd.DataFrame([rrs2[bore]['Head'].mean()], index = [bore], columns = ['Averate WT'])
#         mean2 = pd.concat([temp_df, mean2])
#
# mean2.to_csv(os.path.join(ws, '..', '..', 'Average_WTs_at_bores.csv'))