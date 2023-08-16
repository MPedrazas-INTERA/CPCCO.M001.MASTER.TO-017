
"""
Get recharge rates for specific SP.
Output as shapefiles

@author: MPedrazas
"""
import geopandas as gpd
import pandas as pd
import shutil
import os
import flopy
import numpy as np
from geopandas.tools import sjoin
import matplotlib.pyplot as plt
import glob

def transform_array2col(df, nrows, ncols):
    vals = []
    for i in range(0, nrows):
        for j in range(0, ncols):
            #            print(i,j)
            val = df[i, j]  # change rch array here
            vals.append(val)
    dfval = pd.DataFrame(vals, dtype=float, columns=['rech'])  # + str(myint-1))
    dfval.rech = dfval.rech * 1000 * 365.25 #convert from m/d (MODFLOW units) to mm/yr
    print("Converted 1 array 2 col")
    return dfval

def add_prj(gridShpDir, outputDir):
    # copy in template *.shx, *.shp, and *.prj from template file which contains R,C and X,Y coords (same size)
    tplname = 'grid_with_centroids'
    for file in glob.iglob(os.path.join(outputDir, '*.dbf')):
        name = os.path.splitext(file)[0]
        print(file)
        print(name)
        for ext in ['.prj', '.shx', '.shp']:
            shutil.copyfile(os.path.join(gridShpDir, tplname + ext),
                            os.path.join(outputDir, name + ext))
            print(name + ext)
    return None

def annualRecharge2shapefiles(ws, model_name, exe, gridShpDir, outputDir):
    #Step 0. Create shapefile output directory
    outputDir2 = os.path.join(outputDir, "shapefiles")
    if not os.path.isdir(outputDir2):
        os.makedirs(outputDir2)

    # Step 1. Load modflow model in flopy, get recharge package
    m = flopy.modflow.Modflow.load(model_name
        , verbose=True, model_ws=ws, exe_name=exe, check=False, load_only=['rch'])
    rch = m.get_package("rch")

    # Step 2. Get model geometry from model grid shapefile to generate shapefiles.
    gdf = gpd.read_file(os.path.join(gridShpDir,'grid_with_centroids.shp'))
    my_crs = gdf.crs

    # Step 3. Extract recharge rates (monthly rates, so only need 1 per year)
    Year2SPdict = {0:2014, 12:2015, 24:2016, 36:2017, 48:2018, 60:2019, 72:2020} # zero-based array, SPs are MODFLOW
    plot_vals = []
    for n, sp in enumerate(Year2SPdict.keys()):
        print(n, sp)
        df_rch = rch.rech.array[sp][0]
        plot_vals.append(np.unique(df_rch))
        dfval = transform_array2col(df_rch, 433, 875)
        dfval['row'] = gdf['I']
        dfval['column'] = gdf['J']
        # #export shapefile
        gdf2 = gpd.GeoDataFrame(dfval, crs=my_crs, geometry=gdf.geometry)
        gdf2.to_file(driver='ESRI Shapefile', filename=os.path.join(outputDir2, f'rch_w_geom_Y{Year2SPdict[sp]}.shp'))

    add_prj(gridShpDir, outputDir2)
    plot_vals2 = pd.DataFrame(plot_vals)
    plot_vals3 = plot_vals2 * 1000 * 365.25 #Converting m/day to mm/year
    plot_vals3.to_csv(os.path.join(outputDir2, '2014_2020_Rch_Vals.csv'), index=False, header=False)
    print("Generated shapefiles from recharge package.")
    return None


