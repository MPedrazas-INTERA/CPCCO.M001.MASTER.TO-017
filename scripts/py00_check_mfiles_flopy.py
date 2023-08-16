from operator import index
import time
import os
import sys
import re
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import datetime as dt
import shutil

# Checking 100hr3 model files
# use conda activate irp
# read flow and transport model files using flopy

try:
    import flopy
except:
    fpth = os.path.abspath(os.path.join("..", ".."))
    sys.path.append(fpth)
    import flopy
from flopy.utils.postprocessing import (
    get_transmissivities,
    get_saturated_thickness,
    get_water_table,
    get_gradients)
import flopy.utils.binaryfile as bf

print(sys.version)
print("numpy version: {}".format(np.__version__))
print("matplotlib version: {}".format(mpl.__version__))
print("pandas version: {}".format(pd.__version__))
print("flopy version: {}".format(flopy.__version__))


def get_min_max(arr):
    #arr[arr>1e3] = np.nan
    min_ = np.nanmin(arr)
    avg_ = np.nanmean(arr)
    max_ = np.nanmax(arr)
    print(f'Min: {min_},\n Max: {max_}, \n ave: {avg_}')

def export_wt(work_dir, wt_ele, ts):
    gridShp = 'input/shp/grid_274_geo_rc2.shp'
    grid = gpd.read_file(gridShp)
    dfloc = pd.DataFrame()
    dfloc['row'] = grid['row']
    dfloc['column'] = grid['column']
    dfloc['XCoor'] = grid['XCoor']
    dfloc['YCoor'] = grid['YCoor']
    dfloc['IBND'] = grid['IBND']
    dfloc['val'] = np.reshape(wt_ele, [nr*nc, 1])
    ofile = os.path.join(work_dir, 'output',
                         f'wt_ele_TS{ts}_ver_{today_dt}.csv')
    dfloc.to_csv(ofile, index=False)
    print(f'Save {ofile}\n')

def arr2shp(arr,gridShp,ofile):
    '''
    Export an arry to a shapefile
    '''
    nr, nc = arr.shape
    print(nr, nc)
    val = np.reshape(arr, nr*nc)

    # use model grid shapefile geometry
    # model grid shapefile
    try:
        #gridShp = os.path.join('input', 'shp_files', 'grid_274_geo_rc.shp')
        gdf = gpd.read_file(gridShp)
        #gdf.head(5)
        #gdf.plot()
    except:
        print('ERROR: Something went wrong when reading grid shapefile')
    
    df = pd.DataFrame()
    #df['row'] = gdf['row']
    #df['column'] = gdf['column']
    df['val'] = val

    # export shapefile
    gdf1 = gpd.GeoDataFrame(df, crs='EPSG:4326', geometry=gdf.geometry)
    # ofile_shp = os.path.join(
    #    work_dir, 'scripts', 'output', 'shp', 'Cmax_trit_ts76.shp')
    gdf1.to_file(driver='ESRI Shapefile', filename=ofile)
    print(f'Saved {ofile} ! ! !')

def read_ucn(ifile_ucn):
    #ucnobj = bf.UcnFile(ifile_ucn, precision='double')
    ucnobj = bf.UcnFile(ifile_ucn, precision='single')
    times = ucnobj.get_times()
    data = ucnobj.get_alldata(mflay=None, nodata=-1)
    ntimes, nlay, nr, nc = data.shape
    # times = ucnobj.get_times()
    # for t in times:
    #    conc = ucnobj.get_data(totim=t)
    return data, ntimes, nlay, nr, nc, times, ucnobj

