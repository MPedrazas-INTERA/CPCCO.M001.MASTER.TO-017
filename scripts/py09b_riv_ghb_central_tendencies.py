# -*- coding: utf-8 -*-
"""
Created on Wed May 11 10:28:24 2022
Updated 2023

@author: RWeatherl

Script explores statistical trends general head boundaries and river stage packages used for the 100-H calibration model (2014 - present)
    used to to identify one (or more) "representative" stress periods to be used for predictive model.
    
First, reads in the respective packages and structures their information into dataframes.

Second, calculates the statistical distribution of a number of random grid cell samples.
     - the first stress period is isolated in order to have one copy of each cell in the model grid.
     - random sample of cells are selected, and a "cell number" is attributed to each of these random samples
         (one cell number is simply easier than working with layer-row-column trio). This
         random selection is used to clip the dataframe with all stress periods into a frame
         that only contains those random cells for each sp.
     -  the 50th percentile is taken by ordering the resulting dataframe from lowest value to highest, and
         selecting the median value (in the case of an even number of stress periods,
                                     take the higher ranked value of the two middle values)
     - an empirical cumulative distribution function (ECDF) is calculated and plotted automatically using
         the statsmodels package. This helps to identify any potential trends (or lack thereof) between samples.
         The most representative SPs are those that lie within the highest concentration of plotted ECDFs. Generally there
         are a few to choose from -- user discretion

Changes to be made for different models: relative paths and model file names
                                         ghb_bounds - row location of GHB boundary line
                                         sps - number of stress periods in model


UPDATE 2023: H.Pham detailed how RIV stages were calculated and gave raw data. This data used to find median values/SPs
    at these control points. Since RIV cells are bimodal, these were used to determine which SP to use. The same
    SP used for GHB to ensure same hydraulic conditions.

"""

import os
import pandas as pd
# import statsmodels
from statsmodels.distributions.empirical_distribution import ECDF
import numpy as np
import re
import itertools
from itertools import cycle
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')

plt.style.use('seaborn-whitegrid')

cwd = os.getcwd()
outputDir = os.path.join(cwd, 'output', 'riv_ghb_central_tendencies')
model_ws = os.path.join(os.path.dirname(cwd), 'model_files', 'flow_2014_2022')

# River stage values read in from file that has "control point" measurements.
def read_riv_ctrl_pts(sps):

    ## river control points
    riv_pts = pd.read_excel(os.path.join(cwd, 'output', 'riv_ghb_central_tendencies', 'RiverStage_monthly.xlsx'))
    riv_pts.index = sps  ## sets stress periods as index

    ## actual median values (mean of two middle entries)
    mH = riv_pts['H_GAUGE'].median()
    mD = riv_pts['D_GAUGE'].median()

    ## Stress periods associated with middle entries -- note that median SPs come out the same regardless of ranking by H_ or G_GAUGE
    ## note: the index is 0-based, but the sps are 1-based.
    median_H = pd.DataFrame(riv_pts.sort_values(by = 'H_GAUGE')).reset_index()
    median_D = pd.DataFrame(riv_pts.sort_values(by = 'D_GAUGE')).reset_index()

    median_H.rename({'index': 'SP'}, axis = 1, inplace = True)
    median_D.rename({'index': 'SP'}, axis=1, inplace=True)

    return median_H, median_D

