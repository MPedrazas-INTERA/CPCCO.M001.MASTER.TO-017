"""
This script creates a DB of well info including geographic coordinates AND model coordinates

"""

import glob, os
import pandas as pd
import geopandas as gpd
import numpy as np
import sys
import flopy

def load_mf(flow_model_ws, grid):
    # load an MODLOW flow model -------------------------------------------
    nfiles = []
    for file in os.listdir(flow_model_ws):
        if file.endswith(".nam"):
            nfiles.append(file)
    if len(nfiles) == 1:
        namfile = nfiles[0]
        print(namfile)
    else:
        print("Error. More than one NAM file is in this flow model ws directory")

    ml = flopy.modflow.Modflow.load(namfile,
        model_ws=flow_model_ws,
        load_only=["dis"],
        verbose=False,
        check=False,
        exe_name="mf2k-mst-chprc08dpl",
    )
    nlays, nr, nc, nper = ml.dis.nlay, ml.dis.nrow, ml.dis.ncol, ml.dis.nper
    print(nlays, nr, nc, nper)

    bot = ml.dis.botm
    dfz = pd.DataFrame()
    for lay in range(nlays):
        print(lay)
        bot_array = bot.array[lay]
        vals = []
        for row, col in zip(grid.I, grid.J):
            vals.append(bot_array[row - 1][col - 1])
        dfz[f'botm_{lay + 1}'] = vals
    dfbot = pd.concat([grid[["I","J"]],dfz], axis = 'columns')
    dfbot.rename(columns = {"I":"Row", "J": "Col"}, inplace=True)

    return nlays, dfbot

def read_model_grid():
    """
    input : grid_with_centroids.shp <-- shapefile of model grid
    :return: grid <-- geopandas dataframe for model grid
    """
    print('reading grid file')
    grid = gpd.read_file(os.path.join(root, 'gis', 'shp', 'grid_with_centroids.shp'))
    print('finished reading grid file')
    return grid

def get_wells_ijk(well_list):
    print("Getting row and column info for each monitoring well")
    screens = pd.read_excel(os.path.join(root, 'data', 'well_info', 'Well Screen8-29-2023version-3.3.xlsx'),
                            usecols=['WELL_NAME', 'STD_SCREEN_DEPTH_TOP_M', 'STD_SCREEN_DEPTH_BOTTOM_M'], engine = 'openpyxl')
    screens.drop_duplicates('WELL_NAME', keep='first', inplace=True)

    coordscsv = os.path.join(root, 'data', 'water_levels',
                             "qryWellHWIS.txt")  # dataframe with coords for monitoring wells

    coords = pd.read_csv(coordscsv, delimiter="|")
    wells = coords.loc[coords.NAME.isin(well_list.NAME)]

    ## create GDF from wells dataframe and merge with grid
    mycrs = grid.crs
    wells_gdf = gpd.GeoDataFrame(wells,
                                 geometry=gpd.points_from_xy(wells['XCOORDS'], wells['YCOORDS']),
                                 crs = mycrs)

    gridwells = gpd.sjoin(grid, wells_gdf, how='right')

    df = pd.merge(gridwells, screens, left_on = 'NAME', right_on = 'WELL_NAME')
    df['Ztop'] = df['ZCOORDS'] - df['STD_SCREEN_DEPTH_TOP_M']
    df['Zbot'] = df['ZCOORDS'] - df['STD_SCREEN_DEPTH_BOTTOM_M']
    df2 = df[['NAME', 'I', 'J', 'centroid_x', 'centroid_y', 'YCOORDS', 'XCOORDS', 'Ztop', 'Zbot']].copy()
    df2.rename(columns={"NAME": "ID", "I": "Row", "J": "Col"}, inplace=True)
    return df2

