import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import re
import os
import sys
import pandas as pd
import flopy.utils.binaryfile as bf
from matplotlib.colors import BoundaryNorm, Normalize, LinearSegmentedColormap
import matplotlib.ticker as ticker

'''
Readme
    - Use Python Version 3
    - To run script: use "python main.py scenario_name input_file sp_interval_to_print"
      for example: python main.py mnw2_sce2a_rr1 input/input.csv 12
    - Check output in the output folder. 
    - note: # hardcoded max layers 1-4 if using flag 999


'''


def create_new_dir(directory):
    # directory = os.path.dirname(file_path)
    try:
        os.stat(directory)
    except:
        os.mkdir(directory)
        print(f'Created a new directory {directory}\n')


def create_output_folders():
    create_new_dir('output')
    create_new_dir('output/png')
    create_new_dir('output/shp')
    create_new_dir(f'output/png/conc_{var}')
    create_new_dir(f'output/shp/conc_{var}')


def read_ucn(ifile_ucn):
    #ucnobj = bf.UcnFile(ifile_ucn, precision=precision)
    ucnobj = bf.UcnFile(ifile_ucn, precision='single')
    times = ucnobj.get_times()
    data = ucnobj.get_alldata(mflay=None, nodata=-1)
    ntimes, nlay, nr, nc = data.shape
    # times = ucnobj.get_times()
    # for t in times:
    #    conc = ucnobj.get_data(totim=t)
    return data, ntimes, nlay, nr, nc, times, ucnobj

def active_wells_shp(run_sce):

    # run_sce = 'mnw2_sce6a_rr2'

    wellinfo = f'../../../../../model_packages/pred_2023_2125/{run_sce}/wellinfodxhx_cy2023_2125.csv'
    wellrate = f'../../../../../model_packages/pred_2023_2125/{run_sce}/wellratedxhx_cy2023_2125.csv'

    info = pd.read_csv(wellinfo, skiprows = [0,2], usecols = ['NAME', 'XW', 'YW'], index_col = 'NAME')
    rates = pd.read_csv(wellrate, index_col='ID')

    df = pd.concat([info, rates], axis = 1)

    ext = df[df.index.str.contains("_E_")]
    inj = df[df.index.str.contains("_I_")]

    active_ext = gpd.GeoDataFrame(ext, geometry = gpd.points_from_xy(ext.XW, ext.YW))
    active_inj = gpd.GeoDataFrame(inj, geometry=gpd.points_from_xy(inj.XW, inj.YW))
    active_inj = active_inj[~active_inj.index.str.contains('SF')]  ## drop soil flushing points from df

    active_ext.to_file(os.path.join(os.getcwd(), 'input', 'shp_files', 'extraction_wells.shp'))
    active_inj.to_file(os.path.join(os.getcwd(), 'input', 'shp_files', 'injection_wells.shp'))

    return None


