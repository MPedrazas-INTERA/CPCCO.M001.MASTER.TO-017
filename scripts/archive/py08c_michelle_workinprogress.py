"""
This script generates Cr concentration time sreies plots of simulated and observed concn.
Simulated concentration can be from UCN or TOB output files.

@author: MPedrazas based on @HPham's script for 100-BC
"""

import numpy as np
import flopy.utils.binaryfile as bf
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import BoundaryNorm, Normalize, LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import geopandas as gpd
import datetime as dt
import matplotlib.image as mpimg
import time
import math

def create_new_dir(directory):
    try:
        os.stat(directory)
    except:
        os.mkdir(directory)
        print(f'Created a new directory {directory}\n')

def read_ucn(ifile_ucn, precision):
    ucnobj = bf.UcnFile(ifile_ucn, precision=precision)
    times = ucnobj.get_times()
    data = ucnobj.get_alldata(mflay=None, nodata=-1)/1000 #dividing by 1000 to match units of Obs
    ntimes, nlay, nr, nc = data.shape
    print(f"UCN file dimensions- SPs: {ntimes}, Layers: {nlay}, Rows: {nr}, Columns: {nc}")
    df_times = pd.DataFrame(times)
    return data, ntimes, nlay, nr, nc, times

def read_head(ifile_hds, df, all_lays=False):
    """
       This fn will take in a data frame to loop through Rows, Columns, Times, Layers and extract Heads
       Input:  dataframe
               all_lays = False if you only want the 1st Layer OR
               all_lays = True if you want ALL the model layers
       """
    # import model heads
    hds_obj = bf.HeadFile(ifile_hds, verbose=False)
    times = hds_obj.get_times()
    data = hds_obj.get_alldata(mflay=None)
    ntimes, nlay, nr, nc = data.shape

    if all_lays:
        nlays = range(nlay)
    else:
        nlays = [0]
    vals = []
    for idx, row, col in zip(range(len(df)), df.i, df.j):
        for t_idx, t in enumerate(times):
            for lay in nlays:
                vals.append([data[t_idx][lay][row][col], t, lay + 1, row, col, df.Well_ID.iloc[idx]])  # 237 nodes * 84 times = 19908 vals for L1
    df_return = pd.DataFrame(vals, columns=['Head', 'Time', 'Layer', 'Row', 'Column', 'Well_ID'])
    df_return.drop_duplicates(inplace=True)
    return df_return

def read_file(ifile, delimiter_):
    cols = ['Well Name', 'Date', 'Time', 'Groundwater level (m)']
    # Read
    df = pd.read_csv(ifile, delimiter=delimiter_,
                     skipinitialspace=True, names=cols)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def plot_obs_btc(case, dfObs, wname, fig, ax, k, xylim, grid=True, colors=False, mode = 'normal'):

    ts = time.time()
    st = dt.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    # [1] plot observed concentration ---------------------------------
    dfObs['SAMP_DATE'] = pd.to_datetime(dfObs['SAMP_DATE'])
    dfObsSite = dfObs[dfObs['SAMP_SITE_NAME'] == wname]
    # print(f"Observations for {wname}: {len(dfObsSite)}")
    if (len(dfObsSite) > 0) & (mode != 'mod2obs'): #if there are observations, include a 2014-01-01 timestamp with no data to avoid the date axis from messing up.
        if dfObsSite.SAMP_DATE.iloc[0] != pd.to_datetime(sdate):
            # print(dfObsSite.SAMP_DATE.iloc[0])
            d_row = pd.Series([wname, pd.to_datetime(sdate), np.nan, 31], index=dfObsSite.columns)
            dfObsSite = dfObsSite.append(d_row, ignore_index=True)
            dfObsSite.sort_values(by=['SAMP_DATE'], inplace=True)
    if mode == 'PEST':
        ycol = 'conc2'
        label2use = f'{case}'
        legend_ = True
    if mode == 'mod2obs':
        ycol = 'WeightedConc'
        label2use = f'{caseDict[case]}'#f'mod2obs_{case}'
        legend_ = False
    else:
        ycol = 'STD_VALUE_RPTD'
        label2use = f'Observed'
        legend_ = False #toggle this ON if mode is mod2obs or OFF otherwise.

    styleDict = ['-', '--', '-.', ':']
    if case == 'calibrated_transport_model':
        counter = 0
    if case == 'no_source_transport_model':
        counter = 1
    if colors: #same plot, so each obs plot needs to be a different color
        if case == 'no_source_transport_model':
            dfObsSite[f"{ycol}"] = dfObsSite[f"{ycol}"]*1000 #the UCN is 1000 times smaller than a normal calib run.

        dfObsSite.plot(ax=ax, x='SAMP_DATE', y=ycol,
                       style=styleDict[counter],
                       #style = ['--o'],
                       linewidth=1.3,  # edgecolors='#bdbdbd',  # facecolor='#feb24c',
                       alpha=1, label = label2use, legend=legend_, zorder=9)  # style=['o']

    else: #subplots, so obs will always be blue
        dfObsSite.plot(ax=ax, x='SAMP_DATE', y=ycol,
                       markersize=2, style=['--o'], label = label2use,
                       linewidth=1,  c='k',  # edgecolors='#bdbdbd',  # facecolor='#feb24c',
                       alpha=1, legend=legend_, zorder = 9)  # style=['o']

    # Turn on the minor TICKS, which are required for the minor GRID
    ax.minorticks_on()

    ### Turn this on or off depending on whether odd or even number of models (if odd, comment this out)
    if grid:
        ax.grid(which='major', linestyle='-',
                linewidth='0.1', color='red')
        ax.grid(which='minor', linestyle=':',
                linewidth='0.1', color='black')
        ax.set_xlim([xylim[0], xylim[1]])
    else:
        pass


    if (mode == 'PEST') or (mode == 'mod2obs'):
        # plt.legend()
        ax.set_xlim([xylim[0], xylim[1]])
        ax.set_title(wname)
        print(wname)
        ax.set_ylabel('Cr(VI) (ug/L)')
        ax.set_xlabel('Time (years)')

    if k == 0: #k is figure counter
        # print(k)
        ax.text(xylim[0], 4,
                f'ver: {st}', fontsize=7, color='grey', alpha=0.1)
        # ax.legend(fontsize='small', loc='upper left')
    return fig, ax

