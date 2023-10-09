import os
import glob
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
import flopy.utils.binaryfile as bf


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
    for idx, row, col in zip(range(len(df)), df.Row, df.Col):
        for t_idx, t in enumerate(times):
            for lay in nlays:
                vals.append([data[t_idx][lay][row][col], t, lay + 1, row, col, df.NAME.iloc[idx]])  # 237 nodes * 84 times = 19908 vals for L1
    df_return = pd.DataFrame(vals, columns=['Head', 'Time', 'Layer', 'Row', 'Column', 'NAME'])
    df_return.drop_duplicates(inplace=True)
    # df_return.to_csv(os.path.join('output', 'water_level_data', f'calib_2014_2023', "simulated_heads.csv"), index=False)
    return df_return

def generate_plots(newWL, newWL_raw, mywells, SimHeads, TargetHeads, CalibHeads, plotTargetHeads = False, plotCalibHeads = True):

    for w in mywells.NAME.unique():
        print(w)

        obs_new = newWL.loc[newWL.ID == w]
        dates_new = pd.to_datetime(obs_new.Date)

        obs_new_raw = newWL_raw.loc[newWL_raw.ID == w]
        dates_new_raw = pd.to_datetime(obs_new_raw.Date)

        if plotTargetHeads:
            obs_t = TargetHeads.loc[TargetHeads.Well == w]
            dates_obs_t = pd.to_datetime("2014-01-01") + pd.to_timedelta(obs_t.Time, unit="days")
        elif plotCalibHeads:
            try:
                obs_c = CalibHeads.loc[CalibHeads.Well == w]
                dates_obs_c = pd.to_datetime(obs_c.Time)
            except:
                pass

        sim = SimHeads.loc[(SimHeads.NAME == w) & (SimHeads.Layer == 1)]
        dates_sim = pd.to_datetime("2014-01-01") + pd.to_timedelta(sim.Time, unit="days")

        fig, ax = plt.subplots(figsize=(15, 5))
        if plotTargetHeads: #if target heads is True
            try:
                ax.scatter(dates_obs_t, obs_t.HEAD, label = f"Calibrated", c = "r", edgecolor="darkred", s=4)
                ax.plot(dates_obs_t, obs_t.HEAD, c = "r", ls="--")
            except:
                print(f"Coudn't find {w}")
        elif plotCalibHeads:
            try:
                ax.scatter(dates_obs_c, obs_c["Zero Weight"], label = f"MPR: Simulated", c = "r", edgecolor="darkred", s=15, zorder=2)
                ax.plot(dates_obs_c, obs_c["Zero Weight"], c = "r", ls="--", zorder=4)
                ax.scatter(dates_obs_c, obs_c.Observed, label = f"MPR: Observed", c = "b", edgecolor="navy", s=15, zorder=3)
                ax.plot(dates_obs_c, obs_c.Observed, c = "b", ls="--", zorder=5)
                #ax.scatter(dates_obs_c, obs_c["Simulated"], label = f"MPR: Zero-Weight", c = "grey", edgecolor="darkgrey", s=4, zorder=2)
            except:
                print(f"Coudn't find {w}")

        ax.plot(dates_sim, sim.Head, label = f"Extended Model", color = "darkgreen", alpha=0.7, lw=1.5, zorder=1)

        ax.scatter(dates_new, obs_new["Water Level (m)"], label=f"New Obs", c="purple", edgecolor="purple", s=15, zorder=1)
        ax.plot(dates_new, obs_new["Water Level (m)"], c="purple", ls="--", zorder=5)

        # ax.scatter(dates_new_raw, obs_new_raw["Water Level (m)"], label=f"New Obs (Raw)", c="plum", s=15, zorder=1, alpha = 0.2)
        ax.plot(dates_new_raw, obs_new_raw["Water Level (m)"], c="plum", ls="--", alpha=0.2, zorder=5)

        ax.set_title(f'{w}', fontsize=12, fontweight="bold")
        ax.set_ylabel('Water Level (m)', fontsize=12, fontweight="bold")
        ax.minorticks_on()
        grid = True
        if grid:
            ax.grid(which='major', linestyle='-',
                    linewidth='0.1', color='red')
            ax.grid(which='minor', linestyle=':',
                    linewidth='0.1', color='black')
        else:
            print("grid is OFF")
            pass
        ax.legend()
        plt.xticks(rotation = 45)
        fig.tight_layout()
        ax.set_xlim(pd.to_datetime("2021-01-01"), pd.to_datetime("2023-07-31"))
        # ax.set_xlim(pd.to_datetime("2014-01-01"), pd.to_datetime("2021-01-01"))
        ax.set_ylim([112.8,118])
        # ax.set_ylim([113.5,117.5])
        plt.savefig(os.path.join('output', 'water_level_plots', 'calib_heads', f'{w}_V3.png'))
        plt.close()
    return None


if __name__ == "__main__":
    cwd = os.getcwd()

    mywells = pd.read_csv(os.path.join("input", "monitoring_wells_coords_ij.csv"))

    TargetHeads = pd.read_excel(os.path.join(os.path.dirname(cwd), "data", "water_levels", "calib_2014to2020_heads", "HeadTarg.xlsx"), engine = "openpyxl")
    CalibHeads = pd.read_excel(os.path.join(os.path.dirname(cwd), "data", "water_levels", "calib_2014to2020_heads", "RES_RUM_GHB.xlsx"), engine = "openpyxl")

    myDF = CalibHeads[["Well", "Time", "Observed", "Zero Weight"]]
    myDF.rename(columns = {"Zero Weight" : "Simulated"}, inplace=True)
    myDF.to_csv(os.path.join("output", "water_level_data", "calib_2014_2020", "calib_2014to2020_obs_sim.csv"), index=False)

    newWL = pd.read_csv(os.path.join("output", "water_level_data", "obs_2021_2023", "measured_WLs_monthly.csv"))
    newWL_raw = pd.read_csv(os.path.join("output", "water_level_data", "obs_2021_2023", "measured_WLs_formatted.csv"))

    sce = 'calib_2014_2023'
    hds_file = os.path.join(os.path.dirname(cwd), 'mruns', f'{sce}', f'flow_{sce[-9:]}', '100hr3.hds')
    SimHeads = read_head(hds_file, mywells)
    generate_plots(newWL, newWL_raw, mywells, SimHeads, TargetHeads, CalibHeads, plotTargetHeads = False, plotCalibHeads = False) ###True will be the Heads that plots.