def gen_scrn_fracs(nlays, df, type, dfbot, output_dir):
    print("Calculating Screen Fractions")
    print(df.head())
    # if nlays ==9:
    #     print('reading shapefile for btm elevations to find screen intervals in 9L model')
    #     dfbot = gpd.read_file(os.path.join(root,"gis", "shp", "botm_elev", "botm_elev.shp"))
    # elif nlays == 6:
    #     print('reading shapefile for btm elevations to find screen intervals in 6L model')
    #     dfbot = gpd.read_file(os.path.join(root,"gis", "shp", "botm_elev_6L", "botm_elev_6L.shp"))

    # filter out to only well locations
    dfmerge = pd.merge(df, dfbot, how='left', on=['Row', 'Col'])
    # dfmerge.iloc[:,:-1].to_csv(os.path.join(outputDir, "checking_screen_botms.csv"))

    dfbot = dfmerge.filter(regex='botm')

    outf = open(os.path.join(output_dir, f'{type}_screen_summary_draft.csv'), 'w')
    if nlays == 9:
        outf.write(
            "wellID,scnLen,scnLenL1,scnLenL2,scnLenL3,scnLenL4,"
            "scnLenL5,scnLenL6,scnLenL7,scnLenL8,scnLenL9,fracL1,fracL2,fracL3,fracLenL4,fracL5,fracL6,fracLenL7,fracL8,fracL9\n")  # write header
    elif nlays == 6:
        outf.write(
            "wellID,scnLen,scnLenL1,scnLenL2,scnLenL3,scnLenL4,"
            "scnLenL5,scnLenL6,fracL1,fracL2,fracL3,fracLenL4,fracL5,fracL6\n")  # write header

    # mimic MJ script to get proportion of well screen in each layer using bottom option
    count = len(df)
    eltype = 'BOTTOM'
    mult = 0

    my_string = []
    fracs = []
    for kk in range(0, len(df)):
    # for kk in range(0, 1):
        wellid = df['ID'].iloc[kk]
        print(kk, f"Well {wellid}")
        length = []
        elist = []
        for k in range(0, nlays):
            elev = dfbot.iloc[kk, k]
            elist.append(elev) #list of each layer bottom elevation associated with each well

        # assign list of bottom elevs at cell
        scTop = df.Ztop.iloc[kk]  # value  line 126 from MJ script
        scBot = df.Zbot.iloc[kk]  # value  line 127 from MJ script
        scLen = scTop - scBot  # append list
        # get total length of screens
        length.append(scLen)
        LAYSC = {}
        if eltype == 'BOTTOM':
            for lay in range(1, nlays + 1):
                LAYSC.setdefault(lay, []) #create dictionary for each layer

        for sc in range(0, 1):  #wells only have 1 screen except for well 199-D5-157
            for lay in range(1, nlays + 1):
                elev = dfbot.iloc[kk, lay - 1] #bottom elev for each layer
                print(f"Layer {lay}, Bottom Elev: {elev}")
                if elev != -9999:
                    if scTop > elev and scBot >= elev and mult == 0: #Bottom Elev of layer is deeper than scrnBot
                        LAYSC[lay].append(scTop - scBot)
                        break
                    elif scTop > elev and scBot < elev and mult == 0: #scrnBot is deeper than Bottom Elev of layer
                        LAYSC[lay].append(scTop - elev)
                        mult = 1
                    elif scTop > elev and scBot >= elev and mult == 1:
                        for i in range(1, lay):
                            upelev = dfbot.iloc[kk, lay - 1 - i]  # upelev = row.getValue('L%d_BOT' % (lay - i))
                            if upelev != -9999:
                                LAYSC[lay].append(upelev - scBot)
                                break
                        mult = 0
                        break
                    elif scTop > elev and scBot < elev and mult == 1:
                        for i in range(1, lay):
                            upelev = dfbot.iloc[kk, lay - 1 - i]  # upelev = row.getValue('L%d_BOT' % (lay - i))
                            if upelev != -9999:
                                LAYSC[lay].append(upelev - elev)
                                break
                    elif scTop < elev:
                        continue
        #                else:
        #                    bad=1

        maxsc = []
        ftsc = []
        if eltype == 'BOTTOM':
            for lay in range(1, nlays + 1):
                l1 = LAYSC.values()  # make list of values for screen length
                l2 = sum(l1, [])
                frac = [x / scLen for x in l1] #fraction of screen length in each layer
                fracs.append(frac)

        outf.write("%s,%f," % (wellid, scLen))

        for item in l1: #lengths of screen in each layer
            outf.write("%s," % item)  # screen lengths
        for item in frac: #fractions of screen in each layer
            outf.write("%s," % item)  # fraction of screen in layer
        outf.write('\n')
        my_string.extend([wellid])  # get wellids written to output file for checking

    outf.close()

    # check no wells have been dropped because of rounding errors in elevation
    print("unique well IDs:", df.ID.nunique())
    print("unique well IDs written to csv:", len(my_string))

    return dfbot, dfmerge