def read_flow_files(flow_model_ws):
    # load an MODLOW flow model -------------------------------------------
    ml = flopy.modflow.Modflow.load(
        "DHmodel_2014to2020.nam",
        model_ws=flow_model_ws,
        #load_only=["dis", "bas6", "sfr"],
        verbose=True,
        check=False,
        #forgive=False,
        exe_name="mf2k-mst-chprc08dpl",
    )
    # load_only=["dis", "bas6", "sfr"], verbose=True, check=False, forgive=False
    #top = ml.dis.gettop()
    #bot = ml.dis.getbotm()
    #hk = ml.lpf.hk
    #ml.dis
    #ml.bas6
    #ml.lpf
    nlay, nr, nc, nper = ml.dis.nlay, ml.dis.nrow, ml.dis.ncol, ml.dis.nper
    
    return ml

def read_tran_files(tran_model_ws, name_file, ml):
    # Load MT3D tranport model files --------------------------------------
    #tran_model_ws2 = os.path.join(tran_model_ws, coc)
    mt = flopy.mt3d.mt.Mt3dms.load(
        name_file,
        model_ws=tran_model_ws,
        exe_name="mt3d-mst-chprc08dpl.x",
        modflowmodel=ml,
        verbose=True,
    )
    return mt

def process_mnw2(ml):
    nlay, nr, nc, nper = ml.dis.nlay, ml.dis.nrow, ml.dis.ncol, ml.dis.nper
    sp=1 # MODFLOW index, not python index
    wel_data = ml.mnw2.node_data
    wel = ml.mnw2.stress_period_data.data
    
    df_well_node_data = pd.DataFrame(wel_data)
    df_well_node_data.to_csv(f'output/df_well_node_data.csv', index=False)
    
        
    tmp = pd.DataFrame(ml.mnw2.mnw['699-93-48c_i_dx'].stress_period_data)

    list_wells = list(wel_data['wellid'])
    #df = pd.DataFrame(data=list(range(1,nper+1,1)), columns=['SP'])
    df = pd.DataFrame()

    for wname in list_wells:
        #q = ml.mnw2.mnw['699-93-48c_i_dx'].stress_period_data['qdes']
        df[wname] = ml.mnw2.mnw[wname].stress_period_data['qdes']

    # plot
    df.to_csv(f'output/dfwel_ts.csv', index=False)
    df.plot(legend=False, figsize=(12, 8), grid=False)

    # well which is not active in April 2022 but included in mnw2 package
    list2 = ['199-D5-42_I_DX',
            '199-D5-44_I_DX',
            '199-D7-6_E_DX',
            '199-D8-55_E_DX',
            '199-D8-6_E_DX',
            '199-D8-68_E_DX',
            '199-D8-94_I_DX',
            '199-H1-32_E_HX',
            '199-H1-33_E_HX',
            '199-H1-38_E_HX',
            '199-H1-39_E_HX',
            '199-H1-40_E_HX',
            '199-H3-21_E_HX',
            '199-H3-26_E_HX',
            '199-H3-4_E_HX',
            '199-H4-17_I_HX',
            '199-H4-18_I_HX',
            '199-H4-4_E_HX',
            '199-H4-64_E_HX',
            '199-H4-71_I_HX',
            '199-H4-72_I_HX',
            '199-H4-73_I_HX',
            '199-H4-77_E_HX',
            '199-H4-79_I_HX',
            '199-H4-80_E_DX',
            '199-H4-80_I_DX',
            '199-H6-2_E_HX',
            '199-H6-2_I_HX',
            '199-H6-7_I_HX',
            '199-H6-8_I_HX',
            '699-90-45B_I_HX']
    list3 = [x.lower() for x in list2]
    #
    #df.columns
    df2=df[list3]
    df2.to_csv(f'output/rates_wells_not_active_April_2022.csv', index=False)
    len(list2)



    #wel.array
    #wel[0]

    type(wel)
    #type(wel[0])

    dfwel = pd.DataFrame(data=wel[sp-1])   

    #sp=1 # First sp (regular index, not python index)

    list_wells = list(dfwel['wellid'].unique())
    dfwel.to_csv(f'output/dfwell.csv')