def genREFs(rch_ws, years, nr, nc):
    ######## STEP 1a - GIS Manipulation - reading and joining shapefiles

    print('reading grid shapefile')
    # ## point geometry
    grid_centroids = gpd.read_file(os.path.join(rch_ws, 'input', '100HR_gridded_shapefiles', 'grid_as_centroids.shp'))
    mycrs = grid_centroids.crs

    print('joining recharge with grid')
    for year in years:
        print(year)
        FeatureClass = gpd.read_file(
            os.path.join(rch_ws, 'RET_annual_shapefiles', f'{year}', f'RechargeEstimates_{year}.shp'))
        FeatureClass.to_crs(crs=mycrs, inplace=True)
        gdf = sjoin(grid_centroids, FeatureClass, how='left')
        rch = gdf[['RechargeRa']]  ##---> to format into REF file structure (7 columns, \n after col_max reached)
        rch_ref = rch.fillna(0)
        multiplier = 1 / (365.25 * 1000)  # * 12)  # unit conversion of ANNUAL recharge from mm/year to m/day - 7 s.f.
        rch_ref = rch_ref * multiplier

        print('finished spatial join')

        ###### STEP 1b - Writing out REF files
        ref_path = os.path.join(rch_ws, 'RETtoREFs')
        if not os.path.exists(ref_path):  ## sets or creates folder where ref files will be written
            os.mkdir(ref_path)
        print('writing out ref file')

        parray = np.empty((nr, nc))
        parray.fill(float(0))

        fileName = os.path.join(ref_path, f'rch_{year}.ref')
        f = open(fileName, "w")

        count = 0
        for row in range(nr):
            for col in range(nc):
                count += 1
                parray[row, col] = float(rch_ref.values[count - 1])  ##subtracted 1 for zero-based indexing
                if (parray[row, col] >= 0):
                    f.write(("  %08.06e" % parray[row, col]))
                if ((col + 1) % 7 == 0):
                    f.write("\n")
        f.close()
    return None


######### STEP 2 - Generating and Writing Recharge Pacakge
def writeRch(ref_path, df, ofile, years, nr, nc):
    ######## STEP 2a - Generating the Reference Dictionary:

    print('creating ref file dict')
    refDict = {}
    for year in years:
        if year not in refDict.keys():
            print(f"Ref exists for Year {year}")
            file = pd.read_csv(os.path.join(ref_path, f'rch_{year}_v02.ref'), delim_whitespace=True, header=None).values
            file = file.flatten()
            refDict.update({year: file})

    ########### Step 2b - Writing out recharge package:
    print('writing recharge package')
    # Dataframe with dates
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])

    # Open a file to write *.rch
    fid = open(ofile, 'w')
    fid.write(f'#MODFLOW 2000 RECHARGE PACKAGE\n')  # Line 0 of rch file
    fid.write(f'PARAMETER  0\n')  # Line 1 of rch file
    fid.write(f'         3        50\n')  # Line 2 of rch file

    for t, time in enumerate(range(len(df.sp))):
        print(f'SP={time+1},idx={t}\n') #+1 if zero-based, not the case for pred_2023_2125 dates_df.
        if df.start_date[t].month != 1: #not month 1=January
            fid.write('        -1        -1\n')
        else:  # month 1 = january
            if df.start_date[t].year == 2023:
                fid.write(f'         1         1\n')  # Line 3 of rch file
            else:
                fid.write(f'         1         0\n')  # Line 3 of rch file
            fid.write(
                f'        18   1.00000(10e12.4)                   -1     Recharge SP {time+1}, from {df.start_date[t]} to {df.end_date[t]}\n')  # line 4

            parray2 = np.empty((nr, nc))
            parray2.fill(float(0))
            count = 0
            for row in range(nr):
                for col in range(nc):
                    count += 1
                    parray2[row, col] = float(
                        refDict[df.start_date[t].year][count - 1])  ##subtracted 1 for zero-based indexing
                    if (parray2[row, col] >= 0):
                        fid.write(("  %08.04e" % parray2[row, col]))
                    if ((col + 1) % 10 == 0):
                        fid.write("\n")
                    if ((col + 1) == 875):
                        fid.write("\n")
    fid.close()
    print("Generated recharge package based on Recharge Arrays from RETtoREFs.")
    return None

def col2array(array1d, nr, nc):
    myArray = np.empty((nr, nc))
    myArray.fill(float(0))
    count = 0
    for row in range(nr):
        for col in range(nc):
            count += 1
            myArray[row, col] = float(array1d[count - 1])  ##subtracted 1 for zero-based indexing
    return myArray

