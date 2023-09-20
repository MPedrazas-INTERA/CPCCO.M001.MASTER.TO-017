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
    df_return.to_csv(os.path.join('output', 'water_level_data', f'calib_2014_2023', "simulated_heads.csv"), index=False)
    return df_return

def generate_plots(mywells, CalibHeads, SimHeads):

    for w in mywells.NAME.unique():
        print(w)
        obs = CalibHeads.loc[CalibHeads.Well == w]#.resample('D').mean()
        dates_obs = pd.to_datetime("2014-01-01") + pd.to_timedelta(obs.Time, unit="days")
        sim = SimHeads.loc[(SimHeads.NAME == w) & (SimHeads.Layer == 1)]
        dates_sim = pd.to_datetime("2014-01-01") + pd.to_timedelta(sim.Time, unit="days")

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(dates_obs, obs.HEAD, label = f"Calibrated", c = "r", edgecolor="darkred", s=4)
        ax.scatter(dates_obs, obs.HEAD, c = "r", ls="--")

        ax.plot(dates_sim, sim.Head, label = f"Simulated", color = "cornflowerblue")
        ax.plot(sim.Time, sim.Head, c = "r", ls="--")

        ax.set_title(f'{w}')
        ax.set_ylabel('Water Level (m)')
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
        ax.set_xlim(pd.to_datetime("2014-01-01"), pd.to_datetime("2023-07-31"))
        ax.set_ylim([112.8,118])
        plt.savefig(os.path.join('output', 'water_level_plots', 'calib_heads', f'{w}.png'))
        plt.close()
    return None


if __name__ == "__main__":
    cwd = os.getcwd()
    CalibHeads = pd.read_excel(os.path.join(os.path.dirname(cwd), "data", "water_levels", "calib_2014to2020_heads", "HeadTarg.xlsx"), engine = "openpyxl")
    mywells = pd.read_csv(os.path.join("input", "monitoring_wells_coords_ij.csv"))  # export CSV

    sce = 'calib_2014_2023'
    hds_file = os.path.join(os.path.dirname(cwd), 'mruns', f'{sce}', f'flow_{sce[-9:]}', '100hr3.hds')
    SimHeads = read_head(hds_file, mywells)
    generate_plots(mywells, CalibHeads, SimHeads)