def procees_rch(ml):
    nlay, nr, nc, nper = ml.dis.nlay, ml.dis.nrow, ml.dis.ncol, ml.dis.nper
    rch = ml.rch.rech.array
    rch.shape
    coef_conv = 1000*365.25
    for sp in range(12,13+1, 1):
        # sp=1
        rch_sp = rch[sp-1,0,:,:]*coef_conv
        #rch_sp.shape       
        #
        print(f'sp={sp}')
        get_min_max(rch_sp)
        #rch_sp[rch_sp<62.9] = np.nan
        # Save to png
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        cb1=ax.imshow(rch_sp, vmin=0*coef_conv, vmax=2e-5*coef_conv)
        plt.colorbar(cb1,orientation='horizontal',ax=ax,pad=0.1)
        ofile = f'output/rch/check_rch_sp_{sp}.png'
        fig.savefig(ofile, dpi=300, transparent=False, bbox_inches='tight')
        # save to shp
        gridShp = f'../ucn2png/input/shp_files/grid_with_centroids.shp'
        ofile_shp = f'output/rch/shp/check_rch_sp{sp}.shp'
        arr2shp(rch_sp,gridShp,ofile_shp)
        print(f'Saved {ofile_shp}\n')
    
    # Plot time series of recharge
    #list_rc = []
    #ir, ic = 326, 157
    ir, ic = 344, 157 # A cell at D5-151
    rch_ts = rch[:,0,ir-1,ic-1]*coef_conv
    df_rch_ts = pd.DataFrame(data=rch_ts, columns=[f'r{ir}c{ic}'])
    #df_rch_ts.plot()    
    df_rch_ts.to_csv(f'output/rch_all_ts_row{ir}_col{ic}.csv')
    print('Done processing recharge!!!')

def process_riv(ml):
    nlay, nr, nc, nper = ml.dis.nlay, ml.dis.nrow, ml.dis.ncol, ml.dis.nper
    riv = ml.riv.stress_period_data.data
    type(riv)
    #riv[0]
    sp=0
    riv[sp]['stage']
    riv[sp]['stage'][0] # first cell, 1st sp. 
    cell_id = 2
    #cell_id = [2, 10]

    stage = []    
    for sp in range(len(riv)):
        stage.append(riv[sp]['stage'][cell_id]) # at first cell

    df_riv = pd.DataFrame(data=stage, columns=['Stage_test'])    
    
    df_riv.plot(figsize=(12,8))
    #df_riv.to_csv(f'output/df_riv_check_one_cell.csv')
    print('Done processing riv package!!!\n')

def process_ghb(ml):
    ghb = ml.ghb.stress_period_data.data
    stage = []    
    for sp in range(len(ghb)):
        stage.append(ghb[sp]['bhead'][0])

    df_ghb = pd.DataFrame(data=stage, columns=['Stage_test'])    
    
    df_ghb.plot(figsize=(12,8))
    #df_ghb.to_csv(f'output/df_ghb_check_one_cell_rev031623.csv')
    print('Done processing ghb package!!!\n')
    
def process_hds(wdir, hed_file1):
    #wdir = 'C:/Users/hpham/OneDrive - INTERA Inc/projects/50_100HR3/10_NFA_ECF_Check/'
    #hed_file1 = f'{wdir}/model_files/flow/flow_NFA_v2/DHmodel_2021to2125.hds' # wrong GHB
    hds = bf.HeadFile(hed_file1)
    #h1 = hds1.get_data(kstpkper=(0, sp-1))
    hds = hds.get_alldata()
    nsp, nl, nr, nc = hds.shape
    il, ir, ic =1, 344, 157 # A cell at D5-151
    hds_at_sp = hds[:,il-1,ir-1,ic-1]
    df_hed = pd.DataFrame(data=hds_at_sp, columns=[f'hed_r{ir}c{ic}'])
    df_hed['sp'] = list(range(1, nsp+1, 1))
    df_hed.to_csv(f'output/df_head_check.csv', index=False)

