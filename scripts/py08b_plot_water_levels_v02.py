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

"Author: RWeatherl, modified by MPedrazas"

### --- 1. Import and structure all data --- ###
def import_WL_data():

    data_files = glob.glob(os.path.join(os.path.dirname(cwd), 'data', 'water_levels', '*.xlsx'))

    all_data = {}
    for file in data_files:
       # print(file.split("\\")[-1].split('.')[0]) ## extract filename directory and use as dict key
        k = file.split("\\")[-1].split('.')[0]
        all_data[k] = pd.read_excel(file, sheet_name = None, engine='openpyxl') #, index_col = 0, parse_dates=True)

    strings = [data_files[i].split("\\")[-1].split('.')[0] for i, e in enumerate(data_files)] ## isolate file names without .xlsx extension
    dict1, dict2, dict3 = all_data[strings[0]].copy(), all_data[strings[1]].copy(), all_data[strings[2]].copy() ## separate data from nested dict into simple dict. create copy to avoid edits to original data.

    ## manipulations on individual dictionaries. Create consistent Date, ID, and water level columns to later combine all dicts into 1 df
    for k in dict1:
        dict1[k] = dict1[k].iloc[9:]
        dict1[k].columns = dict1[k].iloc[0]
        dict1[k].drop(dict1[k].index[0], inplace=True)
        dict1[k].set_index('Date and Time', inplace=True)
        dict1[k].index = pd.to_datetime(dict1[k].index)
        dict1[k].index.name = 'Date'
        dict1[k].insert(0, 'ID', k)
        dict1[k].rename(columns = {'Elevation of the water level in the well (m)': 'Water Level (m)'}, inplace = True)
        # print(dict1[k].columns)  ##check correct column name assignment

    for k in dict2:
        dict2[k].set_index('Date/Time', inplace=True)
        dict2[k].index = pd.to_datetime(dict2[k].index)
        dict2[k].index.name = 'Date'
        dict2[k].insert(0, 'ID', k)
        dict2[k].rename(columns={'Elevation (m)': 'Water Level (m)'}, inplace=True)

    for k in dict3:
        dict3[k].set_index('HYD_DATE_TIME_PST', inplace=True)
        dict3[k].index = pd.to_datetime(dict3[k].index)
        dict3[k].index.name = 'Date'
        dict3[k].insert(0, 'ID', k)
        dict3[k].rename(columns={'HYD_HEAD_METERS_NAVD88': 'Water Level (m)'}, inplace=True)

    ## combine all 3 separate dicts into one master dict
    masterdict = {**dict1, **dict2, **dict3}

    ## concatenate all into dataframe
    df = pd.concat([v for k, v in masterdict.items()])[['ID', 'Water Level (m)']]
    df['Water Level (m)'] = pd.to_numeric(df['Water Level (m)'])
    df_sp = df.reset_index()
    ## resample
    df_sp.set_index(['ID', 'Date'], inplace = True)
    ## resample to daily
    df_sp = df_sp.groupby([pd.Grouper(level = 'ID'),
                       pd.Grouper(freq = 'D', level=-1)]).mean()
    # resample to monthly
    df_sp_m = df_sp.groupby([pd.Grouper(level = 'ID'),
                       pd.Grouper(freq = 'MS', level=-1)]).mean()

    return df, df_sp, df_sp_m

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
    #df_return.to_csv(os.path.join('output', 'water_level_data', f'{sce}', "simulated_heads.csv"), index=False)
    return df_return

def read_model_grid():
    """
    input : grid_with_centroids.shp <-- shapefile of model grid
    :return: grid <-- geopandas dataframe for model grid
    """
    print('reading grid file')
    grid = gpd.read_file(os.path.join(os.path.dirname(cwd), 'gis', 'shp', 'grid_with_centroids.shp'))
    print('finished reading grid file')
    return grid

