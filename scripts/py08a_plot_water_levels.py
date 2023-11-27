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
        if not file.endswith("Water Level Detail for Selections9-28-2023.xlsx"):
            print(file.split("\\")[-1].split('.')[0]) ## extract filename directoy and use as dict key
            k = file.split("\\")[-1].split('.')[0]
            all_data[k] = pd.read_excel(file, sheet_name = None, engine='openpyxl') #, index_col = 0, parse_dates=True)

    strings = [data_files[i].split("\\")[-1].split('.')[0] for i, e in enumerate(data_files)] ## isolate file names without .xlsx extension
    dict1, dict2, dict3 = all_data[strings[0]].copy(), all_data[strings[1]].copy(), all_data[strings[2]].copy() ## separate data from nested dict into simple dict. create copy to avoid edits to original data.
    dict4, dict5 = all_data[strings[3]].copy(), all_data[strings[4]].copy()
    ## manipulations on individual dictionaries. Create consistent Date, ID, and water level columns to later combine all dicts into 1 df
    for k in dict1: #100-H_North_ P&T Sensor Data.xlsx
        dict1[k] = dict1[k].iloc[9:]
        dict1[k].columns = dict1[k].iloc[0]
        dict1[k].drop(dict1[k].index[0], inplace=True)
        dict1[k].set_index('Date and Time', inplace=True)
        dict1[k].index = pd.to_datetime(dict1[k].index)
        dict1[k].index.name = 'Date'
        dict1[k].insert(0, 'ID', k)
        dict1[k].rename(columns = {'Elevation of the water level in the well (m)': 'Water Level (m)'}, inplace = True)
        # print(dict1[k].columns)  ##check correct column name assignment

    for k in dict2: #100-H_North_AWLN Data.xlsx
        dict2[k].set_index('Date/Time', inplace=True)
        dict2[k].index = pd.to_datetime(dict2[k].index)
        dict2[k].index.name = 'Date'
        dict2[k].insert(0, 'ID', k)
        dict2[k].rename(columns={'Elevation (m)': 'Water Level (m)'}, inplace=True)

    for k in dict3: #100-H_North_Manual Data.xlsx
        dict3[k].set_index('HYD_DATE_TIME_PST', inplace=True)
        dict3[k].index = pd.to_datetime(dict3[k].index)
        dict3[k].index.name = 'Date'
        dict3[k].insert(0, 'ID', k)
        dict3[k].rename(columns={'HYD_HEAD_METERS_NAVD88': 'Water Level (m)'}, inplace=True)

    for k in dict4: #AWLN Water Level Tracking v2.xlsx
        dict4[k].set_index('Date/Time', inplace=True)
        dict4[k].index = pd.to_datetime(dict4[k].index)
        dict4[k].index.name = 'Date'
        dict4[k].insert(0, 'ID', k)
        dict4[k].rename(columns={'Elevation (m)': 'Water Level (m)'}, inplace=True)

    for k in dict5: #P&T Water Level Tracking v2.xlsx
        print(k)
        dict5[k] = dict5[k].iloc[9:,:4]
        dict5[k].columns = dict5[k].iloc[0]
        dict5[k].drop(dict5[k].index[0], inplace=True)
        dict5[k].set_index('Date and Time', inplace=True)
        dict5[k].index = pd.to_datetime(dict5[k].index)
        dict5[k].index.name = 'Date'
        dict5[k].insert(0, 'ID', k)
        dict5[k].rename(columns={'Elevation of the water level in the well (m)': 'Water Level (m)'}, inplace=True)

    masterdict = {**dict1, **dict2, **dict3, **dict4, **dict5}  ## combine dicts into one master dict
    df = pd.concat([v for k, v in masterdict.items()])[['ID', 'Water Level (m)']] ## concatenate all into dataframe
    df['Water Level (m)'] = pd.to_numeric(df['Water Level (m)'])
    df.drop_duplicates(inplace=True) #size 101474 -> 52954 #duplicates removed

    df_sp = df.reset_index() #resample monthly
    df_sp.set_index(['ID', 'Date'], inplace = True)
    df_sp = df_sp.groupby([pd.Grouper(level = 'ID'),
                       pd.Grouper(freq = 'MS', level=-1)]).mean()

    df_daily = df.reset_index() #resample daily
    df_daily.set_index(['ID', 'Date'], inplace=True)
    df_daily = df_daily.groupby([pd.Grouper(level='ID'),
                           pd.Grouper(freq='D', level=-1)]).mean()

    outputDir = os.path.join(cwd, 'output', 'water_level_data', f"{sce}")
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

    df.to_csv(os.path.join(outputDir, 'measured_WLs_all.csv'))
    df_sp.to_csv(os.path.join(outputDir, 'measured_WLs_monthly.csv'))
    df_daily.to_csv(os.path.join(outputDir, 'measured_WLs_daily.csv'))

    ## resample to monthly to match model SPs. Possibly integrate this directly into plotting function.
    # mydict, mydict_sp = {}, {}
    # for k in dict1.keys():
    #     mydict[k] = dict1[k].iloc[:,2]
    #     mydict_sp[k] = dict1[k].iloc[:,2].apply(pd.to_numeric).resample('MS').mean()
    # for k in dict2.keys():
    #     mydict[k] = dict2[k].iloc[:, 2]
    #     mydict_sp[k] = dict2[k].iloc[:,2].apply(pd.to_numeric).resample('MS').mean()
    # for k in dict3.keys():
    #     mydict[k] = dict3[k].iloc[:,0]
    #     mydict_sp[k] = dict3[k].iloc[:,0].apply(pd.to_numeric).resample('MS').mean()

    return df, df_sp, df_daily

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
    df_return.to_csv(os.path.join('output', 'water_level_data', f'{sce}', "simulated_heads_monthly_flopy.csv"), index=False)
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
    well_lst = df.ID.unique()
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
    # df2csv.to_csv(os.path.join("input", "monitoring_wells_coords_ij.csv"), index=False)  # export CSV
    return df

