import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.patheffects as pe
matplotlib.use('Qt5Agg')
from datetime import datetime

plt.rc('xtick', labelsize=14)
plt.rc('ytick', labelsize=14)

def plot_WLs_multiple_wells(df, well_grps, odir):

    df['EVENT'] = pd.to_datetime(df['EVENT'])

    cnt = 0
    for well_grp in well_grps:
        cnt += 1
        df2 = df[df['NAME'].isin(well_grp)]

        # Group by 'name' and plot time series for each group
        grouped_df = df2.groupby('NAME')

        fig, ax = plt.subplots(figsize=(10, 6))

        for name, group in grouped_df:
            group.sort_values(by=["EVENT"], inplace=True)
            # print(group.index)
            ax.plot(group['EVENT'], group['VAL_FINAL'], ls='--', label=name, zorder=2)
            ax.scatter(group['EVENT'], group['VAL_FINAL'], s = 15, zorder=3)

        plt.xlabel('Date', fontsize=14)
        plt.ylabel('Observed Groundwater Elevation (m)', fontsize=14)
        plt.legend(loc='lower left')

        ### bells and whistles ------------------------------------------------------------------------
        ax.axvline(pd.to_datetime('2021-01-01'), color='gray', linestyle='-', linewidth=1, zorder=1)
        ax.axvline(pd.to_datetime('2023-04-12'), color='gray', linestyle='-', linewidth=1, zorder=1)
        text_label = datetime.now()
        ax.text(0.96, 0.02, text_label, transform=ax.transAxes, horizontalalignment='right', verticalalignment='bottom',
                alpha=0.1)
        text_y = ax.get_ylim()[1] - 0.035 * (ax.get_ylim()[1] - ax.get_ylim()[0])  # for text annotations

        ax.set_xlim(pd.to_datetime("2014-01-01"), pd.to_datetime("2024-02-01"))
        ax.text(pd.to_datetime('2021-02-01'), text_y, 'Post-Calibration Period', ha='left', va='top', rotation=90,
                 color='k', alpha=0.75, path_effects=[pe.withStroke(linewidth=4, foreground='white')], zorder=10)
        ax.text(pd.to_datetime('2023-07-12'), text_y, 'Rebound Period', ha='right', va='top', rotation=90, color='k',
                 alpha=0.75, path_effects=[pe.withStroke(linewidth=4, foreground='white')], zorder=10)
        ax.text(pd.to_datetime('2020-12-01'), text_y, 'Calibration Period', ha='right', va='top', rotation=90,
                 color='k', alpha=0.75, path_effects=[pe.withStroke(linewidth=4, foreground='white')], zorder=10)

        ax.minorticks_on()
        ax.grid(which='major', linestyle='-',
                linewidth='0.1', color='k', alpha=0.85)
        ax.grid(which='minor', linestyle=':',
                linewidth='0.1', color='k', alpha=0.65)
        plt.xticks(rotation=45)

        # Save figure -------
        plt.savefig(os.path.join(odir, f"well_grp{cnt}"), bbox_inches='tight')
        plt.close()

    return None

