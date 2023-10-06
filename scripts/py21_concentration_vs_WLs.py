"""
Plotting functions:
Simulated and observed water levels + simulated and observed Cr(VI) concentrations timeseries
Scatter plots of simulated and observed water levels
Residual/error plots of observed-simulated vs observed water levels
"""

import numpy as np
import os
import flopy.utils.binaryfile as bf
import pandas as pd
import matplotlib.pyplot as plt
import flopy
import geopandas as gpd
import matplotlib
matplotlib.use('Qt5Agg')
from sklearn.metrics import mean_absolute_error,  mean_squared_error, r2_score

plt.rc('xtick', labelsize=14)
plt.rc('ytick', labelsize=14)

def plot_WL_vs_conc(wl_meas, crvi_meas_1, crvi_meas_2, wl_df, conc_df):

    """
    Plot concentration data of interest against water levels in one graph.
    May be used to plot either measured data or simulation results.
    Inputs: water level dataframe, concentration dataframe, data type
    dtype options: simulated, measured, or both. Simply to control style.
    Common errors: double check column names (e.g. "NAME" vs "ID", "time" vs "Date", etc.)
        rename columns outside of function for consistency.
    """
    outputDir = os.path.join(cwd, 'output', 'concentration_vs_WL_plots', 'sim_2014_2023')
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

    for well in wells['NAME']:
        print(well)
        ## set data to be plotted
        toplot_wl = wl_df[wl_df['NAME'] == well]  ## match to the correct input when function is called
        toplot_crvi = conc_df[conc_df['NAME'] == well] ## match to the correct input when function is called

        cr1 = crvi_meas_1.loc[crvi_meas_1['SAMP_SITE_NAME'] == well]  ## match to the correct input when function is called
        try:
            cr2 = crvi_meas_2.loc[crvi_meas_2['NAME'] == well] ## match to the correct input when function is called
        except:
            pass
        wl1 = wl_meas[wl_meas['ID'] == well]

        ## create figure instance and set specs
        fig, ax = plt.subplots(figsize=(15, 5))
        ax.minorticks_on()
        ax.grid(which='major', linestyle='-',
                linewidth='0.1', color='red')
        ax.grid(which='minor', linestyle=':',
                linewidth='0.1', color='black')
        plt.xticks(rotation=45)
        ## conditional title color
        is_in_calibwells = well in calibwells['Well_ID'].values
        if is_in_calibwells:
            ax.set_title(f'{well}', color = 'red')
        else:
            ax.set_title(f'{well}', color = 'black')
        ax.set_ylabel('Water Level (m.asl)')
        ## create secondary axis and specs
        ax2 = ax.twinx()
        ax2.set_ylabel('Cr(VI) (μg/L)')

        ax.plot(toplot_wl['DATE'], toplot_wl['Head'], label='Simulated WL')
        ax2.plot(pd.to_datetime(toplot_crvi['DATE']), toplot_crvi['WeightedConc'], zorder=10,
                 c="darkred", label='Simulated Cr(VI)')
        ax.scatter(wl1.index, wl1['Water Level (m)'], label='Measured WL', c="navy", s=15)
        ax.plot(wl1.index, wl1['Water Level (m)'], c="navy", ls="--")

        ax2.scatter(pd.to_datetime(cr1.index), cr1['STD_VALUE_RPTD'], c='grey', s=15, zorder=1,
                    label='Measured Cr(VI)')  #
        ax2.plot(pd.to_datetime(cr1.index), cr1['STD_VALUE_RPTD'], zorder=10, c="grey",
                 ls="--", alpha=0.7)
        try:
            ax2.scatter(pd.to_datetime(cr2.index), cr2['STD_VALUE_RPTD'], c='magenta', s=15, zorder=1,
                        label='Measured Cr(VI) New')  #
            ax2.plot(pd.to_datetime(cr2.index), cr2['STD_VALUE_RPTD'], zorder=10, c="magenta", ls="--", alpha=1)
        except:
            pass

        ## combined legend
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc=0)
        ax.set_xlim(pd.to_datetime("2014-01-01"), pd.to_datetime("2023-07-31"))
        ax2.set_xlim(pd.to_datetime("2014-01-01"), pd.to_datetime("2023-07-31"))
        # plt.savefig(os.path.join(outputDir, f'{well}_V2.png'))
        plt.close()
    print("Done")

    return None