def generate_map1(arr, ifile, ofile, ptitle, levels, colors, xy, show_well):
    '''
        - Generate 2D plume maps
        - Last updated on 3/15/2022 by hpham
    '''

    # Mapping using GeoPandas
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 8))

    #
    dx = pd.read_csv(f'input/delx.csv')
    dy = pd.read_csv(f'input/dely.csv')
    dx_mesh_edge = dx.X-dx.delx/2
    dy_mesh_edge = dy.Y+dy.dely/2

    cmap = LinearSegmentedColormap.from_list("", colors)

    norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)



    # Plot 1 - show extraction/injection wells ============================
    show_well = True
    if show_well:
        ifile_zone = f'input/shp_files/rebound_study_wells.shp'
        zones = gpd.read_file(ifile_zone)
        zones.plot(ax = ax, color = 'black', label = 'Rebound study wells', markersize = 9, zorder=2.5)
        # #ifile_zone = f'input/shp_files/extraction_wells.shp'
        # ifile_zone = f'../../../../../model_packages/pred_2023_2125/{run_sce}/extraction_wells.shp'
        # extwells = gpd.read_file(ifile_zone)
        # extwells.plot(ax=ax, alpha=1, linewidth=0.5, color='none', label = 'Extraction', 
                        # markersize=9, marker='^',edgecolor='red', zorder=3)    
        # #ifile_zone = f'input/shp_files/injection_wells.shp'
        # ifile_zone = f'../../../../../model_packages/pred_2023_2125/{run_sce}/injection_wells.shp'
        # extwells = gpd.read_file(ifile_zone)
        # extwells.plot(ax=ax, alpha=1, linewidth=0.5, color='none', label = 'Injection', 
                        # markersize=9, marker='v',edgecolor='green', zorder=3)   

    # Plot 2 - show shoreline cells =======================================
    show_shoreline = True
    if show_shoreline:
        ifile_zone = f'input/shp_files/shoreline_cells_100DH.shp'
        zones = gpd.read_file(ifile_zone)
        zones.plot(ax=ax, alpha=1, linewidth=1, color='#7fc97f', label = 'Shoreline')        

    # Plot 3 - show continuing source cells ===============================
    show_cs = True
    if show_cs:
        ifile_zone = f'input/shp_files/cr6_cs_zonation2_filtered_2lines.shp'
        zones = gpd.read_file(ifile_zone)
        zones.columns
        zones.crs
        zones.plot(ax = ax, color = '#e78ac3',
                    alpha=0.5, linewidth=1, edgecolor='#e78ac3',                                               
                    label = 'Source Zone')        

    # Plot 4 - show road layer ============================================
    show_road = True
    if show_road:
        ifile_zone = f'input/shp_files/trvehrcl.shp'
        zones = gpd.read_file(ifile_zone)
        zones.columns
        zones.crs
        zones.plot(color = '#bdbdbd', ax=ax, zorder=20,
                    alpha=0.25, linewidth=1, edgecolor='#bdbdbd',                                               
                    label = 'Road'
                    )        

    # Plot 5 - Show river =================================================
    show_river = True
    if show_river:
        ifile_zone = f'input/shp_files/River.shp'
        zone2 = gpd.read_file(ifile_zone)
        #zone2.plot(ax=ax, alpha=0.3, linewidth=0.5, zorder=4, column='J', categorical=True, legend=True)
        zone2.plot(color='#a6cee3', ax=ax, zorder=10,
                    alpha=0.5, linewidth=0.1, edgecolor='#a6cee3',                       
                     label = 'River')
        #zone2.plot(ax=ax)
        #ax.text(572700, 151650, 'Columbia River', ha='center', rotation=45)

        #zone2.apply(lambda x: ax.annotate(s=x.NAME,xy=x.geometry.centroid.coords[0], ha='center'), axis=1)        
        #for x, y, label in zip(zone2.geometry.centroid.x, zone2.geometry.centroid.y, zone2['NAME']):
        #    ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points", fontsize=8)

    # Plot 6 - CrVI Plume =====================================================
    im = ax.pcolormesh(dx_mesh_edge, dy_mesh_edge, arr,
                       cmap=cmap, norm=norm, alpha=1)
    
    #divider = make_axes_locatable(ax)
    #cax = divider.append_axes("right", size="5%", pad=0.05)
    #fig.colorbar(im, ax=ax, format=ticker.FuncFormatter(
    #    fmt), fraction=0.046, pad=0.04)
    #cbar = fig.colorbar(im, fraction=0.2, pad=0.01, shrink=0.3,
    #                    anchor=(0.1,0.5), 
    #                            ) #format=ticker.FuncFormatter(fmt)
    cbar = fig.colorbar(im, orientation = 'horizontal', shrink=0.5,pad=0.08, 
                        fraction=0.2, aspect=50 )
    #cbar.ax.set_yticklabels(['0','1','2','>3'])
    cbar.set_label('Simulated Cr(VI) Plume (μg/L)', rotation=0, fontsize = 10)
    cbar.set_ticks([0,10,20,48,480])
    cbar.set_ticklabels([0,10,20,48,480])
    cbar.ax.tick_params(labelsize=8)

    #
    ax.set_title(ptitle, fontsize = 8, color='#f0f0f0')
    ax.set_xlim([dx.X.min(), dx.X.max()])
    ax.set_ylim([dy.Y.min(), dy.Y.max()])
    #
    ax.set_xlim([xy[0], xy[1]])  # xmin, xmax
    ax.set_ylim([xy[2], xy[3]])  # ymin, ymax
    ax.set_xlabel('UTM_X (m)')
    ax.set_ylabel('UTM_Y (m)')
    
    ax.legend(fontsize=10,
            frameon=True,
           loc=('upper right'))
            #bbox_to_anchor=(1.22,1),
            #title="LEGEND",
    
    # Add arrow
    if ifile=='input/input_100DH.csv':
        x, y, arrow_length = 0.20, -0.12, 0.12
    else:
        x, y, arrow_length = 0.05, -0.08, 0.12

    ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='#f0f0f0', width=2, headwidth=8),
            ha='center', va='center', fontsize=12,
            xycoords=ax.transAxes)

    # plt.gca().set_aspect('equal', adjustable='box')
    fig.savefig(ofile, dpi=300, transparent=False, bbox_inches='tight')
    print(f'Saved {ofile}\n')
    # plt.show()
    
    plt.close('all')