## open GHB file and manipulate. Assumes the split between 'bhead' and 'conductivity' columns is at 40 characters.
## input -- GHB bounds is row (or column) where GHB is located. sps is range of number of sps
def read_ghb(ghb_bounds, sps):

    ###FIRST: Read and structure data
    print('reading GHB pckg')
    values_ghb = []
    with open(os.path.join(model_ws, '100hr3.ghb')) as f:
        for line in itertools.islice(f, 4, None):
            line = ' '.join(line[i:i+40] for i in range(0, len(line), 40))  ##insert space between bhead and cond (40 chars in)
            line = re.split(r'\s+', line)                                   ##separate string values and hold as list
            line = list(filter(None, line)) #filter to remove empty cells
            values_ghb.append(line)

    ghb = pd.DataFrame(values_ghb,
                       columns = ['layer', 'row', 'column', 'bhead', 'conductivity', 'xyz'])
    print('done reading GHB')

    ### SECOND: Select cells at random for statistical analysis
    sp1_ghb = ghb.loc[ghb['column'] == 'Stress'].index[0]  ## end of first stress period
    ##isolate first stress period to sample layer-row-columns from.
    ghbSamples = ghb.iloc[:sp1_ghb].loc[ghb['row'] == ghb_bounds].sample(n=50, random_state = 1)  ## pick number of random samples as deemed appropriate. random_state = 1 ensures reproducibility
    ghb_lrc = ghbSamples.copy()[['layer', 'row', 'column']]
    ghb_lrc['cell'] = range(len(ghb_lrc))  ## define unique indexer for lrc trio

    ## 108 stress periods in the 2014-2022 calibration model. each unique cell should have 108 values attached to it.
    sps_cycle = cycle(sps)

    df_ghb_samples = pd.merge(ghb_lrc, ghb, how='inner').loc[:, ['layer', 'row', 'column', 'bhead', 'cell']].astype(float)  ##grab all instances of the sampled lrc trios over all sps
    df_ghb_samples['stress period'] = [next(sps_cycle) for sp in range(len(df_ghb_samples))]
    df_ghb_samples['cell'] = df_ghb_samples['cell'] #.astype(int)

    ## sanity check
    ## pick a layer and row from df_ghb_samples and extract from base ghb df. Should match the bhead values per SP in df_ghb_samples for layer and column chosen (row is always 433)
     # t = ghb.loc[ghb['layer'] == '3'].loc[ghb['column'] == '81']

    return ghb, df_ghb_samples




## or if we want to take random samples, read from the RIV package...
def read_riv(sps):

    # open RIV file and manipulate
    print('reading RIV pckg')
    values_riv = []
    with open(os.path.join(model_ws, '100hr3.riv')) as f2:
        for line in itertools.islice(f2, 4, None):
            line = ' '.join(line[i:i+40] for i in range(0, len(line), 40))  ##insert space between stage and cond (40 chars in)
            line = re.split(r'\s+', line)                                   ##separate string values and hold as list
            line = list(filter(None, line)) #filter to remove empty cells
            values_riv.append(line)

    print('done reading RIV')

    riv = pd.DataFrame(values_riv,
                       columns = ['layer', 'row', 'column', 'stage',  'condfact', 'rbot', 'xyz'])


    sp1_riv = riv.loc[riv['column'] == 'Stress'].index[0]  ## end of first stress period
    rivSamples = riv.iloc[:sp1_riv].sample(n=50, random_state = 1)    ## pick number of random samples as deemed appropriate.
    riv_lrc = rivSamples.copy()[['layer', 'row', 'column']]
    riv_lrc['cell'] = range(len(riv_lrc))

    ## 108 stress periods in the 2014-2022 calibration model. each unique cell should have 108 values attached to it.
    sps = cycle(sps)

    df_riv_samples = pd.merge(riv_lrc, riv, how='inner').loc[:, ['layer', 'row', 'column', 'stage', 'cell']].astype(float)
    df_riv_samples['stress period'] = [next(sps) for sp in range(len(df_riv_samples))]
    df_riv_samples['cell'] = df_riv_samples['cell'].astype(int)

    # sanity check
    # pick a layer, row, col from df_riv_samples and extract from base riv df. Should match the stage values per SP in df_riv_samples for layer and column chosen
    # check this for a few of the samples in df_riv_samples
    #  t = riv.loc[riv['layer'] == '4'].loc[riv['row'] == '47'].loc[riv['column'] == '460']

    return riv, df_riv_samples


