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

##take a look at measured concentrations vs measured WLs
def plot_conc_vs_WLs():

    outputDir = os.path.join(cwd, 'output', 'concentration_vs_WL_plots', 'testing_grounds')
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

    for well in wls_meas['ID'].unique():
        toplot_calib = wls_sim[wls_sim['NAME'] == well] ##
        toplot_extend = wls_meas[wls_meas['ID'] == well] ##
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.minorticks_on()
        ax.grid(which='major', linestyle='-',
                linewidth='0.1', color='red')
        ax.grid(which='minor', linestyle=':',
                linewidth='0.1', color='black')
        plt.xticks(rotation=45)
        ax.set_title(f'{well}')
        ax.plot(times['end_date'], toplot_calib['Head'], label = 'Simulated WL')
        ax.plot(toplot_extend.index, toplot_extend['Water Level (m)'], label='Observed WL')
        ax.plot()
        ax.set_ylabel('Water Level (m.asl)')

        ax2 = ax.twinx()
        toplot2_calib = crvi_meas_1[crvi_meas_1['SAMP_SITE_NAME'] == well]  ## 2021 - 2023
        toplot2_extend = crvi_meas_2[crvi_meas_2['NAME'] == well] ## 2021 - 2023
        ax2.scatter(toplot2_calib.index, toplot2_calib['STD_VALUE_RPTD'], c='grey', label='Measured Cr(VI) Calib')
        ax2.plot(pd.to_datetime(toplot2_calib.index), toplot2_calib['STD_VALUE_RPTD'], zorder=10, c="grey",
                ls="--", alpha=0.7)
        ax2.scatter(toplot2_extend.index, toplot2_extend['STD_VALUE_RPTD'], c = 'darkred', label = 'Measured Cr(VI) New')
        ax2.plot(pd.to_datetime(toplot2_extend.index), toplot2_extend['STD_VALUE_RPTD'], zorder=10, c="darkred",
                ls="--", alpha=0.7)

        ax2.set_ylabel('Cr(VI) (μg/L)')
        # ax2.set_ylim(0.1, 500)
        # ax2.set_yscale('log')

        ## combined legend
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc=0)

        plt.savefig(os.path.join(outputDir, f'{well}_v02.png'))

