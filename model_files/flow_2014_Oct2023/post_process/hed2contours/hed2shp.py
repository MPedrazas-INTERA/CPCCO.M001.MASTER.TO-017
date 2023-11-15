import geopandas as gpd
import numpy as np
#import rasterio
from rasterio.transform import from_origin
#from sklearn.neighbors import KNeighborsRegressor
#from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from scipy import interpolate
#import scipy
#import fiona
import os
import re
#import flopy
import sys
import flopy.utils.binaryfile as bf


#Read head solution from a 2D MODFLOW-USG flow model simulation
#Currently testing using python env irp

#Scripts were modified from https://github.com/rosskush/spatialpy

# to run, use syntax: 
# #python hed2shp.py "path_to_grid" "path_to_hds" con_min con_max con_interval crs list_lay list_sp
# e.g., 
# python hed2shp.py "../../../../../gis/shp/grid_with_centroids.shp" "../../100hr3_2023to2125.hds" 110 120 0.1 32149 "4,9" "1,120"
# (Note: Must use double quotation for the paths)
# no space between stress periods or layers in the list_lay or list_sp
# Last updated: 11/22/2022 by hpham


# from skspatial import utils

#pykrige_install = True

#try:
#    from pykrige.ok import OrdinaryKriging
#except:
#    pykrige_install = False

