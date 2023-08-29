"""
This script creates a DB of well info including geographic coordinates AND model coordinates

"""

import os
import pandas as pd
import geopandas as gpd
import numpy as np
import sys

def read_model_grid():
    """
    input : grid_with_centroids.shp <-- shapefile of model grid
    :return: grid <-- geopandas dataframe for model grid
    """
    print('reading grid file')
    grid = gpd.read_file(os.path.join(root, 'gis', 'shp', 'grid_with_centroids.shp'))
    print('finished reading grid file')

    return grid

def get_wells_ij():

    print("Getting row and column info for each well")

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

    dfz = gpd.read_file(os.path.join(root,"gis", "shp", "botm_elev", "botm_elev.shp"))
    dfz.drop('node', axis=1, inplace=True)
    # filter out to only well locations
    dfmerge = pd.merge(df, dfz, how='left', left_on=['I', 'J'], right_on=['row', 'column'])

    df2 = dfmerge.loc[:,['NAME', 'I', 'J', 'XCOORDS', 'YCOORDS', 'ZCOORDS', 'Ztop', 'Zbot', 'geometry_x',
                         'botm_1', 'botm_2', 'botm_3', 'botm_4', 'botm_5', 'botm_6', 'botm_7', 'botm_8', 'botm_9']]

    # Iterate through each row
    for index, row in df2.iterrows():
        well_screen_depth = row['Zbot']

        # Iterate through geological layer depths and find the first layer
        # where well screen depth is greater than or equal to the layer depth
        for layer_number in range(1, len(row)):
            if well_screen_depth >= row[f'Layer{layer_number}Depth']:
                df.at[index, 'LayerName'] = f'Layer{layer_number}'
                break


    #print('finished joining geodataframes')

    # df2csv = df.copy()
    # df2csv.reset_index(inplace=True)
    # print(df2csv.head())
    # print(df2csv.columns)
    # col0 = str(wellrates.shape[0]-1) # hp: had to to this because df.columns[0] is not the first column
    # print(col0)
    #
    # df2csv.rename(columns = {col0:"NAME"}, inplace=True)
    #print(df2csv.head())
    #print(df2csv.columns)
    
    # df2csv.to_csv(os.path.join(output_dir, f"{type}_IJ_XYZ.csv"), index=True)  # export CSV
    return df

def gen_scrn_fracs(df, type, output_dir):
    # df.reset_index(inplace=True) #wellID is Index
    print("Calculating Screen Fractions")
    df.rename(columns = {df.columns[0]: 'ID'}, inplace=True) #renaming first column header to ID
    print(df.head())
    print('reading shapefile for btm elevations to find screen intervals')
    dfz = gpd.read_file(os.path.join(root,"gis", "shp", "botm_elev", "botm_elev.shp"))
    dfz.drop('node', axis=1, inplace=True)
    # filter out to only well locations
    dfmerge = pd.merge(df, dfz, how='left', left_on=['I', 'J'], right_on=['row', 'column'])
    # dfmerge.iloc[:,:-1].to_csv(os.path.join(outputDir, "checking_screen_botms.csv"))

    dfbot = dfmerge.filter(regex='botm')

    outf = open(os.path.join(output_dir, f'{type}_screen_summary_draft.csv'), 'w')
    outf.write(
        "wellID,scnLen,scnLenL1,scnLenL2,scnLenL3,scnLenL4,"
        "scnLenL5,scnLenL6,scnLenL7,scnLenL8,scnLenL9,fracL1,fracL2,fracL3,fracLenL4,fracL5,fracL6,fracLenL7,fracL8,fracL9\n")  # write header

    # mimic MJ script to get proportion of well screen in each layer using bottom option
    count = len(df)
    eltype = 'BOTTOM'
    mult = 0
    nlays = 9#6

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

    return dfz, dfmerge