## original function from py13 (w/minor edits)
def plot_concentrations(myDict):
    outputDir = os.path.join(cwd, 'output', 'concentration_plots', f"comparison_calib_2020_2023", 'rw_tests')
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

    wellDict = {'199-H3-25':"North_PT_SensorData", '199-H3-26':"North_PT_SensorData", '199-H3-27':"North_PT_SensorData", '199-H3-2A': "North_AWLN", '199-H4-12A': "North_Manual",
       '199-H4-15A': "North_Manual", '199-H4-17':"North_PT_SensorData", '199-H4-18': "North_Manual", '199-H4-4':"North_PT_SensorData", '199-H4-5': "North_AWLN",
       '199-H4-64': "North_Manual", '199-H4-65': "North_Manual", '199-H4-8': "North_AWLN", '199-H4-84': "North_AWLN", '199-H4-85': "North_Manual",
       '199-H4-86':"North_PT_SensorData", '199-H4-88': "North_AWLN", '199-H4-89': "North_Manual"}

    times['start_date'] = pd.to_datetime(times['start_date'])
    times['end_date'] = pd.to_datetime(times['end_date'])

    for well in wellDict.keys():
        print(well)

        fig, ax = plt.subplots(figsize=(8, 5))
        for sce in myDict.keys():
            print(sce)

            crvi = myDict[sce][0] #crvi observations
            df_conc = myDict[sce][1] #simulated concs
            ucn_toplot = df_conc[df_conc['SAMP_SITE_NAME'] == well]
            data_toplot = crvi[crvi['NAME'] == well]

            if sce == "calib_2014_2020":
                ###double-check concentrations from ECF-100HR3-22-0047:
                df_conc2 = pd.read_csv(os.path.join(os.path.dirname(cwd), 'mruns', f'{sce}', f'tran_{sce[-9:]}',
                                                    'post_process','mod2obs_monitoring_wells', 'original', 'simulated_conc_mod2obs.csv'))
                try:
                    qc_plot = df_conc2[df_conc2['SAMP_SITE_NAME'] == well]
                except:
                    print(f"No info for {well} for ECF-22-0047")
                ax.plot(pd.to_datetime(ucn_toplot["SAMP_DATE"]), ucn_toplot['WeightedConc'], label=f'Calibrated Model', color = "cornflowerblue")
                ax.scatter(pd.to_datetime(data_toplot['SAMP_DATE_TIME']), data_toplot['STD_VALUE_RPTD'], zorder=10, label = f"Calib Obs", c = "grey", edgecolor="k")
                ax.plot(pd.to_datetime(data_toplot['SAMP_DATE_TIME']), data_toplot['STD_VALUE_RPTD'], zorder=10, c = "grey", ls="--", alpha=0.7)
                ax.plot(pd.to_datetime(qc_plot["SAMP_DATE"]), qc_plot['WeightedConc'], label=f'Calibrated Model ECF', color = "pink")
            if sce == "calib_2014_2023":
                ax.plot(pd.to_datetime(ucn_toplot["SAMP_DATE"]), ucn_toplot['WeightedConc'], label=f'Extended Model', color = "olive")
                ax.scatter(data_toplot.index, data_toplot['STD_VALUE_RPTD'], zorder=10, label = f"New Obs", c = "r", edgecolor="darkred")
                #ax.plot(pd.to_datetime(data_toplot['SAMP_DATE_TIME']), data_toplot['STD_VALUE_RPTD'], zorder=10, c = "r", ls="--", alpha=0.7)
        ax.set_title(f'{wellDict[well]}: {well}')
        ax.set_ylabel('Cr(VI) (ug/L)')
        ax.minorticks_on()
        ax.grid(which='major', linestyle='-',
                linewidth='0.1', color='red')
        ax.grid(which='minor', linestyle=':',
                linewidth='0.1', color='black')
        ax.legend()
        plt.xticks(rotation=45)
        # fig.tight_layout()
        # ax.set_xlabel("Date")
        ax.set_xlim(pd.to_datetime("2014-01-01"), pd.to_datetime("2023-07-31"))
        # plt.savefig(os.path.join(outputDir, f'{well}_MOD2OBS_qcECF-0047.png'))
        #plt.close()
    return None

if __name__ == "__main__":

    cwd = os.getcwd()

    mdir = os.path.join(os.path.dirname(cwd), 'mruns')
    wldir = os.path.join(cwd, 'output', 'water_level_data')
    chemdir = os.path.join(cwd, 'output', 'concentration_data')

    times = pd.read_csv(os.path.join(cwd, 'input', 'sp_2014_2023.csv'))
    wells = pd.read_csv(os.path.join(cwd, 'input', 'monitoring_wells_coords_ij.csv'))

    ## 2014 - 2020, used for calibration
    crvi_meas_1 = pd.read_csv(os.path.join(chemdir, '2014to2020', 'Cr_obs_all.csv'), index_col = 'SAMP_DATE', parse_dates = True)
    ## 2021 - 2023, for extended model
    wls_meas = pd.read_csv(os.path.join(wldir, 'measured_WLs_monthly.csv'), index_col='Date', parse_dates=True)
    crvi_meas_2 = pd.read_csv(os.path.join(chemdir, '2021to2023', 'Cr_obs.csv'), index_col = 'DATE', parse_dates = True)

    sce = 'calib_2014_2023'
    # sces = ['calib_2014_2023', 'calib_2014_2020']
    wls_sim = pd.read_csv(os.path.join(wldir, 'calib_2014_2023', 'simulated_heads.csv'))
    crvi_sim = pd.read_csv(os.path.join(os.path.dirname(cwd), 'mruns', f'{sce}', f'tran_{sce[-9:]}',
                                        'post_process', 'mod2obs_monitoring_wells', 'simulated_conc_mod2obs.csv'))

    myDict = {}
    if sce not in myDict.keys():
        myDict[sce] = [crvi_meas_2, crvi_sim]

    plot_concentrations(myDict)