class interp2d():
    def __init__(self,gdf,attribute,res=None, ulc=(np.nan,np.nan), lrc=(np.nan,np.nan)):
        """
        :param gdf: geopandas GeoDataFrame object, with geometry attribute
        :param attribute: column name in GeoDataFrame object used for spatial interpolation
        :param res: delx and dely representing pixle resolution
        :param ulc: upper left corner (x,y)
        :param lrc: lower right corner (x,y)
        """

        self.gdf = gdf
        self.attribute = attribute
        self.x = gdf.geometry.x.values
        self.y = gdf.geometry.y.values
        self.z = gdf[attribute].values
        self.crs = gdf.crs

        if np.isfinite(ulc[0]) and np.isfinite(lrc[0]):
            self.xmax = lrc[0]
            self.xmin = ulc[0]
            self.ymax = ulc[1]
            self.ymin = lrc[1]
        else:
            self.xmax = gdf.geometry.x.max()
            self.xmin = gdf.geometry.x.min()
            self.ymax = gdf.geometry.y.max()
            self.ymin = gdf.geometry.y.min()
        self.extent = (self.xmin, self.xmax, self.ymin, self.ymax)
        if np.isfinite(res):
            self.res = res
        else:
            # if res not passed, then res will be the distance between xmin and xmax / 1000
            self.res = (self.xmax - self.xmin) / 2000

        self.ncol = int(np.ceil((self.xmax - self.xmin) / self.res)) # delx
        self.nrow = int(np.ceil((self.ymax - self.ymin) / self.res))# dely
    # def points_to_grid(x, y, z, delx, dely):
    def points_to_grid(self):
        """
        :return: array of size nrow, ncol
        http://chris35wills.github.io/gridding_data/
        """
        hrange = ((self.ymin,self.ymax),(self.xmin,self.xmax)) # any points outside of this will be condisdered outliers and not used

        zi, yi, xi = np.histogram2d(self.y, self.x, bins=(int(self.nrow), int(self.ncol)), weights=self.z, range=hrange)
        counts, _, _ = np.histogram2d(self.y, self.x, bins=(int(self.nrow), int(self.ncol)),range=hrange)
        np.seterr(divide='ignore',invalid='ignore') # we're dividing by zero but it's no big deal
        zi = np.divide(zi,counts)
        np.seterr(divide=None,invalid=None) # we'll set it back now
        zi = np.ma.masked_invalid(zi)
        array = np.flipud(np.array(zi))
    
        return array

    def knn_2D(self, k=15, weights='uniform', algorithm='brute', p=2, maxrows = 1000):

        if len(self.gdf) > maxrows:
            raise ValueError('GeoDataFrame should not be larger than 1000 rows, knn is a slow algorithim and can be too much for your computer, Change maxrows at own risk')  # shorthand for 'raise ValueError()'

        array = self.points_to_grid()
        X = []
        # nrow, ncol = array.shape
        frow, fcol = np.where(np.isfinite(array)) # find areas where finite values exist
        for i in range(len(frow)):
            X.append([frow[i], fcol[i]])
        y = array[frow, fcol]

        train_X, train_y = X, y

        knn = KNeighborsRegressor(n_neighbors=k, weights=weights, algorithm=algorithm, p=2)
        knn.fit(train_X, train_y)

        X_pred = []
        for r in range(int(self.nrow)):
            for c in range(int(self.ncol)):
                X_pred.append([r, c])
        y_pred = knn.predict(X_pred)
        karray = np.zeros((self.nrow, self.ncol))
        i = 0
        for r in range(int(self.nrow)):
            for c in range(int(self.ncol)):
                karray[r, c] = y_pred[i]
                i += 1
        return karray

    def interpolate_2D(self, method='linear',fill_value=np.nan):
        # use linear or cubic
        array = self.points_to_grid()
        x = np.arange(0, self.ncol)
        y = np.arange(0, self.nrow)
        # mask invalid values
        array = np.ma.masked_invalid(array)
        xx, yy = np.meshgrid(x, y)
        # get only the valid values
        x1 = xx[~array.mask]
        y1 = yy[~array.mask]
        newarr = array[~array.mask]
        GD1 = interpolate.griddata((x1, y1), newarr.ravel(), (xx, yy), method=method,fill_value=fill_value)

        return GD1

    def smooth_array(self, array, size=np.nan, window=np.nan):
        '''
        array: 2D numpy array representing surface
        size: number of cells to use for averaging (int)
        window: length in distance units for ml object, will calculate size based on resolution of ml object
            i.e. if window = 1000 ft and res = 500 ft, size = int(1000/500) = 2 
        '''

        if np.isnan(window):

            if not isinstance(size,int):
                raise ValueError('size must be type int')

        else:
            size = int(window / self.res)


        mask = np.where(np.isnan(array))


        nn_array = self.interpolate_2D(method='nearest')
        array[mask] = nn_array[mask]

        arrayi = scipy.ndimage.filters.uniform_filter(array, size=size, mode='reflect')
        arrayi[mask] = np.nan

        return arrayi

    def OrdinaryKriging_2D(self, n_closest_points=None,variogram_model='linear', verbose=False, coordinates_type='euclidean',backend='vectorized'):
        # Credit from 'https://github.com/bsmurphy/PyKrige'

        if not pykrige_install:
            raise ValueError('Pykrige is not installed, try pip install pykrige')

        OK = OrdinaryKriging(self.x,self.y,self.z, variogram_model=variogram_model, verbose=verbose,
                     enable_plotting=False, coordinates_type=coordinates_type)

        x,y = np.arange(0,self.ncol), np.arange(0,self.nrow)

        xpts = np.arange(self.xmin + self.res/2,self.xmax+self.res/2, self.res)
        ypts = np.arange(self.ymin + self.res/2,self.ymax+self.res/2, self.res)
        ypts = ypts[::-1]


        xp, yp = [],[]
        for yi in ypts:
            for xi in xpts:
                xp.append(xi)
                yp.append(yi)


        if n_closest_points is not None:
            backend = 'loop'
        # krige_array, ss = OK.execute('points', x, y,n_closest_points=n_closest_points,backend=backend)
        krige_array, ss = OK.execute('points', xp, yp,n_closest_points=n_closest_points,backend=backend)

        krige_array = np.reshape(krige_array,(self.nrow,self.ncol))
        # print(krige_array.shape)


        return krige_array

    def Spline_2D(self):
        array = self.points_to_grid()

        x,y = np.arange(0,self.ncol), np.arange(0,self.nrow)
        frow, fcol = np.where(np.isfinite(array))
        X = []
        for i in range(len(frow)):
            X.append([frow[i], fcol[i]])
        z = array[frow, fcol]

        sarray = interpolate.RectBivariateSpline(frow,fcol,z)
        print(sarray.shape)

        return sarray

    def RBF_2D(self):
        array = self.points_to_grid()
        print(array.shape)

        x,y = np.arange(0,self.ncol), np.arange(0,self.nrow)
        frow, fcol = np.where(np.isfinite(array))
        X = []
        for i in range(len(frow)):
            X.append([frow[i], fcol[i]])
        z = array[frow, fcol]

        rbfi = interpolate.Rbf(frow,fcol,z,kind='cubic')
        gridx, gridy = np.arange(0,self.ncol), np.arange(0, self.nrow)
        print(gridx)
        sarray = rbfi(gridx,gridy)


        print(sarray.shape)
        return sarray


    def write_raster(self,array,path):
        if '.' not in path[-4:]:
            path += '.tif'

        # transform = from_origin(gamx.min(), gamy.max(), res, res)
        transform = from_origin(self.xmin, self.ymax, self.res, self.res)


        new_dataset = rasterio.open(path, 'w', driver='GTiff',
                                    height=array.shape[0], width=array.shape[1], count=1, dtype=array.dtype,
                                    crs=self.gdf.crs, transform=transform, nodata=np.nan)
        new_dataset.write(array, 1)
        new_dataset.close()

        return new_dataset

    def write_contours(self, array,path,val_min=0,val_max=1,interval=0.1, levels = None, crs=None):
        """
        Create matplotlib contour plot object and export to shapefile.
        Parameters
        ----------
        """
        from shapely.geometry import LineString

        if crs is None:
            crs = self.crs

        if levels is None:
            #levels = np.arange(val_min,npval_max,.nanmax(array),interval)
            levels = np.arange(val_min,val_max,interval)

        cextent = np.array(self.extent)
        cextent[0] = cextent[0] + self.res/2.7007
        cextent[1] = cextent[1] + self.res/2.7007
        cextent[2] = cextent[2] - self.res/3.42923
        cextent[3] = cextent[3] - self.res/3.42923

        contours = plt.contour(np.flipud(array),extent=cextent,levels=levels)
        if not isinstance(contours, list):
            contours = [contours]


        geoms = []
        level = []
        for ctr in contours:
            levels = ctr.levels
            for i, c in enumerate(ctr.collections):
                paths = c.get_paths()
                for il, p in enumerate(paths):
                    if len(p.vertices) > 1:
                        geoms.append(LineString(p.vertices))
                        level.append(levels[i])


        cgdf = gpd.GeoDataFrame({'level':level,'geometry':geoms},geometry='geometry')
        cgdf.crs = crs

        cgdf.to_file(os.path.join(path))
        plt.close('all')

    def get_contours(self, array,base=0,interval=100, levels = None, crs=None):
        """
        Create matplotlib contour plot object and return GeoDataFrame.
        Parameters
        ----------
        """
        from shapely.geometry import LineString

        if crs is None:
            crs = self.crs

        if levels is None:
            levels = np.arange(base,np.nanmax(array),interval)

        cextent = np.array(self.extent)
        cextent[0] = cextent[0] + self.res/2.7007
        cextent[1] = cextent[1] + self.res/2.7007
        cextent[2] = cextent[2] - self.res/3.42923
        cextent[3] = cextent[3] - self.res/3.42923

        _fig, _ax = plt.subplots()
        contours = plt.contour(np.flipud(array),extent=cextent,levels=levels)
        if not isinstance(contours, list):
            contours = [contours]


        geoms = []
        level = []
        for ctr in contours:
            levels = ctr.levels
            for i, c in enumerate(ctr.collections):
                paths = c.get_paths()
                for il, p in enumerate(paths):
                    if len(p.vertices) > 1:
                        geoms.append(LineString(p.vertices))
                        level.append(levels[i])

        cgdf = gpd.GeoDataFrame({'level':level,'geometry':geoms},geometry='geometry')
        cgdf.crs = crs

        plt.close(_fig)
        return cgdf



    def plot_image(self,array,title=''):
        fig, axes = plt.subplots(figsize=(10,8))
        plt.imshow(array, cmap='jet',extent=self.extent)
        plt.colorbar()
        plt.title(title)
        fig.tight_layout()
        return axes