def conv_str2num(str):
    '''
    Convert a list of strings to list of numbers
    '''
    clevels = []
    for i in str:
        clevels.append(float(i))
    return clevels


def fmt(x, pos):
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)

def cal_grid_cell_size(gridShp):
    # use model grid shapefile geometry
    try:
        #gridShp = os.path.join('input', 'shp_files', 'grid_274_geo_rc.shp')
        gdf = gpd.read_file(gridShp)
        #gdf.head(5)
        #gdf.plot()
    except:
        print('ERROR: Something went wrong when reading grid shapefile')    
    
    # Get coordinate of cell centers
    #Find the center point
    gdf['Center_point'] = gdf['geometry'].centroid

    gdf['X'] = gdf['Center_point'].apply(lambda p: p.x)
    gdf['Y'] = gdf['Center_point'].apply(lambda p: p.y)
    
    points.to_file(driver = 'ESRI Shapefile', filename = ofile_points)   
    print(f'Saved {ofile_points}\n') 

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
    gdf1 = gpd.GeoDataFrame(df, geometry=gdf.geometry)
    # ofile_shp = os.path.join(
    #    work_dir, 'scripts', 'output', 'shp', 'Cmax_trit_ts76.shp')
    gdf1.to_file(driver='ESRI Shapefile', filename=ofile)
    print(f'Saved {ofile} ! ! !')