def calculate_representative_sp(df_ghb_samples, df_riv_samples):

    p50_ghb = []
    p_ghb = pd.DataFrame()
    for i in df_ghb_samples.cell.unique():
        cell = df_ghb_samples.loc[df_ghb_samples.cell == i]
        cell.sort_values(by='bhead', inplace=True)
        cell.reset_index(
            inplace=True)  # now the dataframe index is the RANK. ## !remember: the number of ranks = number of stress periods, but rank number != stress period
        p50_ghb.append(cell.iloc[int(len(sps) / 2)])  ## middle sp - 50% of data fall below this value
        p_ghb = pd.concat([cell])

    p50_ghb_df = pd.DataFrame(p50_ghb).loc[:, ['layer', 'row', 'column', 'bhead', 'stress period', 'cell']]

    p_ghb.drop(columns='index', inplace=True)
    p_ghb['percentile'] = (p_ghb.index / int(len(sps) / 2)) * 100
    p_ghb.sort_values(by=['stress period'], inplace=True)

    p50_riv = []
    p_riv = pd.DataFrame()
    for cell in df_riv_samples.cell.unique():
        cell = df_riv_samples.loc[df_riv_samples.cell == cell]
        cell.sort_values(by='stage', inplace=True)
        cell.reset_index(inplace=True)
        p50_riv.append(cell.iloc[int(len(sps) / 2)])  ## this is 43rd entry - 50% of data fall below this value
        p_riv = pd.concat([cell])

    p50_riv_df = pd.DataFrame(p50_riv).loc[:, ['layer', 'row', 'column', 'stage', 'stress period', 'cell']]
    p50_riv_df.sort_values(by='stress period', inplace = True)

    p_riv.drop(columns='index', inplace=True)
    p_riv['percentile'] = (p_riv.index / int(len(sps) / 2)) * 100
    p_riv.sort_values(by=['stress period'], inplace=True)

    return p_ghb, p50_ghb_df, p_riv, p50_riv_df


#%% Plot ECDFs for visual analysis, and read out P50 tables

def plot_ecdf():

    from itertools import cycle
    lines = ['-','--','-.',':','-..']
    linecycler = cycle(lines)


    lib = plt.style.library
    plt.rcParams.update({'font.size': 15})
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['font.size'] = 15
    plt.rcParams['legend.fontsize'] = 12

    fig, ax = plt.subplots()
    ## calc 50P, construct ECDF, plot. Plot gives a good idea of what an "average" SP profile looks like thru time
    for cell in df_ghb_samples['cell'].unique():
        sample = list(df_ghb_samples['bhead'].loc[df_ghb_samples['cell']==cell])  ##remember -- cell # is tied to random samples
        ecdf_ghb = ECDF(sample)
        ax.plot(ecdf_ghb.x, ecdf_ghb.y, next(linecycler), label = f'cell {cell}')
        ax.set_title('GHB')
        ax.set_xlabel('bhead (m.asl)', fontsize = 12)
        ax.set_ylabel('cumulative distribution', fontsize = 12)
        ax.set_yticks(np.arange(0,1,.1))
        ax.legend(bbox_to_anchor=(1,1), loc="upper left")
        plt.show()

        # plt.savefig(os.path.join(outputDir, 'GHB_ECDF_50samples.png'))


    # fig, ax = plt.subplots(figsize = (20,10))
    # ##50th percentile
    # p50_riv_dict = {}
    # for cell in df_riv_samples['cell'].unique():
    #     sample = list(df_riv_samples['stage'].loc[df_riv_samples['cell']==cell])
    #     p50_riv_dict[cell] = np.percentile(sample, 50)
    #     ecdf_riv = ECDF(sample)
    #     # ecdf_riv[sample] = ecdf(sample)
    #     ax.set_title('RIV')
    #     ax.set_xlabel('stage (m.asl)', fontsize = 12)
    #     ax.set_ylabel('cumulative distribution', fontsize=12)
    #     ax.plot(ecdf_riv.x, ecdf_riv.y, next(linecycler), label = f'cell {cell}')
    #     ax.set_yticks(np.arange(0,1,.1))
    #     ax.legend(bbox_to_anchor=(1,1), loc="upper left")
    #     plt.show()

        # plt.savefig(os.path.join(outputDir, 'RIV_ECDF_50samples.png'))


    return None

if __name__ == "__main__":

    ghb_bounds = '433'  ## row location of GHB boundary line
    sps = range(1, 109)  ## 108 stress periods in the 2014-2022 calibration model.

    ghb, df_ghb_samples = read_ghb(ghb_bounds, sps)
    # riv, df_riv_samples = read_riv(sps)
    riv = read_riv(sps)

    # p_ghb, p50_ghb_df, p_riv, p50_riv_df = calculate_representative_sp(df_ghb_samples, df_riv_samples)

    plot_ecdf(df_ghb_samples)

    # p50_ghb_df.to_csv(os.path.join(outputDir, 'p50_GHB_50samples.csv'), index = False)
    # p50_riv_df.to_csv(os.path.join(outputDir, 'p50_RIV_50samples.csv'), index=False)
    #

    # ghb_summary = p50_ghb_df.describe()
    # riv_summary = p50_riv_df.describe()
    #
    # for i in riv['xyz'].unique():
    #     riv.loc[riv['xyz'] == i]['stage'].astype('float').plot()