def create_new_dir(directory):
    # directory = os.path.dirname(file_path)
    try:
        os.stat(directory)
    except:
        os.mkdir(directory)
        print(f'Created a new directory {directory}\n')

def print_ver():
    #print('numpy version: {}'.format(np.__version__))                      # 
    #print('pandas version: {}'.format(pd.__version__))                      # 
    #print('gdal version: {}'.format(gdal.__version__))                  # 
    print('geopandas version: {}\n'.format(gpd.__version__))                  # 
    #print('python version: {}'.format(platform.python_version()))           # 
    #print('flopy version:{}'.format(flopy.__version__))

def hed2shp_points_poly(grd_ifile, hed_ifile, path2ofile,crs, list_sp, list_layer):
    '''
    Read head solution using flopy and export the head to poinpt/polygon shp files
    
    Inputs: 
    - Model grid file
    - Head solution (i.e., *.hed file)

    Output: 
    - Heads at cell center (point shapefile)
    - Heads for each model cell (polygon shapefile)
    '''
    #hdsobj=bf.HeadUFile(hed_ifile) # mf-usg
    #usghds = hdsobj.get_data(kstpkper=(0, 0))
    
    # MODFLOW-2000
    print(f'Reading {hed_ifile}\n')
    hds = bf.HeadFile(hed_ifile)
    hds = hds.get_alldata() # [sp, lay, row, col]
    nsp, nl, nr, nc = hds.shape
    

    # Read shp of model grid
    gdf = gpd.read_file(grd_ifile)
    print(f'{gdf.crs}\n')
    
    # Write polygon shapefile of heads ----------------------------------------
    for sp in list_sp:
        for lay in list_layer:
            hds_at_sp_lay = hds[sp-1,lay-1,:,:]
            #gdf=gdf.assign(z=usghds[0].tolist())
            gdf[f'SP{sp}L{lay}'] = np.reshape(hds_at_sp_lay, [nr*nc,1])
    
    
    ofile_polygons = (f'{path2ofile}/heads_polygons.shp')    
    #gdf = gpd.GeoDataFrame(gdf, crs=crs, allow_override=True)
    #gdf = gpd.GeoDataFrame(gdf)
    gdf.to_file(driver = 'ESRI Shapefile', filename = ofile_polygons)      
    print(f'\nSaved {ofile_polygons}\n') 
    
    # Write point shapefile of heads ------------------------------------------
    ofile_points = (f'{path2ofile}/heads_points.shp')
    points = gdf.copy()

    # change geometry 
    points['geometry'] = points['geometry'].centroid  
    points['X'] = points.geometry.apply(lambda p: p.x)
    points['Y'] = points.geometry.apply(lambda p: p.y)
    points.to_file(driver = 'ESRI Shapefile', filename = ofile_points)   
    print(f'Saved {ofile_points}\n') 