def cleanup_screen_fracs(nlays, type, output_dir):
    print("Cleaning up screen fractions")
    #  read in screen lengths and fractions by layer:
    if nlays == 9:
        df = pd.read_csv(os.path.join(output_dir, f'{type}_screen_summary_draft.csv'), sep=',',skiprows=1, header=None,
                       names=['ID','scLen','lenL1','lenL2','lenL3','lenL4','lenL5','lenL6','lenL7','lenL8','lenL9',
                              'fL1','fL2','fL3','fL4','fL5','fL6','fL7','fL8','fL9'], index_col=False)
        ## reorder columns
        df = df[['ID', 'scLen', 'lenL1', 'lenL2', 'lenL3', 'lenL4', 'lenL5', 'lenL6', 'lenL7', 'lenL8', 'lenL9',
                   'fL1', 'fL2', 'fL3', 'fL4', 'fL5', 'fL6', 'fL7', 'fL8', 'fL9']]
    elif nlays ==6:
        df = pd.read_csv(os.path.join(output_dir, f'{type}_screen_summary_draft.csv'), sep=',',skiprows=1, header=None,
                       names=['ID','scLen','lenL1','lenL2','lenL3','lenL4','lenL5','lenL6',
                              'fL1','fL2','fL3','fL4','fL5','fL6'], index_col=False)
        ## reorder columns
        df = df[['ID', 'scLen', 'lenL1', 'lenL2', 'lenL3', 'lenL4', 'lenL5', 'lenL6',
                   'fL1', 'fL2', 'fL3', 'fL4', 'fL5', 'fL6']]

    # clean file formating: search and replace list brackets
    df=df.replace('\[','',regex=True)
    df=df.replace('\]','',regex=True)

    dff=df.copy()
    dff.drop(['ID'], axis=1, inplace=True)
    dff=dff.apply(pd.to_numeric)
    dff['ID']=df['ID']

    ###Fix well if screens are divided into two rows
    fracs = pd.DataFrame()
    for well in dff.ID.unique():
        OneWellAtaTime = dff.loc[dff.ID == well]
        if len(OneWellAtaTime) == 1:
            fracs = fracs.append(OneWellAtaTime)
        elif len(OneWellAtaTime) > 1:
            print(well)
            if nlays == 9:
                df_sum = pd.DataFrame(columns = ['ID', 'scLen', 'lenL1', 'lenL2', 'lenL3', 'lenL4', 'lenL5', 'lenL6','lenL7', 'lenL8', 'lenL9',
                                    'fL1', 'fL2', 'fL3', 'fL4', 'fL5', 'fL6', 'fL7', 'fL8', 'fL9'], data=None)
            elif nlays == 6:
                df_sum = pd.DataFrame(columns = ['ID', 'scLen', 'lenL1', 'lenL2', 'lenL3', 'lenL4', 'lenL5', 'lenL6',
                                    'fL1', 'fL2', 'fL3', 'fL4', 'fL5', 'fL6'], data=None)
            df_sum = {'ID': well, 'scLen': OneWellAtaTime.scLen.sum()}
            for i in range(nlays):
                df_sum[f'lenL{i+1}'] = OneWellAtaTime[f'lenL{i+1}'].sum()
                df_sum[f'fL{i+1}'] = (OneWellAtaTime[f'lenL{i+1}'].sum())/df_sum['scLen']
            fracs = fracs.append(df_sum, ignore_index=True)

    fracs.iloc[:, 2:] = fracs.iloc[:,2:].replace(['0', 0], np.nan)

    ####### Add info on max frac layer and deepest layer for each well
    print("Getting layer info for each well")
    # fracs = pd.read_csv(os.path.join(output_dir, f'{type}_screen_summary.csv'), index_col = 0)
    lyr_dict = {'fL1':1,'fL2':2,'fL3':3,'fL4':4,
                'fL5':5, 'fL6':6,'fL7':7,'fL8':8,'fL9':9}

    max_frac = pd.DataFrame(fracs.loc[:, 'fL1':f'fL{nlays}'].idxmax(axis=1), columns = ['lyrfrac'])
    max_frac = max_frac.replace(to_replace = lyr_dict)

    fracs['MaxFrac_Lay'] = max_frac #get largest screen fraction for each well

    ##Get deepest screened fraction for wells in unconfined layer
    filter = pd.notna(fracs['fL4'])
    fracs.loc[filter, 'Deepest_Lay'] = int(4)
    filter2 = ((fracs['fL3'] > 0) & (pd.isna(fracs['fL4'])))    ##a few unconfined wells only down to layer 3
    fracs.loc[filter2, 'Deepest_Lay'] = int(3)
    ##Get deepest screened fraction for wells in confined layer (RUM-2)
    filterRUM2 = pd.notna(fracs[f'fL{nlays}'])
    fracs.loc[filterRUM2, 'Deepest_Lay'] = int(nlays)
    fracs.to_csv(os.path.join(output_dir, f'{type}_screen_summary.csv'), index=False)
    print(f"Saved '{type}_screen_summary' in {output_dir}")
    return fracs