def plot_btc(dfObs, dfMaxCatPoint, wname, nlay, fig, ax, k, sce, ucn, zn, ocn, xylim, well_labels=False):
    ts = time.time()
    st = dt.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    # [1] plot simulated concentration --------------------------------
    col2plt = f'{wname}'
    if ocn == '':
        if well_labels:
            ax.plot(dfMaxCatPoint['Time_year'], dfMaxCatPoint[col2plt],legend=False,
                               style=['-'],  grid=True, alpha=0.8, linewidth=1., label = f'{wname}_{ucn}')  # label='River Stage (m)' color='#de2d26',
        else:
            dfMaxCatPoint.plot(ax=ax, x='Time_year', y=col2plt,legend=False,
                               style=['-'], grid=True, alpha=0.8, linewidth=1., label=f'{ucn}', color='blue')  # label='River Stage
    elif ucn == '':
        if well_labels:
            dfMaxCatPoint.plot(ax=ax, x='Time_year', y=col2plt,legend=False,
                               style=['-'],  grid=True, alpha=0.8, linewidth=1., label = f'{wname}_{ocn}')  # label='River Stage (m)' color='#de2d26',
        else:
            dfMaxCatPoint.plot(ax=ax, x='Time_year', y=col2plt, legend=False,
                               style=['-'],  grid=True, alpha=0.8, linewidth=1., label = f'{ocn}', color='blue')  # label='River Stage (m)' color='#de2d26',
    ax.set_xlim([xylim[0], xylim[1]])
    if layer_comp:
        ax.set_title(f'{wname}_L{k+1}')
    else:
        ax.set_title(wname)
    ax.set_ylabel('Cr(VI) (ug/L)')
    ax.set_xlabel('Time (years)')
    ax.minorticks_on()
    ax.grid(which='major', linestyle='-',
            linewidth='0.1', color='red')
    ax.grid(which='minor', linestyle=':',
            linewidth='0.1', color='black')
    if k == 0:  #k is figure counter
        pass
        # ax.legend(loc = 'best')
        # ax.text(xylim[0], 4,f'ver: {st}', fontsize=7, color='grey', alpha=0.1)
    return fig, ax