def cleanup_screen_fracs(type, output_dir):
    nlays = 9
    print("Cleaning up screen fractions")
    #  read in screen lengths and fractions by layer:

    df = pd.read_csv(os.path.join(output_dir, f'{type}_screen_summary_draft.csv'), sep=',',skiprows=1, header=None,
                   names=['ID','scLen','lenL1','lenL2','lenL3','lenL4','lenL5','lenL6','lenL7','lenL8','lenL9',
                          'fL1','fL2','fL3','fL4','fL5','fL6','fL7','fL8','fL9'], index_col=False)

    # clean file formating: search and replace list brackets
    df=df.replace('\[','',regex=True)
    df=df.replace('\]','',regex=True)

    dff=df.copy()
    dff.drop(['ID'], axis=1, inplace=True)
    dff=dff.apply(pd.to_numeric)
    dff['ID']=df['ID']
    ## reorder columns
    dff=dff[['ID','scLen','lenL1','lenL2','lenL3','lenL4','lenL5','lenL6','lenL7','lenL8','lenL9',
             'fL1','fL2','fL3','fL4','fL5','fL6','fL7','fL8','fL9']]
    # dff.to_csv(os.path.join(output_dir, f'{type}_screen_summary.csv'), sep=',', header=True, index=False)

    ###Fix well if screens are divided into two rows
    fracs = pd.DataFrame()
    for well in dff.ID.unique():
        OneWellAtaTime = dff.loc[dff.ID == well]
        if len(OneWellAtaTime) == 1:
            fracs = fracs.append(OneWellAtaTime)
        elif len(OneWellAtaTime) > 1:
            print(well)
            df_sum = pd.DataFrame(columns = ['ID', 'scLen', 'lenL1', 'lenL2', 'lenL3', 'lenL4', 'lenL5', 'lenL6','lenL7', 'lenL8', 'lenL9',
                                'fL1', 'fL2', 'fL3', 'fL4', 'fL5', 'fL6', 'fL7', 'fL8', 'fL9'], data=None)
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

    max_frac = pd.DataFrame(fracs.loc[:, 'fL1':'fL9'].idxmax(axis=1), columns = ['lyrfrac'])
    max_frac = max_frac.replace(to_replace = lyr_dict)

    fracs['MaxFrac_Lay'] = max_frac #get largest screen fraction for each well

    ##Get deepest screened fraction for wells in unconfined layer
    filter = pd.notna(fracs['fL4'])
    fracs.loc[filter, 'Deepest_Lay'] = int(4)
    filter2 = ((fracs['fL3'] > 0) & (pd.isna(fracs['fL4'])))    ##a few unconfined wells only down to layer 3
    fracs.loc[filter2, 'Deepest_Lay'] = int(3)
    ##Get deepest screened fraction for wells in confined layer
    filter9 = pd.notna(fracs['fL9'])
    fracs.loc[filter9, 'Deepest_Lay'] = int(9)
    fracs.reset_index(inplace=True)

    fracs.to_csv(os.path.join(output_dir, f'{type}_screen_summary.csv'), index=False)
    print(f"Saved '{type}_screen_summary' in {output_dir}")
    return fracs

def gen_master_csv(df, fracs, ptracks, type, output_dir):
    masterDF = pd.merge(df, fracs, on="ID")
    ###Underscore in new wells messed up the split:
    masterDF.ID = masterDF.ID.str.replace("nw_","nw-") #incase new wells lower case have underscore
    masterDF.ID = masterDF.ID.str.replace("NW_","nw-") #incase new wells upper case have underscore
    masterDF.ID = masterDF.ID.str.replace("SF_","SF-") #incase soil flushing wells upper case have underscore
    masterDF[['Short', 'Function', 'System']] = masterDF['ID'].str.split('_', 2, expand=True)
    masterDF['Aquifer'] = np.where(masterDF['Deepest_Lay'].isin([9]), 'RUM', 'Unconfined')
    ### Revert to underscore for new wells after split
    masterDF.ID = masterDF.ID.str.replace("nw-","nw_") #incase new wells lower case have underscore
    masterDF.ID = masterDF.ID.str.replace("NW-","nw_") #incase new wells upper case have underscore
    masterDF.ID = masterDF.ID.str.replace("SF-","SF_") #incase soil flushing wells upper case have underscore
    masterDF.Short = masterDF.Short.str.replace("nw-","nw_") #incase new wells lower case have underscore
    masterDF.Short = masterDF.Short.str.replace("NW-","nw_") #incase new wells upper case have underscore
    masterDF.Short = masterDF.Short.str.replace("SF-","SF_") #incase soil flushing wells upper case have underscore

    masterDF.to_csv(os.path.join(output_dir, f'{type}_master.csv'), index=False)  # master_spreadsheet

    ptracksDF = pd.merge(df[["ID", "Row","Col"]], ptracks, on="ID", how="right")
    ptracksDF.to_csv(os.path.join(output_dir, f'{type}_ptracks.csv'))
    #ptracksDF.to_csv(os.path.join(cwd, f'{type}_ptracks.csv'), index=False)
    print("finished master spreadsheet and ptracks CSV")
    return masterDF, ptracksDF


if __name__ == "__main__":

    cwd = os.getcwd()
    root = os.path.dirname(cwd)
    grid = read_model_grid()

    output_dir = os.path.join(root, "scripts", "output", "well_info")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    well_list = pd.read_csv(os.path.join(cwd, 'output', 'well_info', 'monitoring_well_list.csv'))
    screens = pd.read_excel(os.path.join(root, 'data', 'well_info', 'Well Screen8-29-2023version-3.3.xlsx'),
                            usecols = ['WELL_NAME', 'STD_SCREEN_DEPTH_TOP_M', 'STD_SCREEN_DEPTH_BOTTOM_M'])
    screens.drop_duplicates('WELL_NAME', keep = 'first', inplace=True)



    # wellcsv = os.path.join(root, "model_packages", "pred_2023_2125", f"{case}", "wellinfodxhx_cy2023_2125.csv")
    # rates = os.path.join(root, "model_packages", "pred_2023_2125", f"{case}","wellinfodxhx_cy2023_2125.csv")
    # types = ['extractionwells','allwells']
    # for type in types:
    #     df = get_wells_ij(wellcsv, rates)  #getting row-col for well coords
    #     gen_scrn_fracs(df, type, output_dir) #calculating fraction of scrn interval in each lay for each well
    #     fracs = cleanup_screen_fracs(type, output_dir) #cleanup previous fn + more layer info
    #     ptracks = get_layer_forPT(fracs) #choosing layers to set particles for PT
    #     masterDF, ptracksDF = gen_master_csv(df, fracs, ptracks, type, output_dir) #generating master spreadsheet + ptracks CSV