if __name__ == "__main__":

    # [0] define run scenario: python main sce
    run_sce = sys.argv[1]

    # [1] Load input file -----------------------------------------------------
    #ifile = f'input/input_100HR3_NFA_ECF.csv'
    #ifile = f'input/input_100HR3_calib_ECF.csv'
    #ifile = f'input/input_plume_postprocess.csv'
    ifile = sys.argv[2]
    ifile_date = f'input/sp_2014_2023.csv'
    show_well = sys.argv[3] # 'Y' show well layer, 
    start_sp = int(sys.argv[4])  # start SP
    stop_sp = int(sys.argv[5])  # start SP
    print_interval = int(sys.argv[6]) # every xxx sp

    ###EXAMPLE: python main.py mnw2_sce3a_rr12 input/input_100DH.csv Y 1 3 1

    #### ======================================================================
    # No modification needed after this line ==================================
    #### ======================================================================

    ## generate active well shapefile for scenario
    #active_wells_shp(run_sce)

    # import datetime for each sp
    dftime = pd.read_csv(ifile_date)


    # read input file ---------------------------------------------------------
    dfin = pd.read_csv(ifile)
    dfin = dfin.set_index('var')

    # Read lines in the input file --------------------------------------------
    sce = dfin['name'].loc['sce']
    var = dfin['name'].loc['var']
    ucn_file = dfin['name'].loc['ucn_file']  # full path to ucn file
    print(f'Reading UCN file: {ucn_file}\n')
    conc_cutoff = float(dfin['name'].loc['conc_cutoff'])
    contour_levels = re.split(',', dfin['name'].loc['contour_levels'])
    contour_levels = conv_str2num(contour_levels)  # convert to list of numbers
    colors = re.split(',', dfin['name'].loc['color_levels'])
    list_sp = re.split(',', dfin['name'].loc['list_sp'])
    list_sp = conv_str2num(list_sp)
    
    

    list_layer = re.split(',', dfin['name'].loc['list_layer'])
    list_layer = conv_str2num(list_layer)
    map_dim = re.split(',', dfin['name'].loc['map_dim'])
    map_dim = conv_str2num(map_dim)

    ucn2png = dfin['name'].loc['ucn2png']
    ucn2shp = dfin['name'].loc['ucn2shp']
    gridShp = dfin['name'].loc['grid_file']  # full path to grid shape file
    precision = dfin['name'].loc['ucn_read_precision']
    conv_factor = float(dfin['name'].loc['conversion_factor'])

    # [1] Map spatial distribution of total mass/activity arriving at water table
    if ucn2png == 'yes':
        '''
        This generates plume maps (in png files): 
            + for a given layers and stress periods, or 
            + for maximum plume footprint (max over all model layers)
        '''

        # Create some output folders to write outputs
        create_output_folders()

        # Read ucn file using flopy -------------------------------------------
        
        data, ntimes, nlay, nr, nc, times, ucnobj = read_ucn(ucn_file)
        print(f'nrow={nr}, ncol={nc}, nlay={nlay}, nsp={ntimes}\n')
        ## nrow=433, ncol=875, nlay=9, nsp=644 (100-HR3 predictive model)
        #df_time = pd.DataFrame(data=times, columns=['Time_day'])
        #df_time['Time_yr'] = df_time['Time_day']/365.25
        #df_time['Time_yr2'] = df_time['Time_yr'] + 2021
        #df_time.to_csv('output/df_time.csv')
        
        #list_sp = conv_str2num(list_sp)
        #print(f'list_sp = {list_sp}')

        if list_sp[0]==999:                    
            list_sp = range(start_sp,stop_sp+1, print_interval)
            #list_sp=[1,2]
            print(f'list_sp = {list_sp} -> export map every {print_interval} sp!!!')
            #print(f'list_sp = {list_sp}')

        
        # dict of sp and date
        dict_dt = {}
        for i in range(ntimes):
            dict_dt[i]=dftime['start_date'].iloc[i]
            

        
        data = np.ma.masked_less_equal(data, conc_cutoff)/conv_factor
        #Cmax_over_layer = np.nanmax(data, 1)
        Cmax_over_layer = np.nanmax(data[:,:4,:,:], 1) # hardcoded max layers 1-4

        vmin, vmax = np.nanmin(data), np.nanmax(data)
        print(f'Cmin={vmin}, Cmax={vmax}\n')

        for ilay in list_layer:
            for isp in list_sp:
                isp2 = str(isp).zfill(3)
                if ilay == 999:
                    arr = Cmax_over_layer[int(isp)-1, :, :]
                    ptitle = f'{run_sce}, Unconfined Aquifer, SP: {isp}, {dict_dt[isp-1]}'
                    # output png file
                    ofile_png = f'output/png/conc_{var}/Conc_{var}_Lay_max_SP_{isp2}.png'
                    #ofile = f'output/png/conc_{var}/Conc_{var}_Lay_max_SP_{int(isp)}.png'
                    if ucn2shp == 'yes':
                        ofile_shp = f'output/shp/conc_{var}/Conc_{var}_Lay_max_SP_{isp2}.shp'
                        arr2shp(arr,gridShp,ofile_shp)
                        print(f'Saved {ofile_shp}\n')
                else:
                    arr = data[int(isp)-1, int(ilay)-1, :, :]
                    ptitle = f'{run_sce}, Layer: {int(ilay)}, SP: {isp}, {dict_dt[isp-1]}'
                    # output png file
                    
                    ofile_png = f'output/png/conc_{var}/Conc_{var}_Lay_{int(ilay)}_SP_{isp2}.png'
                    if ucn2shp == 'yes':
                        ofile_shp = f'output/shp/conc_{var}/Conc_{var}_Lay_{int(ilay)}_SP_{isp2}.shp'
                        arr2shp(arr,gridShp,ofile_shp)
                        print(f'Saved {ofile_shp}\n')

                # Map array arr -----------------------------------------------
                generate_map1(arr, ifile, ofile_png, ptitle, contour_levels,
                              colors, map_dim,show_well)
                #print(f'Saved {ofile_png}\n',)

# extent: 571750.0,150500.0,580500.0,154830.0