def generate_plots(df):
    col = "Water Level (m)"
    for k in df.ID.unique():
        print(k)
        toplot = df.loc[df.ID == k]#.resample('D').mean()
        fig, ax = plt.subplots(figsize=(8, 5))
    try:
        ax.scatter(toplot.index, toplot.loc[:,col], label = f"Observed", c = "r", edgecolor="darkred", s=4)
        ax.plot(toplot.index, toplot.loc[:,col], c = "r", ls="--")
        df = myHds.loc[(myHds.Layer == 1) & (myHds.NAME == k)]
        dates = pd.to_datetime("2014-01-01") + pd.to_timedelta(df.Time, unit="days")
        ax.plot(dates, df.Head, label = f"Simulated", color = "cornflowerblue")
    except:
        print('could not plot')
    ax.set_title(f'{k}: {wellDict[k]}')
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
    plt.savefig(os.path.join('output', 'water_level_plots', f'{sce}', f'{nickname}_{k}.png'))
    plt.close()
    return None

if __name__ == "__main__":

    wellDict = {'199-H3-25': "North PT Sensor Data", '199-H3-26': "North PT Sensor Data", '199-H3-27': "North PT Sensor Data", '199-H3-2A': "North AWLN", '199-H4-12A': "North Manual",
     '199-H4-15A': "North Manual", '199-H4-17': "North PT Sensor Data", '199-H4-18': "North Manual", '199-H4-4': "North PT Sensor Data", '199-H4-5': "North AWLN",
     '199-H4-64': "North Manual", '199-H4-65': "North Manual", '199-H4-8': "North AWLN", '199-H4-84': "North AWLN", '199-H4-85': "North Manual",
     '199-H4-86': "North PT Sensor Data", '199-H4-88': "North AWLN", '199-H4-89': "North Manual",
     '199-H3-10': "RUM-2", '199-H3-12': "RUM-2", '199-H3-13': "RUM-2", '199-H3-30': "RUM-2", '199-H3-32': "RUM-2", '199-H4-90': "RUM-2"}

    cwd = os.getcwd()
    sce = 'obs_2021_Oct2023'
    df, df_sp, df_daily = import_WL_data() ## run once at beginning of workflow

    coordscsv = os.path.join(os.path.dirname(cwd), 'data', 'water_levels', "qryWellHWIS.txt") #dataframe with coords for monitoring wells
    mywells = get_wells_ij(df, coordscsv)

    plot_hds = False
    if plot_hds:
        hds_file = os.path.join(os.path.dirname(cwd), 'mruns', f'{sce}', f'flow_{sce[-9:]}', '100hr3.hds')
        myHds = read_head(hds_file, mywells)
        generate_plots(df) ## provide column label to be plotted