def plot_hds(dfHds, fig, ax, k, wname):
    ax2 = ax.twinx()
    dfHds.Time = pd.to_timedelta(dfHds.Time, unit="days")
    dfHds['Time_year'] = dfHds.Time + pd.to_datetime(sdate)
    plot3 = ax2.plot(dfHds.Time_year, dfHds.Head, color='gray', label="Simulated Heads", alpha=0.4, zorder=1)
    ax2.axhline(y=dfHds.Head.mean(), color='gray', linestyle='dashed', label="Avg WL", alpha=0.4, zorder=1)
    if wname.startswith('199-D'):
        ax2.set_ylim([110, 120])
    elif wname.startswith('199-H'):
        ax2.set_ylim([100, 120])
    ax2.set_ylabel('Head (m)')
    ax2.grid(which='major', axis='both', linestyle='-',
            linewidth='0.1', color='grey', alpha = 0.25)
    if k == 0: #k is figure counter
        pass
        # ax2.legend(fontsize='small', loc='upper right')
    return fig, ax, ax2

def btc_subplot3(dic_ucn_files, plt_id, dfLoc, dfObs, zn, sdate, xylim, outputdir, dfHds, grid=True):
    '''
    # subplot for 8 selected wells,
    # All BTCs (from different scenarios) in a subplot
    '''
    size = len(plt_id)
    if size == 6:
        fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(
            16, 6), sharex=True, sharey=False)
    if size == 5:
        fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(
            16, 6), sharex=True, sharey=False)
    elif size == 4:
        fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(
            12, 6), sharex=True, sharey=False)
    elif size == 3:
        fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(
            16, 3), sharex=True, sharey=False)
    elif size == 2:
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(
            12, 3), sharex=True, sharey=False)

    # Plot sim conc
    for u, ucn in enumerate(dic_ucn_files):
        ifile_ucn = dic_ucn_files[ucn]
        print(f'case={ucn}, path2ucn = {ifile_ucn}\n')

        # [1] Load UCN data =======================================================
        precision = 'double'
        data, ntimes, nlay, nr, nc, times = read_ucn(ifile_ucn, precision)

        # [2] Date time conversion ---------------------------------------------
        df = pd.DataFrame()
        df['Time_day'] = times
        df.Time_day = pd.to_timedelta(df.Time_day, unit="days")
        df['Time_year'] = df.Time_day + pd.to_datetime(sdate)

        # [3] Time series concentration at a location =========================
        dfMaxCatPoint = pd.DataFrame()
        dfMaxCatPoint['Time_year'] = df['Time_year'].copy()

        # [3.1] Get C time series at all obs wells ----------------------------
        fig_axes = [fig.axes[i - 1] for i in plt_id]
        # selected subplot
        for k, ax in enumerate(fig_axes):
            wname = dfLoc['Well_ID'].iloc[k]
            ir, ic, ilay = dfLoc['i'].iloc[k], dfLoc['j'].iloc[k], dfLoc['k'].iloc[k]
            cname = f'{wname}'
            # plot observed concentration
            if u == 0: #for each UCN file, plot OBS once.
                fig, ax = plot_obs_btc(dfObs, wname, fig, ax, k, xylim, grid=False, colors=False, mode = 'normal')

            dfMaxCatPoint.loc[:, cname] = data[:, ilay-1, ir-1, ic-1]
            # Generate BTC plots ----------------------------------------------
            ocn = ''
            fig, ax = plot_btc(dfObs, dfMaxCatPoint, wname, dfLoc.k.iloc[k], fig, ax, k, sce, ucn, zn, ocn, xylim, well_labels=False)
            # # Add heads to BTCs -----------------------------------------------
            if plot_head:
                well_head = dfHds.loc[dfHds.Well_ID == wname]
                #print("*****", dfHds.head())
                fig, ax, ax2 = plot_hds(well_head, fig, ax, k)
            if k == 0:
                if plot_head:
                    ax.legend(fontsize='small', loc='upper right')
                    ax2.legend(fontsize='small', loc='upper left')
                else:
                    ax.legend(fontsize='large', loc='upper right' )
            # Save time series of concentration at points
            ofile_csv = os.path.join(outputdir, 'csv', f'{ucn}_{wname}_L{k+1}_ucn.csv')
            dfMaxCatPoint.to_csv(ofile_csv, index=False)
        # save fig ------------------------------------------------------------
        plt.tight_layout()
        ofile = os.path.join(outputdir, f'Cr_{ucn}_{area}_ucn.png')
        fig.savefig(ofile, dpi=200, transparent=False, bbox_inches='tight')
        print(f'Saved {ofile}\n')