def split_agr(input_text):
    splitted_text = re.split(',', input_text)
    out = []
    for i in splitted_text:
        out.append(int(i))
    return out
   
if __name__ == '__main__':
    
    # [1] Load input file -----------------------------------------------------
    #ifile = f'input/input.csv'
    grd_ifile = sys.argv[1]
    print(f'\nGrid file: {grd_ifile}\n')
    hed_ifile = sys.argv[2]
    print(f'Head file: {hed_ifile}\n')

    vmin = float(sys.argv[3])
    vmax = float(sys.argv[4])
    interval = float(sys.argv[5])
    crs = int(sys.argv[6]) # probably, not need this, enter any number 99999
    list_layer = sys.argv[7] # MODFLOW layer, not python index
    
    list_sp = sys.argv[8] # MODFLOW stress periods, not python 0 base index
    
    list_layer = split_agr(list_layer)
    list_sp = split_agr(list_sp)
    print(list_layer)
    print(list_sp)
    


    #e.g.,
    #python hed2shp.py "path_to_grid" "path_to_hds" con_min con_max con_interval crs list_lay list_sp
    #python hed2shp.py "../../../../../gis/shp/grid_with_centroids.shp" "../../100hr3_2023to2125.hds" 110 120 0.1 32149 "4,9" "1,120"


    # [00] Print version of libs in use =======================================
    print_ver()
    create_new_dir('output')

    # [00] specify input files/info ===========================================
    #grd_ifile='input/grid.shp'     # MODFLOW Model grid file
    #hed_ifile = 'input/model.hds'  # Head solution by MODFLOW
    
    
    path2ofile = 'output'            # To save outputs
    #crs = {'init': f'epsg:{crs}'}   # Coordinate Ref Sys

    # [01] Generate shapefile of head solution =================================
    # This include point shape file and poly shape file.
    #list_sp = [120, 216] # MODFLOW stress periods, not python 0 base index
    #list_layer = [4,9] # MODFLOW layer, not python index
    hed2shp_points_poly(grd_ifile, hed_ifile, path2ofile,crs, list_sp, list_layer)
    # =========================================================================

    # [2] Create head contours ================================================
    # if existing "heads_points.shp", no need to run 1. 
    ifile_shp_head = 'output/heads_points.shp' # Generated from Step 01
    gdf = gpd.read_file(ifile_shp_head)

    #res = 5
    #ml = interp2d(gdf,'z',res=res)
    for sp in list_sp:
        for lay in list_layer:
            print(f'processing sp={sp}, layer={lay}\n')
            ml = interp2d(gdf,f'SP{sp}L{lay}',res=np.nan)
            array = ml.interpolate_2D(method='linear',fill_value=np.nan) #fill_value=np.nan
            #arr_min = np.nanmin(array) # 121.2249
            #arr_max = np.nanmax(array) # 221.73709            

            ofile_contour = f'output/heads_contour_SP{sp}L{lay}.shp'
            ml.write_contours(array,path=ofile_contour,val_min=vmin,val_max=vmax, interval=interval, levels = None, crs=crs)
            # =========================================================================



    '''
    # Quick plot option =======================================================
    opt_show_plot = False
    if opt_show_plot:
        fig  = plt.subplot()
        ax = ml.plot_image(array,'Heads value\n')
        gdf.plot(ax=ax)
        for idx, row in gdf.iterrows():
            plt.annotate(text=row['z'], xy=row['coords'], horizontalalignment='left')
            # plt.annotate(s=row['WL_Res'], xy=row['coords'], horizontalalignment='left')

        CS = plt.contour(np.flipud(array), vmin=121.1,vmax=121.7 ,extent=ml.extent)
        plt.clabel(CS, inline=1, fmt='%1.1f', fontsize=14)
        ax.set_title('linear')
        plt.show()    

    # Write raster: Err, not sure why, come back later. 
    #path = 'test.tif'
    #ml.write_raster(array,path)    
    '''
