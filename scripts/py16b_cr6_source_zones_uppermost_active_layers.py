"""
Based on script 02_get_uppermost_activecells_flow.py from 100HR3 Rel.126 adapted for soil flushing
1. Extracts uppermost active cell at source cell locations
2. Uses this cell to define depth for soil flushing
"""

import os
import pandas as pd
import geopandas as gpd
import numpy as np
import flopy
import flopy.utils.binaryfile as bf

def read_Hds(path2hds):

    # import model heads
    hds_obj = bf.HeadFile(path2hds, verbose=False)
    times = hds_obj.get_times()
    data = hds_obj.get_alldata(mflay=None)
    ntimes, nlay, nr, nc = data.shape

    return data, ntimes, nlay, nr, nc, times


def get_BtmsDF(model_dir, df, all_lays):
    """
    This fn will take in a dataframe to loop through Rows, Columns, Layers and extract Depth for bottoms
    Input:  dataframe
            all_lays = False if you only want the 1st Layer OR
            all_lays = True if you want ALL the model layers
    """
    # import model bottoms
    exe = 'mf2k-mst-chprc08dpv'
    ws = model_dir
    m = flopy.modflow.Modflow.load("DHmodel_2021to2125.nam", verbose=False, model_ws=ws, exe_name=exe, check=False,
                                   load_only='dis')  # load model
    dis = m.get_package("dis")  # get dis object
    btm_obj = m.dis.botm

    if all_lays:
        nlays = range(nlay) #9 layers in model
    else:
        nlays = [0]

    df_tmp = pd.DataFrame()

    df_tmp["Row"] = df.Row
    df_tmp["Column"] = df.Column
    for lay in nlays:
        vals = []
        for row, col in zip(df.Row, df.Column):
            vals.append(btm_obj.array[lay][row-1][col-1])
        df_tmp[f'Bottom_L{lay+1}'] = vals

    df_return = df_tmp

    return df_return

def get_HdsDF(data, df, all_lays):
    """
    This fn will take in a data frame to loop through Rows, Columns, Times, Layers and extract Heads
    Input:  flopy/numpy array (data) contains head information
            all_lays = False if you only want the 1st Layer OR
            all_lays = True if you want ALL the model layers
    Output: dataframe to return with head information for Row, Col, Times, Lays of interest.
    """
    if all_lays:
        nlays = range(nlay)
    else:
        nlays = [0]
    vals = []
    for row, col in zip(df.Row, df.Column):
        for t_idx, t in enumerate(times):
            for lay in nlays:
                vals.append([data[t_idx][lay][row][col], t, lay + 1, row, col])  # 237 nodes * 84 times = 19908 vals for L1
    df_return = pd.DataFrame(vals, columns=['Head', 'Time', 'Layer', 'Row', 'Column'])

    return df_return

def find_upper_active_cells(df_hds, df_btm, df_zon, nlay):
    """ Finds uppermost active cells for specific row colums.
        Input: zonation file with source cells or monitoring well locs (R-C) """

    lst = []
    for idx, row in df_hds.iterrows():
        for lay in range(nlay): #9 layers in model
            if row[0] < df_btm[f'Bottom_L{lay+1}'].loc[(df_btm.Row == row[3]) & (df_btm.Column == row[4])].iloc[0]:#head value for R-C-L node
                # print(f"Head for Row {int(row[3])} - Column {int(row[4])}  is less than Bottom of Layer {lay+1}") #- Layer {int(row[2])}
                pass
            else:
                #print(f"Head for Row {int(row[3])} - Column {int(row[4])}  belongs to Layer {lay+1}")
                lst.append(lay+1)
                break
    df_hds["Active Layer"] = lst
    if len(df_hds.loc[df_hds.Head >= 999]) == 0: # lets check if we have any INACTIVE cells
        print("No inactive cells in all source cells for all SPs...")
    else:
        print("*WARNING* Inactive cells found.")

    df_hds['R-C'] = df_hds['Row'].map(str) + '-' + df_hds['Column'].map(str)
    #Find the deepest (maximum) uppermost layer for entire model timespan

    final_lst = []
    for node in df_hds['R-C'].unique():
        temp = df_hds.loc[df_hds['R-C'] == node]
        final_lst.append([node, temp.Row.unique()[0], temp.Column.unique()[0], max(temp["Active Layer"])])
    df_activ = pd.DataFrame(final_lst, columns = ['Node',  'Row', 'Column', 'Active Layer'])

    # Update layer numbers in zonation file
    for i, rc in enumerate(zip(df_activ.Row, df_activ.Column)):
        # print(rc[0], rc[1])
        idx = df_zon['Layer'].loc[(df_zon.Row == rc[0]) & (df_zon.Column == rc[1])].index
        #print(df_zon['Layer'].loc[(df_zon.Row == rc[0]) & (df_zon.Column == rc[1])])
        if df_activ['Active Layer'][i] >= 4:
            df_zon.Layer.iloc[idx[0]] = 4
        else:
            df_zon.Layer.iloc[idx[0]] = df_activ['Active Layer'][i]
    if df_activ['Active Layer'][i] == 5:
        print(f"*WARNING* Source for {rc[0], rc[1]} has been moved to Deep Layer {4} instead of {5}.")
    elif df_activ['Active Layer'][i] == 6:
        print(f"*WARNING* Source for {rc[0], rc[1]} has been moved to Deep Layer {4} instead of {6}.")
    df_zon_rev = df_zon.copy()

    return df_zon_rev

if __name__ == "__main__":

    cwd = os.getcwd()
    root = os.path.join(os.path.dirname(cwd))

    sce = 'sce3a_rr8_to2125_notfinal'
    model_dir = os.path.join(root, 'mruns', sce, 'flow_2023to2125')

    df_zon = pd.read_csv(os.path.join('..', 'continuing_source_modeling', 'input', "cr6_source_zones.dat"), delim_whitespace=True)
    df_src = df_zon.loc[df_zon.Zone != 1]

    data, ntimes, nlay, nr, nc, times = read_Hds(os.path.join(model_dir, '100hr3_2023to2125.hds'))
    print(f"This model has {ntimes}")
    df_hds = get_HdsDF(data, df_src, all_lays=True) #only care about Heads for Layer 1.
    df_btm = get_BtmsDF(model_dir, df_src, all_lays=True) #get model bottoms for all layers
    df_rev = find_upper_active_cells(df_hds, df_btm, df_zon, nlay)
    df_src_only = df_rev.loc[df_rev.Zone != 1]

    # df_src_only.to_csv(os.path.join(outDir, ofile), sep=' ', index=False)  # Export revised csv



