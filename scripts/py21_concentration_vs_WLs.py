"""
Plot simulated and observed water levels + simulated and observed Cr(VI) concentrations
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


def plot_WL_vs_conc(wl_df, conc_df, dtype):

    """
    Plot concentration data of interest against water levels in one graph.
    May be used to plot either measured data or simulation results.
    Inputs: water level dataframe, concentration dataframe, data type
    dtype options: simulated, measured, or both. Simply to control style.
    Common errors: double check column names (e.g. "NAME" vs "ID", "time" vs "Date", etc.)
        rename columns outside of function for consistency.
    """

    for well in wells['NAME']:

        ## set data to be plotted
        # toplot_crvi = crvi_sim[crvi_sim['SAMP_SITE_NAME'] == well]  ## for testing purposes
        # toplot_wl = wls_sim[wls_sim['NAME'] == well]  ## for testing purposes
        toplot_wl = wl_df[wl_df['NAME'] == well]  ## match to the correct input when function is called
        toplot_crvi = conc_df[conc_df['NAME'] == well] ## match to the correct input when function is called

        ## create figure instance and set specs
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.minorticks_on()
        ax.grid(which='major', linestyle='-',
                linewidth='0.1', color='red')
        ax.grid(which='minor', linestyle=':',
                linewidth='0.1', color='black')
        plt.xticks(rotation=45)
        ## conditional title color -- work in progress.
        # result = wells['NAME'].isin(calibwells['Well_ID'])
        # for index, match in result.iteritems():
        #     if match:
        #         ax.set_title(f'{well}', color = 'red')
        #     else:
        #         ax.set_title(f'{well}', color = 'black')
        ax.set_title(f'{well}')
        ax.set_ylabel('Water Level (m.asl)')
        ## create secondary axis and specs
        ax2 = ax.twinx()
        ax2.set_ylabel('Cr(VI) (μg/L)')
        # ax2.set_ylim(0, 500)
        # ax2.set_yscale('symlog')

        ## flags are set for linestyle
        if dtype == 'simulated':
            ax.plot(toplot_wl['DATE'], toplot_wl['Head'], label='Simulated WL')
            ax2.plot(pd.to_datetime(toplot_crvi['DATE']), toplot_crvi['WeightedConc'], zorder=10,
                     c="darkred", label='Simulated Cr(VI)')
        elif dtype == 'measured':
            ax.scatter(toplot_wl['DATE'], toplot_wl['Head'], label='Measured WL')
            ax.plot(toplot_wl['DATE'], toplot_wl['Head'], zorder=10,
                    ls="--", alpha=0.7)
            ax2.scatter(pd.to_datetime(toplot_crvi['DATE']), toplot_crvi['WeightedConc'], c='darkred',
                        label='Measured Cr(VI)')
            ax2.plot(pd.to_datetime(toplot_crvi['DATE']), toplot_crvi['WeightedConc'], zorder=10, c="darkred",
                    ls="--", alpha=0.7)
        else:  ## freestyle
            pass ## to be filled

        ## combined legend
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc=0)

        # plt.savefig(os.path.join(outputDir, f'{well}.png'))

if __name__ == "__main__":

    cwd = os.getcwd()

    outputDir = os.path.join(cwd, 'output', 'concentration_vs_WL_plots', 'sim_2014_2023')
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

    mdir = os.path.join(os.path.dirname(cwd), 'mruns')
    wldir = os.path.join(cwd, 'output', 'water_level_data')
    chemdir = os.path.join(cwd, 'output', 'concentration_data')

    times = pd.read_csv(os.path.join(cwd, 'input', 'sp_2014_2023.csv'))
    wells = pd.read_csv(os.path.join(cwd, 'input', 'monitoring_wells_coords_ij.csv'))
    calibwells = pd.read_csv(os.path.join(cwd, 'input', 'well_list_v3_for_calibration.csv'))

    ## set WL input file
    wls_ifile = os.path.join(wldir, 'calib_2014_2023', 'simulated_heads.csv')
    wls_sim = pd.read_csv(wls_ifile)
    wls_sim['DATE'] = pd.to_datetime("2014-01-01") + pd.to_timedelta(wls_sim.Time, unit="days")

    ## set concentration input file
    crvi_ifile = os.path.join(mdir, 'calib_2014_2023', f'tran_2014_2023', 'post_process',
                              'mod2obs_monitoring_wells', 'simulated_conc_mod2obs.csv')
    crvi_sim = pd.read_csv(crvi_ifile)
    crvi_sim.rename(columns={'SAMP_SITE_NAME':'NAME',
                     'SAMP_DATE':'DATE'}, inplace = True)

    plot_WL_vs_conc(wls_sim, crvi_sim, 'simulated')


    # 2014 - 2020, used for calibration
    # crvi_meas_1 = pd.read_csv(os.path.join(chemdir, '2014to2020', 'Cr_obs_all.csv'), index_col = 'SAMP_DATE', parse_dates = True)
    # ## 2021 - 2023, for extended model
    # wls_meas = pd.read_csv(os.path.join(wldir, 'obs_2021_2023', 'measured_WLs_monthly.csv'), index_col='Date', parse_dates=True)
    # crvi_meas_2 = pd.read_csv(os.path.join(chemdir, '2021to2023', 'Cr_obs.csv'), index_col = 'DATE', parse_dates = True)