def get_wells_ij(df, coordscsv):
    print("Getting row and column info for each well")
    coords_database = pd.read_csv(coordscsv, delimiter = "|")
    well_lst = list(df['ID'].unique())
    wells = coords_database.loc[coords_database.NAME.isin(well_lst)]

    ## create GDF from wells dataframe and merge with grid
    grid = read_model_grid()
    mycrs = grid.crs
    wells_gdf = gpd.GeoDataFrame(wells,
                                 geometry=gpd.points_from_xy(wells['XCOORDS'], wells['YCOORDS']),
                                 crs=mycrs)

    gridwells = gpd.sjoin(grid, wells_gdf, how='right')
    mywells = gridwells.loc[:, ['NAME', 'XCOORDS', 'YCOORDS', 'I', 'J']]
    mywells = mywells[~mywells.index.duplicated(keep='first')]

    mywells.columns = ['NAME', 'X', 'Y', 'Row', 'Col']
    print('finished joining geodataframes')
    df2csv = mywells.copy()
    df2csv.reset_index(inplace=True)
    print(df2csv.head())
    print(df2csv.columns)
    # df2csv.to_csv(os.path.join("input", "monitoring_wells_coords_ij.csv"), index=False)  # export CSV
    return mywells

def generate_plots():

    for well in df_sp.index.get_level_values('ID').unique():
        toplot = df_sp.xs(well, level='ID')
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(toplot.index.get_level_values('Date'), toplot['Water Level (m)'], c = 'darkred',
                label = 'Observed - Resampled Monthly')
        df = myHds.loc[(myHds.Layer == 1) & (myHds.NAME == well)]
        dates = pd.to_datetime("2014-01-01") + pd.to_timedelta(df.Time, unit="days")
        ax.plot(dates, df.Head, label = f"Simulated", color = "cornflowerblue")
        is_in_calibwells = well in calibwells['Well_ID'].values
        if is_in_calibwells:
            ax.set_title(f'{well}', color = 'red')
        else:
            ax.set_title(f'{well}', color = 'black')
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
        # plt.savefig(os.path.join('output', 'water_level_plots', f'{sce}', 'monthly resampled', f'{well}.png'))
    # plt.close()

    return None

if __name__ == "__main__":

    cwd = os.getcwd()

    calibwells = pd.read_csv(os.path.join(cwd, 'input', 'well_list_v3_for_calibration.csv'))

    df, df_sp, df_sp_m = import_WL_data() ## run once at beginning of workflow
    #df.to_csv(os.path.join(cwd, 'output', 'water_level_data', 'all.csv'))
    # df_sp.to_csv(os.path.join(cwd, 'output', 'water_level_data', 'obs_2021_2023', 'measured_WLs_daily.csv'))

    coordscsv = os.path.join(os.path.dirname(cwd), 'data', 'water_levels', "qryWellHWIS.txt") #dataframe with coords for monitoring wells
    mywells = get_wells_ij(df, coordscsv)

    sce = 'calib_2014_2023'
    hds_file = os.path.join(os.path.dirname(cwd), 'mruns', f'{sce}', f'flow_{sce[-9:]}', '100hr3.hds')
    myHds = read_head(hds_file, mywells)

    # generate_plots()

### --- QC --- ###
##quick check for overlapping occurences##
# wells1, wells2, wells3 = list(dict1.keys()), list(dict2.keys()), list(dict3.keys())
# import itertools
# l = list(itertools.chain(wells1, wells2, wells3))
# from collections import Counter
# Counter(l)

## check resampled wls vs measured wls
odir = os.path.join(cwd, 'output', 'water_level_plots', 'resampling_checks')
if not os.path.isdir(odir):
    os.makedirs(odir)
for well in df['ID'].unique():
    print(well)
    raw = df[df['ID'] == well]
    resampled = df_sp_m.xs(well, level='ID')
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(raw.index, raw['Water Level (m)'], label = 'Observed - Raw')
    ax.plot(resampled.index.get_level_values('Date'), resampled['Water Level (m)'], c = 'darkred',
            label = 'Observed - Resampled Monthly')
    ax.legend()
    ax.grid()
    plt.savefig(os.path.join(odir, f'{well}_monthly.png'))