def plot_Concs_multiple_wells(df, well_grps, odir):

    df.reset_index(inplace=True)
    df['DATE'] = pd.to_datetime(df['DATE'])

    cnt = 0
    for well_grp in well_grps:
        cnt += 1
        df2 = df[df['NAME'].isin(well_grp)]

        # Group by 'name' and plot time series for each group
        grouped_df = df2.groupby('NAME')

        fig, ax = plt.subplots(figsize=(10, 6))

        for name, group in grouped_df:
            group.sort_values(by=["DATE"], inplace=True)
            print(name)
            if name in ["199-D5-103", "199-D5-104", "199-D5-145"]:
                ax.semilogy(group['DATE'], group['STD_VALUE_RPTD'], ls='--', label=name, zorder=2)
                ax.scatter(group['DATE'], group['STD_VALUE_RPTD'], s=15, zorder=3)
            else:
                ax.plot(group['DATE'], group['STD_VALUE_RPTD'], ls='--', label=name, zorder=2)
                ax.scatter(group['DATE'], group['STD_VALUE_RPTD'], s = 15, zorder=3)

        plt.xlabel('Date', fontsize=14)
        plt.ylabel('Observed Crv(VI) Concentration (m)', fontsize=14)
        plt.legend(loc='lower left')

        ### bells and whistles ------------------------------------------------------------------------
        ax.axhline(10, color='gray', alpha = 1, linestyle='-.', linewidth=1, label='10 μg/L', zorder=1)
        ax.axhline(48, color='gray', alpha = 1, linestyle='-.', linewidth=1, label='48 μg/L', zorder=1)
        ax.axvline(pd.to_datetime('2021-01-01'), color='gray', linestyle='-', linewidth=1, zorder=1)
        ax.axvline(pd.to_datetime('2023-04-12'), color='gray', linestyle='-', linewidth=1, zorder=1)
        text_label = datetime.now()
        ax.text(0.96, 0.02, text_label, transform=ax.transAxes, horizontalalignment='right', verticalalignment='bottom',
                alpha=0.1)
        text_y = ax.get_ylim()[1] - 0.035 * (ax.get_ylim()[1] - ax.get_ylim()[0])  # for text annotations

        ax.set_xlim(pd.to_datetime("2014-01-01"), pd.to_datetime("2024-02-01"))
        ax.text(pd.to_datetime('2021-02-01'), text_y, 'Post-Calibration Period', ha='left', va='top', rotation=90,
                 color='k', alpha=0.75, path_effects=[pe.withStroke(linewidth=4, foreground='white')], zorder=10)
        ax.text(pd.to_datetime('2023-07-12'), text_y, 'Rebound Period', ha='right', va='top', rotation=90, color='k',
                 alpha=0.75, path_effects=[pe.withStroke(linewidth=4, foreground='white')], zorder=10)
        ax.text(pd.to_datetime('2020-12-01'), text_y, 'Calibration Period', ha='right', va='top', rotation=90,
                 color='k', alpha=0.75, path_effects=[pe.withStroke(linewidth=4, foreground='white')], zorder=10)

        ax.minorticks_on()
        ax.grid(which='major', linestyle='-',
                linewidth='0.1', color='k', alpha=0.85)
        ax.grid(which='minor', linestyle=':',
                linewidth='0.1', color='k', alpha=0.65)
        plt.xticks(rotation=45)

        # Save figure -------
        plt.savefig(os.path.join(odir, f"well_grp{cnt}"), bbox_inches='tight')
        plt.close()

    return None

if __name__ == "__main__":

    cwd = os.getcwd()
    wdir = os.path.dirname(cwd)

    # Specify wells to plot
    # well_grps = [['199-D5-17', '199-D5-19', '199-D5-133'],
    #               ['199-D5-128', '199-D5-129', '199-D5-133'],
    #               ['199-D5-160', '199-D5-162', '199-D5-163', '199-D5-133'],
    #               ['199-D5-160', '199-D5-162', '199-D5-163', '199-D5-103', '199-D5-150'],
    #               ]

    well_grps = [['199-D5-15', '199-D5-123', '199-D5-142', '199-D5-133'], #EAST OF 100-D-100
                  ['199-D5-106', '199-D1-1', '199-D2-14', '199-D5-103', '199-D5-160', '199-D5-150'], #100-D-100
                  ['199-D5-34', '199-D5-149', '199-D5-104', '199-D5-151', '199-D5-152'], #100-D-56
                  ['199-D5-39', '199-D5-145', '199-D5-146', '199-D5-43' ], #WEST OF 100-D-56
                  ['199-D5-128', '199-D5-17','199-D2-11'], #SOUTH OF SOURCES
                  ['199-D5-33', '199-D5-44', '199-D5-37', '199-D5-41','AT-D-1-M', '35-S']] #NORTHWEST OF SOURCES

    ### OBS. WATER LEVEL PLOTS - WELL GROUPS
    wl_meas_all = pd.read_csv(os.path.join("output","water_level_data","obs_2014_Jan2024","measured_WLs_monthly_all_wells.csv"))

    odir = os.path.join("output","water_level_plots","obs_well_grps")
    if not os.path.isdir(odir):
        os.makedirs(odir)

    plot_WLs_multiple_wells(wl_meas_all, well_grps, odir)

    ### OBS. CONCENTRATION PLOTS - WELL GROUPS
    crvi_meas_2023 = pd.read_csv(os.path.join("output", "concentration_data", '2014to2023', '100D', 'Cr_obs_2014_2023_100D_mp.csv'), parse_dates = True)
    crvi_meas_2024 = pd.read_csv(os.path.join("output", "concentration_data", '2023to2024', '100D', 'Cr_obs_100D.csv'), parse_dates=True)
    crvi_meas_2024 = crvi_meas_2024.loc[crvi_meas_2024.DATE > max(crvi_meas_2023.DATE)]
    crvi_meas_2024.rename(columns={"VAL": "STD_VALUE_RPTD"}, inplace=True)
    crvi_meas_all = pd.concat([crvi_meas_2023, crvi_meas_2024])
    crvi_meas_all.sort_values(by=["DATE"], inplace=True)


    odir = os.path.join("output", "concentration_plots", "obs_well_grps")
    if not os.path.isdir(odir):
        os.makedirs(odir)

    plot_Concs_multiple_wells(crvi_meas_all, well_grps, odir)

