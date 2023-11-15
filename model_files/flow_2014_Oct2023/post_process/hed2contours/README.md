# head2shp
Convert MODFLOW head solution (2D MODFLOW-USG) to shapefiles (e.g., contours, poly, and point shapefiles)

Modified from https://github.com/rosskush/spatialpy

# Requirements: Python 3 with libs: flopy geopandas numpy rasterio matplotlib scipy


=============================================
# INSTALLATION Python Environment using Anaconda
=============================================

[1] Install Anaconda
- Download Anaconda https://repo.anaconda.com/archive/Anaconda3-2022.10-Windows-x86_64.exe
- Install Anaconda to your Windows PC

[2] Setup a new conda environment using one of the two methods below: 

Method 1 (easy, recommended): 
- Download flopy.yml included in this repo to your PC
- From Anaconda Prompt (Anaconda3) windows, type: conda env create -f flopy.yml

Method 2: 
- Open Anaconda Prompt (Anaconda3)
- Check list of current conda environments installed in your PC: conda env list
- Install a new conda environment: conda create -n flopy python=3
- Activate the just created conda environment: conda activate flopy
- Install some libraries needed for the script (all libs at once to avoid conflict): conda install -c conda-forge flopy geopandas numpy rasterio matplotlib scipy
=============================================


=============================================
# RUN SCRIPT ==================================
=============================================
- CLONE THIS REPO: git clone https://github.com/HPham-INTERA/head2shp.git (Windows machine)
- Open program "Anaconda Prompt (Anaconda3)"
- Activate flopy conda env: conda activate flopy
- Go to folder head2shp
- Run this command: 

python hed2shp.py "full_path_to_grid" "full_path_to_hds" con_min con_max con_interval crs

python hed2shp.py "input\grid.shp" "input\model.hds" 121.2 121.7 0.005 32149

or using full paths

python hed2shp.py "c:\Users\hpham\OneDrive - INTERA Inc\projects\51_contours\head2shp\input\grid.shp" "c:\Users\hpham\OneDrive - INTERA Inc\projects\51_contours\head2shp\input\model.hds" 121.2 121.7 0.005 32149



# See outputs in the output folder
heads_contour.cpg  heads_contour.shx  heads_points.shp    heads_polygons.prj
heads_contour.dbf  heads_points.cpg   heads_points.shx    heads_polygons.shp
heads_contour.prj  heads_points.dbf   heads_polygons.cpg  heads_polygons.shx
heads_contour.shp  heads_points.prj   heads_polygons.dbf

![alt text](https://github.com/HPham-INTERA/head2shp/blob/main/output/contour_qgis.png?raw=true)


