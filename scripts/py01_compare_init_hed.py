# pylint: disable=missing-module-docstring
import pandas as pd 
#import geopandas as gpd
import numpy as np 
import matplotlib.pyplot as plt
import flopy.utils.binaryfile as bf
import flopy

'''
Compare two head solutions
Author: hpham@intera.com
'''


def get_min_max(arr):
    arr[arr>1e3] = np.nan
    min_ = np.nanmin(arr)
    avg_ = np.nanmean(arr)
    max_ = np.nanmax(arr)
    #print(f'Min: {min_},\n Max: {max_}, \n ave: {avg_}')

def arr2shp(arr, gridShp, ofile):
    nr, nc = arr.shape
    print(nr, nc)
    val = np.reshape(arr, nr*nc)

    # use model grid shapefile geometry
    # model grid shapefile
    #try:
    #    gridShp = os.path.join('input', 'shp_files', 'grid_274_geo_rc.shp')
    #except:
    #    print('ERROR: Specify path to grid_274_geo_rc.shp')
    gdf = gpd.read_file(gridShp)
    df = pd.DataFrame()
    df['row'] = gdf['row']
    df['column'] = gdf['column']
    df['val'] = val

    # export shapefile
    gdf1 = gpd.GeoDataFrame(df, crs='EPSG:8455', geometry=gdf.geometry)
    gdf1.to_file(driver='ESRI Shapefile', filename=ofile)
    print(f'Saved {ofile} ! ! !')

if __name__ == "__main__":
    # [0] Specify input ucn files =============================================
    #wdir = '/workspace2/mpedrazas/100HR/Rel_126/'
    wdir = f'C:/Users/hpham/OneDrive - INTERA Inc/projects/54_100HR3_Rel145/github/100HR3/model_packages/hist_2014_2021/mnw2_2014_2021/'

    hed_file1 = f'{wdir}/Initial_Head_SP1.hds' 
    #hed_file2 = f'{wdir}/Initial_Head_SP84.hds'
    hed_file2 = f'{wdir}/DHmodel_2014to2020.hds' # 9L model
    
    df_grd = pd.read_csv('input/grid_with_centroids.csv')

    # output directory to save output files
    #out_wdir = 'c:/Users/hpham/OneDrive - INTERA Inc/projects/52_Ranger/26_hfb/'
    out_wdir = f'{wdir}/output/'



    # [1 Read head files    
    hds1 = bf.HeadFile(hed_file1)
    hds2 = bf.HeadFile(hed_file2)
    
    # Save ts of simulated head at a selected location for checking
    #hds = hds1.get_alldata()
    #nsp1, nl1, nr1, nc1 = hds1.shape
    #nsp2, nl2, nr2, nc2 = hds2.shape

    #for sp in [1, 644]:
    sp=1
    h1 = hds1.get_data(kstpkper=(0, sp-1))     
    h1.shape  
    sp=1
    h2 = hds2.get_data(kstpkper=(0, sp-1))
    h2.shape

    nlay, nr, nc = h1.shape

    #list_layers = range(5,12,1)
    list_layers = list(range(1,nlay+1,1))

    # [2] Plot and comparision ================================================
    for lay in list_layers:
        fig, ax = plt.subplots(1, 3, figsize=(10, 6))
        #ax=axes
        
        # subplot 1, ----------------------------------------------------------
        #time_yr = times[sp]/365.25
        arr1 = h1[lay-1,:,:]
        arr2 = h2[lay-1,:,:]
        get_min_max(arr1)
        get_min_max(arr2)

        #arr_old = Cmax_old[sp,:,:]
        cb1=ax[0].imshow(arr1, vmin=100, vmax=130)
        plt.colorbar(cb1,orientation='horizontal',ax=ax[0],pad=0.1)
        ax[0].set_title(f'old model, layer={lay}')
        
        # subplot 2, new ------------------------------------------------------
        #arr_new = Cmax_new[sp,:,:]
        cb2=ax[1].imshow(arr2,vmin=100, vmax=130)
        plt.colorbar(cb2,orientation='horizontal',ax=ax[1],pad=0.1)
        ax[1].set_title(f'new model, layer={lay}')

        # subplot 3, diff = arr1-arr2 -----------------------------------------
        arr_diff = arr1 - arr2
        #arr_diff[arr_diff<1e-4] = np.nan
        #arr_diff = arr_diff[sp,:,:]
        min_ = np.nanmin(arr_diff)
        avg_ = np.nanmean(arr_diff)
        max_ = np.nanmax(arr_diff)
        cb_diff=ax[2].imshow(arr_diff, vmin=-2.5, vmax=2.5)
        plt.colorbar(cb_diff,orientation='horizontal',ax=ax[2],pad=0.1)
        ax[2].set_title(f'Hold-Hnew, min:{str(round(min_,2))}, max:{str(round(max_,2))}, mean:{str(round(avg_,2))},')
        
        # exp diff
        #for lay in range(nlay):
        #if sp == 1:
        df_grd[f'h1_lay{lay}'] = np.reshape(arr1, nr*nc) 
        df_grd[f'h2_lay{lay}'] = np.reshape(arr2, nr*nc) 
        df_grd[f'h1-h2_lay{lay}'] = np.reshape(arr_diff, nr*nc)       
        
        tmp = str(lay).zfill(2)
        ofile = f'output/check_hed_diff_Lay{tmp}_sp{sp}.png'
        fig.savefig(ofile, dpi=300, transparent=False, bbox_inches='tight')
        #plt.show()
        print(f'Saved {ofile}\n')
    
        
    #
    df_grd.to_csv(f'output/check_hed_ts.csv')
    print('Done all!')



    

