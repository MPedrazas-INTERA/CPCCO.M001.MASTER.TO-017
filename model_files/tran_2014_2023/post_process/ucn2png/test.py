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


def generate_map1(arr, ofile, ptitle, levels, colors, xy):
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
    im = ax.pcolormesh(dx_mesh_edge, dy_mesh_edge, arr,
                       cmap=cmap, norm=norm, alpha=1)


    # Plot 5 - show former operational areas (e.g. 200W, 200E, etc.)
    show_OU = False
    if show_OU:
        ifile_zone = f'input/shp_files/bdjurdsv.shp'
        zones = gpd.read_file(ifile_zone)
        zones.plot(ax=ax, alpha=0.25, linewidth=0.5, color='none',
                   edgecolor='#636363', zorder=1, legend=True, label='Waste Site')  # darkred
        # zones.apply(lambda x: ax.annotate(s=x.NAME,
        #                                  xy=x.geometry.centroid.coords[0], ha='center'), axis=1)

    # Plot 6 - show River
    show_river = False
    if show_river:
        ifile_zone = f'input/shp_files/River.shp'
        zones = gpd.read_file(ifile_zone)
        # print(zones.head())
        zones.plot(ax=ax, alpha=0.3, linewidth=0.75, color='#2b8cbe',
                   edgecolor='#2b8cbe', zorder=2, column='NAME', categorical=True, legend=True, label='River')


    # Show system wells -------------------------------------------------------
    # Plot 8a - show extraction wells
    show_ext_wells = False
    if show_ext_wells:
        ifile_zone = f'input/shp_files/extraction_wells.shp'
        zones = gpd.read_file(ifile_zone)
        # print(zones.head())
        zones.plot(ax=ax, alpha=0.75, linewidth=0.15, color='red', markersize=8, marker='^',
                   edgecolor='#3182bd', zorder=3, legend=True, label='Extraction')        

        #zones.apply(lambda x: ax.annotate(s=x.Name,
        #                                  xy=x.geometry.centroid.coords[0], ha='center'), axis=1)
    # Plot 8b - show injection wells
    show_inj_wells = False
    if show_inj_wells:        
        ifile_zone = f'input/shp_files/injection_wells.shp'
        zones = gpd.read_file(ifile_zone)
        # print(zones.head())
        zones.plot(ax=ax, alpha=0.75, linewidth=0.15, color='green', markersize=8, marker='v',
                   edgecolor='#3182bd', zorder=3, legend=True, label='Injection')        
        #zones.plot(alpha=0.25, linewidth=0.75, color='green', markersize=8, marker='v',
        #           edgecolor='#3182bd', zorder=3, legend=True, label='inj')        
        #zones.apply(lambda x: ax.annotate(s=x.Name,
        #                                  xy=x.geometry.centroid.coords[0], ha='center'), axis=1)
    
    # End of showing system wells ---------------------------------------------
    # -------------------------------------------------------------------------


    # Plot 10 - show shoreline cells
    show_shoreline_D = False
    if show_shoreline_D:
        ifile_zone = f'input/shp_files/100D_cells.shp'
        zones = gpd.read_file(ifile_zone)
        # print(zones.head())
        #zones.plot(ax=ax, alpha=0.3, linewidth=0.5, color='none',
        #           edgecolor='green', zorder=4, column='I', categorical=False, legend=True, label='Shoreline')
        zones.plot(ax=ax, alpha=0.3, linewidth=0.5, zorder=4, column='I', categorical=False, legend=True, label='Shoreline')

    show_shoreline_H = False
    if show_shoreline_H:
        ifile_zone = f'input/shp_files/100H_cells.shp'
        zones = gpd.read_file(ifile_zone)
        # print(zones.head())
        zones.plot(ax=ax, alpha=0.3, linewidth=0.5, color='none',
                   edgecolor='green', zorder=4, legend=False, label='River')
    #ax.legend(loc='lower right', fontsize=8, frameon=True)

    show_sources = True
    if show_sources:
        ifile_zone = f'input/shp_files/cr6_cs_zonation2_filtered.shp'
        zones = gpd.read_file(ifile_zone)
        # print(zones.head())
        zones.plot(ax=ax, alpha=0.5, linewidth=0.5, color='none',
                   edgecolor='mediumpurple', zorder=5, column='zone', categorical=True, legend=True) # label='continuing sources'




    #divider = make_axes_locatable(ax)
    #cax = divider.append_axes("right", size="5%", pad=0.05)
    #fig.colorbar(im, ax=ax, format=ticker.FuncFormatter(
    #    fmt), fraction=0.046, pad=0.04)
    fig.colorbar(im, fraction=0.02, pad=0.04, format=ticker.FuncFormatter(fmt))

    #
    ax.set_title(ptitle)
    ax.set_xlim([dx.X.min(), dx.X.max()])
    ax.set_ylim([dy.Y.min(), dy.Y.max()])
    #
    ax.set_xlim([xy[0], xy[1]])  # xmin, xmax
    ax.set_ylim([xy[2], xy[3]])  # ymin, ymax
    ax.set_xlabel('UTM_X (m)')
    ax.set_ylabel('UTM_Y (m)')
    
    ax.legend(loc='upper right', fontsize=8, frameon=True)
    #ax.set_axis_off()
    #title="CPT"
    
    # Add arrow
    x, y, arrow_length = 0.05, 0.2, 0.15
    ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=20,
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
    gdf1 = gpd.GeoDataFrame(df, crs='EPSG:4326', geometry=gdf.geometry)
    # ofile_shp = os.path.join(
    #    work_dir, 'scripts', 'output', 'shp', 'Cmax_trit_ts76.shp')
    gdf1.to_file(driver='ESRI Shapefile', filename=ofile)
    print(f'Saved {ofile} ! ! !')


if __name__ == "__main__":
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 8))
        ifile_zone = f'input/shp_files/100D_cells.shp'
        zones = gpd.read_file(ifile_zone)
        # print(zones.head())
        #zones.plot(ax=ax, alpha=0.3, linewidth=0.5, color='none',
        #           edgecolor='green', zorder=4, column='I', categorical=False, legend=True, label='Shoreline')
        zones.plot(ax=ax, alpha=0.3, linewidth=0.5, zorder=4, column='I', categorical=False, legend=True, label='Shoreline')
