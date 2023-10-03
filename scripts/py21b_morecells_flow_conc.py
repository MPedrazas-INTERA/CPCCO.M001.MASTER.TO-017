import os
import glob
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
import flopy.utils.binaryfile as bf

cwd = os.getcwd()
wdir = os.path.dirname(cwd)

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
    for idx, row, col in zip(range(len(df)), df.Row, df.Column):
        for t_idx, t in enumerate(times):
            for lay in nlays:
                vals.append([data[t_idx][lay][row][col], t, lay + 1, row, col, df.NAME.iloc[idx]])  # 237 nodes * 84 times = 19908 vals for L1
    df_return = pd.DataFrame(vals, columns=['Head', 'Time', 'Layer', 'Row', 'Column', 'NAME'])
    df_return.drop_duplicates(inplace=True)
    df_return["Date"] = pd.to_datetime("2014-01-01") + pd.to_timedelta(df_return.Time, unit="days")
    df_return.to_csv(os.path.join('output', 'water_level_data', f'{sce}', "sim_hds_flopy_100H_sources.csv"), index=False)
    return df_return

def read_ucn(ifile_ucn, df, precision = "double",all_lays = "True"):
    ucnobj = bf.UcnFile(ifile_ucn, precision=precision)
    times = ucnobj.get_times()
    data = ucnobj.get_alldata(mflay=None, nodata=-1) / 1000  # dividing by 1000 to match units of Obs
    ntimes, nlay, nr, nc = data.shape
    print(f"UCN file dimensions- SPs: {ntimes}, Layers: {nlay}, Rows: {nr}, Columns: {nc}")
    if all_lays:
        nlays = range(nlay)
    else:
        nlays = [0]
    vals = []
    for idx, row, col in zip(range(len(df)), df.Row, df.Column):
        for t_idx, t in enumerate(times):
            for lay in nlays:
                vals.append([data[t_idx][lay][row][col], t, lay + 1, row, col,
                             df.NAME.iloc[idx]])  # 237 nodes * 84 times = 19908 vals for L1
    df_return = pd.DataFrame(vals, columns=['Conc', 'Time', 'Layer', 'Row', 'Column', 'NAME'])
    df_return.drop_duplicates(inplace=True)
    df_return["Date"] = pd.to_datetime("2014-01-01") + pd.to_timedelta(df_return.Time, unit="days")
    df_return.to_csv(os.path.join('output', 'concentration_data', f'2014to2023', "sim_conc_flopy_100H_sources.csv"), index=False)
    return df_return

def plot_WL_vs_conc(wl_df, conc_df, nlays =9):

    """
    Plot concentration data of interest against water levels in one graph.
    """
    outputDir = os.path.join(cwd, 'output', 'concentration_vs_WL_plots', 'sim_2014_2023', 'sources')
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)
    hdsColors = ["seagreen", "green", "lawngreen", "dodgerblue", "darkblue", "slateblue", "midnightblue", "cyan", "darkviolet"]
    concColors = ["rosybrown", "lightcoral", "indianred", "brown", "firebrick", "maroon", "red", "orangered", "chocolate"]
    lsLst = ["-", "--"]*9
    for well in wl_df['NAME'].unique():
        print(well)
        ## set data to be plotted
        toplot_wl = wl_df[wl_df['NAME'] == well]  ## match to the correct input when function is called
        toplot_crvi = conc_df[conc_df['NAME'] == well] ## match to the correct input when function is called

        ## create figure instance and set specs
        fig, ax = plt.subplots(figsize=(15, 5))
        ax2 = ax.twinx()
        for lay in range(4):
            crvi = toplot_crvi.loc[toplot_crvi.Layer == lay+1]
            wl = toplot_wl.loc[toplot_wl.Layer == lay+1]

            ax.plot(pd.to_datetime(wl['Date']), wl['Head'], label=f'Sim WL - L{lay+1}', c= hdsColors[lay], ls = lsLst[lay])
            ax2.plot(pd.to_datetime(crvi['Date']), crvi['Conc'], zorder=10,
                     c = concColors[lay], label=f'Sim Cr(VI) - L{lay+1}', ls = lsLst[lay])
        ax.minorticks_on()
        ax.grid(which='major', linestyle='-',
                linewidth='0.1', color='red')
        ax.grid(which='minor', linestyle=':',
                linewidth='0.1', color='black')
        plt.xticks(rotation=45)

        ax.set_title(f'{well}', color='black')
        ax.set_ylabel('Water Level (m.asl)')
        ax2.set_ylabel('Cr(VI) (μg/L)')

        ## combined legend
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc=0)
        ax.set_xlim(pd.to_datetime("2014-01-01"), pd.to_datetime("2023-07-31"))
        ax2.set_xlim(pd.to_datetime("2014-01-01"), pd.to_datetime("2023-07-31"))
        plt.savefig(os.path.join(outputDir, f'{well}.png'))
        plt.close()
    print("Done")
    return None