def crossplots_WL_individual(wls_obs, wls_sim, mode):

    """
    Generates a crossplot of simulated vs observed water levels (or other variable of interest)
    at discrete time points.
    """
    plt.rc('xtick', labelsize=14)
    plt.rc('ytick', labelsize=14)

    outputDir = os.path.join(cwd, 'output', 'water_level_plots', 'crossplots')
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

    for well in wells.NAME.unique():
        print(well)
        ## set data to be plotted
        wls_sim.index = wls_sim["DATE"]
        mywell_sim = wls_sim[wls_sim['NAME'] == well]
        mywell_obs = wls_obs[wls_obs['ID'] == well]

        toplot = pd.merge(mywell_obs, mywell_sim, left_index=True, right_index=True, how="inner")
        toplot.rename(columns={"Head": "Simulated", "Water Level (m)": "Observed"}, inplace=True)
        toplot.dropna(subset=["Observed"], inplace=True)

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.plot(toplot['Observed'], toplot['Simulated'], 'o', markerfacecolor="steelblue", markeredgecolor='blue',
                markeredgewidth=1,markersize=10, alpha =0.5, zorder=1)
        ax.plot([0, 1], [0, 1], color='red', linewidth=0.5, transform=ax.transAxes, zorder=10)

        ## conditional title color
        is_in_calibwells = well in calibwells['Well_ID'].values
        if is_in_calibwells:
            ax.set_title(f'{well} ({wellDict[well]})', color='navy', fontweight='bold', fontsize=14)
        else:
            ax.set_title(f'{well} ({wellDict[well]})', color='black', fontweight='bold', fontsize=14)

        ax.set_ylabel('Simulated Head 2021-2023 (m)', fontweight='bold', fontsize=14)
        ax.set_xlabel('Observed Head 2021-2023 (m)', fontweight='bold', fontsize=14)
        ax.set_xlim([112.8, 118])
        ax.set_ylim([112.8, 118])

        ax.minorticks_on()
        ax.grid(which='major', linestyle='-',
                linewidth='0.1', color='darkred')
        ax.grid(which='minor', linestyle=':',
                linewidth='0.1', color='black')
        plt.xticks(rotation=45)

        ### Add Statistics
        r2 = r2_score(toplot['Observed'], toplot["Simulated"]).round(3)  # r2:coefficient of determination
        mae = mean_absolute_error(toplot["Observed"], toplot["Simulated"]).round(3)
        ax.text(113, 117.75, '$\mathregular{r^2}$ = ' + str(r2), fontsize=14)
        ax.text(113, 117.5, f'MAE = {mae} m', fontsize=14)

        # plt.savefig(os.path.join(outputDir, f'{well}_{mode}.png'), bbox_inches='tight')
        plt.close()
        print("Done")
    return None

