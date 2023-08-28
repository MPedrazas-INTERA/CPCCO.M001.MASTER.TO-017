import os
import glob
import pandas as pd
import geopandas as gpd
import numpy as np
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
       # print(file.split("\\")[-1].split('.')[0]) ## extract filename directoy and use as dict key
        k = file.split("\\")[-1].split('.')[0]
        all_data[k] = pd.read_excel(file, sheet_name = None, engine='openpyxl') #, index_col = 0, parse_dates=True)

    strings = [data_files[i].split("\\")[-1].split('.')[0] for i, e in enumerate(data_files)] ## isolate file names without .xlsx extension
    dict1, dict2, dict3 = all_data[strings[0]].copy(), all_data[strings[1]].copy(), all_data[strings[2]].copy() ## separate data from nested dict into simple dict. create copy to avoid edits to original data.


    for k in dict1:
        dict1[k] = dict1[k].iloc[9:]
        dict1[k].columns = dict1[k].iloc[0]
        dict1[k].drop(dict1[k].index[0], inplace=True)
        dict1[k].index.name = 'DT'
        dict1[k].set_index('Date and Time', inplace=True)
        dict1[k].index = pd.to_datetime(dict1[k].index)
        # print(dict1[k].columns)  ##check correct column name assignment

    for k in dict2:
        dict2[k].set_index('Date/Time', inplace=True)
        dict2[k].index = pd.to_datetime(dict2[k].index)

    for k in dict3:
        dict3[k].set_index('HYD_DATE_TIME_PST', inplace=True)
        dict3[k].index = pd.to_datetime(dict3[k].index)


    return dict1, dict2, dict3

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

def get_wells_ij(dict1, dict2, dict3, coordscsv):
    print("Getting row and column info for each well")
    coords_database = pd.read_csv(coordscsv, delimiter = "|")
    well_lst = list(dict1.keys()) + list(dict2.keys()) + list(dict3.keys())
    mywells = coords_database.loc[coords_database.NAME.isin(well_lst)]

    ## create GDF from wells dataframe and merge with grid
    grid = read_model_grid()
    mycrs = grid.crs
    wells_gdf = gpd.GeoDataFrame(mywells,
                                 geometry=gpd.points_from_xy(mywells['XCOORDS'], mywells['YCOORDS']),
                                 crs=mycrs)

    gridwells = gpd.sjoin(grid, wells_gdf, how='right')
    df = gridwells.loc[:, ['NAME', 'XCOORDS', 'YCOORDS', 'I', 'J']]
    df = df[~df.index.duplicated(keep='first')]

    df.columns = ['NAME', 'X', 'Y', 'Row', 'Col']
    print('finished joining geodataframes')
    df2csv = df.copy()
    df2csv.reset_index(inplace=True)
    print(df2csv.head())
    print(df2csv.columns)
    df2csv.to_csv(os.path.join("output", "water_level_plots", "monitoring_wells_coords_ij.csv"), index=False)  # export CSV
    return df

def generate_plots(dict1, dict2, dict3):

    for mydict in [dict1, dict2, dict3]:
        if mydict == dict3:
            col = 'HYD_HEAD_METERS_NAVD88'
            title_spec = "100-H North Manual Data"
            nickname = "North_Manual"
        elif mydict == dict2:
            col = 'Elevation (m)'
            title_spec = '100-H North AWLN'
            nickname = "North_AWLN"

        elif mydict == dict1:
            col = 'Elevation of the water level in the well (m)'
            col2 = 'Elevation of the water level in the well(m)'
            title_spec = "100-H North P&T Sensor Data"
            nickname = "North_PT_SensorData"
        for k in mydict.keys():
            print(k)
            toplot = mydict[k]#.resample('D').mean()
            fig, ax = plt.subplots(figsize=(8, 5))
            if mydict == dict3:  ## dict3 are manual measurements -- scatter plot best
                ax.scatter(toplot.index, toplot.loc[:,col], label = f"Observed", c = "r", edgecolor="darkred", s=4)
                ax.plot(toplot.index, toplot.loc[:, col], c="r", ls="--")
                df = myHds.loc[(myHds.Layer == 1) & (myHds.NAME == k)]
                dates = pd.to_datetime("2014-01-01") + pd.to_timedelta(df.Time, unit = "days")
                ax.plot(dates, df.Head, label = f"Simulated", color = "cornflowerblue")
            else:
                try:
                    ax.scatter(toplot.index, toplot.loc[:,col], label = f"Observed", c = "r", edgecolor="darkred", s=4)
                    ax.plot(toplot.index, toplot.loc[:,col], c = "r", ls="--")
                    df = myHds.loc[(myHds.Layer == 1) & (myHds.NAME == k)]
                    dates = pd.to_datetime("2014-01-01") + pd.to_timedelta(df.Time, unit="days")
                    ax.plot(dates, df.Head, label = f"Simulated", color = "cornflowerblue")
                except:
                    ax.scatter(toplot.index, toplot.loc[:, col2], label = f"Observed", c = "r", edgecolor="darkred", s=4)
                    ax.plot(toplot.index, toplot.loc[:,col], c = "r", ls="--")
                    df = myHds.loc[(myHds.Layer == 1) & (myHds.NAME == k)]
                    dates = pd.to_datetime("2014-01-01") + pd.to_timedelta(df.Time, unit="days")
                    ax.plot(dates, df.Head, label = f"Simulated", color = "cornflowerblue")
            ax.set_title(f'{title_spec}: {k}')
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
            # ax.set_xlabel("Date")
            ax.set_xlim(pd.to_datetime("2014-01-01"), pd.to_datetime("2023-07-31"))
            ax.set_ylim([112.8,118])
            plt.savefig(os.path.join('output', 'water_level_plots', f'{nickname}_{k}.png'))
            plt.close()
    return None

if __name__ == "__main__":

    cwd = os.getcwd()

    dict1, dict2, dict3 = import_WL_data() ## run once at beginning of workflow
    coordscsv = os.path.join(os.path.dirname(cwd), 'data', 'water_levels', "qryWellHWIS.txt") #dataframe with coords for monitoring wells
    mywells = get_wells_ij(dict1, dict2, dict3, coordscsv)

    hds_file = r"C:\100HR3-Rebound\mruns\calib_2014_2023\flow_2014_2023\100hr3.hds"
    myHds = read_head(hds_file, mywells)

    generate_plots(dict1, dict2, dict3) ## provide column label to be plotted

### --- QC --- ###
##quick check for overlapping occurences##
# wells1, wells2, wells3 = list(dict1.keys()), list(dict2.keys()), list(dict3.keys())
# import itertools
# l = list(itertools.chain(wells1, wells2, wells3))
# from collections import Counter
# Counter(l)