def get_layer_forPT(nlays, fracs): ## determines layer K based on filter screen fractions in each layer
    ### For particle tracking, we will set particles in every layer (04/03/2023)
    myLays = []
    print(f'Noted that particles were placed in aquifers only, not the aquitard \n')
    for well in np.unique(fracs.ID):
        mywell = fracs.loc[fracs.ID == well]
        #for n in range(1,10):
        for n in [2,3,4, nlays]: # hpham ignores aquitard layers 5-8 (aquitard)
            # print(mywell[f'fL{n}'].iloc[0])
            if pd.notna(mywell[f'fL{n}'].iloc[0]):
                myLays.append([well, mywell[f'fL{n}'].iloc[0], n])
    ptracks = pd.DataFrame(myLays, columns = ["ID", "Frac", "Lay"])
    ptracks["LocalZ"] = 0.5
    return ptracks

def gen_master_csv(nlays, df, fracs, ptracks, type, output_dir):
    masterDF = pd.merge(df, fracs, on="ID")
    masterDF['Aquifer'] = np.where(masterDF['Deepest_Lay'].isin([nlays]), 'RUM', 'Unconfined')
    masterDF.to_csv(os.path.join(output_dir, f'{type}_master.csv'), index=False)  # master_spreadsheet

    ptracksDF = pd.merge(df[["ID", "Row","Col"]], ptracks, on="ID", how="right")
    ptracksDF.to_csv(os.path.join(output_dir, f'{type}_ptracks.csv'), index=False)
    #ptracksDF.to_csv(os.path.join(cwd, f'{type}_ptracks.csv'), index=False)
    print("finished master spreadsheet and ptracks CSV")
    return masterDF, ptracksDF


if __name__ == "__main__":

    cwd = os.getcwd()
    root = os.path.join(os.path.dirname(cwd))
    grid = read_model_grid()

    case = 'calib_2014_2020'#'calib_2014_2023'
    flow_model_ws = os.path.join(root, "mruns", f"{case}", f"flow_{case[-9:]}")

    cluster = False
    if cluster:
        case = sys.argv[1]
    else:
        case = case

    output_dir = os.path.join(root, "scripts", "output", "well_info", f"{case}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    types = ['monitoring_wells']
    for type in types:
        nlays, dfbot = load_mf(flow_model_ws, grid)
        well_list = pd.read_csv(os.path.join(cwd, "input", f"{type}_coords_ij.csv"), usecols=[0])  #getting list of monitoring wells (NAME)
        df = get_wells_ijk(well_list) #getting IJK, screen interval (Ztop, Zbot) and XY information
        gen_scrn_fracs(nlays, df, type, dfbot, output_dir) #calculating fraction of scrn interval in each lay for each well
        fracs = cleanup_screen_fracs(nlays, type, output_dir) #cleanup previous fn + more layer info
        ptracks = get_layer_forPT(nlays, fracs) #choosing layers to set particles for PT
        masterDF, ptracksDF = gen_master_csv(nlays, df, fracs, ptracks, type, output_dir) #generating master spreadsheet + ptracks CSV