def crossplots_WL_subplots(wls_obs, wls_obs2, wls_sim, wls_sim2):

    """
    Generates grouped crossplots of simulated vs observed water levels (or other variable of interest)
    at discrete time points. Groups determined geospatially (riverside to inland, proximity to sources)
    """
    plt.rc('xtick', labelsize=14)
    plt.rc('ytick', labelsize=14)

    outputDir = os.path.join(cwd, 'output', 'water_level_plots', 'crossplots')
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

    group1 = ['199-H3-25', '199-H3-26', '199-H3-27']  ## Inland
    group2 = ['199-H3-2A', '199-H4-86']  ## Inland near 100-H-46 source
    group3 = [ '199-H4-84', '199-H4-88']  ## Midland near 183-H-SEB source
    group4 = ['199-H4-8', '199-H4-17', '199-H4-18', '199-H4-65', '199-H4-85', '199-H4-89'] ## Midland
    group5 = ['199-H4-4', '199-H4-5', '199-H4-12A', '199-H4-15A', '199-H4-64'] ## Riverside
    groups = [group1, group2, group3, group4,group5] #

    for val, grp in enumerate(groups):
        size = len(grp)
        if size == 6:
            fig, axes = plt.subplots(nrows=2, ncols=3, gridspec_kw={'width_ratios': [1,1,1]},
                                     figsize=(14, 8), sharex=False, sharey=False)
        if size == 5:
            fig, axes = plt.subplots(nrows=2, ncols=3, gridspec_kw={'width_ratios': [1,1,1]},
                                     figsize=(14, 8), sharex=False, sharey=False)
        elif size == 4:
            fig, axes = plt.subplots(nrows=2, ncols=2, gridspec_kw={'width_ratios': [1,1]},
                                     figsize=(14, 8), sharex=False, sharey=False)
        elif size == 3:
            fig, axes = plt.subplots(nrows=1, ncols=3, gridspec_kw={'width_ratios': [1,1,1]},
                                     figsize=(14, 4), sharex=False, sharey=False)
        elif size == 2:
            fig, axes = plt.subplots(nrows=1, ncols=2, gridspec_kw={'width_ratios': [1,1]},
                                     figsize=(9, 4), sharex=False, sharey=False)
        else:
            pass

        axes = axes.flatten()
        fig.suptitle('Groundwater Levels', fontweight='bold', fontsize = 14)
        for i, well in enumerate(grp):
            ax = axes[i]
            print("Well: ",well)
            flag = "True"
            for idx in range(2):
                print("Idx: ",idx)
                if idx == 0:
                    mywell_obs = wls_obs.loc[wls_obs['ID'] == well]
                    wls_sim.index = wls_sim["DATE"]
                    mywell_sim = wls_sim[wls_sim['NAME'] == well]
                    toplot = pd.merge(mywell_obs, mywell_sim, left_index=True, right_index=True, how="inner")
                    toplot.rename(columns={"Head": "Simulated", "Water Level (m)": "Observed"}, inplace=True)
                    toplot.dropna(subset=["Observed"], inplace=True)
                elif idx == 1:
                    try:
                        mywell_sim = wls_sim2[wls_sim2['Well'] == well]
                        mywell_obs = wls_obs2.loc[wls_obs2['Well'] == well]
                        #mywell_obs["Time1"] = mywell_obs.Time.apply(lambda x : x.replace(day=1)) #rounded down by 15 days
                        # mywell_obs.index = pd.to_datetime(mywell_obs.Time1)
                        # toplot = pd.merge(mywell_obs, mywell_sim, left_index=True, right_index=True, how="inner")
                        toplot = pd.merge(mywell_obs, mywell_sim, on="Time", how="inner")
                        # toplot.rename(columns={"Head": "Simulated", "Water Level (m)": "Observed"}, inplace=True)
                        toplot.dropna(subset=["Observed"], inplace=True)
                        print("Found: ",idx, well, len(toplot))
                        if len(toplot) == 0:
                            flag = "NA"
                    except:
                        print(f"{well} not found in 2014-2020 observations from MPR")
                        flag = "NA"
                        print("Not Found: ", idx, well, len(toplot))

                if idx == 0:
                    ax.plot(toplot['Observed'], toplot['Simulated'], 'o', markerfacecolor="steelblue", markeredgecolor='blue',
                            markeredgewidth=1, markersize=10, alpha=0.5, zorder=9, label = "2021 to 2023")
                    ax.plot([0, 1], [0, 1], color='red', linewidth=0.5, transform=ax.transAxes, zorder=10)
                elif idx == 1 and (flag != "NA"):
                    ax.plot(toplot['Observed'], toplot['Simulated'], 'o', markerfacecolor="olive", markeredgecolor='darkgreen',
                            markeredgewidth=1, markersize=10, alpha=0.5, zorder=8, label = "2014 to 2020")
                    ax.plot([0, 1], [0, 1], color='red', linewidth=0.5, transform=ax.transAxes, zorder=10)

                ### Add Statistics
                if idx == 0:
                    print("P5 stat: ",len(toplot))
                    r2 = r2_score(toplot['Observed'], toplot["Simulated"]).round(3)  # r2:coefficient of determination
                    mae = mean_absolute_error(toplot["Observed"], toplot["Simulated"]).round(3)
                    ax.text(113, 117.5, '2021 - 2022: ' + '$\mathregular{r^2}$ = ' + str(r2), fontsize=9)
                    ax.text(113, 117, '2021 - 2022: ' + f'MAE = {mae} m', fontsize=9)
                elif idx == 1 and (flag != "NA"):
                    r2 = r2_score(toplot['Observed'], toplot["Simulated"]).round(3)  # r2:coefficient of determination
                    mae = mean_absolute_error(toplot["Observed"], toplot["Simulated"]).round(3)
                    ax.text(113, 116.5, '2014 - 2020: ' + '$\mathregular{r^2}$ = ' + str(r2), fontsize=9)
                    ax.text(113, 116, '2014 - 2020: ' + f'MAE = {mae} m', fontsize=9)

            ### conditional title color
            is_in_calibwells = well in calibwells['Well_ID'].values
            if is_in_calibwells:
                ax.set_title(f'{well} ({wellDict[well]})', color='navy', fontsize=14)
            else:
                ax.set_title(f'{well} ({wellDict[well]})', color='black', fontsize=14)

            ax.set_ylabel('Simulated (m)', fontsize=14)
            ax.set_xlabel('Observed (m)', fontsize=14)
            ax.label_outer()
            ax.set_xlim([112.8, 118])
            ax.set_ylim([112.8, 118])

            ax.minorticks_on()
            ax.grid(which='major', linestyle='-',
                    linewidth='0.1', color='darkred')
            ax.grid(which='minor', linestyle=':',
                    linewidth='0.1', color='black')
            # plt.xticks(rotation=45)
            ax.legend(loc="lower right")

            # Hide any remaining empty subplots
        for i in range(len(groups), len(axes)):
            if len(toplot) == 0:
                fig.delaxes(axes[i])
            else:
                pass
        fig.tight_layout()
        plt.savefig(os.path.join(outputDir, f'grp{val+1}_V5.png'), bbox_inches='tight', dpi=600)

        plt.close()
        print("Done")

    return None

