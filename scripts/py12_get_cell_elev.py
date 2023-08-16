import flopy
import flopy.utils.binaryfile as bf
import pandas as pd 
import os
import numpy as np 
import geopandas as gpd

def load_mf(flow_model_ws):
    # load an MODLOW flow model -------------------------------------------
    #flow_model_ws = f'/home/hpham/100HR3/mruns/sce3a_rr8_to2032/flow_2023to2032'
    ml = flopy.modflow.Modflow.load(
        "100hr3_2023to2032.nam",
        model_ws=flow_model_ws,
        load_only=["dis", "bas6"],
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
    print(nlay, nr, nc, nper)
    return ml,nlay, nr, nc, nper



if __name__ == "__main__":

    #wdir = f'c:/Users/hpham/Documents/100HR3/'
    wdir = f'/home/hpham/100HR3'
    ifile = os.path.join(wdir,'gis','shp','grid_with_centroids.shp') #
    flow_model_ws = f'{wdir}/mruns/sce3a_rr8_to2032_notfinal/flow_2023to2032'

    #
    ofile = os.path.join(wdir,'gis','shp','layer_top_bot_ele.shp') #

    #
    
    # Specify cell location to get top elevatain
    #dic_loc = {'NW_11':[210,615], 'NW_12':[284,666]} # lay, row, col
    
    ml,nlay, nr, nc, nper = load_mf(flow_model_ws)
    rt = gpd.read_file(ifile)

    top = ml.dis.gettop()
    bot = ml.dis.getbotm()


    rt['top1'] = np.reshape(top, (nr*nc,1))
    for lay in range(2,nlay+1,1):
        rt[f'top{lay}'] = np.reshape(bot[lay-1-1,:,:], (nr*nc,1))
    
    rt['bot9'] = np.reshape(bot[nlay-1,:,:], (nr*nc,1))

    rt.to_file(ofile)
    print(f'Saved {ofile}\n')


    
    '''
    out1 = []
    for i in dic_loc.keys():
        print(i)
        nr, nc = dic_loc[i]
        out2 = [i]
        out2.append(top[nr-1, nc-1]) # top 1
        for lay in range(2,nlay+1,1):
            top_tmp = bot[lay-1-1, nr-1, nc-1] # top 2 to the last layer
            out2.append(top_tmp)
        out1.append(out2)
    print(out1)
    # save
    col = ['NAME'] + [f'top{i+1}' for i in range(nlay)]
    df=pd.DataFrame(data=out1, columns=col)
    print(df)
    df.to_csv(f'output/cell_loc_new_wells.csv', index=False)
    '''







    
    