def read_model_grid():
    """
    input : grid_with_centroids.shp <-- shapefile of model grid
    :return: grid <-- geopandas dataframe for model grid
    """
    print('reading grid file')
    grid = gpd.read_file(os.path.join(root, 'gis', 'shp', 'grid_with_centroids.shp'))
    print('finished reading grid file')
    return grid

def get_wells_coords(wells, grid):
    print("Getting coords info for each row, col")
    df = pd.merge(wells, grid, left_on = ["Row", "Column"], right_on = ['I', 'J'])
    df.to_csv(os.path.join(cwd, "input", f"100H_sources_XY.csv"), index=False)
    return df

if __name__ == "__main__":

    cwd = os.getcwd()

    # dictionaries to relate waste site groups to source zone areas:
    wastesiteDict = {1: '100-D-100 Sidewall', 2: '100-D-56-2 Pipeline', 3: '100-H-46-WS',
                     5: '107-H-RB', 4: '183-H-SEB'}
    grpDict = {3: 1, 4: 1, 14: 1, 19: 2, 6: 2, 18: 2, 9: 3, 10: 4, 13: 5, 25: 5, 12: 5}

    ssmDir = os.path.join("..", 'model_packages', 'hist_2014_2023', 'ssm')
    df_zon = pd.read_csv(os.path.join(ssmDir, "cr6_source_zones.dat"), delim_whitespace=True)
    df_src = df_zon.loc[df_zon['Zone'].isin(
        [9, 10, 12, 13, 25])]  # 100-H Waste Sites
    df_src['Group'] = df_src['Zone'].map(grpDict)  # group source zones into 5 groups based on waste site location
    df_src['R_C'] = df_src.Row.map(str) + '_' + df_src['Column'].map(str)
    df_src["WasteSite"] = df_src['Group'].map(wastesiteDict)

    sources = pd.DataFrame()
    df_src["NAME"] = ""
    for ws in df_src.WasteSite.unique():
        print(ws)
        mydf = df_src.loc[df_src.WasteSite == ws]
        for idx in range(len(mydf)):
            mydf.reset_index(drop=True, inplace=True)
            # print(idx)
            mydf["NAME"].iloc[idx] = mydf.WasteSite.map(str).iloc[idx] + '_' + str(idx)
        sources = sources.append(mydf)

    sce = 'calib_2014_2023'
    hds_file = os.path.join(os.path.dirname(cwd), 'mruns', f'{sce}', f'flow_{sce[-9:]}', '100hr3.hds')
    # myHds = read_head(hds_file, sources, all_lays = True)
    myHds = pd.read_csv(os.path.join('output', 'water_level_data', f'{sce}', "sim_hds_flopy_100H_sources.csv"))

    ucn_file = os.path.join(os.path.dirname(cwd), 'mruns', f'{sce}', f'tran_{sce[-9:]}', 'MT3D001.UCN')
    # myConcs = read_ucn(ucn_file, sources, precision = "double",all_lays = "True")
    myConcs = pd.read_csv(os.path.join('output', 'concentration_data', '2014to2023', "sim_conc_flopy_100H_sources.csv"))

    ### Plot WLs and CONCs:
    # plot_WL_vs_conc(myHds, myConcs, nlays = 9)

    root = os.path.join(os.path.dirname(cwd))
    grid = read_model_grid()
    well_list = pd.read_csv(os.path.join(cwd, "input", f"100H_sources.csv"))  # getting list of fake wells
    df = get_wells_coords(well_list, grid)  # getting XY info using GRID