def calculate_plot_residuals(wls_obs, wls_obs2, wls_sim, wls_sim2):

    """
    Note that the statistical definition of residuals is the difference between actual and fitted values.
    So technically speaking, observed - simulated = residual for the calibration period only.
    The difference between actual and **forecasted** values is the error.
    So observed - simulated = error for the validation period.
    See: https://en.wikipedia.org/wiki/Errors_and_residuals
    """

    outputDir = os.path.join(cwd, 'output', 'water_level_plots', 'residual_plots')
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

    group1 = ['199-H3-25', '199-H3-26', '199-H3-27']  ## Inland
    group2 = ['199-H3-2A', '199-H4-86']  ## Inland near 100-H-46 source
    group3 = ['199-H4-84', '199-H4-88']  ## Midland near 183-H-SEB source
    group4 = ['199-H4-8', '199-H4-17', '199-H4-18', '199-H4-65', '199-H4-85', '199-H4-89']  ## Midland
    group5 = ['199-H4-4', '199-H4-5', '199-H4-12A', '199-H4-15A', '199-H4-64']  ## Riverside
    groups = [group1, group2, group3, group4, group5]  #

    for val, grp in enumerate(groups):
        size = len(grp)
        if size == 6:
            fig, axes = plt.subplots(nrows=2, ncols=3, gridspec_kw={'width_ratios': [1, 1, 1]},
                                     figsize=(14, 8), sharex=False, sharey=False)
        if size == 5:
            fig, axes = plt.subplots(nrows=2, ncols=3, gridspec_kw={'width_ratios': [1, 1, 1]},
                                     figsize=(14, 8), sharex=False, sharey=False)
        elif size == 4:
            fig, axes = plt.subplots(nrows=2, ncols=2, gridspec_kw={'width_ratios': [1, 1]},
                                     figsize=(14, 8), sharex=False, sharey=False)
        elif size == 3:
            fig, axes = plt.subplots(nrows=1, ncols=3, gridspec_kw={'width_ratios': [1, 1, 1]},
                                     figsize=(14, 4), sharex=False, sharey=False)
        elif size == 2:
            fig, axes = plt.subplots(nrows=1, ncols=2, gridspec_kw={'width_ratios': [1, 1]},
                                     figsize=(9, 4), sharex=False, sharey=False)
        else:
            pass

        axes = axes.flatten()
        fig.suptitle('Model Deviations', fontweight='bold', fontsize=14)
        for i, well in enumerate(grp):
            ax = axes[i]
            print("Well: ", well)
            flag = "True"
            for idx in range(2):
                print("Idx: ", idx)
                if idx == 0:
                    mywell_obs = wls_obs.loc[wls_obs['ID'] == well]
                    wls_sim.index = wls_sim["DATE"]
                    mywell_sim = wls_sim[wls_sim['NAME'] == well]
                    toplot = pd.merge(mywell_obs, mywell_sim, left_index=True, right_index=True, how="inner")
                    toplot.rename(columns={"Head": "Simulated", "Water Level (m)": "Observed"}, inplace=True)
                    toplot.dropna(subset=["Observed"], inplace=True)
                    toplot['Error'] = toplot['Observed'] - toplot['Simulated']
                elif idx == 1:
                    try:
                        mywell_sim = wls_sim2[wls_sim2['Well'] == well]
                        mywell_obs = wls_obs2.loc[wls_obs2['Well'] == well]
                        toplot = pd.merge(mywell_obs, mywell_sim, on="Time", how="inner")
                        toplot.dropna(subset=["Observed"], inplace=True)
                        toplot['Residual'] = toplot['Observed'] - toplot['Simulated']
                        print("Found: ", idx, well, len(toplot))
                        if len(toplot) == 0:
                            flag = "NA"
                    except:
                        print(f"{well} not found in 2014-2020 observations from MPR")
                        flag = "NA"
                        print("Not Found: ", idx, well, len(toplot))

                if idx == 0:
                    ax.plot(toplot['Observed'], toplot['Error'], 'o', markerfacecolor="steelblue",
                            markeredgecolor='blue',
                            markeredgewidth=1, markersize=10, alpha=0.5, zorder=9, label="2021 to 2023")
                    # ax.plot([0, 1], [0, 1], color='red', linewidth=0.5, transform=ax.transAxes, zorder=10)
                    ax.axhline(y=0, color='r', linestyle='-')
                elif idx == 1 and (flag != "NA"):
                    ax.plot(toplot['Observed'], toplot['Residual'], 'o', markerfacecolor="olive",
                            markeredgecolor='darkgreen',
                            markeredgewidth=1, markersize=10, alpha=0.5, zorder=8, label="2014 to 2020")
                    # ax.plot([0, 1], [0, 1], color='red', linewidth=0.5, transform=ax.transAxes, zorder=10)
                    plt.axhline(y=0, color='r', linestyle='-')

            ### conditional title color
            is_in_calibwells = well in calibwells['Well_ID'].values
            if is_in_calibwells:
                ax.set_title(f'{well} ({wellDict[well]})', color='navy', fontsize=14)
            else:
                ax.set_title(f'{well} ({wellDict[well]})', color='black', fontsize=14)

            ax.set_ylabel('Observed - Simulated (m)', fontsize=14)
            ax.set_xlabel('Observed (m)', fontsize=14)
            ax.label_outer()
            ax.set_xlim([112.8, 118])
            ax.set_ylim(-2,2)

            ax.minorticks_on()
            ax.grid(which='major', linestyle='-',
                    linewidth='0.1', color='darkred')
            ax.grid(which='minor', linestyle=':',
                    linewidth='0.1', color='black')
            # plt.xticks(rotation=45)
            ax.legend(loc="lower right")

            # Hide any remaining empty subplots
        for i in range(len(groups), len(axes)):
            if len(toplot) == 0:
                fig.delaxes(axes[i])
            else:
                pass
        fig.tight_layout()

        plt.savefig(os.path.join(outputDir, f'grp{val+1}_deviations.png'), bbox_inches='tight', dpi=600)

        plt.close()
        print("Done")