def btc_subplot3_tob(dic_ocn_files, dfLoc, plt_id, dfObs, zn, sce, sdate, odir4png, xylim, dfHds, grid=True, mode = 'normal'):
    '''
    # subplot for selected number of wells,
    # All BTCs (from different scenarios) in a subplot
    '''

    size = len(plt_id)
    if size == 6:
        fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(
            16, 6), sharex=True, sharey=False)
    if size == 5:
        fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(
            16, 6), sharex=True, sharey=False)
    elif size == 4:
        fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(
            12, 6), sharex=True, sharey=False)
    elif size == 3:
        fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(
            16, 3), sharex=True, sharey=False)
    elif size == 2:
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(
            12, 3), sharex=True, sharey=False)
    elif size == 1:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(
            5, 3))

    # Define fig size, it be easiest to do even/odds...room for improvement
    # fs = len(plt_id)  # figure size
    # nr = math.ceil(fs / 2)
    # fig, ax = plt.subplots(nrows=nr, ncols=2, figsize=(16, (3 * nr)), sharex=True, sharey=False)

    for o, ocn in enumerate(dic_ocn_files):
        path2ocn = dic_ocn_files[ocn]

        # [1] Convert ocn to csv ------------------------------------------
        if mode == 'PEST':
            ifile_ocn = f'{path2ocn}/Cr_sim_bySPs_PEST_run1.csv'
        elif mode == 'mod2obs':
            ifile_ocn = f'{path2ocn}/simulated_conc_mod2obs.csv'
        else:
            ocn2csv(path2ocn)
            ifile_ocn = f'{path2ocn}/STUFF_OCN.csv'
        print(f'case = {ocn}, path2file = {ifile_ocn}\n')

        # [2] Load data =======================================================
        df_ocn = pd.read_csv(ifile_ocn)
        df_ocn.drop_duplicates(inplace=True)

        # [3] Date time conversion ---------------------------------------------
        if mode != 'mod2obs':
            df = pd.DataFrame()
            df['Time_day'] = df_ocn.tte.unique()
            df.Time_day = pd.to_timedelta(df.Time_day, unit="days")
            df['Time_year'] = df.Time_day + pd.to_datetime(sdate)
            df.sort_values(inplace=True, by='Time_year')

            # =====================================================================
            # [3] Time series concentration at a location =========================
            # =====================================================================
            dfMaxCatPoint = pd.DataFrame()
            dfMaxCatPoint['Time_year'] = df['Time_year'].copy()

        # [3.1] Get C time series at all obs wells ----------------------------
        fig_axes = [fig.axes[i-1] for i in plt_id]
        # selected subplot
        for k, ax in enumerate(fig_axes):
            wname = dfLoc['Well_ID'].iloc[k]
            ir, ic, ilay = dfLoc['i'].iloc[k], dfLoc['j'].iloc[k], dfLoc['k'].iloc[k]
            cname = f'{wname}'
            # print(cname)

            # plot observed concentration
            if o == 0: #plot OBS for first OCN instance
                fig, ax = plot_obs_btc(ocn, dfObs, wname, fig, ax, k, xylim, grid=True, colors=False, mode= 'normal') #make grid False if total number of datasets is ODD
            if mode == 'PEST':
                fig, ax = plot_obs_btc(ocn, df_ocn, wname, fig, ax, k, xylim, grid=True, colors=True, mode = 'PEST')
            elif mode == 'mod2obs':
                fig, ax = plot_obs_btc(ocn, df_ocn, wname, fig, ax, k, xylim, grid=True, colors=True, mode = 'mod2obs')
            else: #normal TOB output
                a = df_ocn.conc.loc[(df_ocn.wellid == dfLoc['Well_ID'].iloc[k])]
                if len(a.values[:]) == len(df):  # number of SPs
                    dfMaxCatPoint[cname] = a.values[:]/1000
                    # print(dfMaxCatPoint[cname].head())
                    for m in range(len(dfMaxCatPoint)):
                        # print(dfMaxCatPoint[cname].iloc[m])
                        if isinstance(dfMaxCatPoint[cname].iloc[m], float):
                            # print(":)")
                            pass
                        else:
                            if ("-" in dfMaxCatPoint[cname].iloc[m]) and ("E-" not in dfMaxCatPoint[cname].iloc[m]):
                                print("typo from STUFF.ocn: ", cname)
                                dfMaxCatPoint[cname].iloc[m] = 0
                                # dfMaxCatPoint[cname].iloc[m] = str(dfMaxCatPoint[cname].iloc[m]).replace("-", "E-")
                                print(dfMaxCatPoint[cname].iloc[m])
                    dfMaxCatPoint[cname] = pd.to_numeric(dfMaxCatPoint[cname], downcast="float")  # make numeric

                    # Generate BTC plots ------------------------------------------
                    ucn = ''
                    # print(dfMaxCatPoint.head())
                    fig, ax = plot_btc(dfObs, dfMaxCatPoint, wname, dfLoc.k.iloc[k], fig, ax, k, sce, ucn, zn, ocn,
                                       xylim, well_labels=False)

                    # Save time series of concentration at points
                    ofile_csv = os.path.join(outputdir, 'csv', f'{ocn}_{wname}_tob.csv')
                    dfMaxCatPoint.to_csv(ofile_csv, index=False)
                    # print(f'Saved {ofile_csv}\n')

                else:
                    print(
                        f'*WARNING* Conc time series size does NOT match number of SPs: {dfLoc.Well_ID.iloc[k]} Layer {dfLoc.k.iloc[k]}')

            #If y-axis upper limit is <=50, make = 50.
            if (ax.get_ylim()[1] < 50):
                print(f"Warning. Y-axis upper limit is too low: {ax.get_ylim()[1]}\nUpdating to 50.")
                ax.set_ylim([-1, 50])
            else:
                print(ax.get_ylim()[1])

            # # Add heads to BTCs -----------------------------------------------
            if plot_head:
                well_head = dfHds.loc[dfHds.Well_ID == wname]
                fig, ax, ax2 = plot_hds(well_head, fig, ax, k, wname)

            if k == 0:
                if plot_head:
                    ax.legend(fontsize='small', loc='upper right')
                    ax2.legend(fontsize='small', loc='upper left')
                else:
                    ax.legend(prop={'size': 10}, loc='upper right' )

        # save fig ----------------------------------------------------------------
        # plt.tight_layout()
        # ofile = f'{odir4png}/Cr_{ocn}_{area}_tob.png'
        # fig.savefig(ofile, dpi=200, transparent=False, bbox_inches='tight')
        # print(f'Saved {ofile}\n')

    # # save fig ----------------------------------------------------------------
    plt.tight_layout()
    ofile = f'{odir4png}/Cr_allwells_{area}_tob.png'
    fig.savefig(ofile, dpi=200, transparent=False, bbox_inches='tight')
    print(f'Saved {ofile}\n')