def process_ssm(mt, df, ofile, dfgrid):
    ssm = mt.ssm.stress_period_data.data 
    mt.ssm
   
    ssm_cell_data = ssm[0]
    df_ssm_cell_data = pd.DataFrame(ssm_cell_data)

    df_ssm_cell_data.rename(columns={'i':'I', 'j':'J'}, inplace=True)
    dfgrid2 = pd.merge(dfgrid, df_ssm_cell_data, how='left', on=['I', 'J'])
    dfgrid2.to_csv(f'output/df_ssm_cell_data_sp1.csv')

    
    #type(ssm)
    n_ssm_cells = len(ssm[0]['css'])
    total_mass = []
    print(df.head())
    for irow in range(n_ssm_cells): # 4       202       612
        mass_loading = []
        for sp in range(len(ssm)):
            mass_loading.append(ssm[sp]['css'][irow])
        
        df[f'mload_row{irow}'] = mass_loading
        df[f'mass_row{irow}'] = df[f'mload_row{irow}']*df[f'spLen']/1e9
        total_mass.append(df[f'mass_row{irow}'].sum())
        
    #        
    #ofile = f'output/df_mass_loading_check_hist.csv'

    # plot total mass for each stress period
    cols = [f'mass_row{irow}' for irow in range(n_ssm_cells)]
    df.plot(x='SPstart', y=cols, legend=False, figsize=(12,6))

    # plot total mass for each stress period
    col2 = [f'mload_row{irow}' for irow in range(n_ssm_cells)]
    df.plot(x='SPstart', y=col2, legend=False, figsize=(12,6))

    df[['sp','SPstart','spLen'] + cols].to_csv(ofile)
    print(f'Saved {ofile}\n')

    # Get stats
    df_stat = df[cols].sum(axis=1)
    total_mass_ssm = df_stat.sum() # 50.5 kg    
    
    print(f'total mass = {total_mass_ssm} (kg)\n')
    return df
    
def plot_peak_conc(ml, ucn_file, dfgrid):
    '''
    Hardcoded column to seperate D/H areas
    '''
    sep_col = 355
    data, ntimes, nlay, nr, nc, times, ucnobj = read_ucn(ucn_file)
    #data.shape
    # read cbb to get cell volume

    ib = ml.bas6.ibound.array.astype(int)
    #ib.shape

    # Calculate for each sp
    col = [f'c{i}' for i in [1,2,3,4,9]]  
    CmaxD, CmaxH = [], []
    for sp in range(1, ntimes+1,1):
        dfmass = dfgrid[['I','J']].copy()
        for lay in range(1,nlay+1, 1):
            conc = data[sp-1,:,:,:].astype(float)
            #conc.shape
            dfmass[f'ib{lay}'] = np.reshape(ib[lay-1,:,:], [nr*nc,1]) 
            dfmass[f'c{lay}'] = np.reshape(conc[lay-1,:,:], [nr*nc,1]) 
            
        
          
        dfmass_aq_D = dfmass[col].loc[dfmass['J'] < sep_col]
        dfmass_aq_H = dfmass[col].loc[dfmass['J'] >= sep_col]
        CmaxD.append(np.nanmax(dfmass_aq_D, axis=0))
        CmaxH.append(np.nanmax(dfmass_aq_H, axis=0))


    # time series of max concentration
    df_Cmax_D = pd.DataFrame(data=CmaxD, columns=col)
    df_Cmax_D['SPstart'] = df_pred['SPstart']
    df_Cmax_D.plot(x='SPstart', y=col, figsize=(10,6))    

    df_Cmax_H = pd.DataFrame(data=CmaxH, columns=col)
    df_Cmax_H['SPstart'] = df_pred['SPstart']
    df_Cmax_H.plot(x='SPstart', y=col, figsize=(10,6))  

