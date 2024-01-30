import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np


def gen_gdf(chemdata):
    df = pd.merge(chemdata, wells[["ID", "X", "Y"]], left_on="NAME", right_on="ID")
    df['DATE'] = df['DATE'].dt.strftime('%Y-%m-%d')
    # Create a GeoDataFrame from the merged DataFrame
    geometry = [Point(xy) for xy in zip(df['X'], df['Y'])]

    dummy = gpd.read_file(os.path.join(wdir, "gis", "shp", "River.shp"))  # get correct projection
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=dummy.crs)

    return gdf

def resample_to_monthly(wells, df):
    """
    :param df: columns need to be named NAME/ID and EVENT/DATE
    :param woi: list of WELLS of interest
    :return: df_monthly
    """
    df.DATE = pd.to_datetime(df.DATE)
    df_monthly = pd.DataFrame()
    for well in wells.ID.unique():
        try:
            print(well)
            mywell = df.loc[df.NAME == well]
            mywell2 = mywell.resample('MS', on='DATE').mean() #MS is first day of month, M is last day of month.
            mywell2["NAME"] = well
            df_monthly = df_monthly.append(mywell2)
        except:
            pass
    df_monthly.dropna(subset=["VAL"], inplace=True)
    df_monthly.reset_index(inplace=True)
    return df_monthly

if __name__ == "__main__":
    cwd = os.getcwd()
    wdir = os.path.dirname(cwd)

    zone = "100D"
    wells = pd.read_csv(os.path.join(cwd, 'input', 'monitoring_wells_coords_ij_100D.csv'))

    chemdir = os.path.join(cwd, 'output', 'concentration_data', '2014to2023', f'{zone}')
    chemdata1 = pd.read_csv(os.path.join(chemdir, "Cr_obs_2014_2023_100D_mp.csv"))
    chemdata1.rename(columns={"STD_VALUE_RPTD": "VAL"}, inplace=True)
    chemdata1['DATE'] = pd.to_datetime(chemdata1['DATE'])
    chemdata1.drop(columns=["REVIEW_QUALIFIER"], inplace=True)

    ### STEP 1: Data wrangling chemdata2 (Nov to Jan 2024 data) so it looks like chemdata1:
    rawchemdata2 = pd.read_excel(os.path.join(wdir, "data", "hydrochemistry","100D_ChemData_NovthroughJan2024.xlsx"), engine="openpyxl")
    # Melt the DataFrame to unpivot the columns "Apr-23" to "Jan-24" into rows
    chemdata2 = pd.melt(rawchemdata2, id_vars=['FullName', 'TYPE', 'NAME'], var_name='DATE', value_name='VAL')
    chemdata2['DATE'] = chemdata2['DATE'].astype(str)
    chemdata2['DATE'] = chemdata2['DATE'].str.replace(r'\.\d+', '')
    chemdata2['DATE'] = pd.to_datetime(chemdata2['DATE'])
    chemdata2 = chemdata2[['NAME', 'DATE', 'VAL', 'TYPE']]
    # Remove rows where VAL == 'X'
    chemdata2 = chemdata2[chemdata2['VAL'] != 'X']
    # Remove rows where VAL is NaN
    chemdata2 = chemdata2.dropna(subset=['VAL'])

    # Extract letters from VAL column and put them in FLAGS column
    chemdata2['FLAG'] = chemdata2['VAL'].apply(lambda x: x.split('(')[-1][0] if isinstance(x, str) and '(' in x else None)
    chemdata2['VAL'] = chemdata2['VAL'].apply(lambda x: x.split('(')[0].strip() if isinstance(x, str) else x)
    # Save Nov to Jan 2024 chemistry data
    chemdata2.to_csv(os.path.join(cwd, 'output', 'concentration_data', '2023to2024', f'{zone}', "Cr_obs_100D.csv"), index=False)
    chemdata2.drop(columns=["TYPE", 'FLAG'], inplace=True)
    ### STEP 2: NOT DONE YET. Make sure all the values in chemdata2 from April 2023 to Oct 2023 exist in chemdata1.

    ### STEP 3: Generate shapefile
    chemdata2_Nov23 = chemdata2.loc[chemdata2.DATE >= pd.to_datetime("11/01/2023")]
    combined_chemdata = pd.concat([chemdata1, chemdata2_Nov23])
    combined_chemdata["VAL"] = combined_chemdata["VAL"].astype(float)
    combined_chemdata.sort_values(by=["NAME", "DATE"], inplace=True)

    # Export as a shapefile: RAW DATA
    gdf = gen_gdf(chemdata = combined_chemdata)
    output_shapefile = os.path.join(wdir,  "gis", "shp", 'chem_obs_cy2014_Jan2024_raw.shp')
    gdf.to_file(output_shapefile, driver='ESRI Shapefile')

    # Export as a shapefile: RAW DATA
    combined_chemdata_monthly = resample_to_monthly(wells=wells, df=combined_chemdata)
    gdf2 = gen_gdf(chemdata = combined_chemdata_monthly)
    output_shapefile = os.path.join(wdir,  "gis", "shp", 'chem_obs_cy2014_Jan2024_monthly.shp')
    gdf2.to_file(output_shapefile, driver='ESRI Shapefile')
    print("Saved shapefiles")