if __name__ == "__main__":


    ### SET FILE DIRECTORIES
    cwd = os.getcwd()

    mdir = os.path.join(os.path.dirname(cwd), 'mruns')
    wldir = os.path.join(cwd, 'output', 'water_level_data')
    chemdir = os.path.join(cwd, 'output', 'concentration_data')

    times = pd.read_csv(os.path.join(cwd, 'input', 'sp_2014_2023.csv'))
    wells = pd.read_csv(os.path.join(cwd, 'input', 'monitoring_wells_coords_ij.csv'))
    calibwells = pd.read_csv(os.path.join(cwd, 'input', 'well_list_v3_for_calibration.csv'))

    ### SET WELL NAME ASSOCIATIONS
    wellDict = {'199-H3-25': "North PT Sensor Data", '199-H3-26': "North PT Sensor Data", '199-H3-27': "North PT Sensor Data", '199-H3-2A': "North AWLN", '199-H4-12A': "North Manual",
     '199-H4-15A': "North Manual", '199-H4-17': "North PT Sensor Data", '199-H4-18': "North Manual", '199-H4-4': "North PT Sensor Data", '199-H4-5': "North AWLN",
     '199-H4-64': "North Manual", '199-H4-65': "North Manual", '199-H4-8': "North AWLN", '199-H4-84': "North AWLN", '199-H4-85': "North Manual",
     '199-H4-86': "North PT Sensor Data", '199-H4-88': "North AWLN", '199-H4-89': "North Manual" }


    ### IMPORT FILES
    ## Simulated WL, 2014 to 2023 [MONTHLY/SPs], using FLOPY
    # wls_sim_SP = pd.read_csv(os.path.join(wldir, 'calib_2014_2023', 'simulated_heads_monthly_flopy.csv'))
    # wls_sim_SP['DATE'] = pd.to_datetime("2014-01-01") + pd.to_timedelta(wls_sim_SP.Time, unit="days")
    ## Using MOD2OBS monthly instead:
    wls_sim_SP = pd.read_csv(os.path.join(wldir, 'calib_2014_2023', 'simulated_heads_monthly.dat'), delimiter=r"\s+", names = ["ID", "Date", "Time", "Head"])
    wls_sim_SP["NAME"] = "199-" + wls_sim_SP["ID"].str.strip().str[:-3]  # monitoring wells
    wls_sim_SP["Layer"] = wls_sim_SP["ID"].str.strip().str[-1].astype(int)
    wls_sim_SP = wls_sim_SP.loc[wls_sim_SP.Layer == 1]
    wls_sim_SP['Date'] = pd.to_datetime(wls_sim_SP['Date'])
    wls_sim_SP.rename(columns={"Date": "DATE"}, inplace=True)

    ### Simulated WL, 2014 to 2023 [DAILY]: Daily simulated values from mod2obs require a bit more data wrangling.
    wls_sim_daily = pd.read_csv(os.path.join(wldir, 'calib_2014_2023', 'simulated_heads_daily.dat'), delimiter=r"\s+", names = ["ID", "Date", "Time", "Head"])
    wls_sim_daily["NAME"] = "199-" + wls_sim_daily["ID"].str.strip().str[:-3]  # monitoring wells
    wls_sim_daily["Layer"] = wls_sim_daily["ID"].str.strip().str[-1].astype(int)
    wls_sim_daily = wls_sim_daily.loc[wls_sim_daily.Layer == 1]
    wls_sim_daily['Date'] = pd.to_datetime(wls_sim_daily['Date'])
    wls_sim_daily.rename(columns={"Date": "DATE"}, inplace=True)

    ## Simulated CONC, 2014 to 2023:
    crvi_ifile = os.path.join(mdir, 'calib_2014_2023', f'tran_2014_2023', 'post_process',
                              'mod2obs_monitoring_wells', 'simulated_conc_mod2obs.csv')
    crvi_sim = pd.read_csv(crvi_ifile)
    crvi_sim.rename(columns={'SAMP_SITE_NAME':'NAME','SAMP_DATE':'DATE'}, inplace = True)

    ### Observed CONC for 2014 to 2021, and 2021 - 2023:
    crvi_meas_1 = pd.read_csv(os.path.join(chemdir, '2014to2020', 'Cr_obs_avg_bySPs.csv'), index_col = 'SAMP_DATE', parse_dates = True)
    crvi_meas_2 = pd.read_csv(os.path.join(chemdir, '2021to2023', 'Cr_obs.csv'), index_col = 'DATE', parse_dates = True)

    ### Observed WL for 2021 to 2023:
    wl_meas = pd.read_csv(os.path.join(wldir, 'obs_2021_2023', 'measured_WLs_monthly.csv'), index_col='Date', parse_dates=True)
    wl_meas_daily = pd.read_csv(os.path.join(wldir, 'obs_2021_2023', 'measured_WLs_daily.csv'), index_col='Date', parse_dates=True)

    ### Observed WL for 2014 to 2020:
    wl_2014 = pd.read_csv(os.path.join("output", "water_level_data", "calib_2014_2020", "calib_2014to2020_obs_sim.csv")) ###monthly/SP-averaged
    wl_meas_2014 = wl_2014[["Well", "Time", "Observed"]]
    wl_sim_2014 = wl_2014[["Well", "Time", "Simulated"]]

    ### PLOTTING

    ## Plot WLs and CONCs:
    # plot_WL_vs_conc(wl_meas, crvi_meas_1, crvi_meas_2, wls_sim_SP, crvi_sim)

    ### Plot WLs scatterplots:
    mode = "monthly"
    if mode == "monthly":
        wls_obs = wl_meas #averaged by SP = monthly
        wls_obs2 = wl_meas_2014
        wls_sim = wls_sim_SP
        wls_sim2 = wl_sim_2014
    if mode == "daily":
        wls_obs = wl_meas_daily
        wls_sim =wls_sim_daily

    # crossplots_WL_individual(wls_obs, wls_sim, mode)

    crossplots_WL_subplots(wls_obs, wls_obs2, wls_sim, wls_sim2)

    ## Plot deviations
    calculate_plot_residuals(wls_obs, wls_obs2, wls_sim, wls_sim2)