def btc_1fig_multiple_wells_tob(wells, dic_ocn_files, dfLoc, dfObs, sce, sdate, odir4png, xylim, grid=True):
    '''
    # All BTCs (from different scenarios) in one plot
    '''
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(
        16, 9), sharex=True, sharey=True)

    print(dic_ocn_files)
    for i, ocn in enumerate(dic_ocn_files):
        path2ocn = dic_ocn_files[ocn]
        # Convert ucn to csv ------------------------------------------
        ocn2csv(path2ocn)

        ifile_ocn = f'{path2ocn}/STUFF_OCN.csv'
        print(f'case = {ocn}, path2file = {ifile_ocn}\n')

        # [1] Load data =======================================================
        df_ocn = pd.read_csv(ifile_ocn)
        df_ocn.drop_duplicates(inplace=True)
        # [] Date time conversion ---------------------------------------------
        df = pd.DataFrame()
        df['Time_day'] = df_ocn.tte.unique()
        df.Time_day = pd.to_timedelta(df.Time_day, unit="days")
        df['Time_year'] = df.Time_day + pd.to_datetime(sdate)

        # [3] Time series concentration at a location =========================
        dfMaxCatPoint = pd.DataFrame()
        dfMaxCatPoint['Time_year'] = df['Time_year'].copy()

        # [3.1] Get C time series at all obs wells ----------------------------
        for k, well in enumerate(wells):
            wname = well
            # print(wname)
            cname = f'{wname}'
            # print(cname)

            # plot observed concentration
            if i == 0:
               fig, ax = plot_obs_btc(dfObs, wname, fig, ax, k, xylim, grid, colors=True, mode = 'normal')

            a = df_ocn.conc.loc[(df_ocn.wellid == well)]
            if len(a.values[:]) == len(df):  # number of SPs
                dfMaxCatPoint[cname] = a.values[:]#/1000
                for m in range(len(dfMaxCatPoint)):
                    if ("-" in dfMaxCatPoint[cname].iloc[m]) and ("E-" not in dfMaxCatPoint[cname].iloc[m]):
                        print("typo from STUFF.ocn: ", cname)
                        dfMaxCatPoint[cname].iloc[m] = 0
                        print(dfMaxCatPoint[cname].iloc[m])
                dfMaxCatPoint[cname] = pd.to_numeric(dfMaxCatPoint[cname], downcast="float") #make numeric
                dfMaxCatPoint[cname].to_csv(os.path.join(odir4png, 'csv', f'{ocn}_{cname}.csv'))
                # print(f'Saved outputdir/csv/{ocn}_{cname}.csv')
                # Generate BTC plots ------------------------------------------
                ucn = ''
                ax = plot_btc(dfObs, dfMaxCatPoint, wname, 1, fig, ax, k, sce, ucn, zn, ocn, xylim, well_labels=True)
            else:
                print(
                    f'*WARNING* Concentration time series size does not match number of SPs: ',
                    dfLoc.Well_ID.loc['Well_ID' == wname],
                    ' Layer ',dfLoc.k.loc['Well_ID' == wname])

    ax.set_title('Well Comparison')
    # ax.legend()
    # Customize the major grid
    ax.grid(which='major', linestyle='-',
            linewidth='0.1', color='red')
    # Customize the minor grid
    ax.grid(which='minor', linestyle=':',
            linewidth='0.1', color='black')
    ax.set_xlim([xylim[0], xylim[1]])

    # save fig ----------------------------------------------------------------
    ofile = f'{odir4png}/Cr_allwells_{area}_tob.png'
    fig.savefig(ofile, dpi=200, transparent=False, bbox_inches='tight')
    # print(f'Saved {ofile}\n')

