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


## original function from py13 for insp
def plot_concentrations_ALL(myDict):
    outputDir = os.path.join(cwd, 'output', 'concentration_plots', f"comparison_calib_2020_2023")
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

    wellDict = {'199-H3-25':"North_PT_SensorData", '199-H3-26':"North_PT_SensorData", '199-H3-27':"North_PT_SensorData", '199-H3-2A': "North_AWLN", '199-H4-12A': "North_Manual",
       '199-H4-15A': "North_Manual", '199-H4-17':"North_PT_SensorData", '199-H4-18': "North_Manual", '199-H4-4':"North_PT_SensorData", '199-H4-5': "North_AWLN",
       '199-H4-64': "North_Manual", '199-H4-65': "North_Manual", '199-H4-8': "North_AWLN", '199-H4-84': "North_AWLN", '199-H4-85': "North_Manual",
       '199-H4-86':"North_PT_SensorData", '199-H4-88': "North_AWLN", '199-H4-89': "North_Manual"}

    times['start_date'] = pd.to_datetime(times['start_date'])

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
                df_conc2 = pd.read_csv(os.path.join(os.path.dirname(cwd), 'mruns', f'{sce}', f'tran_{sce[-9:]}', 'post_process','mod2obs_monitoring_wells', 'original', 'simulated_conc_mod2obs.csv'))
                try:
                    qc_plot = df_conc2[df_conc2['SAMP_SITE_NAME'] == well]
                except:
                    print(f"No info for {well} for ECF-22-0047")
                ax.plot(pd.to_datetime(ucn_toplot["SAMP_DATE"]), ucn_toplot['WeightedConc'], label=f'Calibrated Model', color = "cornflowerblue")
                ax.scatter(pd.to_datetime(data_toplot['SAMP_DATE_TIME']), data_toplot['STD_VALUE_RPTD'], zorder=10, label = f"Calib Obs", c = "grey", edgecolor="k", s=10)
                ax.plot(pd.to_datetime(data_toplot['SAMP_DATE_TIME']), data_toplot['STD_VALUE_RPTD'], zorder=10, c = "grey", ls="--", alpha=0.7)
                ax.plot(pd.to_datetime(qc_plot["SAMP_DATE"]), qc_plot['WeightedConc'], label=f'Calibrated Model ECF', color = "pink")
            if sce == "calib_2014_2023":
                ax.plot(pd.to_datetime(ucn_toplot["SAMP_DATE"]), ucn_toplot['WeightedConc'], label=f'Extended Model', color = "olive")
                ax.scatter(pd.to_datetime(data_toplot['SAMP_DATE_TIME']), data_toplot['STD_VALUE_RPTD'], zorder=10, label = f"New Obs", c = "r", edgecolor="darkred", s=10)
                ax.plot(pd.to_datetime(data_toplot['SAMP_DATE_TIME']), data_toplot['STD_VALUE_RPTD'], zorder=10, c = "r", ls="--", alpha=0.7)
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

def plot_conc_vs_WLs():

    for well in wls['ID'].unique():
        toplot = wls[wls['ID'] == well]
        fig, ax = plt.subplots()
        ax.grid()
        ax.plot(toplot.index, toplot['Water Level (m)'])

        ax2 = ax.twinx()
        toplot2 = crvi[crvi['NAME'] == well]
        ax2.scatter(toplot2.index, toplot2['STD_VALUE_RPTD'], c = 'darkred')

if __name__ == "__main__":

    cwd = os.getcwd()

    mdir = os.path.join(os.path.dirname(cwd), 'mruns')
    wldir = os.path.join(cwd, 'output', 'water_level_data')
    chemdir = os.path.join(cwd, 'output', 'concentration_data')

    wells = pd.read_csv(os.path.join(cwd, 'input', 'monitoring_wells_coords_ij.csv'))

    wls = pd.read_csv(os.path.join(wldir, 'measured_WLs_monthly.csv'), index_col = 'Date', parse_dates = True)
    crvi = pd.read_csv(os.path.join(chemdir, '2021to2023', 'Cr_obs.csv'),
                                    usecols = ['NAME', 'SAMP_DATE_TIME', 'STD_VALUE_RPTD', 'tte'],
                       index_col = 'SAMP_DATE_TIME', parse_dates = True)

    # sces = ['calib_2014_2023', 'calib_2014_2020']
    # myDict = {}
    # for sce in sces:
    #     if sce == 'calib_2014_2023':
    #         times = pd.read_csv(os.path.join(cwd, 'input', 'sp_2014_2023.csv'))
    #         crvi_filt = pd.read_csv(os.path.join(chemdir, "2021to2023",
    #                                              "Cr_obs.csv"))
    #     if sce == "calib_2014_2020":
    #         crvi_filt = pd.read_csv(os.path.join(chemdir, "2014to2020",
    #                                              "Cr_obs_avg_bySPs.csv"))  # chem data used to calibrate 2014-2020 model
    #         crvi_filt.rename(columns={"SAMP_SITE_NAME": "NAME", "SAMP_DATE": "SAMP_DATE_TIME"}, inplace=True)
    #
    #
    #     df_conc = pd.read_csv(
    #         os.path.join(os.path.dirname(cwd), 'mruns', f'{sce}', f'tran_{sce[-9:]}', 'post_process',
    #                      'mod2obs_monitoring_wells', 'simulated_conc_mod2obs.csv'))
    #         # if sce == "calib_2014_2020":
    #         # df_conc["WeightedConc"] = df_conc["WeightedConc"]/1000 ?
    #
    #
    #     if sce not in myDict.keys():
    #         myDict[sce] = [crvi_filt, df_conc]
    #
    # plot_concentrations_ALL(myDict)