def extend_recharge_package(mydf, ref_path, nr, nc, start_year):
    """
    This script generates the recharge addendum. Do not use as is, paste to original recharge pacakge you plan on extending.
    :param mydf: dataframe that will actually be appended (only those SPs + start, end dates)
    :param ref_path: path to refs generated from RET shapefiles for recharge
    :param nr: model number of rows
    :param nc: model number of columns
    :param start_year: year recharge package begins in - needed for a flag in the RCH package
    :return: recharge package addendum to add to original recharge package
    """
    fid = open(ofile, 'w')
    for t, sp in enumerate(mydf.sp):
        print(f'SP={sp}\n')
        if mydf.SPstart.iloc[t].month != 1: #monthly SPs that aren't January
            fid.write('        -1        -1\n')
        else:  # SPs (monthly or annual) that are January
            if mydf.SPstart.iloc[t].year == start_year:
                fid.write(f'         1         1\n')  # Line 3 of pred rch file
            else:
                fid.write(f'         1         0\n')
            fid.write(
                f'        18   1.00000(10e12.4)                   -1     Recharge SP {sp}, from {mydf.SPstart.iloc[t]} to {mydf.SPend.iloc[t]}\n')  # line 4
            year = mydf.SPstart.iloc[t].year
            print(f"Only iterating once through {year}")
            print(f"Reading ref for Year {year}")
            ref = pd.read_csv(os.path.join(ref_path, f'rch_{year}.ref'), delim_whitespace=True, header=None).values
            ref = ref.flatten()
            myArray = np.empty((nr, nc))
            myArray.fill(float(0))
            count = 0
            for row in range(nr):
                for col in range(nc):
                    count += 1
                    myArray[row, col] = float(ref[count - 1])  ##subtracted 1 for zero-based indexing
                    if (myArray[row, col] >= 0):
                        fid.write(("  %08.04e" % myArray[row, col]))
                    if ((col + 1) % 10 == 0):
                        fid.write("\n")
                    if ((col + 1) == 875):
                        fid.write("\n")
            print(f"Wrote array for year {year}")
    fid.close()

if __name__ == "__main__":

    cwd = os.getcwd()
    # outputDir = os.path.join(os.path.dirname(cwd), 'model_packages', 'hist_2014_2021', 'rch', 'output')
    outputDir = os.path.join(os.path.dirname(cwd), 'model_packages', 'pred_2023_2125', 'rch', 'output')
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    nr, nc = 433, 875  # number of modelgrid rows and columns
    rch_ws = os.path.dirname(outputDir)
    ref_path = os.path.join(rch_ws, 'RETtoREFs')

    ## If you'd like to write a recharge file using REFs (from scratch):
    write_rch_pckg = True
    if write_rch_pckg:
        ofile = os.path.join(outputDir, f'100hr3_2023to2125.rch')
        inputDir = os.path.join(cwd, "input")
        years = list(range(2023,2125+1))
        dates_df = pd.read_csv(os.path.join(inputDir, "sp_2023to2125.csv"))
        writeRch(ref_path, dates_df, ofile, years, nr, nc)

    ### If you'd like to append/extend a recharge package
    ##Define dates you wish to append to recharge package:
    append = False
    if append:
        df = pd.read_csv("input/sp_2014_2022.csv")
        df.dropna(inplace=True)
        df.SPstart = pd.to_datetime(df.SPstart); df.SPend = pd.to_datetime(df.SPend)
        df.sp = df.sp.astype(int)
        mydf = df.loc[df.sp > 84] #Appending to existing recharge package, extending from Dic 2020 to Dic 2022.
        start_year = 2014
        ofile = os.path.join(rch_ws, "output", "2021to2022.rch")
        extend_recharge_package(mydf, ref_path, nr, nc, start_year)

    ### Load model in flopy, convert recharge to shapefiles:
    # gridShpDir = os.path.join(os.path.dirname(cwd), 'gis', 'shp', 'grid_with_centroids')
    # exe = os.path.join(os.path.dirname(cwd), "executables", "windows", "mf2k-mst-chprc08dpv.exe")
    # ws = os.path.join(os.path.dirname(cwd), "model_files", "flow_2014_2020")
    # model_name = "DHmodel_2014to2020.nam"
    # annualRecharge2shapefiles(ws, model_name, exe, gridShpDir, outputDir)

    ### Convert RET shapefiles to REF files:
    # years = [2021, 2022]
    # nr, nc = 433, 875  # number of modelgrid rows and columns
    # rch_ws = os.path.dirname(outputDir)
    # genREFs(rch_ws, years, nr, nc)