if __name__ == "__main__":

    cwd = os.getcwd()
    cluster = False
    ### Get path to pngs for run: ---------------------------------------
    if cluster:
        create_new_dir(os.path.join(os.path.dirname(cwd), 'BTCs'))
        outputbase = os.path.join(os.path.dirname(cwd), 'BTCs')
        odir = os.path.basename(cwd) #auto-updated.
    else:
        create_new_dir(os.path.join(os.path.dirname(cwd), 'output', 'Cr_simulated'))
        outputbase = os.path.join(os.path.dirname(cwd), 'output', 'Cr_simulated')
        odir = "BTCs_forPresentation" #"BTCs_forECF" #"qc_TOBv2" #UPDATE this directory - where figures will be SAVED


    outputdir = os.path.join(outputbase, odir)
    create_new_dir(outputdir)
    create_new_dir(os.path.join(outputdir, 'csv'))

    qc_TOB = False  # toggle ON when comparing UCN to TOB (qcTOB)
    if qc_TOB:
        list_loc = ['well_list_qcTOB.csv']
        layer_comp = True # toggle ON when comparing layers of UCN to qc TOB
        dic_id = {'100-D-100 Sidewall 2': [1, 2, 3, 4, 5, 6], #6
                  '183-H Solar Evaporation Basins 1': [1, 2, 3, 4, 5, 6]} #6
    else:
        list_loc = ['well_list_v3.csv']
        layer_comp = False  # toggle ON when comparing layers of UCN to qc TOB
        dic_id = {'100-D-100 Sidewall 1': [1, 2, 3, 4, 5],  # 5
                  '100-D-100 Sidewall 2': [1, 2, 3],  # 3
                  '100-D-100 Sidewall 3': [1, 2, 3, 4],  # 4
                  '100-D-56-2 Pipeline 1': [1, 2],  # 2
                  '100-D-56-2 Pipeline 2': [1, 2],  # 2
                  '100-H-46 Waste Site 1': [1, 2],  # 2
                  '100-H-46 Waste Site 2': [1, 2],  # 2
                  '107-H Retention Basin 1': [1, 2, 3, 4],  # 4
                  '107-H Retention Basin 2': [1, 2, 3, 4],  # 4
                  '183-H Solar Evaporation Basins 1': [1, 2],  # 2
                  '183-H Solar Evaporation Basins 2': [1, 2, 3]}  # 3

    # Get observed Cr(IV) concentration ---------------------------------------
    mode = 'mod2obs'
    # [1] use mode 'normal' when postprocessing TOB
    # [2] use mode 'PEST' when post-processing TOB output from PEST post-processing
    # [3] use mode 'mod2obs' when postprocessing mod2obs

    if cluster:
        dfObs = pd.read_csv(os.path.join(cwd, "Cr_obs_avg_bySPs.csv"))
    else:
        dfObs = pd.read_csv(os.path.join(os.path.dirname(cwd), "output", "Cr_obs_smooth", "Cr_obs_avg_bySPs.csv"))
    
    ### Get simulated Cr(IV) concentration---------------------------------------
    if cluster:
        wdir = cwd
        sce = 'ManCalib'
        cases = [odir]
    else:
        wdir = os.path.join(os.path.dirname(cwd))
        #wdir = os.path.join(os.path.dirname(cwd), 'input')
        sce = 'Manual' #'PEST' #'mod2obs' #PEST #'PEST'  # 'qc_TOB' #'Transport_2014-2020P18_CP'
        cases = ['calibrated_transport_model','no_source_transport_model'] #['try1','try2'] 'Calibration_v3', # cases = ['9_Model_RUM-NoFlow','8_Model_RUM-GHB']
        # caseDict = {'ManCalib_v10': 'Continuing Source', 'NoSource': 'No Source'}
        caseDict = {'calibrated_transport_model': 'Continuing Source', 'no_source_transport_model': 'No Source'}
    zn = 'all_zones'

    dic_ucn_files, dic_ocn_files = {}, {}
    for case in cases:
        if cluster:
            dic_ocn_files[f'{case}'] = f'{wdir}'
        else:
            dic_ocn_files[f'{case}'] = f'{wdir}/{case}'  #f'{wdir}/{sce}/{case}' # PESTrun qc TOB

    ### Timespan for Cr(IV) concentration timeseries plots ---------------------------------------
    sdate = '2014-01-01'  #model start time
    if qc_TOB:
        xylim = [dt.datetime(2014, 1, 1), dt.datetime(2014, 12, 31), 0, 100] #first 12SPs for qcTOB
    else:
        xylim = [dt.datetime(2014, 1, 1), dt.datetime(2020, 12, 31), 0, 100]

    plot_head = False #adds secondary axis with simulated WLs for wells of interest.
    if cluster:
        path2hds = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(cwd))), 'flow', 'Model_RUM-GHB', 'DHmodel_2014to2020.hds')
    else:
        path2hds = os.path.join(os.path.dirname(cwd), 'model_files', 'flow', 'Model_RUM-GHB', 'DHmodel_2014to2020.hds')

    # =========================================================================
    # no changes after this line ----------------------------------------------
    # -------------------------------------------------------------------------

    for ifile_loc in list_loc:
        if cluster:
            df = pd.read_csv(os.path.join(cwd, f'{ifile_loc}'))
        else:
            df = pd.read_csv(os.path.join(os.path.dirname(cwd), 'input', f'{ifile_loc}'))
        if plot_head:
            dfHds = read_head(path2hds, df, all_lays=False)
            print(dfHds.head())
        else:
            dfHds = pd.DataFrame()
            print("No head values")
        plot_individual_wells = True
        if not plot_individual_wells:
            for area in df.Area.unique(): #plot by Area
                print(area)
                dfLoc = df.loc[df.Area == area]
                #Function 1: Post-process TOB or MOD2OBS output
                btc_subplot3_tob(dic_ocn_files, dfLoc,
                             dic_id[area], dfObs, zn, sce, sdate, outputdir, xylim, dfHds, grid=True, mode=mode)
        else:  #plot individual wells
            for area in df.Well_ID.unique(): #using Well_ID instead of area for individual plots
                print(area)
                dfLoc = df.loc[df.Well_ID == area]
                #Function 1: Post-process TOB or MOD2OBS output
                btc_subplot3_tob(dic_ocn_files, dfLoc,
                             [1], dfObs, zn, sce, sdate, outputdir, xylim, dfHds, grid=True, mode=mode)

        #Unused functions for model:
        # Function 2: Post-process UCN
        # btc_subplot3(dic_ucn_files, dic_id[area], dfLoc, dfObs, zn, sdate, xylim, outputdir, dfHds, grid=True)
        #Function 3: Post-process TOB for certain wells
        # btc_1fig_multiple_wells_tob(['199-D5-34', '199-D5-151'], dic_ocn_files, df,
        #                 dfObs, sce, sdate, outputdir, xylim, grid=False)