if __name__ == "__main__":   
    
    # full path to this cript
    #work_dir = f'C:/Users/hpham/OneDrive - INTERA Inc/projects/50_100HR3/10_NFA_ECF_Check/'
    work_dir = f's:/AUS/CHPRC.C003.HANOFF/Rel.141/10_NFA_ECF_Check'
    
    # full path to NFA pred flow model files
    #flow_model_ws = f'{work_dir}/model_files/flow_NFA_2125_rev_ghb_mnw2/'
    flow_model_ws = f'{work_dir}/model_files/flow_calib_2014to2020/'
    
    
    # full path to transport model files
    tran_model_ws_hist = f'{work_dir}/model_files/trans_calib_2014to2020/' # hist 2014-2020 model
    tran_model_ws_pred = f'{work_dir}/model_files/trans_NFA_2125_rev_ghb_mnw2_ccn1/' # NFA
    name_file = 'DHModel_Chromium.nam'

    # head files
    hed_file1 = f'{work_dir}/model_files/flow_NFA_2125_rev_ghb_mnw2/DHmodel_2021to2125.hds' # wrong GHB
    
    # SP and date
    df_hist = pd.read_csv(f'{work_dir}/scripts/input/sp_2014_2020.csv')
    df_hist['SPstart'] = pd.to_datetime(df_hist['SPstart'])
    df_pred = pd.read_csv(f'{work_dir}/scripts/input/stress_periods_2021-2125.csv')
    df_pred['SPstart'] = pd.to_datetime(df_pred['SPstart'])
    # Read in grid ingo
    dfgrid = pd.read_csv(f'input/grid_with_centroids.csv')
    
    
    # Readin model files
    ml = read_flow_files(flow_model_ws)
    mt = read_tran_files(tran_model_ws_hist, name_file, ml)
    mt_pred = read_tran_files(tran_model_ws_pred, name_file, ml)
    
    # [01] Process MWN2 =======================================================
    #process_mnw2(ml)

    # [02] Process the RCH file ===============================================
    #procees_rch(ml)
    
    # [03] Process RIV ========================================================
    process_riv(ml)

    # [04] Process GHB ========================================================
    process_ghb(ml)

    # [05] Process HDS ========================================================
    #wdir = 'C:/Users/hpham/OneDrive - INTERA Inc/projects/50_100HR3/10_NFA_ECF_Check/'
    #hed_file1 = f'{work_dir}/model_files/flow/flow_NFA_v2/DHmodel_2021to2125.hds' # wrong GHB
    #process_hds(wdir, hed_file1)

    # =========================================================================
    # Process transport files =================================================
    # =========================================================================

    # [06] Process ssm file for the hist model ================================
    ofile = f'output/df_mass_loading_check_hist_ssm.csv'
    #process_ssm(mt, df_hist, ofile, dfgrid)

    # [07] Process ssm file for the pred model ================================
    ofile = f'output/df_mass_loading_check_pred_ssm.csv'
    #process_ssm(mt_pred, df_pred, ofile,dfgrid)

    # [08] Max aquifer concentrations =========================================
    ucn_file = f'../ucn2png/input/MT3D001_single.UCN'
    #plot_peak_conc(ml, ucn_file, dfgrid)    

    
    #df=df_pred.copy()
    # 
    print('Done all!!!/n')




    # Get MNW2 info

        
    '''
    # Load head solution --------------------------------------------------
    hdsobj = bf.HeadFile(f'{flow_model_ws}/P2Rv8.3.hds')
    hds = hdsobj.get_alldata()

    #
    nsp, nl, nr, nc = hds.shape

    # Load MT3D tranport model files --------------------------------------
    tran_model_ws2 = os.path.join(tran_model_ws, coc)
    mt = flopy.mt3d.mt.Mt3dms.load(
        "P2RGWM.nam",
        model_ws=tran_model_ws2,
        exe_name="mt3d-mst-chprc08dpl.x",
        modflowmodel=ml,
        verbose=True,
    )
    '''


    '''
    al = mt.dsp.al     # long. disp,
    pr = mt.btn.prsity  # porosity
    rhob = mt.rct.rhob  # bulk density
    '''
