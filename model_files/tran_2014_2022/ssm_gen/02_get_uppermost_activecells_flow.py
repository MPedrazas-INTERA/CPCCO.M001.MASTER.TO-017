#import geopandas as gpd
import pandas as pd
import os
import flopy
import flopy.utils.binaryfile as bf
from itertools import cycle
import numpy as np

def read_Hds(path2hds):
    # import model heads
    hds_obj = bf.HeadFile(path2hds, verbose=False)
    times = hds_obj.get_times()
    data = hds_obj.get_alldata(mflay=None)
    ntimes, nlay, nr, nc = data.shape
    return data, ntimes, nlay, nr, nc, times

def get_BtmsDF(path2flow, df, all_lays):
    """
    This fn will take in a dataframe to loop through Rows, Columns, Layers and extract Depth for bottoms
    Input:  dataframe
            all_lays = False if you only want the 1st Layer OR
            all_lays = True if you want ALL the model layers
    """
    # import model bottoms
    exe = 'mf2k-mst-chprc08dpv'
    ws = path2flow
    m = flopy.modflow.Modflow.load("DHmodel_2014to2020.nam", verbose=False, model_ws=ws, exe_name=exe, check=False,
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
        # for t_idx, t in enumerate(times):
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

def find_upper_active_cells(df_hds, config='SPECIAL'):
    """ Finds uppermost active cells for specific row colums.
        Input: zonation file with source cells or monitoring well locs (R-C) """

    if config == 'SPECIAL':
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
        if target == 'src_cells':
            #Find the deepest (maximum) uppermost layer for entire model timespan
            if not modify_ssm:
                final_lst = []
                for node in df_hds['R-C'].unique():
                    temp = df_hds.loc[df_hds['R-C'] == node]
                    final_lst.append([node, temp.Row.unique()[0], temp.Column.unique()[0], max(temp["Active Layer"])])
                df_activ = pd.DataFrame(final_lst, columns = ['Node',  'Row', 'Column', 'Active Layer'])

                # Update layer numbers in zonation file
                for i, rc in enumerate(zip(df_activ.Row, df_activ.Column)):
                    # print(rc[0], rc[1])
                    idx = df_zon['Layer'].loc[(df_zon.Row == rc[0]) & (df_zon.Column == rc[1])].index
                    print(df_zon['Layer'].loc[(df_zon.Row == rc[0]) & (df_zon.Column == rc[1])])
                    if df_activ['Active Layer'][i] >= 4:
                        df_zon.Layer.iloc[idx[0]] = 4
                    else:
                        df_zon.Layer.iloc[idx[0]] = df_activ['Active Layer'][i]
                if df_activ['Active Layer'][i] == 5:
                    print(f"*WARNING* Source for {rc[0], rc[1]} has been moved to Deep Layer {4} instead of {5}.")
                elif df_activ['Active Layer'][i] == 6:
                    print(f"*WARNING* Source for {rc[0], rc[1]} has been moved to Deep Layer {4} instead of {6}.")
                df_zon_rev = df_zon.copy()
            if modify_ssm: #we want active layer in every SP
                df_activ = df_hds.copy()
                # Update layer numbers in zonation file
                for i, rc in enumerate(zip(df_activ.Row, df_activ.Column)):
                    # print(rc[0], rc[1])
                    idx = df_zon['Layer'].loc[(df_zon.Row == rc[0]) & (df_zon.Column == rc[1])].index
                    print(df_zon['Layer'].loc[(df_zon.Row == rc[0]) & (df_zon.Column == rc[1])])
                    if df_activ['Active Layer'][i] >= 4:
                        df_zon.Layer.iloc[idx[0]] = 4
                    else:
                        df_zon.Layer.iloc[idx[0]] = df_activ['Active Layer'][i]
                if df_activ['Active Layer'][i] == 5:
                    print(f"*WARNING* Source for {rc[0], rc[1]} has been moved to Deep Layer {4} instead of {5}.")
                elif df_activ['Active Layer'][i] == 6:
                    print(f"*WARNING* Source for {rc[0], rc[1]} has been moved to Deep Layer {4} instead of {6}.")
                df_zon_rev = df_activ.copy()
        else:  # well_cells
            df_zon_rev = df_hds.copy()

    if config == 'STANDARD':
        df_dry = df_hds.loc[df_hds.Head > 900] #lets check if we have any dry cells, this is only true for a different MODFLOW config
        if len(df_dry) == 0:
            print("No dry cells in Layer 1 for all SPs, so no need update.")
        else:
            print("Checking dry cells in all other layers.")
            df_dry = df_dry.drop_duplicates(['Row', 'Column']) #remove TS duplicates
            df_dry_allLays = get_HdsDF(df_dry, all_lays=True)  #iterate through all layers
            #### make sure you're not DROPPING an entire Row,Col that's always dry.
            #### If ture, it's OK, but print out a statement about this.

            df_wet = df_dry_allLays.loc[(df_dry_allLays.Head < 900)] #drop dry cells
            df_wet['R-C'] = df_wet['Row'].map(str) + '-' + df_wet['Column'].map(str)

            #Find the uppermost layer per TS
            correctLayer = []
            for node in df_wet['R-C'].unique():
                oneNodeAtaTime = df_wet.loc[df_wet['R-C'] == node]
                for t in oneNodeAtaTime.Time.unique():
                    oneSPataTime = oneNodeAtaTime.loc[oneNodeAtaTime['Time'] == t]
                    layer = min(oneSPataTime.Layer)
                    correctLayer.append([node, t, layer, oneSPataTime.Row.unique()[0], oneSPataTime.Column.unique()[0]])
            df_final = pd.DataFrame(correctLayer, columns=['R-C', 'Time', 'Layer', 'Row', 'Column'])

            #Find the maximum uppermost layer for entire model timespan
            final_lst = []
            for node in df_final['R-C'].unique():
                temp = df_final.loc[df_final['R-C'] == node]
                final_lst.append([node, temp.Row.unique()[0], temp.Column.unique()[0], max(temp.Layer)])
            df_final2 = pd.DataFrame(final_lst, columns = ['Node',  'Row', 'Column','Active Layer'])

            #Replace dry nodes in zonation file with updated layer number
            for i, rc in enumerate(zip(df_final2.Row, df_final2.Column)):
                #print(rc[0],rc[1])
                idx = df_zon['Layer'].loc[(df_zon.Row == rc[0]) & (df_zon.Column == rc[1])].index
                df_zon.Layer.iloc[idx[0]] = df_final2['Active Layer'][i]
                #print(df_zon['Layer'].loc[(df_zon.Row == rc[0]) & (df_zon.Column == rc[1])])
                if df_final2['Active Layer'][i] > 4:
                    print(f"*WARNING* Source for {rc[0],rc[1]} has been moved to Deep Layers.")
            df_zon_rev = df_zon.copy()

    return df_zon_rev

if __name__ == "__main__":

    # directories
    cluster = True #toggle ON or OFF depending on whether script is ran in cluster or OneDrive

    model_dir = os.path.join('S:/', 'PSC', 'CHPRC.C003.HANOFF', 'Rel.126')
    cwd = os.getcwd()
    if cluster:
        outDir = cwd
        inputDir = cwd
        path2flow = path2hds = os.path.join("..", "flow_calib_9L")
    else: #OneDrive
        outDir = os.path.join(model_dir, 'predictive_model', 'output', 'src_zone')
        if not os.path.exists(outDir):
            os.makedirs(outDir)
        inputDir = os.path.join(model_dir, 'predictive_model', "input", "tran2014_2020")
        path2flow = os.path.join(model_dir, 'Updated_Model_9L')
    
    path2hds = os.path.join(path2flow,'DHmodel_2014to2020.hds') #DHmodel_2021to2125.hds
    print("Using HDS file here: ", path2hds)
    ### Define target and configuration:
    target = 'src_cells' #'src_cells' #'well_cells'
    config = 'SPECIAL' #keep this modflow config for 100-HR
    modify_ssm = True #this handle only works for target = src_cells
    #Note. If running in cluster, the only config you need is 'src_cells' and modify_ssm=True.

    if target == 'src_cells':
        # import source zonation file
        if cluster:
            df_zon = pd.read_csv("cr6_source_zones.dat", delim_whitespace=True)
        else:
            df_zon = pd.read_csv(os.path.join("..", "input", "cr6_source_zones.dat"), delim_whitespace=True)
        df_src = df_zon.loc[df_zon.Zone != 1]

    else: #'well_cells'
        df_wel = pd.read_csv(os.path.join("..", "input",'well_list_v3.csv'))
        df_wel.rename(columns={'i':'Row', 'j': 'Column', 'k':'Layer'}, inplace=True)
        df_src = df_wel.copy()


    data, ntimes, nlay, nr, nc, times = read_Hds(path2hds)
    print(f"This model has {ntimes}")
    df_hds = get_HdsDF(data, df_src, all_lays=False) #only care about Heads for Layer 1.
    df_btm = get_BtmsDF(path2flow, df_src, all_lays=True) #get model bottoms for all layers
    df_rev = find_upper_active_cells(df_hds, config='SPECIAL')

    if target == 'src_cells':
        if not modify_ssm: #generating new .dat with uppermost active layer during entire timespan
            ofile = 'cr6_source_zones_9L.dat'
            df_src_only = df_rev.loc[df_rev.Zone != 1]
            df_src_only.to_csv(os.path.join(outDir, ofile), sep=' ', index=False) # Export revised csv
            ##below we structure data into format to be read by script 05_make_StartingParticleFile
            df_src_only = df_src_only[['Zone', 'Row', 'Column', 'Layer']] #re-order columns
            df_src_only.sort_values(by = 'Zone', inplace = True)  ##sort by zone number
            num = cycle(range(len(df_src_only)))
            df_src_only['num'] = [next(num) for i in range(len(df_src_only))]
            df_src_only['num'] += 1  ##create 1-based column to append to unique indice
            df_src_only['Zone'] = 'SRC_' + df_src_only['Zone'].astype('str') + '_' + df_src_only['num'].astype('str') #re-name row values to unique indices
            df_src_only.loc[:,['Zone','Row','Column','Layer']].to_csv(os.path.join(outDir, "src_zones_9L.csv"),
                                                                      sep=' ', index=False)  # Export revised csv, only source Zones
            print(f'{ofile} has been saved')
        if modify_ssm: #modifying SSSM package to update with active layer for each SP for each source cell.
            fin = "100HR3_2014_2020_transport_stomp2ssm.ssm" #"100HR3_2014_2020_transport_stomp2ssm.ssm"
            fout = "100HR3_2014_2020_transport_stomp2ssm_activLays.ssm"

            time = df_rev.iloc[0:ntimes]["Time"].copy()
            timeDict = time.to_dict()
            newLines = []
            counter = 0
            mysp = []
            with open(os.path.join(inputDir, fin), "r") as f_in, open(os.path.join(outDir, fout), 'w') as f_out:
                lines = f_in.read().splitlines()
                for idx, line in enumerate(lines):
                    if line == ' 290':
                        counter += 1
                        #print(counter)
                        mysp.append(counter) #get SPs
                    if (idx >= 2) & (line != ' 290') & (line != ' -1'):
                        mystr = line.split()
                        mylayer = int(mystr[0])
                        myrow = int(mystr[1])
                        mycolumn = int(mystr[2])
                        myactivelayer = df_rev["Active Layer"].loc[(df_rev["Row"] == myrow)
                                                                   & (df_rev["Column"] == mycolumn)
                                                                   & (df_rev["Time"] == timeDict[counter-1])]
                        if myactivelayer.iloc[0] > 4: #make it equal to 4, source cannot be in deep layers
                            newLine = f"         {4}       {myrow}       {mycolumn} {mystr[3]}        {mystr[4]}\n"
                        else:
                            newLine = f"         {myactivelayer.iloc[0]}       {myrow}       {mycolumn} {mystr[3]}        {mystr[4]}\n"
                        newLines.append(newLine)
                        f_out.write(newLine) #write out lines with updated layers = all the source cell lines
                    else:
                        f_out.write(line) #write out original lines if nothing to do with source cell location
                        f_out.write("\n")


    if target == 'well_cells': #get stats for active layer, then export csv
        df_wel['R-C'] = df_wel['Row'].map(str) + '-' + df_wel['Column'].map(str)
        df_rev2 = df_rev.merge(df_wel, how='left', on = 'R-C')

        #df_rev2.to_csv("wells_layers.csv", index=False)
        lst = []
        for well in df_rev2.Well_ID.unique():
            oneWellataTime = df_rev2.loc[df_rev2.Well_ID == well]
            for lay in range(nlay):
                oneLayataTime = oneWellataTime.loc[oneWellataTime['Active Layer'] == lay+1]
                lst.append([well, oneWellataTime["R-C"].unique()[0], lay+1, len(oneLayataTime)])
        df_stats = pd.DataFrame(lst, columns = ["Well_ID", "R-C", "Active Layer", "Count"])
        df_stats2 = df_stats.loc[df_stats.Count != 0]

        #Add corresponding depth to bottom of layer for each active layer:
        df_btm['R-C'] = df_btm['Row'].map(str) + '-' + df_btm['Column'].map(str)
        lst2=[]
        for i, node in enumerate(df_stats2["R-C"]):
            # for lay in range(nlay):
            layer = df_stats2["Active Layer"].iloc[i]
            btm_value = df_btm[f"Bottom_L{layer}"] .loc[(df_btm["R-C"] == df_stats2["R-C"].iloc[i])]# & ( == df_stats2["Active Layer"].iloc[i])]
            lst2.append([node, btm_value.iloc[0]])
        df_temp = pd.DataFrame(lst2, columns = ["R-C", "Model_Btm"])
        df_stats3 = pd.concat([df_stats2.reset_index(drop=True), df_temp], axis=1)
        df_stats_final = df_stats3.T.drop_duplicates().T.copy()

        outDir = os.path.join(os.path.dirname(cwd), 'output', 'src_zone')
        if not os.path.exists(outDir):
            os.makedirs(outDir)
        ofile = 'well_active_lays_rev2.dat'
        df_stats_final.to_csv(os.path.join(outDir, ofile), sep='\t', index=False)
        print(f'{ofile} has been saved')



